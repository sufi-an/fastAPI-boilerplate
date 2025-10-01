from app.permissions.base import IsSuperAdmin, permissions, IsAdmin
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional

# from app.permissions.base import  IsSuperAdmin, permissions
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import (
    create_user,
    get_users,
    # get_student_by_id,
    # update_student,
    # delete_student,
)
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


# Create an user
@router.post("/", response_model=UserResponse)
# @permissions([IsSuperAdmin])
async def create(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    return await create_user(db, user)


# get users List
@router.get("/", response_model=List[UserResponse])
@permissions([IsSuperAdmin])
async def list(
    request: Request, db: AsyncSession = Depends(get_db), search: Optional[str] = None
):
    return await get_users(db, search)
