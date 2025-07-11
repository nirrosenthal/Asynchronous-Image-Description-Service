import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.job_manager import JobManager
from app.enums import JobStatus
from app.models import Job

@pytest.fixture
def mock_session():
    """Create a mocked async database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session

@pytest.fixture
def job_manager(mock_session):
    """Create a JobManager instance with mocked session."""
    return JobManager(mock_session)

@pytest.mark.asyncio
async def test_create_job(job_manager, mock_session):
    """Test creating a new job with mocked database."""
    # Act
    job = await job_manager.create_job("test_image.jpg")
    
    # Assert
    assert job.id is not None
    assert job.status == JobStatus.QUEUED
    assert job.image_path.endswith(".jpg")
    assert job.generated_by == "vision-node-gpt"
    assert job.image_path.startswith(job.id)
    
    # Verify database operations were called
    mock_session.add.assert_called_once_with(job)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(job)

@pytest.mark.asyncio
async def test_get_job_found(job_manager, mock_session):
    """Test retrieving an existing job."""
    # Arrange
    job_id = "test-job-id"
    expected_job = Job(id=job_id, image_path="test.jpg", status=JobStatus.QUEUED)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_job
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await job_manager.get_job(job_id)
    
    # Assert
    assert result == expected_job
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_job_not_found(job_manager, mock_session):
    """Test retrieving a non-existent job."""
    # Arrange
    job_id = "non-existent-id"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await job_manager.get_job(job_id)
    
    # Assert
    assert result is None
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_job_status_success(job_manager, mock_session):
    """Test updating job status successfully."""
    # Arrange
    job_id = "test-job-id"
    existing_job = Job(id=job_id, image_path="test.jpg", status=JobStatus.QUEUED)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_job
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
    
    # Assert
    assert result.status == JobStatus.PROCESSING
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_job)

@pytest.mark.asyncio
async def test_update_job_status_not_found(job_manager, mock_session):
    """Test updating status of non-existent job."""
    # Arrange
    job_id = "non-existent-id"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
    
    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()

@pytest.mark.asyncio
async def test_update_job_result_success(job_manager, mock_session):
    """Test updating job with processing result successfully."""
    # Arrange
    job_id = "test-job-id"
    image_description = "A beautiful landscape"
    existing_job = Job(id=job_id, image_path="test.jpg", status=JobStatus.PROCESSING)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_job
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await job_manager.update_job_result(job_id, image_description)
    
    # Assert
    assert result.status == JobStatus.DONE
    assert result.image_description == image_description
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_job)

@pytest.mark.asyncio
async def test_update_job_result_not_found(job_manager, mock_session):
    """Test updating result of non-existent job."""
    # Arrange
    job_id = "non-existent-id"
    image_description = "A beautiful landscape"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await job_manager.update_job_result(job_id, image_description)
    
    # Assert
    assert result is None
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called() 