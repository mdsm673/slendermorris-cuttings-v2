"""Database maintenance utilities"""
from datetime import datetime, timedelta
from app import app, db
from models import SampleRequest
import logging

logger = logging.getLogger(__name__)

def archive_old_requests(days_to_keep=365):
    """
    Archive old requests (currently just logs, no deletion per requirements)
    In production, this could move old records to an archive table
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    with app.app_context():
        old_requests = SampleRequest.query.filter(
            SampleRequest.date_submitted < cutoff_date
        ).count()
        
        logger.info(f"Found {old_requests} requests older than {days_to_keep} days")
        logger.info("No deletion performed - data retention policy requires 1 year minimum retention")
        
        return old_requests

def database_health_check():
    """Check database connectivity and basic health"""
    try:
        with app.app_context():
            # Test connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            
            # Get statistics
            total_requests = SampleRequest.query.count()
            outstanding = SampleRequest.query.filter_by(status='Outstanding').count()
            in_progress = SampleRequest.query.filter_by(status='In Progress').count()
            dispatched = SampleRequest.query.filter_by(status='Dispatched').count()
            
            logger.info(f"Database health check passed")
            logger.info(f"Total requests: {total_requests}")
            logger.info(f"Outstanding: {outstanding}, In Progress: {in_progress}, Dispatched: {dispatched}")
            
            return {
                'status': 'healthy',
                'total_requests': total_requests,
                'outstanding': outstanding,
                'in_progress': in_progress,
                'dispatched': dispatched
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}

def backup_database():
    """
    Create a database backup (placeholder - actual implementation depends on deployment)
    Replit handles automatic backups
    """
    logger.info("Database backup initiated - handled by Replit infrastructure")
    return True

if __name__ == "__main__":
    # Run maintenance tasks
    print("Running database maintenance...")
    health = database_health_check()
    print(f"Database health: {health}")
    
    archived = archive_old_requests()
    print(f"Archived records check: {archived} old records found (not deleted)")