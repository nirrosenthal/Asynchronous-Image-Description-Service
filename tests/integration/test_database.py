import pytest
from app.database import init_db, AsyncSessionLocal
from app.models import Job
from app.enums import JobStatus

@pytest.mark.asyncio
async def test_database_connection() -> None:
    """Test that the database connection and session work."""
    await init_db()
    async with AsyncSessionLocal() as session:
        assert session is not None

@pytest.mark.asyncio
async def test_job_model() -> None:
    """Test creating and retrieving a Job model instance."""
    await init_db()
    async with AsyncSessionLocal() as session:
        job = Job(
            image_path="/test/path/image.jpg",
            file_extension=".jpg",
            status=JobStatus.QUEUED
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        
        assert job.id is not None
        assert job.status == JobStatus.QUEUED
        assert job.image_path == "/test/path/image.jpg"
        assert job.file_extension == ".jpg" 