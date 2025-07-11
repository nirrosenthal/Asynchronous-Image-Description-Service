from celery import Celery
import asyncio
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.job_manager import JobManager
from app.services.image_processor import ImageProcessor
from app.enums import JobStatus

# Initialize Celery
celery_app = Celery(
    "image_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, max_retries=settings.TASK_MAX_RETRIES, default_retry_delay=settings.TASK_RETRY_DELAY)
def process_image_task(self, job_id: str, file_path: str) -> dict:
    """
    Process image task with retry mechanism.
    
    Args:
        job_id: The job identifier
        file_path: Path to the image file to process
        
    Returns:
        dict: Processing result with job_id, status, and description
    """
    try:
        result = asyncio.run(_process_image_async(job_id, file_path))
        return result
    except Exception as exc:
        # Update job status to failed
        asyncio.run(_update_job_failed(job_id, str(exc)))
        raise self.retry(exc=exc, countdown=settings.TASK_RETRY_DELAY)

async def _process_image_async(job_id: str, file_path: str) -> dict:
    """
    Async image processing workflow.
    
    Args:
        job_id: The job identifier
        file_path: Path to the image file to process
        
    Returns:
        dict: Processing result
    """
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        image_processor = ImageProcessor()
        
        # Update status to processing
        await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Process image
        description = await image_processor.process_image(file_path)
        
        # Update job with result
        await job_manager.update_job_result(job_id, description)
        
        return {
            "job_id": job_id, 
            "status": "completed", 
            "description": description
        }

async def _update_job_failed(job_id: str, error_message: str) -> None:
    """
    Update job status to failed.
    
    Args:
        job_id: The job identifier
        error_message: Error message to log
    """
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        await job_manager.update_job_status(job_id, JobStatus.FAILED) 