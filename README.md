# HMP Server - Technical Documentation

**HearMyPaper Server** is a FastAPI-based REST API service that provides backend functionality for the HearMyPaper platform, including document processing, authentication, project management, and audio conversion features.

---

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Setup & Installation](#setup--installation)
- [Development](#development)
- [Running the Server](#running-the-server)
- [Docker Deployment](#docker-deployment)
- [API Endpoints](#api-endpoints)
- [Database](#database)
- [Code Quality](#code-quality)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)

---

## Overview

The HMP Server is a microservice responsible for:

- **Authentication & Authorization**: JWT-based user authentication with credential management
- **Project Management**: CRUD operations for user projects
- **PDF Processing**: PDF to audio conversion using document analysis
- **Submission Handling**: Management of document submissions and versioning
- **Audit Logging**: Tracking of system events and user activities
- **Health Checks**: Service health monitoring

### Key Features

- Asynchronous request handling with FastAPI
- PostgreSQL database with alembic migrations (dbmate)
- Role-based access control (RBAC)
- JWT token-based authentication
- PDF analysis with PyMuPDF
- Audio synthesis integration (espeak-ng)
- Container-ready with Docker multi-stage builds

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | ≥0.116.1 |
| **Runtime** | Python | ≥3.13 |
| **Database** | PostgreSQL | (configured externally) |
| **ORM** | SQLAlchemy | ≥2.0.43 |
| **Async DB** | asyncpg | ≥0.30.0 |
| **Auth** | PyJWT | ≥2.10.1 |
| **PDF Processing** | PyMuPDF | ≥1.25.2 |
| **Cryptography** | cryptography | ≥45.0.7 |
| **Config** | pydantic-settings | ≥2.10.1 |
| **Migration Tool** | dbmate | (external CLI tool) |
| **Development** | ruff, mypy | See pyproject.toml |

---

## Architecture

### Directory Structure

```
server/
├── app/                      # Application source code
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── auth/                # Authentication & JWT handling
│   │   ├── router.py        # Auth endpoints
│   │   ├── service.py       # Auth business logic
│   │   ├── models.py        # Auth data models
│   │   └── ...
│   ├── credentials/         # User credentials management
│   ├── project/             # Project CRUD operations
│   ├── submission/          # Submission handling
│   ├── pdf_to_audio/        # PDF to audio conversion
│   ├── audit/               # Audit logging
│   ├── shared/              # Shared utilities & middleware
│   └── ...
├── db/                      # Database layer
│   └── migrations/          # Database migration files (dbmate format)
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yaml      # Local development environment
├── pyproject.toml          # Project dependencies & metadata
├── mypy.ini                # Type checking configuration
└── .pre-commit-config.yaml # Pre-commit hooks configuration
```

### Request Flow

```
HTTP Request
    ↓
FastAPI Router (auth/project/submission/etc.)
    ↓
Service Layer (Business Logic)
    ↓
SQLAlchemy Models
    ↓
PostgreSQL Database
    ↓
Response (JSON via Pydantic)
```

---

## Setup & Installation

### Prerequisites

- **Python 3.13+** (check with `python --version`)
- **PostgreSQL 13+** (for database)
- **Docker & Docker Compose** (optional, for containerized setup)
- **Git**

### 1. Clone the Repository

```bash
cd /path/to/hearmypaper/server
```

### 2. Create a Python Virtual Environment

```bash
# Create virtual environment
python3.13 -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project in development mode
pip install -e .

# Install development tools (optional, but recommended)
pip install -e ".[dev]"
```

### 4. Configure Environment Variables

Create a `.env` file in the server root (or set system environment variables):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hearmypaper
DB_USER=hearmypaper_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hearmypaper

# JWT Configuration
JWT_SECRET_KEY=your_very_secure_secret_key_change_this_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

### 5. Initialize the Database

```bash
# Install dbmate if not already installed
# See: https://github.com/amacneil/dbmate

# Run migrations
dbmate up
```

---

## Development

### Run Linting & Type Checking

```bash
# Lint with ruff
ruff check .

# Auto-fix ruff issues
ruff check . --fix

# Type checking with mypy
mypy .
```

### Pre-commit Hooks

To automatically run linting and type-checking before commits:

```bash
# Install pre-commit hooks
pre-commit install

# (Optional) Run hooks manually on all files
pre-commit run --all-files
```

### Running Locally (Without Docker)

```bash
# Make sure PostgreSQL is running and migrations are applied
dbmate up

# Start the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# API will be available at: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## Running the Server

### Production Mode (FastAPI CLI)

```bash
# Run with fastapi CLI
fastapi run app/main.py --port 8000

# Or with uvicorn (production server)
pip install uvicorn[standard]
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Health Check

```bash
curl http://localhost:8000/health
# Response: "I'm good"
```

---

## Docker Deployment

### Build Docker Image

```bash
# Build development image
docker build --target dev -t hmp-server:dev .

# Build production image
docker build --target prod -t hmp-server:prod .
```

### Run with Docker Compose (Development)

```bash
# Start all services (server + PostgreSQL)
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f server
```

### Docker Compose Configuration

The `docker-compose.yaml` provides:
- **server** service: FastAPI application with hot reload
- **postgres** service: PostgreSQL database
- **Volume mounts** for live code editing
- **Environment variables** for configuration

### Production Deployment

```bash
# Build production image
docker build --target prod -t ghcr.io/your-org/hmp-server:prod .

# Push to GitHub Container Registry
docker push ghcr.io/your-org/hmp-server:prod

# Pull and run on deployment host
docker run -e DATABASE_URL=<db_url> -e JWT_SECRET_KEY=<secret> \
  -p 8000:8000 \
  ghcr.io/your-org/hmp-server:prod
```

---

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/login` - User login, returns JWT token
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

### Projects (`/project`)
- `GET /project/` - List all projects
- `POST /project/` - Create new project
- `GET /project/{project_id}` - Get project details
- `PUT /project/{project_id}` - Update project
- `DELETE /project/{project_id}` - Delete project

### Submissions (`/submission`)
- `GET /submission/` - List submissions
- `POST /submission/` - Create submission
- `GET /submission/{submission_id}` - Get submission details
- `DELETE /submission/{submission_id}` - Delete submission

### PDF to Audio (`/pdf-to-audio`)
- `POST /pdf-to-audio/convert` - Convert PDF to audio file
- `GET /pdf-to-audio/status/{job_id}` - Check conversion status

### Credentials (`/credentials`)
- `GET /credentials/` - Get user credentials
- `PUT /credentials/` - Update credentials
- `DELETE /credentials/` - Delete credentials

### Audit (`/audit`)
- `GET /audit/logs` - Retrieve audit logs
- `GET /audit/user/{user_id}` - Get user-specific audit logs

### Health Check
- `GET /health` - Service health check

See OpenAPI docs at `/docs` for interactive API documentation.

---

## Database

### Migrations

Migrations are managed using **dbmate** and stored in `db/migrations/`.

```bash
# Create a new migration
dbmate new create_users_table

# Apply pending migrations
dbmate up

# Rollback last migration
dbmate down

# Check migration status
dbmate status
```

### Connection

- **Sync connection**: `psycopg2-binary` for initial setup/migrations
- **Async connection**: `asyncpg` for application runtime

### Environment Variable

```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
```

---

## Code Quality

### Ruff (Linting)

Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
```

Run linter:
```bash
ruff check .
ruff check . --fix  # Auto-fix
```

### Mypy (Type Checking)

Configuration in `mypy.ini`:

```ini
[mypy]
python_version = 3.13
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
```

Run type checker:
```bash
mypy .
```

### Pre-commit Hooks

Defined in `.pre-commit-config.yaml`:
- ruff (lint & format)
- mypy (type checking)
- yaml validation
- trailing whitespace

---

## CI/CD Pipeline

### Continuous Integration (CI)

Triggered on every push to any branch:

1. **Lint with ruff**: Check code style
2. **Type check with mypy**: Verify type annotations
3. **Fail fast**: Stop on any linting/type errors

**Workflow file**: `.github/workflows/ci.yml`

### Continuous Deployment (CD)

Triggered on push to `main` or `prod` branch:

1. **Build Docker image** with `--target prod`
2. **Push to GitHub Container Registry (GHCR)**:
   - `ghcr.io/<owner>/hmp-server:dev` (on main push)
   - `ghcr.io/<owner>/hmp-server:prod` (on prod push)
   - Also tagged with commit SHA for immutability
3. **Deploy to DigitalOcean App Platform**:
   - Automatically triggered after image push
   - Uses DigitalOcean API with stored credentials

**Workflow file**: `.github/workflows/cd.yml`

### Required Secrets for CD

Set these in GitHub repository settings:
- `DO_ACCESS_TOKEN` - DigitalOcean API token
- `DO_APP_ID` - DigitalOcean App Platform application ID

### Required Permissions

Workflow requires:
- `packages: write` - Push to GitHub Container Registry
- `contents: read` - Access source code

---

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Error

**Problem**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Verify DATABASE_URL in `.env` file
- Check database credentials

#### 2. Migration Errors

**Problem**: `dbmate: error running migration`

**Solution**:
```bash
# Check migration status
dbmate status

# If stuck, manually check database state
# and verify migration files in db/migrations/
```

#### 3. Port Already in Use

**Problem**: `Address already in use` on port 8000

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
fastapi run app/main.py --port 8001
```

#### 4. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
- Ensure you're in the server directory: `cd server/`
- Verify virtual environment is activated: `source .venv/bin/activate`
- Reinstall project: `pip install -e .`

#### 5. Type Checking Errors

**Problem**: Mypy reports `Cannot find a typed package`

**Solution**:
```bash
# Install type stubs if available
pip install types-<package-name>

# Or ignore in mypy.ini
# Add: ignore_missing_imports = True
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View FastAPI debug output:
```bash
export DEBUG=true
uvicorn app.main:app --reload
```

---

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Keep functions small and focused
- Write docstrings for public APIs

### Before Committing

```bash
# 1. Run linting
ruff check . --fix

# 2. Run type checking
mypy .

# 3. Run tests (if available)
pytest

# 4. Commit with pre-commit hooks
git commit -m "Your message"
```

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **dbmate Repository**: https://github.com/amacneil/dbmate
- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **Mypy Documentation**: https://mypy.readthedocs.io/

---

**Last Updated**: 2025-11-04  
**Project Version**: 0.1.0  
**Python Version**: ≥3.13
