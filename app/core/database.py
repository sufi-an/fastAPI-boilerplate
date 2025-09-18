from sqlmodel import SQLModel, create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker, Session

# SQLAlchemy-compatible engine
engine = create_engine(settings.DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency for FastAPI routes
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
