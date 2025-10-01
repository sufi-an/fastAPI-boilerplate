from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: Session, user_data: UserCreate) -> User:
    try:
        hashed_password = hash_password(user_data.password)
        print(hashed_password)
        user_data.password = hashed_password
        new_user = User(**user_data.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh()

        return new_user
    except Exception as e:
        print(e)
        raise e
