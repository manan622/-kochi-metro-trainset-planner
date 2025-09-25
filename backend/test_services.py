#!/usr/bin/env python3
"""
Test script to verify AI service initialization
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_service_initialization():
    """Test initialization of all AI services"""
    print("Testing AI service initialization...")
    
    # Test Hugging Face service
    print("\n1. Testing Hugging Face service initialization...")
    try:
        from app.services.huggingface_service import initialize_huggingface_service, get_huggingface_service
        huggingface_service = initialize_huggingface_service()
        print(f"   Hugging Face service initialized: {huggingface_service}")
        print(f"   Hugging Face service type: {type(huggingface_service)}")
        print(f"   get_huggingface_service(): {get_huggingface_service()}")
    except Exception as e:
        print(f"   ERROR initializing Hugging Face service: {e}")
        import traceback
        traceback.print_exc()
    
    # Test OCR service
    print("\n2. Testing OCR service initialization...")
    try:
        from app.services.ocr_service import initialize_ocr_service, get_ocr_service
        ocr_service = initialize_ocr_service()
        print(f"   OCR service initialized: {ocr_service}")
        print(f"   OCR service type: {type(ocr_service)}")
        print(f"   get_ocr_service(): {get_ocr_service()}")
    except Exception as e:
        print(f"   ERROR initializing OCR service: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Gemini service (if API key is available)
    print("\n3. Testing Gemini service initialization...")
    try:
        from app.services.gemini_service import initialize_gemini_service, get_gemini_service
        # Use a dummy API key for testing initialization
        gemini_service = initialize_gemini_service("dummy-api-key")
        print(f"   Gemini service initialized: {gemini_service}")
        print(f"   Gemini service type: {type(gemini_service)}")
        print(f"   get_gemini_service(): {get_gemini_service()}")
    except Exception as e:
        print(f"   ERROR initializing Gemini service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service_initialization()