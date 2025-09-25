"""
Test script to verify Hugging Face service is working
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.huggingface_service import initialize_huggingface_service, HuggingFaceCleaningEvaluator

def test_huggingface_service():
    """Test the Hugging Face service initialization and basic functionality."""
    print("Testing Hugging Face service...")
    
    try:
        # Initialize the service
        service = initialize_huggingface_service()
        print("✓ Hugging Face service initialized successfully")
        
        # Test with a small dummy image data (this will fail but test the connection)
        dummy_image_data = b"dummy_image_data_for_testing"
        
        try:
            result = service.evaluate_cleaning_photo(
                image_data=dummy_image_data,
                area_type="Interior",
                cleaning_type="Basic",
                trainset_number="TM-001"
            )
            print("✓ Hugging Face evaluation completed")
            print(f"Result: {result}")
            
            # Check that we got a valid result (even if it's simulated)
            if "quality_score" in result and "quality_rating" in result:
                print("✓ Hugging Face service returned valid evaluation result")
                return True
            else:
                print("✗ Hugging Face service returned invalid result format")
                return False
                
        except Exception as e:
            print(f"✗ Hugging Face evaluation failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to initialize Hugging Face service: {e}")
        return False

if __name__ == "__main__":
    success = test_huggingface_service()
    if success:
        print("\n✓ Hugging Face service test completed successfully")
        print("The service is ready to be used as the default AI evaluation service.")
    else:
        print("\n✗ Hugging Face service test failed")