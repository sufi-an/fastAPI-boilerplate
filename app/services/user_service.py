from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from typing import List, Optional


async def create_user(db: Session, user_data: UserCreate) -> User:
    try:
        hashed_password = hash_password(user_data.password)
        print(hashed_password)
        user_data.password = hashed_password
        new_user = User(**user_data.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except Exception as e:
        print(e)
        raise e


async def get_users(db: AsyncSession, search: Optional[str] = None) -> List[User]:
    filters = []

    if search:
        filters.append(User.name.ilike(f"%{search}%"))

    return db.query(User).all()
