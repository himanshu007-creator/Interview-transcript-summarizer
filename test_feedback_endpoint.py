#!/usr/bin/env python3
"""
Test script for the feedback processing endpoint.
"""

import asyncio
import sys
import os
sys.path.append('.')

from fastapi_backend.main import app
from fastapi_backend.handlers.product_feedback import ProductFeedbackProcessor

# Try different test client imports
try:
    from fastapi.testclient import TestClient
except ImportError:
    try:
        from starlette.testclient import TestClient
    except ImportError:
        print("Could not import TestClient, will test processor directly")
        TestClient = None

def test_endpoint_integration():
    """Test the feedback endpoint integration."""
    
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
    
    # Test data
    test_request = {
        "product_name": "TestProduct",
        "feedback": "This product is excellent and works perfectly!",
        "model": "anthropic/claude-3.5-sonnet"
    }
    
    print("Testing feedback processing endpoint...")
    print(f"Request: {test_request}")
    
    # Test the endpoint
    try:
        response = client.post("/feedback/process", json=test_request)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Endpoint responded successfully")
            print(f"Response: {result}")
            
            # Verify response structure
            required_fields = ["product_name", "feedback", "classification", "response", "model"]
            for field in required_fields:
                if field in result:
                    print(f"✓ Field '{field}' present: {result[field]}")
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
            processor = ProductFeedbackProcessor()
            result = await processor.process_feedback(
                product_name="TestProduct",
                feedback="This product is excellent and works perfectly!"
            )
            
            print("✓ Processor test successful")
            print(f"Result: {result}")
            
            # Verify response structure
            required_fields = ["product_name", "feedback", "classification", "response", "model"]
            for field in required_fields:
                if field in result:
                    print(f"✓ Field '{field}' present: {result[field]}")
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
    
    # Test missing product_name
    invalid_request = {
        "feedback": "This is feedback without product name"
    }
    
    response = client.post("/feedback/process", json=invalid_request)
    print(f"Missing product_name - Status: {response.status_code}")
    
    # Test empty product_name
    invalid_request = {
        "product_name": "",
        "feedback": "This is feedback with empty product name"
    }
    
    response = client.post("/feedback/process", json=invalid_request)
    print(f"Empty product_name - Status: {response.status_code}")
    
    # Test missing feedback
    invalid_request = {
        "product_name": "TestProduct"
    }
    
    response = client.post("/feedback/process", json=invalid_request)
    print(f"Missing feedback - Status: {response.status_code}")

def test_examples_endpoint():
    """Test that the examples endpoint includes feedback processing."""
    
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
        
        # Check if feedback processing example is included
        feedback_example = None
        for example in examples.get("examples", []):
            if example.get("endpoint") == "/feedback/process":
                feedback_example = example
                break
        
        if feedback_example:
            print("✓ Feedback processing example found in /langchain/examples")
            print(f"Description: {feedback_example.get('description')}")
        else:
            print("✗ Feedback processing example not found in /langchain/examples")
    else:
        print(f"✗ Examples endpoint failed with status {response.status_code}")

if __name__ == "__main__":
    print("=== Testing Feedback Processing Endpoint ===")
    
    # Check if API key is configured
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("✗ OPENROUTER_API_KEY not configured")
        sys.exit(1)
    else:
        print("✓ OPENROUTER_API_KEY configured")
    
    test_endpoint_integration()
    test_validation_errors()
    test_examples_endpoint()
    
    print("\n=== Test Complete ===")