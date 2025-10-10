
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        
        user_dict = user_data.model_dump()
        user_dict['password'] = hashed_password
        
        new_user = User(**user_dict)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    

    async def get_by_email_or_mobile(self, email: str, mobile_no: str) -> Optional[User]:
        """
        Fetches a user by their email or mobile number.
        """
        stmt = select(User).where(
            (User.email == email) | 
            (User.mobile_no == mobile_no)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()