from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.database import get_db
from app.services.auth_service import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    create_dummy_users,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas import Token, UserLogin, UserResponse

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint - authenticate user and return JWT token.
    
    Dummy users:
    - admin/admin123 (MANAGEMENT role)
    - inspector/inspect123 (INSPECTION role) 
    - worker/work123 (WORKER role)
    """
    # Ensure dummy users exist
    create_dummy_users(db)
    
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout():
    """
    Logout endpoint - in a real implementation, this would invalidate the token.
    For this dummy implementation, client should just discard the token.
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user

@router.get("/users/seed")
async def seed_users(db: Session = Depends(get_db)):
    """Seed dummy users - for development purposes."""
    create_dummy_users(db)
    return {"message": "Dummy users created successfully"}

@router.get("/users/list")
async def list_users(db: Session = Depends(get_db)):
    """List all available users - for development purposes."""
    from app.services.auth_service import DUMMY_USERS
    return {
        "available_users": [
            {
                "username": user["username"],
                "password": user["password"],
                "role": user["role"].value
            }
            for user in DUMMY_USERS
        ]
    }