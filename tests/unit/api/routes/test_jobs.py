import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.enums import JobStatus
from app.models import Job
from datetime import datetime

@pytest.fixture
def mock_job_manager():
    """Mock JobManager dependency."""
    manager = AsyncMock()
    return manager

@pytest.fixture
def mock_image_processor():
    """Mock ImageProcessor dependency."""
    processor = MagicMock()  # Use MagicMock for sync methods
    processor.validate_uploaded_file = MagicMock()  # This is a sync method
    processor.get_file_extension = MagicMock()  # This is a sync method
    processor.save_uploaded_file = AsyncMock()  # This is an async method
    return processor

@pytest.fixture
def client(mock_job_manager, mock_image_processor):
    """Create a test client with mocked dependencies."""
    from app.api.dependencies import get_job_manager, get_image_processor
    
    def override_get_job_manager():
        return mock_job_manager
    
    def override_get_image_processor():
        return mock_image_processor
    
    app.dependency_overrides[get_job_manager] = override_get_job_manager
    app.dependency_overrides[get_image_processor] = override_get_image_processor
    
    yield TestClient(app)
    
    # Clean up
    app.dependency_overrides.clear()

def test_submit_job_success(client: TestClient, mock_job_manager: AsyncMock, mock_image_processor: AsyncMock) -> None:
    """Test successful job submission."""
    # Mock validation function
    mock_image_processor.get_file_extension.return_value = '.jpg'
    
    # Mock job creation
    mock_job = Job(
        id="test-job-id",
        image_path="test_image.jpg",
        file_extension=".jpg",
        status=JobStatus.QUEUED,
        generated_by="vision-node-gpt",
        created_at=datetime.now()
    )
    mock_job_manager.create_job.return_value = mock_job
    
    # Mock file saving
    mock_image_processor.save_uploaded_file.return_value = "test_image.jpg"
    
    # Mock Celery task
    with patch('app.api.routes.jobs.process_image_task') as mock_task:
        # Test file upload
        response = client.post(
            "/api/v1/submit",
            files={"file": ("test.jpg", b"fake image content", "image/jpeg")}
        )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "queued"
    assert data["message"] == "Job submitted successfully"
    
    # Verify service calls - check that methods were called
    mock_job_manager.create_job.assert_called_once()
    mock_image_processor.save_uploaded_file.assert_called_once()

def test_submit_job_invalid_file_type(client: TestClient, mock_job_manager: AsyncMock, mock_image_processor: AsyncMock) -> None:
    """Test job submission with invalid file type."""
    # Mock validation to raise an exception for invalid file type
    from fastapi import HTTPException
    mock_image_processor.validate_uploaded_file.side_effect = HTTPException(
        status_code=400, detail="File must be an image"
    )
    
    response = client.post(
        "/api/v1/submit",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]
    
    # Verify services were not called since validation failed
    mock_job_manager.create_job.assert_not_called()
    mock_image_processor.save_uploaded_file.assert_not_called()

def test_submit_job_file_too_large(client: TestClient, mock_job_manager: AsyncMock, mock_image_processor: AsyncMock) -> None:
    """Test job submission with file too large."""
    # Create a large file content (larger than MAX_FILE_SIZE)
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    
    response = client.post(
        "/api/v1/submit",
        files={"file": ("large_image.jpg", large_content, "image/jpeg")}
    )
    
    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]
    
    # Verify services were not called
    mock_job_manager.create_job.assert_not_called()
    mock_image_processor.save_uploaded_file.assert_not_called()

def test_get_job_status_success(client: TestClient, mock_job_manager: AsyncMock) -> None:
    """Test successful job status retrieval."""
    # Mock job retrieval
    mock_job = Job(
        id="test-job-id",
        image_path="test_image.jpg",
        file_extension=".jpg",
        status=JobStatus.PROCESSING,
        created_at=datetime.now()
    )
    mock_job_manager.get_job.return_value = mock_job
    
    response = client.get("/api/v1/status/test-job-id")
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "processing"
    assert "created_at" in data
    
    mock_job_manager.get_job.assert_called_once_with("test-job-id")

def test_get_job_status_not_found(client: TestClient, mock_job_manager: AsyncMock) -> None:
    """Test job status retrieval for non-existent job."""
    mock_job_manager.get_job.return_value = None
    
    response = client.get("/api/v1/status/non-existent-id")
    
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]
    
    mock_job_manager.get_job.assert_called_once_with("non-existent-id")

def test_get_job_result_success(client: TestClient, mock_job_manager: AsyncMock) -> None:
    """Test successful job result retrieval."""
    # Mock completed job
    mock_job = Job(
        id="test-job-id",
        image_path="test_image.jpg",
        file_extension=".jpg",
        status=JobStatus.DONE,
        image_description="A beautiful landscape",
        generated_by="vision-node-gpt",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_job_manager.get_job.return_value = mock_job
    
    response = client.get("/api/v1/result/test-job-id")
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "done"
    assert data["image_description"] == "A beautiful landscape"
    assert data["generated_by"] == "vision-node-gpt"
    
    mock_job_manager.get_job.assert_called_once_with("test-job-id")

def test_get_job_result_not_found(client: TestClient, mock_job_manager: AsyncMock) -> None:
    """Test job result retrieval for non-existent job."""
    mock_job_manager.get_job.return_value = None
    
    response = client.get("/api/v1/result/non-existent-id")
    
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]
    
    mock_job_manager.get_job.assert_called_once_with("non-existent-id")

def test_get_job_result_not_completed(client: TestClient, mock_job_manager: AsyncMock) -> None:
    """Test job result retrieval for incomplete job."""
    # Mock incomplete job
    mock_job = Job(
        id="test-job-id",
        image_path="test_image.jpg",
        file_extension=".jpg",
        status=JobStatus.PROCESSING,
        created_at=datetime.now()
    )
    mock_job_manager.get_job.return_value = mock_job
    
    response = client.get("/api/v1/result/test-job-id")
    
    assert response.status_code == 400
    assert "Job not completed" in response.json()["detail"]
    
    mock_job_manager.get_job.assert_called_once_with("test-job-id") 