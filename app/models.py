from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from app.enums import JobStatus
import uuid

Base = declarative_base()

def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())

class Job(Base):
    """SQLAlchemy model for a job record."""
    __tablename__ = "jobs"
    
    id: str = Column(String(36), primary_key=True, default=generate_uuid)
    status: JobStatus = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    image_path: str = Column(String(500), nullable=False)
    file_extension: str = Column(String(10), nullable=False)
    image_description: str = Column(Text, nullable=True)
    generated_by: str = Column(String(100), nullable=False, default="vision-node-gpt")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 