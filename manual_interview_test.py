#!/usr/bin/env python3
"""
Manual test for the interview processing endpoint using direct processor testing.
"""

import asyncio
import sys
import os
sys.path.append('.')

from fastapi_backend.handlers.interview_processor import InterviewProcessor

async def test_interview_processing():
    """Test the interview processor with a realistic transcript."""
    
    print("=== Manual Interview Processing Test ===")
    
    # Test transcript
    test_transcript = """00:00:10   introduction   Hi, I'm Sarah. I'm a software engineer with 5 years of experience at TechCorp.
00:02:30   background   I've been working primarily with Python and React, building web applications.
00:04:15   problem_solving   Recently, I solved a challenging performance issue in our API that was causing 3-second response times.
00:06:00   solution   I implemented database query optimization and added Redis caching, reducing response time to 200ms.
00:08:30   technical_details   I used connection pooling, indexed the most queried columns, and implemented a cache-aside pattern.
00:10:45   challenges   The main challenge was identifying the bottleneck without disrupting the production system.
00:12:20   results   The optimization improved user experience significantly and reduced server costs by 30%.
00:14:00   questions   What opportunities are there for growth in this role?"""
    
    try:
        # Initialize processor
        processor = InterviewProcessor()
        print(f"✓ Processor initialized with model: {processor.model_name}")
        
        # Process the transcript
        print(f"Processing transcript ({len(test_transcript)} characters)...")
        result = await processor.process_interview(test_transcript)
        
        # Display results
        print("\n=== PROCESSING RESULTS ===")
        print(f"Success: {result.get('success', 'Unknown')}")
        print(f"Model: {result.get('model', 'Unknown')}")
        print(f"Processing Time: {result.get('processing_time', 'Unknown')}s")
        
        print(f"\n--- SUMMARY ---")
        print(result.get('summary', 'No summary available'))
        
        print(f"\n--- HIGHLIGHTS ({len(result.get('highlights', []))}) ---")
        for i, highlight in enumerate(result.get('highlights', []), 1):
            print(f"{i}. {highlight}")
        
        print(f"\n--- LOWLIGHTS ({len(result.get('lowlights', []))}) ---")
        for i, lowlight in enumerate(result.get('lowlights', []), 1):
            print(f"{i}. {lowlight}")
        
        print(f"\n--- CANDIDATE INFORMATION ---")
        entities = result.get('key_named_entities', {})
        for key, value in entities.items():
            print(f"{key}: {value}")
        
        print("\n✓ Interview processing completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("✗ OPENROUTER_API_KEY not configured")
        sys.exit(1)
    
    asyncio.run(test_interview_processing())