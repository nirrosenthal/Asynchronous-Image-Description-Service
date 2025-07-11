from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.enums import JobStatus

class JobSubmitResponse(BaseModel):
    """Response model for job submission."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Submission message")

class JobStatusResponse(BaseModel):
    """Response model for job status query."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="Job creation timestamp")

class JobResultResponse(BaseModel):
    """Response model for job result retrieval."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    image_description: str = Field(..., description="Generated image description")
    generated_by: str = Field(..., description="Service that generated the description")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp") 