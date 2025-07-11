from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.api.dependencies import get_job_manager, get_image_processor
from app.services.job_manager import JobManager
from app.services.image_processor import ImageProcessor
from app.validators import JobSubmitResponse, JobStatusResponse, JobResultResponse
from app.enums import JobStatus
from app.tasks import process_image_task
from app.config import settings

router = APIRouter()

@router.post("/submit", response_model=JobSubmitResponse)
async def submit_job(
    file: UploadFile = File(...),
    job_manager: JobManager = Depends(get_job_manager),
    image_processor: ImageProcessor = Depends(get_image_processor)
):
    """Submit an image for processing."""
    # Read file content first
    file_content = await file.read()
    
    # Validate file size
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Validate uploaded file
    image_processor.validate_uploaded_file(file, file_content)
    
    # Get file extension and create job
    file_extension = image_processor.get_file_extension(file.filename)
    job = await job_manager.create_job(file.filename, file_extension)
    
    # Save uploaded file
    await image_processor.save_uploaded_file(file_content, job.image_path)
    
    # Queue processing task
    process_image_task.delay(job.id, job.image_path)
    
    return JobSubmitResponse(
        job_id=job.id,
        status=job.status,
        message="Job submitted successfully"
    )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Get job status."""
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at
    )

@router.get("/result/{job_id}", response_model=JobResultResponse)
async def get_job_result(
    job_id: str,
    job_manager: JobManager = Depends(get_job_manager)
):
    """Get job result."""
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    return JobResultResponse(
        job_id=job.id,
        status=job.status,
        image_description=job.image_description,
        generated_by=job.generated_by,
        created_at=job.created_at,
        completed_at=job.updated_at
    ) 