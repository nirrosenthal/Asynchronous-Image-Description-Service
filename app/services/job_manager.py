from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Job
from app.enums import JobStatus
from datetime import datetime
from typing import Optional
import uuid
import os

class JobManager:
    """Service for managing job operations in the database."""
    
    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize JobManager with a database session."""
        self.db_session = db_session
    
    async def create_job(self, original_filename: str) -> Job:
        """Create a new job record with UUID-based filename."""
        job_uuid = str(uuid.uuid4())
        file_extension = os.path.splitext(original_filename)[1]
        image_filename = f"{job_uuid}{file_extension}"
        
        job = Job(
            id=job_uuid,
            image_path=image_filename,
            status=JobStatus.QUEUED,
            generated_by="vision-node-gpt"
        )
        self.db_session.add(job)
        await self.db_session.commit()
        await self.db_session.refresh(job)
        return job
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        result = await self.db_session.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def update_job_status(self, job_id: str, status: JobStatus) -> Optional[Job]:
        """Update job status."""
        job = await self.get_job(job_id)
        if job:
            job.status = status
            await self.db_session.commit()
            await self.db_session.refresh(job)
        return job
    
    async def update_job_result(self, job_id: str, image_description: str) -> Optional[Job]:
        """Update job with processing result."""
        job = await self.get_job(job_id)
        if job:
            job.image_description = image_description
            job.status = JobStatus.DONE
            await self.db_session.commit()
            await self.db_session.refresh(job)
        return job 