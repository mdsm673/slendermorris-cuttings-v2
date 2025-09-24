"""Production configuration settings"""
import os

class Config:
    """Production configuration"""
    
    # Detect production environment first
    is_production = os.environ.get("REPLIT_DEPLOYMENT") == "1" or os.environ.get("FLASK_ENV") == "production"
    
    # Security - require SESSION_SECRET in production
    session_secret = os.environ.get("SESSION_SECRET")
    if not session_secret and is_production:
        raise RuntimeError("Production deployment requires SESSION_SECRET environment variable to be set")
    SECRET_KEY = session_secret or "dev-secret-key-change-in-production"
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours
    
    # Database configuration - MANDATORY environment variable enforcement
    database_url = os.environ.get("DATABASE_URL")
    
    # CRITICAL: Always use environment DATABASE_URL (never hard-code credentials)
    if not database_url:
        if is_production:
            raise RuntimeError("CRITICAL: DATABASE_URL environment variable is required for production deployment")
        else:
            raise RuntimeError("CRITICAL: DATABASE_URL environment variable is required for development")
    
    # Validate database URL format
    if not database_url.startswith(('postgresql://', 'postgres://')):
        raise ValueError(f"CRITICAL: DATABASE_URL must be a PostgreSQL connection string, got: {database_url[:50]}...")
    
    # Use ONLY the environment-provided DATABASE_URL (security compliance)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Data retention
    DATA_RETENTION_DAYS = 365  # 1 year minimum
    ARCHIVE_AFTER_MONTHS = 4  # Archive dispatched records after 4 months
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    
    # Email settings
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Admin settings - require password in production
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password and is_production:
        raise RuntimeError("Production deployment requires ADMIN_PASSWORD environment variable to be set")
    ADMIN_PASSWORD = admin_password or "Matthew1234"  # fallback only in development
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
    
    # Request limits
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max request size
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