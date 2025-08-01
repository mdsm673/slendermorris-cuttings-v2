# Overview

This is a Flask-based fabric sample ordering system that allows customers to request fabric samples and provides an admin dashboard for managing those requests. The application features a customer-facing form for submitting sample requests and an administrative interface for tracking and managing orders through different status stages (Outstanding, In Progress, Dispatched).

## Recent Changes (August 2025)
- **Form Layout Update**: Combined Company Name and Customer Name into single "Company Name / Customer Name" field
- **Field Positioning**: Moved Email Address to top row alongside combined name field  
- **Fabric Selection**: Replaced checkboxes with 5 simple text input fields under "Fabric Cuttings - Type Here"
- **Database Schema**: Added Reference field to customer information section
- **Address Labels**: Customized to use "Suburb" and "State" for Australian market
- **Admin Dashboard**: Updated to display combined company/customer field in single column
- **Design System**: Implemented Zara-inspired clean white background with black text styling
- **Typography**: Added Playfair Display serif for headers and Helvetica for body text
- **Branding**: Replaced generic logo with Slender Morris Furnishings company logo
- **Email System**: Implemented SMTP email notifications with Gmail integration
- **Terminology Update**: Changed all references from "samples" to "cutting" throughout the application
- **Dispatch Notifications**: Corrected email recipients to orders@slendermorris.com and slendermorris@gmail.com
- **Email Timezone**: Updated to use Sydney, Australia timezone with date-only format (absolutely no time references)
- **Email Date Fix**: Corrected all email templates to properly display Sydney timezone dates without any time components
- **Footer Navigation**: Added "Back to Website - Click Here" link to https://slendermorris.dearportal.com in dark navy blue, opens in new tab
- **Success Popup Update**: Removed Close and Submit Another Request buttons, automatically redirects to main website after 3 seconds
- **Security Hardening** (August 1, 2025):
  - Implemented comprehensive input validation and sanitization
  - Added rate limiting for form submissions (5 per 5 minutes) and login attempts
  - Enhanced session security with HTTPS-only cookies and 2-hour timeout
  - Added security headers (X-Frame-Options, X-XSS-Protection, HSTS)
  - Implemented failed login tracking with IP-based lockout (5 attempts/15 min)
  - Added role-based access control with decorator enforcement
  - Created error pages (404, 500) for better user experience
  - Maximum request size limit (2MB) to prevent abuse
- **Data Retention**: Confirmed 1-year minimum retention policy with no automatic deletion

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
- **Admin Access**: Password-based authentication with Werkzeug secure hashing
- **Session Storage**: Secure Flask sessions with HttpOnly, Secure, and SameSite flags
- **Access Control**: Decorator-based route protection with @require_admin
- **Security Features**:
  - Failed login attempt tracking with IP-based lockout
  - Rate limiting on login attempts (5 attempts per 15 minutes)
  - 2-hour session timeout for security
  - Automatic session clearing on logout
  - Comprehensive audit logging for login attempts

## Email Notification System
- **SMTP Integration**: Gmail SMTP server configuration for sending automated emails
- **Customer Confirmations**: Automatic email sent upon fabric cutting request submission
- **Admin Notifications**: Internal alerts sent to orders@slendermorris.com and slendermorris@gmail.com for new requests
- **Dispatch Notifications**: Automated emails sent when order status changes to "Dispatched" (customer + internal team)
- **Email Recipients**:
  - New Request: Customer (confirmation), orders@slendermorris.com, slendermorris@gmail.com
  - Dispatch: Original customer, orders@slendermorris.com, slendermorris@gmail.com
  - In Progress Status: No email notifications triggered

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