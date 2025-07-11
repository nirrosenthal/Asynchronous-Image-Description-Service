from typing import Optional, Tuple
import asyncio
import os
import magic
from fastapi import UploadFile, HTTPException
from app.config import settings

class ImageProcessor:
    """Service for processing images and managing file uploads."""
    
    # Allowed image file extensions
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
    
    def __init__(self) -> None:
        """Initialize ImageProcessor with upload directory from settings."""
        self.upload_dir = settings.UPLOAD_DIR
    
    def validate_image_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate image file using combined approach.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check content type
        if not file.content_type.startswith('image/'):
            return False, "File must be an image"
        
        # Check file extension
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File extension '{file_ext}' is not allowed. Allowed extensions: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        return True, ""
    
    def validate_image_content(self, file_content: bytes) -> Tuple[bool, str]:
        """
        Validate image content using magic numbers.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            if not mime_type.startswith('image/'):
                return False, f"File content type '{mime_type}' is not an image"
            return True, ""
        except Exception as e:
            return False, f"Error validating file content: {str(e)}"
    
    def get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return os.path.splitext(filename.lower())[1]
    
    def validate_and_get_extension(self, file: UploadFile, file_content: bytes) -> str:
        """
        Validate image file and return the file extension.
        
        Raises:
            HTTPException: If validation fails
        """
        # Basic validation
        is_valid, error_msg = self.validate_image_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Content validation
        is_valid, error_msg = self.validate_image_content(file_content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Return file extension
        return self.get_file_extension(file.filename)
    
    async def process_image(self, image_path: str) -> str:
        """Process image and return description."""
        # Validate file exists
        full_path = os.path.join(self.upload_dir, image_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image file not found: {full_path}")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Mock image processing result
        return "A beautiful landscape with mountains and trees"
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return the saved path."""
        os.makedirs(self.upload_dir, exist_ok=True)
        file_path = os.path.join(self.upload_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return filename 