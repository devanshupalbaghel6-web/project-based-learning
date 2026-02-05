"""
Authentication Dependencies

FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import auth_service
from app.db.repositories import get_repos

# Bearer token security scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Get current user ID from JWT token.
    
    This is a dependency that extracts and validates the JWT token
    from the Authorization header and returns the user ID.
    """
    token = credentials.credentials
    
    # Decode token
    payload = auth_service.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_current_user(user_id: str = Depends(get_current_user_id)) -> dict:
    """
    Get current user from database.
    
    This dependency fetches the full user object from the database
    using the user ID from the JWT token.
    """
    repos = get_repos()
    user = await repos.users.find_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Get current user ID if token is provided, None otherwise.
    
    This is useful for endpoints that can work with or without authentication.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None
