import os
import logging
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# LangChain imports
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableSequence, RunnableBranch

# OpenRouter integration
from fastapi_backend.openrouter import ChatOpenRouter

# Load environment variables
load_dotenv()


class ProductFeedbackProcessor:
    def __init__(self, model_name: str = "anthropic/claude-3.5-sonnet"):
        self.model_name = model_name
        
        # Verify API key is configured
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY must be configured in environment")
        
        # Initialize the model with reduced token limits
        self.model = ChatOpenRouter(
            model_name=self.model_name,
            max_tokens=512,  # Reduced from default to save tokens
            temperature=0.3  # Lower temperature for more consistent, shorter responses
            )
            
        # Initialize chain components (will be created lazily)
        self._classification_chain = None
        self._response_branch = None
    
    async def process_feedback(self, product_name: str, feedback: str) -> Dict[str, Any]:
        # Record start time for performance monitoring
        start_time = time.time()
        try:
            # Input validation
            if not product_name or not isinstance(product_name, str):
                raise ValueError("product_name must be a non-empty string")
            
            if not feedback or not isinstance(feedback, str):
                raise ValueError("feedback must be a non-empty string")
            
            # Sanitize inputs and truncate if too long to save tokens
            product_name = product_name.strip()[:50]  # Limit product name length
            feedback = feedback.strip()[:300]  # Limit feedback length to save tokens
            
            if not product_name:
                raise ValueError("product_name cannot be empty after trimming")
            
            if not feedback:
                raise ValueError("feedback cannot be empty after trimming")
            
            logging.info(f"Processing feedback for product: {product_name}")
            
            # Step 1: Classify feedback sentiment
            classification_start = time.time()
            classification = await self.classify_feedback(product_name, feedback)
            classification_time = time.time() - classification_start
            
            logging.info(f"Classification completed in {classification_time:.2f}s: {classification}")
            
            # Step 2: Generate appropriate response based on classification
            response_start = time.time()
            response = await self.generate_response(product_name, feedback, classification)
            response_time = time.time() - response_start
            
            logging.info(f"Response generation completed in {response_time:.2f}s")
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Return successful result
            result = {
                "product_name": product_name,
                "feedback": feedback,
                "classification": classification,
                "response": response,
                "model": self.model_name,
                "processing_time": round(total_time, 3),
                "success": True
            }
    
            logging.info(f"Feedback processing completed successfully in {total_time:.2f}s")
            return result
            
        except ValueError as e:
            # Handle validation errors
            processing_time = time.time() - start_time
            error_msg = f"Input validation failed: {str(e)}"
            logging.error(error_msg)
            
            return {
                "product_name": product_name if 'product_name' in locals() else "",
                "feedback": feedback if 'feedback' in locals() else "",
                "classification": "escalate",
                "response": "We apologize, but there was an issue processing your feedback. Please contact our customer service team for assistance.",
                "model": self.model_name,
                "processing_time": round(processing_time, 3),
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            # Handle all other processing errors with comprehensive fallback
            processing_time = time.time() - start_time
            error_msg = f"Processing failed: {str(e)}"
            logging.error(error_msg, exc_info=True)
            
            # Provide fallback response based on available information
            fallback_product = product_name if 'product_name' in locals() and product_name else "your product"
            fallback_response = (
                f"Thank you for your feedback about {fallback_product}. "
                "We're currently experiencing technical difficulties. "
                "Our team will review your feedback and respond soon. "
                "For immediate assistance, please contact support."
            )
            
            return {
                "product_name": product_name if 'product_name' in locals() else "",
                "feedback": feedback if 'feedback' in locals() else "",
                "classification": "escalate",
                "response": fallback_response,
                "model": self.model_name,
                "processing_time": round(processing_time, 3),
                "success": False,
                "error": error_msg
            }
    
    def _create_classification_chain(self) -> RunnableSequence:
        if self._classification_chain is not None:
            return self._classification_chain
            
        # Create classification prompt template - shortened to save tokens
        classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """Classify customer feedback into one category:
- positive: satisfied/happy
- negative: dissatisfied/complaining  
- neutral: questions/unclear
- escalate: threats/severe issues

Respond with ONLY the category name."""),
            ("human", """Product: {product_name}
Feedback: {feedback}

Category:""")
        ])
    
        # Create output parser
        output_parser = StrOutputParser()
        
        # Create and cache the classification chain
        self._classification_chain = classification_prompt | self.model | output_parser
        
        return self._classification_chain
    
    def _create_positive_response_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """Generate a brief, friendly response to positive feedback. Thank the customer and encourage future engagement. Keep response under 100 words."""),
            ("human", """Product: {product_name}
Feedback: {feedback}

Response:""")
        ])
    
    def _create_negative_response_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """Generate a brief, empathetic response to negative feedback. Apologize, offer help, and provide next steps. Keep response under 100 words."""),
            ("human", """Product: {product_name}
            Feedback: {feedback}

            Response:""")
        ])
    
    def _create_neutral_response_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """Generate a brief response to neutral feedback. Thank them and ask for more details. Keep response under 100 words."""),
            ("human", """Product: {product_name}
Feedback: {feedback}

Response:""")
        ])
    
    def _create_escalation_response_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """Generate a brief escalation response. Acknowledge the concern and explain human agent will follow up. Keep response under 100 words."""),
            ("human", """Product: {product_name}
Feedback: {feedback}

Response:""")
        ])
    
    def _create_response_branch(self) -> RunnableBranch:
        if self._response_branch is not None:
            return self._response_branch
        
        # Create output parser for responses
        output_parser = StrOutputParser()
        
        # Create response chains for each classification type
        positive_chain = self._create_positive_response_template() | self.model | output_parser
        negative_chain = self._create_negative_response_template() | self.model | output_parser
        neutral_chain = self._create_neutral_response_template() | self.model | output_parser
        escalation_chain = self._create_escalation_response_template() | self.model | output_parser
        
        # Create fallback response chain for processing failures
        fallback_template = ChatPromptTemplate.from_messages([
            ("system", """Generate a brief fallback response acknowledging feedback and providing general assistance. Keep under 100 words."""),
            ("human", """Product: {product_name}
Feedback: {feedback}

Response:""")
        ])
        fallback_chain = fallback_template | self.model | output_parser
        
        # Create the response branch with conditional routing
        self._response_branch = RunnableBranch(
            # Route based on classification results
            (lambda x: x.get("classification") == "positive", positive_chain),
            (lambda x: x.get("classification") == "negative", negative_chain),
            (lambda x: x.get("classification") == "neutral", neutral_chain),
            (lambda x: x.get("classification") == "escalate", escalation_chain),
            # Default fallback for any other case
            fallback_chain
        )
        
        return self._response_branch
    
    def _create_complete_processing_chain(self) -> RunnableSequence:
        # Get the individual chain components
        classification_chain = self._create_classification_chain()
        response_branch = self._create_response_branch()
        
        # Create a chain that first classifies, then generates response
        def process_and_combine(inputs):
            async def _process():
                # First, classify the feedback
                classification = await classification_chain.ainvoke(inputs)
                classification = classification.strip().lower()
                
                # Validate classification
                valid_categories = ["positive", "negative", "neutral", "escalate"]
                if classification not in valid_categories:
                    classification = "escalate"
                
                # Create input for response generation
                response_input = {
                    "product_name": inputs["product_name"],
                    "feedback": inputs["feedback"],
                    "classification": classification
                }
                
                # Generate response
                response = await response_branch.ainvoke(response_input)
                
                return {
                    "classification": classification,
                    "response": response.strip(),
                    "product_name": inputs["product_name"],
                    "feedback": inputs["feedback"]
                }
            
            return _process()
        
        return process_and_combine
    
    async def classify_feedback(self, product_name: str, feedback: str) -> str:
        try:
            classification_chain = self._create_classification_chain()
            result = await classification_chain.ainvoke({
                "product_name": product_name,
                "feedback": feedback
            })
            
            # Clean and validate the result
            classification = result.strip().lower()
            valid_categories = ["positive", "negative", "neutral", "escalate"]
            
            if classification in valid_categories:
                return classification
            else:
                # If result is not a valid category, default to escalate
                logging.warning(f"Invalid classification result: {classification}. Defaulting to escalate.")
                return "escalate"
                
        except Exception as e:
            # Fallback to escalate if classification fails
            logging.error(f"Classification failed: {e}. Defaulting to escalate.")
            return "escalate"
    async def generate_response(self, product_name: str, feedback: str, classification: str) -> str:
        try:
            response_branch = self._create_response_branch()
            result = await response_branch.ainvoke({
                "product_name": product_name,
                "feedback": feedback,
                "classification": classification
            })
            
            return result.strip()
            
        except Exception as e:
            # Fallback response if generation fails - shortened to save tokens
            logging.error(f"Response generation failed: {e}. Using fallback response.")
            return f"Thank you for your feedback about {product_name}. We appreciate your input. For assistance, please contact our customer service team."
    
    async def process_with_complete_chain(self, product_name: str, feedback: str) -> Dict[str, Any]:
        try:
            # Create the complete processing chain
            complete_chain = self._create_complete_processing_chain()
            
            # Process through the complete chain
            result = await complete_chain({
                "product_name": product_name,
                "feedback": feedback
            })
            
            return result
            
        except Exception as e:
            logging.error(f"Complete chain processing failed: {e}")
            # Fallback to individual processing methods
            classification = await self.classify_feedback(product_name, feedback)
            response = await self.generate_response(product_name, feedback, classification)
            
            return {
                "classification": classification,
                "response": response,
                "product_name": product_name,
                "feedback": feedback
            }
    
    async def test_classification_prompt(self, product_name: str, feedback: str) -> str:
        return await self.classify_feedback(product_name, feedback)
    
    async def test_response_generation(self, product_name: str, feedback: str, classification: str) -> str:
        return await self.generate_response(product_name, feedback, classification)
