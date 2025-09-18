from fastapi import FastAPI
from app.core.database import create_db_and_tables
from contextlib import asynccontextmanager
from app.api.v1 import api_router
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
# Run database migrations automatically (useful for local dev, but handled by Docker in production)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Running startup tasks...")
    create_db_and_tables()  # Ensures tables are created
    yield  # Yield control to FastAPI
    print("Shutting down...")  # Runs on shutdown (optional)

app = FastAPI(
    lifespan=lifespan,
    title="Teacher Data Entry", 
    version="1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    default_skip=0,
    default_limit=100,
    max_limit=1000)

"""  """
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In app/main.py

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Teacher Data Entry",
        version="1.0.0",
        routes=app.routes,
    )
    
    # Check if 'components' exists, if not, create it
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
        
    # Now it's safe to add securitySchemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi
"""  """
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Teacher Data Entry Portal API"}
