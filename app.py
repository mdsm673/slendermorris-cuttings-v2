import os
import logging
import time
from functools import wraps

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def retry_db_operation(max_retries=3, delay=2):
    """Decorator to retry database operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                        return False
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    logger.error(f"Unexpected error in database operation: {e}")
                    return False
            return False
        return wrapper
    return decorator

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Security headers middleware
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# initialize the app with the extension
db.init_app(app)

@retry_db_operation(max_retries=3, delay=2)
def initialize_database():
    """Initialize database tables with retry logic"""
    try:
        with app.app_context():
            # Import models first
            from models import SampleRequest, ArchivedRequest  # Import specific models
            
            # Test database connection
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            logger.info("Database connection successful")
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def setup_application():
    """Setup application components that don't require database"""
    try:
        with app.app_context():
            # Routes are already imported at module level
            # Try to initialize database
            db_success = initialize_database()
            
            if db_success:
                # Initialize data integrity manager only if database is available
                try:
                    from data_integrity import data_integrity_manager
                    logger.info("Data integrity manager initialized")
                except Exception as e:
                    logger.warning(f"Data integrity manager initialization failed: {e}")
            else:
                logger.warning("Application started without database connection. Some features may be limited.")
                
    except Exception as e:
        logger.error(f"Application setup failed: {e}")

# Import routes immediately so they're available when gunicorn loads the app
# This must be done after db.init_app(app) to ensure the app context is available
try:
    import routes
    logger.info("Routes imported successfully during app initialization")
except Exception as e:
    logger.error(f"Failed to import routes: {e}")

# Defer database initialization - don't do it during import
# This will be called from main.py or when the app actually starts
