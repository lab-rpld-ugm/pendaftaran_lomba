#!/usr/bin/env python3
"""
Test script to verify ProfileVerificationHelper context processor
"""

from app import create_app

def test_context_processor():
    print("=== Testing Context Processor ===")
    
    app = create_app()
    with app.app_context():
        print("✓ App context created")
        
        # Test importing ProfileVerificationHelper
        try:
            from app.utils.verification import ProfileVerificationHelper
            print("✓ ProfileVerificationHelper imported successfully")
        except ImportError as e:
            print(f"✗ Import error: {e}")
            return False
        
        # Test context processor
        with app.test_request_context():
            try:
                # Get the context processor function
                context_processors = app.template_context_processors[None]
                print(f"✓ Found {len(context_processors)} context processors")
                
                # Execute context processors
                context = {}
                for processor in context_processors:
                    context.update(processor())
                
                if 'ProfileVerificationHelper' in context:
                    print("✓ ProfileVerificationHelper available in template context")
                    return True
                else:
                    print("✗ ProfileVerificationHelper NOT available in template context")
                    print(f"Available keys: {list(context.keys())}")
                    return False
                    
            except Exception as e:
                print(f"✗ Context processor error: {e}")
                return False

if __name__ == "__main__":
    success = test_context_processor()
    if success:
        print("\n✓ All tests passed! ProfileVerificationHelper should work in templates.")
    else:
        print("\n✗ Tests failed. There may still be issues with template context.")