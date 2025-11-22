"""
File Management API endpoints
Handles file uploads and downloads
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_user_owns_resource
from app.core.config import settings
from app.models.user import User
from app.services.event_service import EventService


# Create API router
router = APIRouter(prefix="/files", tags=["Files"])


def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """
    Save uploaded file to disk
    
    Args:
        upload_file: Uploaded file from request
        destination: Destination path
    
    Returns:
        Path: Path where file was saved
    """
    try:
        # Create directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return destination
    
    finally:
        upload_file.file.close()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file
    
    **Requires:** Valid JWT token
    
    **Request:**
    - file: File to upload (multipart/form-data)
    
    **Returns:**
    - file_path: Path where file was saved
    - filename: Original filename
    - size: File size in bytes
    
    **Errors:**
    - 400: File too large or invalid type
    - 401: Not authenticated
    """
    # Check file size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f} MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Validate file type (allow images only)
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create path: uploads/users/{user_id}/{date}/filename
    date_path = datetime.now().strftime("%Y-%m-%d")
    destination_dir = settings.UPLOAD_DIR / "users" / str(current_user.id) / date_path
    destination = destination_dir / unique_filename
    
    # Save file
    saved_path = save_upload_file(file, destination)
    
    # Get relative path for database storage
    relative_path = str(saved_path.relative_to(settings.UPLOAD_DIR.parent))
    
    return {
        "message": "File uploaded successfully",
        "file_path": relative_path,
        "filename": file.filename,
        "size": file_size,
        "content_type": file.content_type
    }


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a file
    
    **Requires:** Valid JWT token
    
    **Parameters:**
    - file_path: Path to file (relative to project root)
    
    **Returns:**
    - File content
    
    **Errors:**
    - 404: File not found
    - 403: Not authorized to access this file
    
    **Security:**
    Users can only download files from their own uploads directory
    """
    # Construct full path
    full_path = Path(file_path)
    
    # Check if file exists
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Security check: ensure user can only access their own files
    # Check if path contains user's ID
    if f"users/{current_user.id}/" not in str(full_path) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this file"
        )
    
    # Return file
    return FileResponse(
        path=str(full_path),
        filename=full_path.name,
        media_type="application/octet-stream"
    )


@router.get("/event/{event_id}/image")
async def get_event_image(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get image associated with an event
    
    **Requires:** Valid JWT token
    
    **Parameters:**
    - event_id: Event ID
    
    **Returns:**
    - Image file
    
    **Errors:**
    - 404: Event or image not found
    - 403: Not authorized to access this event
    """
    # Get event
    event = EventService.get_event_by_id(db, event_id)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check authorization
    verify_user_owns_resource(event.user_id, current_user)
    
    # Check if event has image
    if not event.image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event has no associated image"
        )
    
    # Get image path
    image_path = Path(event.image_path)
    
    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )
    
    # Return image
    return FileResponse(
        path=str(image_path),
        media_type="image/jpeg"
    )


@router.delete("/delete/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file
    
    **Requires:** Valid JWT token
    
    **Parameters:**
    - file_path: Path to file
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 404: File not found
    - 403: Not authorized
    """
    # Construct full path
    full_path = Path(file_path)
    
    # Check if file exists
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Security check
    if f"users/{current_user.id}/" not in str(full_path) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this file"
        )
    
    # Delete file
    full_path.unlink()
    
    return {
        "message": "File deleted successfully",
        "file_path": file_path
    }


# Health check
@router.get("/health/check")
async def files_health_check():
    """
    Health check for files API
    """
    return {
        "status": "ok",
        "service": "files"
    }
