#!/usr/bin/env python3
"""
Test script to verify photo upload and AI evaluation functionality with a real image
"""
import sys
import os
from PIL import Image
import io

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_real_image():
    """Test with a real image"""
    print("Testing with a real image...")
    
    try:
        # Create a simple test image using PIL
        from PIL import Image, ImageDraw
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color = 'red')
        d = ImageDraw.Draw(img)
        d.text((10,10), "Test Image", fill=(255,255,0))
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        print(f"Created test image with size: {len(img_byte_arr)} bytes")
        
        # Test the services
        from app.services.huggingface_service import initialize_huggingface_service
        from app.services.ocr_service import initialize_ocr_service
        
        # Initialize services
        huggingface_service = initialize_huggingface_service()
        ocr_service = initialize_ocr_service()
        
        print(f"Hugging Face service: {huggingface_service}")
        print(f"OCR service: {ocr_service}")
        
        # Test Hugging Face evaluation
        print("\nTesting Hugging Face evaluation...")
        if huggingface_service:
            try:
                result = huggingface_service.evaluate_cleaning_photo(
                    image_data=img_byte_arr,
                    area_type="Interior",
                    cleaning_type="Basic",
                    trainset_number="TS-001"
                )
                print(f"Hugging Face evaluation result: {result}")
            except Exception as e:
                print(f"ERROR in Hugging Face evaluation: {e}")
        
        # Test OCR evaluation
        print("\nTesting OCR evaluation...")
        if ocr_service:
            try:
                result = ocr_service.evaluate_cleaning_photo(
                    image_data=img_byte_arr,
                    area_type="Interior",
                    cleaning_type="Basic",
                    trainset_number="TS-001"
                )
                print(f"OCR evaluation result: {result}")
            except Exception as e:
                print(f"ERROR in OCR evaluation: {e}")
                import traceback
                traceback.print_exc()
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_image()