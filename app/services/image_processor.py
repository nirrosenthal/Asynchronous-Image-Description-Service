from typing import Optional
import asyncio
import os
from app.config import settings

class ImageProcessor:
    """Service for processing images and managing file uploads."""
    
    def __init__(self) -> None:
        """Initialize ImageProcessor with upload directory from settings."""
        self.upload_dir = settings.UPLOAD_DIR
    
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