"""Production configuration settings"""
import os

class Config:
    """Production configuration"""
    
    # Detect production environment first
    is_production = os.environ.get("REPLIT_DEPLOYMENT") == "1" or os.environ.get("FLASK_ENV") == "production"
    
    # Environment-specific Flask settings
    DEBUG = False if is_production else True
    TESTING = False
    
    # Environment-specific logging levels
    LOG_LEVEL = "INFO" if is_production else "DEBUG"
    
    # Security - require SESSION_SECRET in production
    session_secret = os.environ.get("SESSION_SECRET")
    if not session_secret and is_production:
        raise RuntimeError("Production deployment requires SESSION_SECRET environment variable to be set")
    SECRET_KEY = session_secret or "dev-secret-key-change-in-production"
    
    # Environment-specific cookie security
    SESSION_COOKIE_SECURE = True if is_production else False  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True  # No JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours
    
    # Database configuration - BULLETPROOF PROTECTION MEASURES
    database_url = os.environ.get("DATABASE_URL")
    
    # CRITICAL: Always use environment DATABASE_URL (never hard-code credentials)
    if not database_url:
        if is_production:
            raise RuntimeError("CRITICAL: DATABASE_URL environment variable is required for production deployment")
        else:
            raise RuntimeError("CRITICAL: DATABASE_URL environment variable is required for development")
    
    # BULLETPROOF DATABASE PROTECTION: Prevent accidental deletion/disconnection
    DATABASE_PROTECTION_ENABLED = True
    ALLOW_DATABASE_DELETION = False  # NEVER allow database deletion in production
    MINIMUM_BACKUP_COUNT = 3  # Require minimum backups before operations
    
    # PRODUCTION DEPLOYMENT SECURITY HARDENING
    if is_production:
        # Force HTTPS in production
        SESSION_COOKIE_SECURE = True
        # Strict transport security
        FORCE_HTTPS = True
        # Database connection security
        DATABASE_SSL_REQUIRED = True
        # Enhanced logging
        AUDIT_LOG_ENABLED = True
    
    # Validate database URL format
    if not database_url.startswith(('postgresql://', 'postgres://')):
        raise ValueError(f"CRITICAL: DATABASE_URL must be a PostgreSQL connection string, got: {database_url[:50]}...")
    
    # SSL HARDENING: Enforce TLS for Neon connections (defense-in-depth)
    # Append sslmode=require if not present to ensure encrypted connections
    if 'sslmode=' not in database_url:
        import logging
        separator = '&' if '?' in database_url else '?'
        database_url = f"{database_url}{separator}sslmode=require"
        logging.info("🔒 SSL hardening: Appended sslmode=require to DATABASE_URL")
    
    # Verify Neon pooler endpoint usage (recommended for serverless Postgres)
    if 'neon.tech' in database_url.lower() or 'neon.postgres' in database_url.lower():
        if '.pooler.' in database_url.lower():
            import logging
            logging.info("✅ Neon pooler endpoint detected - optimal for serverless connection management")
        else:
            import logging
            logging.warning("⚠️ Direct Neon compute endpoint detected - consider using pooler endpoint for better cold-start resilience")
    
    # Use ONLY the environment-provided DATABASE_URL (security compliance)
    SQLALCHEMY_DATABASE_URI = database_url
    # Environment-specific database connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 20 if is_production else 5,  # More connections in production
        "max_overflow": 40 if is_production else 10,  # Higher overflow in production
        "pool_timeout": 30 if is_production else 10,  # Longer timeout in production
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Data retention - EXTENDED FOR BUSINESS COMPLIANCE
    DATA_RETENTION_DAYS = 365  # 1 year minimum for database records
    BACKUP_RETENTION_DAYS = 90  # MINIMUM 90 days for backup files (business requirement)
    ARCHIVE_AFTER_MONTHS = 4  # Archive dispatched records after 4 months
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    
    # Email settings
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Admin settings - SECURITY HARDENED
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password and is_production:
        # PRODUCTION SECURITY: Require ADMIN_PASSWORD environment variable
        raise RuntimeError("CRITICAL: Production deployment requires ADMIN_PASSWORD environment variable to be set for security")
    ADMIN_PASSWORD = admin_password or "Matthew1234"  # fallback for development only
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
    
    # Request limits
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max request size
    
    # Environment-specific error handling
    PROPAGATE_EXCEPTIONS = False if is_production else True
    SEND_FILE_MAX_AGE_DEFAULT = 31536000 if is_production else 0  # 1 year cache in prod, no cache in dev
    MAX_FABRIC_CUTTINGS = 5
    MAX_FIELD_LENGTH = {
        'company_name': 100,
        'email': 120,
        'phone': 20,
        'reference': 100,
        'street_address': 200,
        'city': 100,
        'state_province': 100,
        'postal_code': 20,
        'country': 100,
        'fabric_cutting': 200,
        'additional_notes': 1000
    }