from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import tasks
from app.models import Task
from app.db import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="A RESTful API for task management with CRUD operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tasks.router, prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint - API health check"""
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00"}
