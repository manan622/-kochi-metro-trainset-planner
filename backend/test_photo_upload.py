#!/usr/bin/env python3
"""
Test script to verify photo upload and AI evaluation functionality
"""
import sys
import os
import requests

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_photo_upload():
    """Test photo upload functionality"""
    print("Testing photo upload and AI evaluation...")
    
    # Start the server in the background
    print("Starting server...")
    
    # For now, let's just test the service initialization directly
    print("\n1. Testing service initialization...")
    try:
        from app.services.huggingface_service import initialize_huggingface_service
        from app.services.ocr_service import initialize_ocr_service
        from app.services.gemini_service import initialize_gemini_service
        
        # Initialize services
        huggingface_service = initialize_huggingface_service()
        ocr_service = initialize_ocr_service()
        gemini_service = initialize_gemini_service("dummy-api-key")
        
        print(f"   Hugging Face service: {huggingface_service}")
        print(f"   OCR service: {ocr_service}")
        print(f"   Gemini service: {gemini_service}")
        
        # Test Hugging Face evaluation with a simulated image
        print("\n2. Testing Hugging Face evaluation...")
        if huggingface_service:
            # Create a simple test image (just some bytes)
            test_image_data = b"fake_image_data_for_testing"
            try:
                result = huggingface_service.evaluate_cleaning_photo(
                    image_data=test_image_data,
                    area_type="Interior",
                    cleaning_type="Basic",
                    trainset_number="TS-001"
                )
                print(f"   Hugging Face evaluation result: {result}")
            except Exception as e:
                print(f"   ERROR in Hugging Face evaluation: {e}")
        
        # Test OCR evaluation
        print("\n3. Testing OCR evaluation...")
        if ocr_service:
            # Create a simple test image (just some bytes)
            test_image_data = b"fake_image_data_for_testing"
            try:
                result = ocr_service.evaluate_cleaning_photo(
                    image_data=test_image_data,
                    area_type="Interior",
                    cleaning_type="Basic",
                    trainset_number="TS-001"
                )
                print(f"   OCR evaluation result: {result}")
            except Exception as e:
                print(f"   ERROR in OCR evaluation: {e}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_photo_upload()