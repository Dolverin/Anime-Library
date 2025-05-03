from fastapi import FastAPI

# Import necessary components from our app
from backend.app import models
from backend.app.database import engine, Base
from backend.app.routers import animes, episodes

# Create database tables
# This should ideally be handled by migrations (e.g., Alembic) in production
# But for development, creating them here is convenient.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the anime router
app.include_router(animes.router)

# Include the episodes router
app.include_router(episodes.router)

@app.get("/")
def read_root():
    return {"message": "Anime Library API"}

# Placeholder for future routes
# Example:
# from . import routes
# app.include_router(routes.router)
