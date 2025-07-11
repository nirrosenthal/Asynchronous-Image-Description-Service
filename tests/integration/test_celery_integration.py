#!/usr/bin/env python3
"""Integration tests for Celery functionality."""

import pytest
import os
import tempfile
from pathlib import Path
from app.database import init_db
from app.services.job_manager import JobManager
from app.services.image_processor import ImageProcessor
from app.database import AsyncSessionLocal
from app.enums import JobStatus

@pytest.mark.asyncio
async def test_celery_integration():
    """Test the Celery integration workflow."""
    print("Testing Celery integration...")
    
    # Initialize database
    await init_db()
    
    # Create data/images directory if it doesn't exist
    data_dir = Path("data/images")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test job first
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        job = await job_manager.create_job("test_integration_image.jpg", ".jpg")
        print(f"Created job: {job.id}")
        
        # Now create the test image file with the correct filename
        test_image_path = data_dir / job.image_path
        with open(test_image_path, "wb") as temp_file:
            # Write some dummy image data (minimal JPEG header)
            temp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        try:
            # Simulate the task processing
            image_processor = ImageProcessor()
            
            # Update status to processing
            await job_manager.update_job_status(job.id, JobStatus.PROCESSING)
            print(f"Job status updated to: {job.status}")
            
            # Process image (this would normally be done by Celery)
            description = await image_processor.process_image(job.image_path)
            print(f"Image processed: {description}")
            
            # Update job with result
            await job_manager.update_job_result(job.id, description)
            print(f"Job completed with status: {job.status}")
            
            # Retrieve the final job
            final_job = await job_manager.get_job(job.id)
            print(f"Final job status: {final_job.status}")
            print(f"Final job description: {final_job.image_description}")
            
            # Assert the job was processed successfully
            assert final_job.status == JobStatus.DONE
            assert final_job.image_description is not None
            
        finally:
            # Clean up the test file
            if test_image_path.exists():
                test_image_path.unlink() 