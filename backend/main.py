from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.models.database import engine, SessionLocal
from app.models import models
from app.routers import auth, trainsets, cleaning

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Initialize AI services
    print("Starting AI service initialization in lifespan...")
    
    # Initialize Hugging Face service
    try:
        print("Initializing Hugging Face service...")
        hugging_face_token = os.getenv("HUGGING_FACE_TOKEN")
        if hugging_face_token:
            cleaning.huggingface_service = cleaning.initialize_huggingface_service(hugging_face_token)
            print("Hugging Face AI service initialized successfully with API key")
        else:
            cleaning.huggingface_service = cleaning.initialize_huggingface_service()
            print("Hugging Face AI service initialized without API key (rate limited)")
        print(f"Hugging Face service object: {cleaning.huggingface_service}")
    except Exception as e:
        cleaning.huggingface_service = None
        print(f"Failed to initialize Hugging Face AI service: {e}")
        import traceback
        traceback.print_exc()
    
    # Initialize Gemini AI service
    gemini_api_key = "AIzaSyD66l2j_rcxVJAq6WkQEWURxXb7hkT7sDI"  # Your provided API key
    try:
        print("Initializing Gemini service...")
        if gemini_api_key and gemini_api_key != "YOUR_API_KEY_HERE":
            cleaning.gemini_service = cleaning.initialize_gemini_service(gemini_api_key)
            print("Gemini AI service initialized successfully")
            print(f"Gemini service object: {cleaning.gemini_service}")
        else:
            cleaning.gemini_service = None
            print("WARNING: Gemini API key not configured.")
    except Exception as e:
        cleaning.gemini_service = None
        print(f"Failed to initialize Gemini AI service: {e}")
        import traceback
        traceback.print_exc()
    
    # Initialize OCR service
    try:
        print("Initializing OCR service...")
        cleaning.ocr_service = cleaning.initialize_ocr_service()
        print("OCR AI service initialized successfully")
        print(f"OCR service object: {cleaning.ocr_service}")
    except Exception as e:
        cleaning.ocr_service = None
        print(f"Failed to initialize OCR AI service: {e}")
        import traceback
        traceback.print_exc()
    
    print("AI service initialization completed.")
    print(f"Final service states - Gemini: {cleaning.gemini_service}, Hugging Face: {cleaning.huggingface_service}, OCR: {cleaning.ocr_service}")
    
    yield

app = FastAPI(
    title="Kochi Metro Trainset Induction Planner",
    description="A comprehensive system for planning nightly trainset induction operations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(trainsets.router, prefix="/api", tags=["trainsets"])
app.include_router(cleaning.router, tags=["cleaning"])

@app.get("/")
async def root():
    return {"message": "Kochi Metro Trainset Induction Planner API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)