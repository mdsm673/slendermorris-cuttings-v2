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
                        raise  # Re-raise the OperationalError after all retries
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                # Let other exceptions bubble up immediately
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
    """CRITICAL: Test database connectivity in ALL environments - create tables only in development"""
    is_production = os.environ.get("REPLIT_DEPLOYMENT") == "1" or os.environ.get("FLASK_ENV") == "production"
    
    with app.app_context():
        # Import models module to register all models
        import models
        
        # CRITICAL: ALWAYS test database connection in ALL environments
        logger.info(f"🔍 CRITICAL: Testing database connectivity (Environment: {'PRODUCTION' if is_production else 'DEVELOPMENT'})")
        
        try:
            with db.engine.connect() as connection:
                # Test actual database connectivity
                result = connection.execute(db.text('SELECT 1 as connectivity_test'))
                test_result = result.fetchone()
                if test_result and test_result[0] == 1:
                    logger.info("✅ CRITICAL: Database connectivity verified - connection active")
                else:
                    raise RuntimeError("Database connectivity test failed - unexpected result")
        except Exception as e:
            logger.error(f"🚨 CRITICAL DATABASE FAILURE: Connection test failed: {e}")
            logger.error("🚨 BUSINESS IMPACT: Application cannot serve requests without database")
            logger.error("🚨 IMMEDIATE ACTION REQUIRED: Check DATABASE_URL and network connectivity")
            raise RuntimeError(f"CRITICAL: Database connectivity test failed in {'PRODUCTION' if is_production else 'DEVELOPMENT'}: {e}")
        
        # Environment-specific operations
        if is_production:
            logger.info("🏭 PRODUCTION: Database connection verified - skipping table creation")
            # Verify critical tables exist in production
            try:
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'sample_requests'"))
                    table_result = result.fetchone()
                    if not table_result:
                        raise RuntimeError("CRITICAL: Unable to query database schema - connection may be unstable")
                    table_count = table_result[0]
                    if table_count == 0:
                        raise RuntimeError("CRITICAL: sample_requests table missing in production database")
                    logger.info("✅ PRODUCTION: Critical tables verified")
            except Exception as e:
                logger.error(f"🚨 PRODUCTION DATABASE ERROR: Table verification failed: {e}")
                raise RuntimeError(f"CRITICAL PRODUCTION FAILURE: Database tables missing or inaccessible: {e}")
        else:
            logger.info("🔧 DEVELOPMENT: Creating database tables")
            db.create_all()
            logger.info("✅ DEVELOPMENT: Database tables created successfully")
        
        logger.info("✅ Database initialization completed successfully")
        return True

def setup_application():
    """Setup application components - CRITICAL: REQUIRES database connection"""
    try:
        # CRITICAL: Initialize database with MANDATORY connection
        # If database fails, application MUST NOT continue
        logger.info("CRITICAL: Attempting database initialization - NO FALLBACK ALLOWED")
        
        db_success = initialize_database()
        logger.info("✅ CRITICAL: Database initialization completed successfully")
        
        # Initialize data integrity manager only after successful database connection
        try:
            from data_integrity import data_integrity_manager
            logger.info("✅ Data integrity manager initialized")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Data integrity manager initialization failed: {e}")
            raise RuntimeError(f"CRITICAL APPLICATION FAILURE: Data integrity manager required for business operations: {e}")
        
        logger.info("🟢 APPLICATION READY: All critical systems operational")
        
    except OperationalError as e:
        logger.error(f"🚨 CRITICAL DATABASE FAILURE: Connection failed after retries: {e}")
        logger.error("🚨 BUSINESS DATA AT RISK: Application cannot operate without database")
        logger.error("🚨 REQUIRED ACTION: Check DATABASE_URL and network connectivity")
        # HARD FAIL - Never continue without database
        raise RuntimeError(f"CRITICAL FAILURE: Application requires database connection for business operations. Database error: {e}")
    except Exception as e:
        logger.error(f"🚨 CRITICAL APPLICATION FAILURE: Setup error: {e}")
        logger.error("🚨 BUSINESS OPERATIONS HALTED: Cannot continue without critical systems")
        # HARD FAIL - Never continue with configuration errors
        raise RuntimeError(f"CRITICAL FAILURE: Application setup failed: {e}")

# Initialize database when running under Gunicorn (not just when main.py is called directly)
def init_db_for_gunicorn():
    """Initialize database for Gunicorn workers - CRITICAL: HARD FAIL if database unavailable"""
    logger.info("🔄 Starting CRITICAL database initialization for Gunicorn worker")
    try:
        setup_application()
        logger.info("🟢 Gunicorn worker ready: Database connection verified")
    except Exception as e:
        logger.error(f"🚨 CRITICAL GUNICORN WORKER FAILURE: {e}")
        logger.error("🚨 BUSINESS IMPACT: Worker cannot serve requests without database")
        logger.error("🚨 ESCALATION REQUIRED: Database connection or configuration failure")
        # HARD FAIL - Gunicorn worker MUST NOT start without database
        raise RuntimeError(f"CRITICAL WORKER FAILURE: Gunicorn worker requires database for business operations: {e}")

# Import routes immediately so they're available when gunicorn loads the app
# This must be done after db.init_app(app) to ensure the app context is available
try:
    import routes
    logger.info("Routes imported successfully during app initialization")
except Exception as e:
    logger.error(f"Failed to import routes: {e}")

# Initialize database for Gunicorn workers (when not running main.py directly)
# This ensures database initialization happens even under Gunicorn
if __name__ != "__main__":
    # Running under Gunicorn or being imported as a module
    init_db_for_gunicorn()
