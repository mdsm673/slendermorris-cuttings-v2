# Overview

This is a Flask-based fabric sample ordering system that allows customers to request fabric samples and provides an admin dashboard for managing those requests. The application features a customer-facing form for submitting sample requests and an administrative interface for tracking and managing orders through different status stages (Outstanding, In Progress, Dispatched).

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme for responsive UI
- **Client-side Interaction**: Vanilla JavaScript for form handling, tooltips, and enhanced user experience
- **Styling**: Bootstrap CSS framework with custom CSS overrides for branding and layout improvements
- **Icons**: Font Awesome for consistent iconography throughout the interface

## Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Application Structure**: Modular design with separate files for models, routes, and configuration
- **Session Management**: Flask sessions for admin authentication with password hashing
- **Database Models**: Single SampleRequest model tracking customer info, shipping details, fabric selections, and order status
- **Request Processing**: Form-based data collection with JSON storage for fabric selections

## Data Storage
- **Database**: SQLite for development with configurable database URL for production deployment
- **ORM**: SQLAlchemy with DeclarativeBase for model definitions
- **Connection Management**: Connection pooling with pool recycling and health checks
- **Schema**: Single table architecture storing all request data with status tracking fields

## Authentication & Authorization
- **Admin Access**: Simple password-based authentication using Werkzeug password hashing
- **Session Storage**: Flask sessions to maintain admin login state
- **Access Control**: Route-level protection for administrative functions
- **Security**: Environment variable configuration for production password management

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and connection management
- **Werkzeug**: WSGI utilities and security functions for password hashing

## Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN with dark theme
- **Font Awesome**: Icon library for UI elements
- **Custom CSS/JS**: Local static files for application-specific styling and behavior

## Deployment & Infrastructure
- **ProxyFix**: Werkzeug middleware for handling proxy headers in production
- **Environment Variables**: Configuration management for database URLs and admin credentials
- **CSV Export**: Built-in Python csv module for data export functionality

## Development Tools
- **Python Logging**: Built-in logging configuration for debugging
- **SQLite**: Default database for development environment
- **Flask Debug Mode**: Development server with hot reloading capabilities