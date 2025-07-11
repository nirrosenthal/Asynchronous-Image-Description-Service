import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.job_manager import JobManager

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