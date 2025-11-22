"""
Database connection and session management
This file handles SQLAlchemy engine, session creation, and base model
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


# Create SQLAlchemy engine
# check_same_thread=False is needed for SQLite to work with FastAPI
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # Log all SQL queries in debug mode
)

# Create SessionLocal class
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit transactions
    autoflush=False,   # Don't auto-flush changes
    bind=engine        # Bind to our engine
)

# Create Base class for declarative models
# All database models will inherit from this
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    This will be used in FastAPI routes to get a database connection
    
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Yields:
        Session: Database session
    """
    # Create new database session
    db = SessionLocal()
    try:
        # Yield the session to the caller
        yield db
    finally:
        # Always close the session after use
        db.close()


def init_db() -> None:
    """
    Initialize database
    Creates all tables defined in models
    Should be called once at application startup
    """
    # Import all models here so they are registered with Base
    from app.models import user, event, password_reset
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def drop_all_tables() -> None:
    """
    Drop all tables from database
    WARNING: This will delete all data!
    Use only for development/testing
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped")


if __name__ == "__main__":
    # Test database connection
    print(f"Database URL: {settings.DATABASE_URL}")
    print("Testing database connection...")
    
    try:
        # Try to connect
        with engine.connect() as conn:
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
