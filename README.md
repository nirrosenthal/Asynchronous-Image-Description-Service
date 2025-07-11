# Asynchronous Image Description Service

A FastAPI-based service that processes images asynchronously using Celery and Redis, providing AI-powered image descriptions.

## Features

- **Asynchronous Image Processing**: Upload images and get descriptions asynchronously
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

### Production Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Asynchronous-Image-Description-Service
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your production values:
   # - Uncomment Docker Redis URLs and comment local ones
   # - Adjust CELERY_WORKERS as needed
   ```

3. **Start the services**
   ```bash
   docker-compose --profile production up -d
   ```

4. **Check service status**
   ```bash
   docker-compose ps
   ```

5. **View logs**
   ```bash
   docker-compose logs -f web
   docker-compose logs -f worker
   ```

### Development Environment

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your development values:
   # - Uncomment Docker Redis URLs and comment local ones
   ```

2. **Start development services**
   ```bash
   docker-compose --profile development up -d
   ```

3. **The API will be available at**: http://localhost:8000

4. **API Documentation**: http://localhost:8000/docs

### Running Tests

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your test values:
   # - Set DATABASE_URL=sqlite+aiosqlite:///./data/test.db
   # - Uncomment test Redis URLs and comment others
   ```

2. **Run tests**
   ```bash
   docker-compose --profile test up --abort-on-container-exit
   ```

## API Endpoints

### Submit Image for Processing
```http
POST /api/v1/submit
Content-Type: multipart/form-data

file: <image_file>
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "Job submitted successfully"
}
```

### Get Job Status
```http
GET /api/v1/status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "created_at": "2023-01-01T00:00:00"
}
```

### Get Job Result
```http
GET /api/v1/result/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "done",
  "image_description": "A beautiful landscape with mountains and trees",
  "generated_by": "vision-node-gpt",
  "created_at": "2023-01-01T00:00:00",
  "completed_at": "2023-01-01T00:02:00"
}
```

## Local Development

### Prerequisites

- Python 3.10+
- Redis

### Setup

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Start Redis**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

6. **Start Celery worker**
   ```bash
   celery -A app.tasks worker --loglevel=info
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_tasks.py -v
```

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
