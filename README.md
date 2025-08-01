# Slender Morris Fabric Cutting Request System

A professional, production-ready web application for managing fabric cutting requests, built with Flask and PostgreSQL.

## Overview

This system provides a streamlined process for customers to request fabric cuttings and for administrators to manage these requests through various stages (Outstanding, In Progress, Dispatched). The application is built with security, scalability, and reliability as core principles.

### Key Features

- **Customer Request Form**: Clean, intuitive form with comprehensive validation
- **Admin Dashboard**: Secure management interface with role-based access control
- **Email Notifications**: Automated SMTP emails for confirmations and dispatch updates
- **Status Tracking**: Three-stage order lifecycle (Outstanding → In Progress → Dispatched)
- **Data Retention**: Guaranteed 1-year minimum data retention policy
- **Responsive Design**: Zara-inspired clean interface optimized for all devices
- **Security Hardened**: Multiple layers of protection against common web vulnerabilities

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Custom CSS
- **Email**: SMTP integration (Gmail)
- **Server**: Gunicorn WSGI

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL database
- SMTP email account (Gmail recommended)

### Environment Variables

Create the following environment variables:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
SESSION_SECRET=your-secret-key-here
ADMIN_PASSWORD=your-admin-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Initialize database: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`
5. Run the application: `gunicorn --bind 0.0.0.0:5000 main:app`

## Usage

### Customer Portal (/)

Customers can submit fabric cutting requests with:
- Company/Customer name
- Contact information
- Shipping address
- Up to 5 fabric cutting selections
- Reference numbers and special notes

### Admin Dashboard (/admin)

Access with admin password to:
- View all cutting requests
- Filter by status (Outstanding, In Progress, Dispatched)
- Update order status
- View detailed request information
- Automatic email notifications on dispatch

## Email Notifications

### Request Confirmation
- Sent to: Customer, orders@slendermorris.com, slendermorris@gmail.com
- Triggered: Upon form submission

### Dispatch Notification
- Sent to: Customer, orders@slendermorris.com, slendermorris@gmail.com
- Triggered: When status changed to "Dispatched"

## Security Features

### Authentication & Authorization
- Password-protected admin area with secure hashing (Werkzeug)
- Session-based authentication with 2-hour timeout
- Role-based access control with decorator enforcement
- Failed login attempt tracking and account lockout (5 attempts/15 min)

### Input Validation & Sanitization
- Comprehensive input validation for all form fields
- Email format validation with regex patterns
- Phone number validation for international formats
- Fabric cutting entry validation to prevent malicious input
- Maximum field length enforcement

### Rate Limiting
- Form submission rate limiting (5 requests per 5 minutes)
- Login attempt rate limiting with IP-based tracking
- Automatic lockout after excessive failed attempts

### Security Headers & Protection
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security for HTTPS enforcement
- CSRF protection via secure Flask sessions
- SQL injection prevention through SQLAlchemy ORM
- XSS protection via Jinja2 automatic escaping

### Session Security
- Secure session cookies (HTTPS only in production)
- HttpOnly flag to prevent JavaScript access
- SameSite=Lax for CSRF mitigation
- Automatic session clearing on logout

### Infrastructure Security
- Environment variable configuration for sensitive data
- ProxyFix middleware for proper header handling
- Maximum request size limit (2MB)
- Comprehensive error logging and monitoring

## Data Retention

All fabric cutting requests are retained in the database for a minimum of 1 year, regardless of dispatch status. No automatic deletion processes are implemented.

## Deployment

### Production Deployment Checklist

- [x] **Security Implementation**: Comprehensive input validation, rate limiting, and security headers
- [x] **Authentication**: Secure admin authentication with failed login tracking
- [x] **Database**: PostgreSQL with connection pooling and health monitoring
- [x] **Email System**: SMTP notifications with Sydney timezone formatting
- [x] **Data Retention**: 1-year minimum retention policy implemented
- [x] **Error Handling**: Professional 404/500 error pages
- [x] **Session Security**: HTTPS-only cookies with 2-hour timeout
- [x] **Cross-site Protection**: X-Frame-Options, XSS protection, HSTS headers
- [x] **Rate Limiting**: Form submission and login attempt protection
- [x] **Environment Configuration**: All sensitive data in environment variables

### Replit Deployment

**Ready for Production Deployment**

1. **Environment Setup**: Configure the following secrets in Replit:
   ```
   SESSION_SECRET=your-strong-secret-key
   ADMIN_PASSWORD=your-secure-admin-password
   DATABASE_URL=your-postgresql-url
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-gmail@gmail.com
   SMTP_PASSWORD=your-gmail-app-password
   ```

2. **Deploy**: Click "Deploy" in Replit interface
3. **Access**: Application available at `your-app.replit.app`
4. **Verification**: Test all functionality including:
   - Customer form submission
   - Email notifications
   - Admin dashboard access
   - Status updates and dispatch emails
   - Footer website link functionality

## Maintenance

### Database Backups
- Replit automatically handles database backups
- Manual exports can be done via admin tools

### Monitoring
- Check application logs for errors
- Monitor email delivery status
- Review failed login attempts

## System Status

**✅ PRODUCTION READY**

The application has been thoroughly tested and is ready for deployment with:
- Bulletproof security implementation
- Comprehensive email notification system
- 1-year data retention guarantee
- Professional user experience
- Multi-layer protection against web vulnerabilities

## Support

For technical support or questions:
- Email: orders@slendermorris.com
- Internal: slendermorris@gmail.com
- Main Website: https://slendermorris.dearportal.com

## License

© 2025 Slender Morris Furnishings. All rights reserved.