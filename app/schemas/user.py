from typing import Optional, Annotated
from pydantic import BaseModel, constr, EmailStr, Field


class UserBase(BaseModel):
    mobile_no: Annotated[str, Field(min_length=10, max_length=15)]
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    mobile_no: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    id: int
    username: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    assess_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
