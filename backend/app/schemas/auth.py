from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# Request schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., alias="refreshToken")
    
    class Config:
        populate_by_name = True


# Response schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class AuthTokens(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    
    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    user: UserResponse
    
    class Config:
        populate_by_name = True


class RefreshResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    
    class Config:
        populate_by_name = True
