import os
import logging
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# LangChain imports
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel

# OpenRouter integration
from fastapi_backend.openrouter import ChatOpenRouter

# Load environment variables
load_dotenv()


class InterviewProcessor:
    def __init__(self, model_name: str = "anthropic/claude-3.5-sonnet"):
        self.model_name = model_name
        
        # Verify API key is configured
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY must be configured in environment")
        
        # Initialize the model with appropriate settings for interview processing
        self.model = ChatOpenRouter(
            model_name=self.model_name,
            max_tokens=1024,  # Higher token limit for comprehensive summaries
            temperature=0.3   # Lower temperature for consistent, structured responses
        )
        
        # Initialize parallel processing chains (will be created lazily)
        self._parallel_chains = None
    
    async def process_interview(self, transcript: str) -> Dict[str, Any]:
        """
        Main method to process interview transcript through parallel AI analysis.
        
        Args:
            transcript: Timestamped interview transcript
            
        Returns:
            Dict containing summary, highlights, lowlights, and key_named_entities
        """
        # Record start time for performance monitoring
        start_time = time.time()
        
        try:
            # Input validation and preprocessing
            processed_transcript = await self.preprocess_transcript(transcript)
            
            logging.info(f"Processing interview transcript ({len(processed_transcript)} characters)")
            
            # Execute parallel processing chains
            parallel_start = time.time()
            parallel_chains = self._create_parallel_chains()
            
            # Run all three chains in parallel
            results = await parallel_chains.ainvoke({
                "transcript": processed_transcript
            })
            
            parallel_time = time.time() - parallel_start
            logging.info(f"Parallel processing completed in {parallel_time:.2f}s")
            
            # Combine and validate results
            combined_results = self._combine_results(results)
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Return successful result
            final_result = {
                **combined_results,
                "model": self.model_name,
                "processing_time": round(total_time, 3),
                "success": True
            }
            
            logging.info(f"Interview processing completed successfully in {total_time:.2f}s")
            return final_result
            
        except ValueError as e:
            # Handle validation errors
            processing_time = time.time() - start_time
            error_msg = f"Input validation failed: {str(e)}"
            logging.error(error_msg)
            
            return self._create_fallback_response(
                transcript if 'transcript' in locals() else "",
                error_msg,
                processing_time
            )
            
        except Exception as e:
            # Handle all other processing errors with comprehensive fallback
            processing_time = time.time() - start_time
            error_msg = f"Processing failed: {str(e)}"
            logging.error(error_msg, exc_info=True)
            
            return self._create_fallback_response(
                transcript if 'transcript' in locals() else "",
                error_msg,
                processing_time
            )
    
    async def preprocess_transcript(self, transcript: str) -> str:
        """
        Preprocess and validate interview transcript.
        
        Args:
            transcript: Raw interview transcript
            
        Returns:
            Cleaned and validated transcript
            
        Raises:
            ValueError: If transcript is invalid or improperly formatted
        """
        if not transcript or not isinstance(transcript, str):
            raise ValueError("transcript must be a non-empty string")
        
        # Remove trailing spaces and normalize formatting
        cleaned_transcript = transcript.strip()
        
        if not cleaned_transcript:
            raise ValueError("transcript cannot be empty after trimming")
        
        # Validate minimum length for meaningful processing
        if len(cleaned_transcript) < 50:
            raise ValueError("transcript must be at least 50 characters long")
        
        # Validate maximum length to prevent token overflow
        if len(cleaned_transcript) > 50000:
            raise ValueError("transcript must be less than 50,000 characters")
        
        # Basic format validation - check for timestamp-like patterns
        lines = cleaned_transcript.split('\n')
        timestamp_lines = [line for line in lines if self._has_timestamp_pattern(line)]
        
        if len(timestamp_lines) < 2:
            logging.warning("Transcript may not contain proper timestamp formatting")
        
        # Normalize line endings and remove excessive whitespace
        normalized_lines = []
        for line in lines:
            normalized_line = ' '.join(line.split())  # Normalize whitespace
            if normalized_line:  # Skip empty lines
                normalized_lines.append(normalized_line)
        
        processed_transcript = '\n'.join(normalized_lines)
        
        logging.info(f"Transcript preprocessed: {len(lines)} lines -> {len(normalized_lines)} lines")
        return processed_transcript
    
    def _has_timestamp_pattern(self, line: str) -> bool:
        """Check if a line contains a timestamp pattern like 00:00:10 or similar."""
        import re
        # Look for patterns like HH:MM:SS or MM:SS at the beginning of lines
        timestamp_pattern = r'^\s*\d{1,2}:\d{2}(:\d{2})?\s+'
        return bool(re.match(timestamp_pattern, line))
    
    def _create_parallel_chains(self) -> RunnableParallel:
        """
        Create parallel LangChain processing architecture for interview analysis.
        
        Returns:
            RunnableParallel containing three processing chains
        """
        if self._parallel_chains is not None:
            return self._parallel_chains
        
        # Create output parser
        output_parser = StrOutputParser()
        
        # Chain 1: Interview Summarization
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert interview analyst. Create a comprehensive but concise summary of the interview transcript.

Focus on:
- Overall interview flow and structure
- Key topics discussed
- Candidate's main responses and approaches
- Interview outcome and general impression

Keep the summary between 150-300 words. Be objective and professional."""),
            ("human", """Interview Transcript:
{transcript}

Summary:""")
        ])
        
        summary_chain = summary_prompt | self.model | output_parser
        
        # Chain 2: Highlights and Lowlights Extraction
        highlights_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert interview analyst. Extract key highlights (positive findings) and lowlights (concerning or off-track findings) from the interview.

Return your response in this exact JSON format:
{{
  "highlights": ["highlight 1", "highlight 2", "highlight 3"],
  "lowlights": ["lowlight 1", "lowlight 2"]
}}

Highlights should include:
- Strong technical skills demonstrated
- Good problem-solving approaches
- Positive behavioral indicators
- Relevant experience mentioned

Lowlights should include:
- Knowledge gaps or weaknesses
- Poor communication or unclear responses
- Red flags or concerning behaviors
- Off-topic or irrelevant responses

Provide 3-5 highlights and 1-3 lowlights. Be specific and actionable."""),
            ("human", """Interview Transcript:
{transcript}

JSON Response:""")
        ])
        
        highlights_chain = highlights_prompt | self.model | output_parser
        
        # Chain 3: Candidate Information Extraction
        entities_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert interview analyst. Extract key candidate information and tangible details from the interview transcript.

Return your response in this exact JSON format:
{{
  "role": "position they're applying for or current role",
  "current_company": "their current or most recent company",
  "experience_years": "years of relevant experience",
  "key_skills": "main technical skills mentioned",
  "education": "educational background if mentioned",
  "location": "location if mentioned",
  "other_details": "any other relevant tangible information"
}}

Only include information that is explicitly mentioned in the transcript. Use "Not mentioned" for fields where no information is provided. Be factual and avoid assumptions."""),
            ("human", """Interview Transcript:
{transcript}

JSON Response:""")
        ])
        
        entities_chain = entities_prompt | self.model | output_parser
        
        # Create parallel execution of all three chains
        self._parallel_chains = RunnableParallel(
            summary=summary_chain,
            highlights_lowlights=highlights_chain,
            entities=entities_chain
        )
        
        return self._parallel_chains
    
    def _combine_results(self, results: Dict[str, str]) -> Dict[str, Any]:
        """
        Combine and validate results from parallel processing chains.
        
        Args:
            results: Dictionary containing results from parallel chains
            
        Returns:
            Combined and validated results dictionary
        """
        import json
        
        combined = {
            "summary": "",
            "highlights": [],
            "lowlights": [],
            "key_named_entities": {}
        }
        
        # Process summary
        if "summary" in results:
            combined["summary"] = results["summary"].strip()
        
        # Process highlights and lowlights
        if "highlights_lowlights" in results:
            try:
                highlights_data = json.loads(results["highlights_lowlights"])
                combined["highlights"] = highlights_data.get("highlights", [])
                combined["lowlights"] = highlights_data.get("lowlights", [])
            except json.JSONDecodeError:
                logging.warning("Failed to parse highlights/lowlights JSON, using fallback")
                combined["highlights"] = ["Unable to extract highlights due to parsing error"]
                combined["lowlights"] = ["Unable to extract lowlights due to parsing error"]
        
        # Process entities
        if "entities" in results:
            try:
                entities_data = json.loads(results["entities"])
                combined["key_named_entities"] = entities_data
            except json.JSONDecodeError:
                logging.warning("Failed to parse entities JSON, using fallback")
                combined["key_named_entities"] = {"error": "Unable to extract entities due to parsing error"}
        
        return combined
    
    def _create_fallback_response(self, transcript: str, error_msg: str, processing_time: float) -> Dict[str, Any]:
        """
        Create a fallback response when processing fails.
        
        Args:
            transcript: Original transcript (may be empty)
            error_msg: Error message
            processing_time: Time spent processing
            
        Returns:
            Fallback response dictionary
        """
        return {
            "summary": "Unable to process interview transcript due to technical difficulties. Please try again or contact support.",
            "highlights": ["Processing failed - unable to extract highlights"],
            "lowlights": ["Processing failed - unable to extract lowlights"],
            "key_named_entities": {
                "error": "Unable to extract candidate information due to processing failure"
            },
            "model": self.model_name,
            "processing_time": round(processing_time, 3),
            "success": False,
            "error": error_msg
        }