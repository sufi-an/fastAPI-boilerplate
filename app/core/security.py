from passlib.context import CryptContext


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
