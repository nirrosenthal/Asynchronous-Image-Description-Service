import pytest
from app.services.job_manager import JobManager
from app.database import AsyncSessionLocal, init_db
from app.enums import JobStatus

@pytest.mark.asyncio
async def test_create_job() -> None:
    """Test creating a new job."""
    await init_db()
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        job = await job_manager.create_job("test_image.jpg")
        
        assert job.id is not None
        assert job.status == JobStatus.QUEUED
        assert job.image_path.endswith(".jpg")
        assert job.generated_by == "vision-node-gpt"

@pytest.mark.asyncio
async def test_get_job() -> None:
    """Test retrieving a job by ID."""
    await init_db()
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        created_job = await job_manager.create_job("test_image.jpg")
        
        retrieved_job = await job_manager.get_job(created_job.id)
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id

@pytest.mark.asyncio
async def test_update_job_status() -> None:
    """Test updating job status."""
    await init_db()
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        job = await job_manager.create_job("test_image.jpg")
        
        updated_job = await job_manager.update_job_status(job.id, JobStatus.PROCESSING)
        assert updated_job.status == JobStatus.PROCESSING

@pytest.mark.asyncio
async def test_update_job_result() -> None:
    """Test updating job with processing result."""
    await init_db()
    async with AsyncSessionLocal() as session:
        job_manager = JobManager(session)
        job = await job_manager.create_job("test_image.jpg")
        
        updated_job = await job_manager.update_job_result(job.id, "A beautiful landscape")
        assert updated_job.status == JobStatus.DONE
        assert updated_job.image_description == "A beautiful landscape" 