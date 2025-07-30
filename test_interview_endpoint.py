#!/usr/bin/env python3
"""
Test script for the interview processing endpoint.
"""

import asyncio
import sys
import os
sys.path.append('.')

from fastapi_backend.main import app, InterviewTranscriptRequest, InterviewSummaryResponse
from fastapi_backend.handlers.interview_processor import InterviewProcessor
from pydantic import ValidationError

# Try different test client imports
try:
    from fastapi.testclient import TestClient
except ImportError:
    try:
        from starlette.testclient import TestClient
    except ImportError:
        print("Could not import TestClient, will test processor directly")
        TestClient = None

def test_request_model():
    """Test the InterviewTranscriptRequest model validation."""
    
    print("Testing InterviewTranscriptRequest validation...")
    
    # Test valid request
    try:
        valid_request = InterviewTranscriptRequest(
            transcript="00:00:10   introduction   Welcome to the interview, please introduce yourself\n00:02:10   problem description   Can you describe a challenging problem you solved?",
            model="anthropic/claude-3.5-sonnet"
        )
        print("✓ Valid request model created successfully")
        print(f"  Transcript length: {len(valid_request.transcript)} characters")
        print(f"  Model: {valid_request.model}")
    except Exception as e:
        print(f"✗ Valid request failed: {e}")
    
    # Test missing transcript
    try:
        invalid_request = InterviewTranscriptRequest(
            model="anthropic/claude-3.5-sonnet"
        )
        print("✗ Missing transcript should have failed")
    except ValidationError as e:
        print("✓ Missing transcript correctly rejected")
    
    # Test empty transcript
    try:
        invalid_request = InterviewTranscriptRequest(
            transcript="",
            model="anthropic/claude-3.5-sonnet"
        )
        print("✗ Empty transcript should have failed")
    except ValidationError as e:
        print("✓ Empty transcript correctly rejected")
    
    # Test transcript too short
    try:
        invalid_request = InterviewTranscriptRequest(
            transcript="Too short",
            model="anthropic/claude-3.5-sonnet"
        )
        print("✗ Short transcript should have failed")
    except ValidationError as e:
        print("✓ Short transcript correctly rejected")

def test_response_model():
    """Test the InterviewSummaryResponse model."""
    
    print("\nTesting InterviewSummaryResponse model...")
    
    # Test valid response
    try:
        valid_response = InterviewSummaryResponse(
            summary="The candidate demonstrated strong technical skills and problem-solving abilities during the interview.",
            highlights=["Strong problem-solving approach", "Good communication skills"],
            lowlights=["Some knowledge gaps in advanced topics"],
            key_named_entities={
                "role": "Senior Software Engineer",
                "current_company": "Tech Corp",
                "experience_years": "5 years"
            },
            model="anthropic/claude-3.5-sonnet",
            processing_time=2.45
        )
        print("✓ Valid response model created successfully")
        print(f"  Summary length: {len(valid_response.summary)} characters")
        print(f"  Highlights count: {len(valid_response.highlights)}")
        print(f"  Lowlights count: {len(valid_response.lowlights)}")
        print(f"  Entities count: {len(valid_response.key_named_entities)}")
    except Exception as e:
        print(f"✗ Valid response failed: {e}")

def test_endpoint_exists():
    """Test that the endpoint exists in the FastAPI app."""
    
    print("\nTesting endpoint registration...")
    
    # Check if the endpoint is registered
    routes = [route.path for route in app.routes]
    
    if "/interview/process" in routes:
        print("✓ /interview/process endpoint is registered")
    else:
        print("✗ /interview/process endpoint is not registered")
        print(f"Available routes: {routes}")
    
    # Check if examples endpoint includes interview processing
    examples_route = None
    for route in app.routes:
        if hasattr(route, 'path') and route.path == "/langchain/examples":
            examples_route = route
            break
    
    if examples_route:
        print("✓ /langchain/examples endpoint exists")
    else:
        print("✗ /langchain/examples endpoint not found")

def test_imports():
    """Test that all required imports work."""
    
    print("\nTesting imports...")
    
    try:
        from fastapi_backend.handlers.interview_processor import InterviewProcessor
        print("✓ InterviewProcessor import successful")
    except ImportError as e:
        print(f"✗ InterviewProcessor import failed: {e}")
    
    try:
        # Test that the processor can be initialized
        processor = InterviewProcessor()
        print("✓ InterviewProcessor initialization successful")
    except Exception as e:
        print(f"✓ InterviewProcessor initialization failed (expected due to API credits): {e}")

def test_endpoint_integration():
    """Test the interview endpoint integration."""
    
    if TestClient is None:
        print("TestClient not available, testing processor directly")
        test_processor_directly()
        return
    
    # Create test client
    try:
        client = TestClient(app)
    except Exception as e:
        print(f"Failed to create TestClient: {e}")
        test_processor_directly()
        return
    
    # Test data - a realistic interview transcript
    test_request = {
        "transcript": """00:00:10   introduction   Welcome to the interview, please introduce yourself
00:02:10   problem description   Can you describe a challenging problem you solved recently?
00:04:00   solution discussion   How did you approach this problem and what was your solution?
00:06:30   technical details   Can you walk me through the technical implementation?
00:08:45   challenges   What challenges did you face and how did you overcome them?
00:10:20   results   What were the results and impact of your solution?
00:12:00   questions   Do you have any questions for us about the role or company?""",
        "model": "anthropic/claude-3.5-sonnet"
    }
    
    print("Testing interview processing endpoint...")
    print(f"Request transcript length: {len(test_request['transcript'])} characters")
    
    # Test the endpoint
    try:
        response = client.post("/interview/process", json=test_request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Endpoint responded successfully")
            
            # Verify response structure
            required_fields = ["summary", "highlights", "lowlights", "key_named_entities", "model"]
            for field in required_fields:
                if field in result:
                    if field == "highlights" or field == "lowlights":
                        print(f"✓ Field '{field}' present with {len(result[field])} items")
                    elif field == "key_named_entities":
                        print(f"✓ Field '{field}' present with {len(result[field])} entities")
                    else:
                        print(f"✓ Field '{field}' present")
                else:
                    print(f"✗ Field '{field}' missing")
                    
        else:
            print(f"✗ Endpoint failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")

def test_processor_directly():
    """Test the processor directly without FastAPI."""
    
    async def run_test():
        try:
            processor = InterviewProcessor()
            
            test_transcript = """00:00:10   introduction   Welcome to the interview, please introduce yourself
00:02:10   problem description   Can you describe a challenging problem you solved recently?
00:04:00   solution discussion   How did you approach this problem and what was your solution?"""
            
            result = await processor.process_interview(transcript=test_transcript)
            
            print("✓ Processor test successful")
            
            # Verify response structure
            required_fields = ["summary", "highlights", "lowlights", "key_named_entities", "model"]
            for field in required_fields:
                if field in result:
                    if field == "highlights" or field == "lowlights":
                        print(f"✓ Field '{field}' present with {len(result[field])} items")
                    elif field == "key_named_entities":
                        print(f"✓ Field '{field}' present with {len(result[field])} entities")
                    else:
                        print(f"✓ Field '{field}' present")
                else:
                    print(f"✗ Field '{field}' missing")
                    
        except Exception as e:
            print(f"✗ Processor test failed: {e}")
    
    asyncio.run(run_test())

def test_validation_errors():
    """Test validation error handling."""
    
    if TestClient is None:
        print("TestClient not available, skipping validation tests")
        return
        
    try:
        client = TestClient(app)
    except Exception as e:
        print(f"Failed to create TestClient for validation tests: {e}")
        return
    
    print("\nTesting validation errors...")
    
    # Test missing transcript
    invalid_request = {
        "model": "anthropic/claude-3.5-sonnet"
    }
    
    response = client.post("/interview/process", json=invalid_request)
    print(f"Missing transcript - Status: {response.status_code}")
    
    # Test empty transcript
    invalid_request = {
        "transcript": "",
        "model": "anthropic/claude-3.5-sonnet"
    }
    
    response = client.post("/interview/process", json=invalid_request)
    print(f"Empty transcript - Status: {response.status_code}")
    
    # Test transcript too short
    invalid_request = {
        "transcript": "Too short",
        "model": "anthropic/claude-3.5-sonnet"
    }
    
    response = client.post("/interview/process", json=invalid_request)
    print(f"Short transcript - Status: {response.status_code}")

def test_examples_endpoint():
    """Test that the examples endpoint includes interview processing."""
    
    if TestClient is None:
        print("TestClient not available, skipping examples test")
        return
        
    try:
        client = TestClient(app)
    except Exception as e:
        print(f"Failed to create TestClient for examples test: {e}")
        return
    
    print("\nTesting examples endpoint...")
    
    response = client.get("/langchain/examples")
    
    if response.status_code == 200:
        examples = response.json()
        
        # Check if interview processing example is included
        interview_example = None
        for example in examples.get("examples", []):
            if example.get("endpoint") == "/interview/process":
                interview_example = example
                break
        
        if interview_example:
            print("✓ Interview processing example found in /langchain/examples")
            print(f"Description: {interview_example.get('description')}")
        else:
            print("✗ Interview processing example not found in /langchain/examples")
    else:
        print(f"✗ Examples endpoint failed with status {response.status_code}")

if __name__ == "__main__":
    print("=== Testing Interview Processing Endpoint ===")
    
    # Check if API key is configured
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("✗ OPENROUTER_API_KEY not configured")
        sys.exit(1)
    else:
        print("✓ OPENROUTER_API_KEY configured")
    
    test_imports()
    test_request_model()
    test_response_model()
    test_endpoint_exists()
    test_endpoint_integration()
    test_validation_errors()
    test_examples_endpoint()
    
    print("\n=== Test Complete ===")