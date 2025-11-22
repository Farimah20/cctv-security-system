"""
Main FastAPI application
Entry point for the CCTV Security System API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.database import init_db
from app.core.config import settings, create_directories
from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.users import router as users_router
from app.api.files import router as files_router

# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for CCTV Security Monitoring System with AI-powered threat detection",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows mobile app to make requests to our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    Runs when server starts
    - Creates necessary directories
    - Initializes database tables
    """
    print("\n" + "=" * 60)
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)
    
    # Create required directories
    print("📁 Creating directories...")
    create_directories()
    
    # Initialize database
    print("🗄️  Initializing database...")
    init_db()
    
    print("✅ Application started successfully!")
    print(f"📍 API Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    Runs when server stops
    """
    print("\n" + "=" * 60)
    print("👋 Shutting down application...")
    print("=" * 60 + "\n")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API welcome message
    
    Returns basic information about the API
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Used to verify API is running
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include authentication router
# All auth endpoints will be available at /auth/*
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(users_router)
app.include_router(files_router)

# Run application
if __name__ == "__main__":
    """
    Run the application with uvicorn server
    
    Usage:
        python -m app.main
    
    Or:
        uvicorn app.main:app --reload
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,        # Port number
        reload=True       # Auto-reload on code changes (development only)
    )
