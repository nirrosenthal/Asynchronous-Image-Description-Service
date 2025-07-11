# Asynchronous Image Description Service

A FastAPI-based service that processes images asynchronously using Celery and Redis, providing AI-powered image descriptions.

## Features

- **Asynchronous Image Processing**: Upload images and get descriptions (mocked) asynchronously
- **RESTful API**: Clean REST API with proper validation and error handling
- **Celery Integration**: Background task processing with Redis as message broker
- **SQLite Database**: Lightweight database for job tracking
- **Docker Support**: Full containerization with docker-compose
- **Comprehensive Testing**: Unit and integration tests

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │   FastAPI   │    │   Celery    │
│             │◄──►│   Web App   │◄──►│   Worker    │
└─────────────┘    └─────────────┘    └─────────────┘
                          │                    │
                          ▼                    ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   SQLite    │    │    Redis    │
                   │  Database   │    │   Broker    │
                   └─────────────┘    └─────────────┘
```

## Quick Start with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup and Run

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Asynchronous-Image-Description-Service
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration:
   # - Set WEB_HOST=0.0.0.0
   # - Set WEB_PORT=8000 (or your preferred port)
   # - Set REDIS_HOST=localhost
   # - Set REDIS_PORT=6379
   # - Set CELERY_BROKER_URL=redis://redis:${REDIS_PORT}
   # - Set CELERY_RESULT_BACKEND=redis://redis:${REDIS_PORT}
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Check service status**
   ```bash
   docker-compose ps
   ```

5. **View logs**
   ```bash
   docker-compose logs -f web
   docker-compose logs -f worker
   docker-compose logs -f redis
   ```

6. **Access the API**
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### Development Environment

The service now runs without profiles. All services start together:

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration values
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **The API will be available at**: http://localhost:8000

4. **API Documentation**: http://localhost:8000/docs

### Running Tests

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration values
   ```

2. **Run tests locally**
   ```bash
   # Install test dependencies
   pip install pytest pytest-asyncio pytest-mock

   # Run all tests
   pytest

   # Run with verbose output
   pytest -v

   # Run specific test file
   pytest tests/unit/test_tasks.py -v
   ```

## API Usage Examples

### Using curl

#### 1. Submit an Image for Processing

**Linux/macOS:**
```bash
curl -X POST "http://localhost:8000/api/v1/submit" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

**Windows Command Prompt:**
```cmd
curl -X POST "http://localhost:8000/api/v1/submit" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@C:\path\to\your\image.jpg"
```

**Windows PowerShell:**
```powershell
curl -X POST "http://localhost:8000/api/v1/submit" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@C:\path\to\your\image.jpg"
```

**Response:**
```json
{
  "job_id": "0b66c4f6-f2c7-42d5-9c1b-c01a50c98118",
  "status": "queued",
  "message": "Job submitted successfully"
}
```

#### 2. Check Job Status

```bash
curl -X GET "http://localhost:8000/api/v1/status/8006955a-8b34-4afd-9487-84490fc25803"
```

**Response:**
```json
{
  "job_id": "8006955a-8b34-4afd-9487-84490fc25803",
  "status": "done",
  "created_at": "2025-07-11T22:56:10"
}
```

#### 3. Get Job Result

```bash
curl -X GET "http://localhost:8000/api/v1/result/8006955a-8b34-4afd-9487-84490fc25803"
```

**Response:**
```json
{
  "job_id": "8006955a-8b34-4afd-9487-84490fc25803",
  "status": "done",
  "image_description": "A beautiful landscape with mountains and trees",
  "generated_by": "vision-node-gpt",
  "created_at": "2025-07-11T22:56:10",
  "completed_at": "2025-07-11T22:56:12"
}
```

#### 4. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### 5. Test Error Handling

```bash
# Test with invalid job ID
curl -w "HTTP Status: %{http_code}\n" "http://localhost:8000/api/v1/status/invalid-id"
```

**Response:**
```
HTTP Status: 404
```

### Using Python

```python
import requests

# Submit image
with open('/path/to/your/image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/submit',
        files={'file': f}
    )
    job_data = response.json()
    job_id = job_data['job_id']
    print(f"Job submitted: {job_id}")

# Check status
status_response = requests.get(f'http://localhost:8000/api/v1/status/{job_id}')
print(f"Status: {status_response.json()}")

# Get result
result_response = requests.get(f'http://localhost:8000/api/v1/result/{job_id}')
print(f"Result: {result_response.json()}")
```

### Using the Swagger UI

1. Open your browser and navigate to: `http://localhost:8000/docs`
2. Click on the **POST /api/v1/submit** endpoint
3. Click "Try it out"
4. Upload your image file
5. Click "Execute"

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/submit` | Submit image for processing |
| `GET` | `/api/v1/status/{job_id}` | Get job status |
| `GET` | `/api/v1/result/{job_id}` | Get job result |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | API documentation (Swagger UI) |
| `GET` | `/redoc` | API documentation (ReDoc) |

## Development with Docker Compose

### Prerequisites

- Docker
- Docker Compose

### Setup and Development

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration values
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **View logs for development**
   ```bash
   # View all logs
   docker-compose logs -f

   # View specific service logs
   docker-compose logs -f web
   docker-compose logs -f worker
   docker-compose logs -f redis
   ```

4. **Restart services after code changes**
   ```bash
   # Restart specific service
   docker-compose restart web

   # Restart all services
   docker-compose restart
   ```

5. **Rebuild after dependency changes**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Running Tests with Docker

```bash
# Run tests in a temporary container
docker-compose run --rm web pytest

# Run tests with verbose output
docker-compose run --rm web pytest -v

# Run specific test file
docker-compose run --rm web pytest tests/unit/test_tasks.py -v

# Run tests with coverage
docker-compose run --rm web pytest --cov=app
```

## Troubleshooting

### Common Issues

#### 1. Services not starting
```bash
# Check service status
docker-compose ps

# View logs for specific service
docker-compose logs web
docker-compose logs worker
docker-compose logs redis
```

#### 2. Celery worker connection issues
Make sure your `.env` file has the correct Redis URLs:
```bash
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
```

#### 3. Port conflicts
If you get port binding errors, change the port in your `.env` file:
```bash
WEB_PORT=8001  # or any available port
```

#### 4. File upload issues
- Ensure the image file exists and is accessible
- Check file size (max 10MB by default)
- Verify file format is supported (jpg, png, gif, etc.)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEB_PORT` | Web application port | `8000` |
| `REDIS_PORT` | Redis port for production/development | `6379` |
| `REDIS_TEST_PORT` | Redis port for testing | `6380` |
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./data/app.db` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379` |
| `CELERY_WORKERS` | Number of Celery worker processes | `1` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `10485760` (10MB) |
| `UPLOAD_DIR` | Directory for uploaded images | `data/images` |
| `TASK_MAX_RETRIES` | Maximum task retry attempts | `3` |
| `TASK_RETRY_DELAY` | Delay between retries in seconds | `60` |

## Docker Services

All services are configured to work together seamlessly with environment-driven configuration.

- **web**: FastAPI application
- **worker**: Celery worker for background tasks
- **redis**: Redis message broker and result backend

## Project Structure

```
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration settings
│   ├── models.py          # SQLAlchemy models
│   ├── database.py        # Database connection setup
│   ├── tasks.py           # Celery task definitions
│   ├── enums.py           # Enumeration definitions
│   ├── api/               # API layer
│   │   ├── dependencies.py # FastAPI dependencies
│   │   └── routes/        # API route definitions
│   └── services/          # Business logic layer
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── data/                 # File storage
├── docker-compose.yml    # All services with profiles
└── Dockerfile           # Application container
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License. 
