# Project Dependencies

This project uses the following Python packages:

## Core Framework
- Flask>=3.1.1 - Web framework
- Flask-SQLAlchemy>=3.1.1 - SQL toolkit and ORM
- SQLAlchemy>=2.0.42 - Database abstraction layer
- Werkzeug>=3.1.3 - WSGI utilities

## Database
- psycopg2-binary>=2.9.10 - PostgreSQL adapter

## Server
- gunicorn>=23.0.0 - WSGI HTTP Server

## Utilities
- email-validator==2.1.0 - Email validation

## Installation

Dependencies are automatically managed by Replit through the `pyproject.toml` file.

For local development, you can install these packages using:
```bash
pip install flask>=3.1.1 flask-sqlalchemy>=3.1.1 gunicorn>=23.0.0 psycopg2-binary>=2.9.10 sqlalchemy>=2.0.42 werkzeug>=3.1.3 email-validator==2.1.0
```