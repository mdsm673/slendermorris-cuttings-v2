"""Production configuration settings"""
import os

class Config:
    """Production configuration"""
    
    # Security
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Data retention
    DATA_RETENTION_DAYS = 365  # 1 year minimum
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    
    # Email settings
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Admin settings
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
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