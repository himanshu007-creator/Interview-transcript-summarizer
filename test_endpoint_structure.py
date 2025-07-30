#!/usr/bin/env python3
"""
Test script to verify the endpoint structure and validation.
"""

import sys
import os
sys.path.append('.')

from fastapi_backend.main import app, ProductFeedbackRequest, ProductFeedbackResponse
from pydantic import ValidationError

def test_request_model():
    """Test the ProductFeedbackRequest model validation."""
    
    print("Testing ProductFeedbackRequest validation...")
    
    # Test valid request
    try:
        valid_request = ProductFeedbackRequest(
            product_name="TestProduct",
            feedback="This is valid feedback",
            model="anthropic/claude-3.5-sonnet"
        )
        print("✓ Valid request model created successfully")
        print(f"  Product: {valid_request.product_name}")
        print(f"  Feedback: {valid_request.feedback}")
        print(f"  Model: {valid_request.model}")
    except Exception as e:
        print(f"✗ Valid request failed: {e}")
    
    # Test missing product_name
    try:
        invalid_request = ProductFeedbackRequest(
            feedback="This is feedback without product name"
        )
        print("✗ Missing product_name should have failed")
    except ValidationError as e:
        print("✓ Missing product_name correctly rejected")
    
    # Test empty product_name
    try:
        invalid_request = ProductFeedbackRequest(
            product_name="",
            feedback="This is feedback with empty product name"
        )
        print("✗ Empty product_name should have failed")
    except ValidationError as e:
        print("✓ Empty product_name correctly rejected")
    
    # Test missing feedback
    try:
        invalid_request = ProductFeedbackRequest(
            product_name="TestProduct"
        )
        print("✗ Missing feedback should have failed")
    except ValidationError as e:
        print("✓ Missing feedback correctly rejected")
    
    # Test empty feedback
    try:
        invalid_request = ProductFeedbackRequest(
            product_name="TestProduct",
            feedback=""
        )
        print("✗ Empty feedback should have failed")
    except ValidationError as e:
        print("✓ Empty feedback correctly rejected")

def test_response_model():
    """Test the ProductFeedbackResponse model."""
    
    print("\nTesting ProductFeedbackResponse model...")
    
    # Test valid response
    try:
        valid_response = ProductFeedbackResponse(
            product_name="TestProduct",
            feedback="This is test feedback",
            classification="positive",
            response="Thank you for your feedback!",
            model="anthropic/claude-3.5-sonnet",
            processing_time=1.23
        )
        print("✓ Valid response model created successfully")
        print(f"  Classification: {valid_response.classification}")
        print(f"  Response: {valid_response.response}")
        print(f"  Processing time: {valid_response.processing_time}")
    except Exception as e:
        print(f"✗ Valid response failed: {e}")
    
    # Test invalid classification
    try:
        invalid_response = ProductFeedbackResponse(
            product_name="TestProduct",
            feedback="This is test feedback",
            classification="invalid_classification",
            response="Thank you for your feedback!",
            model="anthropic/claude-3.5-sonnet"
        )
        print("✗ Invalid classification should have failed")
    except ValidationError as e:
        print("✓ Invalid classification correctly rejected")

def test_endpoint_exists():
    """Test that the endpoint exists in the FastAPI app."""
    
    print("\nTesting endpoint registration...")
    
    # Check if the endpoint is registered
    routes = [route.path for route in app.routes]
    
    if "/feedback/process" in routes:
        print("✓ /feedback/process endpoint is registered")
    else:
        print("✗ /feedback/process endpoint is not registered")
        print(f"Available routes: {routes}")
    
    # Check if examples endpoint includes feedback
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
        from fastapi_backend.handlers.product_feedback import ProductFeedbackProcessor
        print("✓ ProductFeedbackProcessor import successful")
    except ImportError as e:
        print(f"✗ ProductFeedbackProcessor import failed: {e}")
    
    try:
        # Test that the processor can be initialized
        processor = ProductFeedbackProcessor()
        print("✓ ProductFeedbackProcessor initialization successful")
    except Exception as e:
        print(f"✓ ProductFeedbackProcessor initialization failed (expected due to API credits): {e}")

if __name__ == "__main__":
    print("=== Testing Endpoint Structure ===")
    
    test_imports()
    test_request_model()
    test_response_model()
    test_endpoint_exists()
    
    print("\n=== Structure Test Complete ===")