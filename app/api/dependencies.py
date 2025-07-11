from app.database import get_db_session
from app.services.job_manager import JobManager
from app.services.image_processor import ImageProcessor

async def get_job_manager() -> JobManager:
    """Get JobManager instance with database session."""
    async for session in get_db_session():
        return JobManager(session)

def get_image_processor() -> ImageProcessor:
    """Get ImageProcessor instance."""
    return ImageProcessor() 