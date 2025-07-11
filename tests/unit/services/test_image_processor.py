import pytest
import tempfile
import os
from app.services.image_processor import ImageProcessor

@pytest.fixture
def image_processor() -> ImageProcessor:
    """Create an ImageProcessor instance for testing."""
    return ImageProcessor()

@pytest.mark.asyncio
async def test_process_image(image_processor: ImageProcessor) -> None:
    """Test processing an image file."""
    # Create a temporary test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        f.write(b'test image content')
        f.flush()
        
        # Mock the upload directory
        image_processor.upload_dir = os.path.dirname(f.name)
        filename = os.path.basename(f.name)
        
        result = await image_processor.process_image(filename)
        
        assert result == "A beautiful landscape with mountains and trees"
        
        os.unlink(f.name)

@pytest.mark.asyncio
async def test_process_image_file_not_found(image_processor: ImageProcessor) -> None:
    """Test processing a non-existent image file."""
    with pytest.raises(FileNotFoundError, match="Image file not found"):
        await image_processor.process_image("non_existent_image.jpg")

@pytest.mark.asyncio
async def test_save_uploaded_file(image_processor: ImageProcessor) -> None:
    """Test saving an uploaded file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        image_processor.upload_dir = temp_dir
        
        file_content = b'test file content'
        filename = 'test_image.jpg'
        
        saved_path = await image_processor.save_uploaded_file(file_content, filename)
        
        assert saved_path == filename
        assert os.path.exists(os.path.join(temp_dir, filename))
        
        # Verify file content
        with open(os.path.join(temp_dir, filename), 'rb') as f:
            assert f.read() == file_content

@pytest.mark.asyncio
async def test_save_uploaded_file_creates_directory(image_processor: ImageProcessor) -> None:
    """Test that save_uploaded_file creates the upload directory if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use a subdirectory that doesn't exist
        sub_dir = os.path.join(temp_dir, "uploads", "images")
        image_processor.upload_dir = sub_dir
        
        file_content = b'test file content'
        filename = 'test_image.jpg'
        
        saved_path = await image_processor.save_uploaded_file(file_content, filename)
        
        assert saved_path == filename
        assert os.path.exists(sub_dir)
        assert os.path.exists(os.path.join(sub_dir, filename)) 