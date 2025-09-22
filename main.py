from app import app, setup_application
import logging
import sys

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Setup application with graceful database handling
        logger.info("Starting application setup...")
        setup_application()
        logger.info("Application setup completed successfully")
        
        # Start the Flask development server
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.info("Application will still attempt to start without full initialization")
        try:
            # Try to start the app even if setup failed
            app.run(host="0.0.0.0", port=5000, debug=True)
        except Exception as startup_error:
            logger.critical(f"Critical startup failure: {startup_error}")
            sys.exit(1)
