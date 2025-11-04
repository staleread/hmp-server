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
