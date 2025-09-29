from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum
from sqlalchemy.orm import validates, relationship

from app.models.base import Base

class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_no = Column(String(14), unique=True, nullable=False)  # Required field
    full_name = Column(String(50), nullable=True)  # Optional field
    email = Column(String(100), unique=True, nullable=False)  # Max length 100
    role = Column(Enum(UserRole), nullable=False)  # Enum
    password = Column(String, nullable=False)

    username = Column(String(15), unique=True, nullable=False)

    created_at = Column(String, nullable=False, server_default="CURRENT_TIMESTAMP")  # Default DB value


    # One-to-one relationship with Teacher
    teacher = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")



    @validates("mobile_no")
    def sync_username(self, key, value):
        """Ensures username is always the same as mobile number"""
        self.username = value
        return value
