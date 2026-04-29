from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.api.dependencies import get_current_user
from app.application.auth_service import AuthService
from app.config import settings
from app.infrastructure.models import User

router = APIRouter()

class LoginRequest(BaseModel):
    tenant_id: int
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    tenant_id: int
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    try:
        user = AuthService.authenticate_user(request.tenant_id, request.email, request.password)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role},
            expires_delta=access_token_expires
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id), "tenant_id": user.tenant_id}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    try:
        user = AuthService.create_user(
            request.tenant_id,
            request.email,
            request.password,
            request.first_name,
            request.last_name
        )

        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id), "tenant_id": user.tenant_id}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    try:
        payload = AuthService.verify_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = AuthService.get_user_from_payload(payload)

        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role}
        )

        return {
            "access_token": access_token,
            "refresh_token": request.refresh_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
