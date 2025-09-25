from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.models.database import engine, SessionLocal
from app.models import models
from app.routers import auth, trainsets

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(trainsets.router, prefix="/api", tags=["trainsets"])

@app.get("/")
async def root():
    return {"message": "Kochi Metro Trainset Induction Planner API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)