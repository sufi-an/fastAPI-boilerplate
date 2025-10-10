from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.pagination import PaginationParams
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from fastapi import  HTTPException


async def create_user(user_data: UserCreate, user_repo: UserRepository) -> User:
    
    # Check if user already exists (optional)
    existing_user = await user_repo.get_by_email_or_mobile(
        email=user_data.email, 
        mobile_no=user_data.mobile_no
    )
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )
    
    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    
    
    return await user_repo.create_user(user_data=user_data,hashed_password=hashed_password)
        
    
async def get_users(
    db: AsyncSession, 
    search: Optional[str] = None,
    pagination: PaginationParams = None, 
) -> Tuple[List[User], int]:
    try:
        # Build base query
        query = select(User)
        
        if search:
            query = query.where(User.full_name.ilike(f"%{search}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination and get items
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
        
        items_result = await db.execute(query)
        items = items_result.scalars().all()
        
        return items, total
    except Exception as e:
        print(f"Error in get_users: {e}")
        raise e



async def update_user(db: AsyncSession,user_id: int, user_data: UserUpdate) -> User:
    try:
        stmt = select(User).where(
            (User.id == user_id) 
        )
        result = await db.execute(stmt)
        user_instance = result.scalar_one_or_none()
        if not user_instance:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update task fields
        update_user_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_user_data.items():
            setattr(user_instance, key, value)
        
        db.add(user_instance)
        db.commit()
        db.refresh(user_instance)
        
        return user_instance

    except Exception as e:
        await db.rollback()
        print(e)
        raise e