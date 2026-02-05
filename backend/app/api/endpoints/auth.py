"""
Authentication API Endpoints

Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from app.services.auth_service import auth_service
from app.db.repositories import get_repos
from app.core.config import settings
from app.api.dependencies.auth import get_current_user, get_current_user_id

router = APIRouter()


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: str


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """
    Register a new user.
    
    Creates a new user account and returns a JWT token.
    """
    repos = get_repos()
    
    # Check if user already exists
    existing_user = await repos.users.find_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = auth_service.get_password_hash(user_data.password)
    
    # Create user
    user_dict = {
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hashed_password,
        "onboarding_completed": False,
        "is_active": True
    }
    
    user_id = await repos.users.create(user_dict)
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        user_id=user_id,
        email=user_data.email,
        name=user_data.name
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    
    Returns a JWT token on successful authentication.
    """
    repos = get_repos()
    
    # Find user
    user = await repos.users.find_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not auth_service.verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user["_id"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        user_id=user["_id"],
        email=user["email"],
        name=user["name"]
    )


@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile.
    
    Returns the authenticated user's profile information.
    """
    # Remove sensitive data
    current_user.pop("hashed_password", None)
    return current_user


@router.put("/me")
async def update_current_user_profile(
    update_data: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update current user profile.
    
    Allows user to update their profile information.
    """
    repos = get_repos()
    
    # Don't allow updating email or password through this endpoint
    update_data.pop("email", None)
    update_data.pop("password", None)
    update_data.pop("hashed_password", None)
    
    success = await repos.users.update(current_user_id, update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"status": "success", "message": "Profile updated"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password.
    
    Requires old password for verification.
    """
    repos = get_repos()
    
    # Verify old password
    if not auth_service.verify_password(old_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Hash new password
    hashed_password = auth_service.get_password_hash(new_password)
    
    # Update password
    success = await repos.users.update(
        current_user["_id"],
        {"hashed_password": hashed_password}
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"status": "success", "message": "Password changed"}
