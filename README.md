# Task Management REST API

A RESTful API for task management built with FastAPI and SQLAlchemy.

## Features

- ✅ Create, Read, Update, Delete (CRUD) operations
- ✅ Pagination support
- ✅ Filtering by status and priority
- ✅ Statistics endpoint
- ✅ Soft delete functionality
- ✅ Comprehensive API documentation (Swagger UI & ReDoc)
- ✅ Unit tests with pytest

## Installation

```bash
# Clone repository
git clone <repository-url>
cd task_api_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

API Documentation
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
API Endpoints
METHOD	ENDPOINT	DESCRIPTION
GET	/	API root
GET	/api/v1/health	Health check
POST	/api/v1/tasks/	Create task
GET	/api/v1/tasks/	List tasks
GET	/api/v1/tasks/{id}	Get task by ID
PUT	/api/v1/tasks/{id}	Update task
DELETE	/api/v1/tasks/{id}	Delete task
GET	/api/v1/tasks/stats	Get statistics

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py -v


task_api_project/
├── app/                    # Application code
│   ├── main.py            # FastAPI application
│   ├── db.py              # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── routes/            # API routes
│   └── services/          # Business logic
├── tests/                 # Unit tests
├── requirements.txt       # Dependencies
└── README.md             # Documentation

Technologies
FastAPI: Web framework
SQLAlchemy: ORM
Pydantic: Data validation
SQLite: Database (development)
Pytest: Testing framework

---

# 1. Setup project
python setup.py

# 2. Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Create environment file
cp .env.example .env

# 4. Run the API
uvicorn app.main:app --reload

# 5. Visit docs
open http://localhost:8000/docs

# 6. Run tests
pytest tests/ -v --cov=app

Software Requirements

1. Python (Required)
VERSION	DOWNLOAD LINK
Python 3.9+	https://www.python.org/downloads/
Python 3.10+ (Recommended)	https://www.python.org/downloads/

2. Code Editor (Optional but Recommended)
OPTION	DOWNLOAD LINK
Visual Studio Code	https://code.visualstudio.com/
PyCharm Community	https://www.jetbrains.com/pycharm/download/

3. Terminal/Command Prompt
Windows: Command Prompt or PowerShell (built-in)
Mac: Terminal (built-in)
Linux: Terminal (built-in)