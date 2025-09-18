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
    env_file:
      - ./.env
    ports:
      - "8000:8000"
    volumes:
      # Mount the local 'app' directory into the container for hot reloading
      - ./app:/code/app
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

```bash
```