Project Folder Structure

```bash
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── some_router.py
│   ├── core/
│   │   ├── config.py       # Pydantic settings, reads from .env
│   │   ├── database.py     # Database session management
│   │   ├── jwt.py          # JWT creation and decoding logic
│   │   └── security.py     # Password hashing and verification
│   ├── deps/
│   │   └── auth.py         # FastAPI dependencies for auth
│   ├── models/
│   │   └── user_model.py   # SQLModel database models
│   ├── permissions/
│   │   └── base.py         # Permission decorators/classes
│   ├── schemas/
│   │   └── user_schema.py  # Pydantic schemas for API I/O
│   ├── services/
│   │   └── user_service.py # Business logic
│   └── main.py             # FastAPI app instance creation
├── migrations/             # Alembic migration files
│   ├── versions/
│   └── env.py
├── tests/                  # Pytest tests
├── .env                    # Environment variables (secret)
├── .gitignore              # Files to ignore in Git
├── alembic.ini             # Alembic configuration
├── docker-compose.yml      # Docker Compose services definition
├── Dockerfile              # Docker image instructions for the app
└── requirements.txt        # Python dependencies
```

Prerequisit:
Git
DOcker

requirements.txt
```bash
fastapi[all]==0.110.0
uvicorn[standard]==0.29.0
sqlmodel==0.0.16
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic[email]
pydantic-settings==2.1.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
httpx==0.27.0
pytest==8.0.2
python-jose[cryptography]
```

.env
```bash
# --- Application Settings ---
PROJECT_NAME="My FastAPI Project"
API_V1_STR="/api/v1"

# --- Database Settings ---
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
POSTGRES_SERVER=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}

# --- JWT Settings ---
SECRET_KEY="<your_super_secret_key_here>" # Generate with: openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

gitignore
```bash
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
.venv/
env/
.env

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Docker
.dockerignore
docker-compose.override.yml

# IDEs
.idea/
.vscode/

```



Dockerfile
```bash
# Start with the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /code/app
COPY ./alembic.ini /code/alembic.ini
COPY ./migrations /code/migrations

# The command to run the application will be specified in docker-compose.yml
# This allows for flexibility (e.g., running tests or the server)
```



docker-compose.yml
```bash
version: '3.8'

services:
  # Database Service (PostgreSQL)
  db:
    image: postgres:17
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Application Service (FastAPI)
  app:
    build: .
    container_name: fast-app
    env_file:
      - ./.env
    ports:
      - "8000:8000"
    volumes:
      # Mount the local 'app' directory into the container for hot reloading
      - ./app:/code/app
      - ./migrations:/code/migrations
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head && 
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

volumes:
  postgres_data:
```


run


```bash
docker-compose up  --build
```


migrations/env.py
```bash
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your models here
from app.models import Base  # Make sure this is your declarative base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# Override DB URL from .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```



models/__init__.py
```bash
from .base import Base


from .user import User

```

models/base.py
```bash
from sqlalchemy.orm import declarative_base

Base = declarative_base()

```
migration commands
```bash
docker exec -it app alembic revision --autogenerate -m "Create initial tables"
docker-compose exec app alembic upgrade head

undo: docker-compose exec app alembic downgrade base
```


```bash
```