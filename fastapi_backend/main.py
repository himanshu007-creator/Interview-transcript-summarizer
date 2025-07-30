from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

from .openrouter import get_openrouter_model
from .langchain_example import (
    run_simple_example, 
    run_parallel_example, 
    run_sequence_example,
    create_simple_chain
)
from .handlers.product_feedback import ProductFeedbackProcessor
from .handlers.interview_processor import InterviewProcessor

# Load environment variables
load_dotenv()

app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI application with OpenRouter AI/LLM integration and LangChain",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "anthropic/claude-3.5-sonnet"


class ChatResponse(BaseModel):
    response: str
    model: str


class TopicRequest(BaseModel):
    topic: str


class CategoryRequest(BaseModel):
    category: str


class ProductFeedbackRequest(BaseModel):
    product_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Name of the product being reviewed",
        example="TestProduct"
    )
    feedback: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="Customer feedback text",
        example="This product is excellent and works perfectly!"
    )
    model: Optional[str] = Field(
        default="anthropic/claude-3.5-sonnet",
        description="OpenRouter model to use for processing",
        example="anthropic/claude-3.5-sonnet"
    )

    @validator('product_name')
    def validate_product_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Product name cannot be empty')
        return v.strip()

    @validator('feedback')
    def validate_feedback(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Feedback cannot be empty')
        return v.strip()

    @validator('model')
    def validate_model(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Model name cannot be empty string')
        return v.strip() if v else "anthropic/claude-3.5-sonnet"


class InterviewTranscriptRequest(BaseModel):
    transcript: str = Field(
        ..., 
        min_length=50, 
        max_length=50000,
        description="Timestamped interview transcript",
        example="00:00:10   introduction   Welcome to the interview, please introduce yourself\n00:02:10   problem description   Can you describe a challenging problem you solved?"
    )
    model: Optional[str] = Field(
        default="anthropic/claude-3.5-sonnet",
        description="OpenRouter model to use for processing",
        example="anthropic/claude-3.5-sonnet"
    )

    @validator('transcript')
    def validate_transcript(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Transcript cannot be empty')
        return v.strip()

    @validator('model')
    def validate_model(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Model name cannot be empty string')
        return v.strip() if v else "anthropic/claude-3.5-sonnet"


class InterviewSummaryResponse(BaseModel):
    summary: str = Field(
        ..., 
        description="Overall interview summary",
        example="The candidate demonstrated strong technical skills and problem-solving abilities during the interview."
    )
    highlights: List[str] = Field(
        ..., 
        description="Key positive findings from the interview",
        example=["Strong problem-solving approach", "Good communication skills", "Relevant experience"]
    )
    lowlights: List[str] = Field(
        ..., 
        description="Concerning or off-track findings from the interview",
        example=["Some knowledge gaps in advanced topics", "Could improve on system design concepts"]
    )
    key_named_entities: Dict[str, str] = Field(
        ..., 
        description="Candidate information extracted as key-value pairs",
        example={
            "role": "Senior Software Engineer",
            "current_company": "Tech Corp",
            "experience_years": "5 years",
            "key_skills": "Python, React, AWS"
        }
    )
    model: str = Field(
        ..., 
        description="OpenRouter model used for processing",
        example="anthropic/claude-3.5-sonnet"
    )
    processing_time: Optional[float] = Field(
        None, 
        description="Processing time in seconds",
        example=2.45
    )


class ProductFeedbackResponse(BaseModel):
    product_name: str = Field(
        ...,
        description="Name of the product that was reviewed",
        example="TestProduct"
    )
    feedback: str = Field(
        ...,
        description="Original customer feedback text",
        example="This product is excellent and works perfectly!"
    )
    classification: str = Field(
        ...,
        description="Sentiment classification result",
        example="positive"
    )
    response: str = Field(
        ...,
        description="Generated response to the feedback",
        example="Thank you for your positive feedback about TestProduct!"
    )
    model: str = Field(
        ...,
        description="OpenRouter model used for processing",
        example="anthropic/claude-3.5-sonnet"
    )
    processing_time: Optional[float] = Field(
        default=None,
        description="Time taken to process the feedback in seconds",
        example=1.23
    )

    @validator('classification')
    def validate_classification(cls, v):
        valid_classifications = ['positive', 'negative', 'neutral', 'escalate']
        if v not in valid_classifications:
            raise ValueError(f'Classification must be one of: {", ".join(valid_classifications)}')
        return v


@app.get("/")
async def root():
    """Root endpoint returning basic API information."""
    return {
        "message": "FastAPI Backend API",
        "version": "1.0.0",
        "description": "FastAPI application with OpenRouter integration and LangChain"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/feedback/process", response_model=ProductFeedbackResponse)
async def process_product_feedback(request: ProductFeedbackRequest):
    """
    Process product feedback through sentiment classification and response generation.
    
    This endpoint:
    1. Validates the input request (product_name and feedback are required)
    2. Checks API key configuration
    3. Processes feedback through LangChain classification and response generation
    4. Returns structured response with classification and generated reply
    5. Handles errors gracefully with appropriate HTTP status codes
    """
    try:
        # Validate API key configuration
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Configuration Error",
                    "message": "OPENROUTER_API_KEY not configured. Please check server configuration.",
                    "type": "configuration_error"
                }
            )
        
        # Initialize the feedback processor with the requested model
        try:
            processor = ProductFeedbackProcessor(model_name=request.model)
        except ValueError as e:
            # Handle processor initialization errors (e.g., invalid model)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Processor Initialization Failed",
                    "message": str(e),
                    "type": "initialization_error"
                }
            )
        
        # Process the feedback
        result = await processor.process_feedback(
            product_name=request.product_name,
            feedback=request.feedback
        )
        
        # Check if processing was successful
        if not result.get("success", True):
            # Processing failed but we have a fallback response
            error_detail = result.get("error", "Unknown processing error")
            
            # Log the error but return the fallback response
            import logging
            logging.warning(f"Feedback processing failed with fallback: {error_detail}")
            
            # Return the fallback response with a 200 status since we have a valid response
            return ProductFeedbackResponse(
                product_name=result["product_name"],
                feedback=result["feedback"],
                classification=result["classification"],
                response=result["response"],
                model=result["model"],
                processing_time=result.get("processing_time")
            )
        
        # Return successful processing result
        return ProductFeedbackResponse(
            product_name=result["product_name"],
            feedback=result["feedback"],
            classification=result["classification"],
            response=result["response"],
            model=result["model"],
            processing_time=result.get("processing_time")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except ValueError as e:
        # Handle validation errors from Pydantic or processor
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "type": "validation_error"
            }
        )
        
    except Exception as e:
        # Handle any other unexpected errors
        import logging
        logging.error(f"Unexpected error in feedback processing endpoint: {e}", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your feedback. Please try again later.",
                "type": "internal_error"
            }
        )


@app.post("/interview/process", response_model=InterviewSummaryResponse)
async def process_interview_transcript(request: InterviewTranscriptRequest):
    """
    Process interview transcript through parallel AI analysis.
    
    This endpoint:
    1. Validates the input transcript (must be 50-50,000 characters)
    2. Checks API key configuration
    3. Processes transcript through parallel LangChain analysis (summary, highlights/lowlights, entities)
    4. Returns structured response with all analysis results
    5. Handles errors gracefully with appropriate HTTP status codes and fallback responses
    """
    try:
        # Validate API key configuration
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Configuration Error",
                    "message": "OPENROUTER_API_KEY not configured. Please check server configuration.",
                    "type": "configuration_error"
                }
            )
        
        # Initialize the interview processor with the requested model
        try:
            processor = InterviewProcessor(model_name=request.model)
        except ValueError as e:
            # Handle processor initialization errors (e.g., invalid model)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Processor Initialization Failed",
                    "message": str(e),
                    "type": "initialization_error"
                }
            )
        
        # Process the interview transcript
        result = await processor.process_interview(transcript=request.transcript)
        
        # Check if processing was successful
        if not result.get("success", True):
            # Processing failed but we have a fallback response
            error_detail = result.get("error", "Unknown processing error")
            
            # Log the error but return the fallback response
            import logging
            logging.warning(f"Interview processing failed with fallback: {error_detail}")
            
            # Return the fallback response with a 200 status since we have a valid response
            return InterviewSummaryResponse(
                summary=result["summary"],
                highlights=result["highlights"],
                lowlights=result["lowlights"],
                key_named_entities=result["key_named_entities"],
                model=result["model"],
                processing_time=result.get("processing_time")
            )
        
        # Return successful processing result
        return InterviewSummaryResponse(
            summary=result["summary"],
            highlights=result["highlights"],
            lowlights=result["lowlights"],
            key_named_entities=result["key_named_entities"],
            model=result["model"],
            processing_time=result.get("processing_time")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except ValueError as e:
        # Handle validation errors from Pydantic or processor
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "type": "validation_error"
            }
        )
        
    except Exception as e:
        # Handle any other unexpected errors
        import logging
        logging.error(f"Unexpected error in interview processing endpoint: {e}", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your interview transcript. Please try again later.",
                "type": "internal_error"
            }
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat endpoint using OpenRouter models."""
    try:
        # Check if API key is configured
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OPENROUTER_API_KEY not configured"
            )
        
        # Get the model
        model = get_openrouter_model(request.model)
        
        # Generate response
        response = model.invoke(request.message)
        
        return ChatResponse(
            response=response.content,
            model=request.model
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/langchain/simple")
async def langchain_simple_chat(request: ChatRequest):
    """Simple LangChain chat endpoint."""
    try:
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OPENROUTER_API_KEY not configured"
            )
        
        chain = create_simple_chain()
        result = await chain.ainvoke({"input": request.message})
        
        return {
            "response": result,
            "model": request.model,
            "chain_type": "simple"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/langchain/parallel")
async def langchain_parallel_example(request: TopicRequest):
    """Parallel LangChain example - generates both joke and poem."""
    try:
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OPENROUTER_API_KEY not configured"
            )
        
        result = await run_parallel_example()
        
        return {
            "topic": request.topic,
            "results": result,
            "chain_type": "parallel"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/langchain/sequence")
async def langchain_sequence_example(request: CategoryRequest):
    """Sequence LangChain example - generates topic then content."""
    try:
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OPENROUTER_API_KEY not configured"
            )
        
        result = await run_sequence_example()
        
        return {
            "category": request.category,
            "result": result,
            "chain_type": "sequence"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_available_models():
    """List some popular OpenRouter models."""
    return {
        "models": [
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-haiku",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro"
        ]
    }


@app.get("/langchain/examples")
async def list_langchain_examples():
    """List available LangChain examples."""
    return {
        "examples": [
            {
                "endpoint": "/langchain/simple",
                "description": "Simple chat using LangChain prompt template",
                "method": "POST",
                "body": {"message": "Your question here", "model": "anthropic/claude-3.5-sonnet"}
            },
            {
                "endpoint": "/langchain/parallel",
                "description": "Parallel execution - generates joke and poem simultaneously",
                "method": "POST", 
                "body": {"topic": "programming"}
            },
            {
                "endpoint": "/langchain/sequence",
                "description": "Sequential execution - generates topic then writes about it",
                "method": "POST",
                "body": {"category": "technology"}
            },
            {
                "endpoint": "/feedback/process",
                "description": "Product feedback processing - classifies sentiment and generates appropriate responses",
                "method": "POST",
                "body": {
                    "product_name": "TestProduct",
                    "feedback": "This product is excellent and works perfectly!",
                    "model": "anthropic/claude-3.5-sonnet"
                },
                "response_example": {
                    "product_name": "TestProduct",
                    "feedback": "This product is excellent and works perfectly!",
                    "classification": "positive",
                    "response": "Thank you for your positive feedback about TestProduct!",
                    "model": "anthropic/claude-3.5-sonnet",
                    "processing_time": 1.23
                }
            },
            {
                "endpoint": "/interview/process",
                "description": "Interview transcript processing - generates summary, highlights, lowlights, and candidate information through parallel AI analysis",
                "method": "POST",
                "body": {
                    "transcript": "00:00:10   introduction   Welcome to the interview, please introduce yourself\n00:02:10   problem description   Can you describe a challenging problem you solved?\n00:04:00   solution discussion   How did you approach this problem?",
                    "model": "anthropic/claude-3.5-sonnet"
                },
                "response_example": {
                    "summary": "The candidate demonstrated strong technical skills and problem-solving abilities during the interview.",
                    "highlights": ["Strong problem-solving approach", "Good communication skills", "Relevant experience"],
                    "lowlights": ["Some knowledge gaps in advanced topics"],
                    "key_named_entities": {
                        "role": "Senior Software Engineer",
                        "current_company": "Tech Corp",
                        "experience_years": "5 years",
                        "key_skills": "Python, React, AWS"
                    },
                    "model": "anthropic/claude-3.5-sonnet",
                    "processing_time": 2.45
                }
            }
        ]
    }