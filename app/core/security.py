from datetime import timedelta, datetime
from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

# define a password hasing context (bcrypt hashing)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Token Settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100  # Settings.ACCESS_TOKEN_EXPIRE_MINUTES


# Function to hash a password
def hash_password(password: str) -> str:
    print(password)
    return pwd_context.hash(password)


# Function to ferify a hash password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Function for verify a JWT Token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"www-Authentication": "Bearer"},
        )


# Function to create JWT token (access token )
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
