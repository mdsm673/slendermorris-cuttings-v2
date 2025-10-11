# Overview

This is a Flask-based fabric sample ordering system that allows customers to request fabric samples and provides an admin dashboard for managing those requests. The application features a customer-facing form for submitting sample requests and an administrative interface for tracking and managing orders through different status stages (Outstanding, In Progress, Dispatched).

## Recent Changes

### October 2025 - Production Hardening & UI Fixes
- **Admin Dashboard Table Optimization** (October 10, 2025):
  - **Column Width Rebalancing**: Fabric column reduced to 15% with 180px max-width (was 22% unlimited), Company increased to 15%, Email increased to 18% for better space distribution
  - **Compact Table Layout**: Reduced row padding (0.4rem for cells, 0.5rem for headers) for more efficient use of screen space
  - **Top Scrollbar**: Added synchronized scrollbar above table so users don't need to scroll down entire page to access horizontal scrolling
  - **Fabric Column Optimization**: Fabrics now stack vertically in narrow column with smaller badges (0.75rem font, compact padding)
  - **Table Width**: Reduced min-width from 1200px to 900px for more compact layout
  - **Bidirectional Scroll Sync**: JavaScript ensures top and bottom scrollbars stay synchronized with flag-based approach to prevent loops
- **Database Schema Fix** (October 10, 2025):
  - Added missing `iliv_email_sent` column to `archived_requests` table
  - Fixed backup creation failure caused by schema mismatch
  - Column: `BOOLEAN NOT NULL DEFAULT FALSE` to track ILIV email status in archived records
  - Ensures data integrity tools (backup snapshot, integrity check) work correctly
- **Data Integrity Tools Cleanup** (October 10, 2025):
  - Removed non-functional "Run Recovery Scan" button from UI
  - Updated page title from "Data Integrity & Recovery" to "Data Integrity Check"
  - Aligned UI with actual backend capabilities (integrity check and backup snapshot)
  - Cleaned up dead code referencing non-existent database_recovery module
- **Production Security Hardening** (October 10, 2025):
  - Fixed admin authentication to use `CUTTINGS_ADMIN_PASSWORD` environment variable exclusively
  - Removed hard-coded password fallback for enhanced security (production fails safely if secret missing)
  - Implemented SSL enforcement: automatically appends `sslmode=require` to DATABASE_URL for encrypted connections
  - Enhanced health monitoring: CRITICAL alerts only after 3 consecutive failures (prevents false alarms from Neon autosuspend)
  - Database connection resiliency improvements for serverless Postgres (Neon) cold-start handling

### August 2025
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
- **Admin Password Update**: Changed admin login password to "Matthew1234" (case sensitive) as requested
- **Bulletproof Archive System** (August 2, 2025):
  - Implemented automatic archiving of dispatched records after 4 months
  - Created separate archive table for permanent retention
  - Records are NEVER deleted, only moved to archive
  - All archived records remain searchable and retrievable
  - Added admin interface to view and search archived records
  - Manual archive trigger available from admin dashboard
- **Comprehensive Search Functionality** (August 2, 2025):
  - Added powerful search box to admin dashboard that searches across ALL text fields
  - Search includes: company/customer names, emails, references, fabric cuttings, addresses, phone numbers, notes, etc.
  - Search functionality available on both active records and archived records pages
  - Case-insensitive search with partial matching support
  - Clear visual feedback showing current search terms
  - Preserves filters and sorting when searching
- **Real-time Search & UI Improvements** (August 2, 2025):
  - Implemented real-time search with instant yellow highlighting (like browser Ctrl+F)
  - Fixed fabric column to display ALL fabrics for each record (no truncation)
  - Added thick black horizontal lines between table rows for better visual separation
  - Optimized table layout to fit on one screen without horizontal scrolling
  - Shortened date formats to MM/DD for space efficiency
  - Made table more compact while maintaining readability
- **Delete Functionality Removed** (August 2, 2025):
  - Removed delete button and functionality from admin dashboard
  - Records are archived automatically after 4 months when dispatched
  - All records are permanently retained in either active or archive tables
  - No manual deletion capability - focusing on automatic archiving system only
- **Email ILIV Feature Completed** (August 4, 2025):
  - Added gold "Email ILIV" button next to status dropdown for records with fabric selections
  - Clicking button opens modal with pre-filled email template including fabric list
  - Editable recipients field (text area) pre-populated with 4 email addresses
  - Single email sent to all recipients for reply-all functionality
  - Email subject: "[ATT: Juris] - Cuttings Request - Slender Morris"
  - Comprehensive error handling with null-safe DOM element access
  - Immediate visual feedback: Gold "ILIV EMAIL SENT" badge appears under status
  - Uses existing SMTP infrastructure for reliable email delivery
  - Multiple emails can be sent in same session without page refresh
  - Modal auto-closes after successful send with complete state reset
- **Permanent ILIV Email Tracking** (August 5, 2025):
  - Added `iliv_email_sent` database field to permanently track email status
  - Gold "ILIV EMAIL SENT" badges now persist across page reloads and deployments
  - Historical email status preserved in archived records
  - Database automatically updated when ILIV emails are sent successfully
- **Extended Backup Retention & Bulletproof Database Protection** (September 24, 2025):
  - EXTENDED backup retention from 30 days to **MINIMUM 90 DAYS** for business compliance
  - Implemented bulletproof database protection to prevent accidental deletion/disconnection
  - Added forbidden operation blocking (delete_database, drop_database, etc.)
  - Enforced minimum backup count requirements before allowing operations
  - Added comprehensive database protection configuration with fail-safes
  - Created automatic backup cleanup that maintains 90-day retention policy

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
- **ILIV Supplier Requests**: Manual email function to request fabric cuttings from ILIV suppliers via admin dashboard
- **Email Recipients**:
  - New Request: Customer (confirmation), orders@slendermorris.com, slendermorris@gmail.com
  - Dispatch: Original customer, orders@slendermorris.com, slendermorris@gmail.com
  - ILIV Request: orders@slendermorris.com, slendermorris@gmail.com, export@iliv.co.uk, jurijs_peremots@smd-textiles.co.uk
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