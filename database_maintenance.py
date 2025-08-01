"""Database maintenance utilities"""
from datetime import datetime, timedelta
from app import app, db
from models import SampleRequest, ArchivedRequest
import logging

logger = logging.getLogger(__name__)

def archive_dispatched_requests(months_before_archive=4):
    """
    Archive dispatched requests older than 4 months to permanent archive table.
    Records are NEVER deleted - only moved to archive for long-term retention.
    """
    # Calculate cutoff date (4 months ago)
    cutoff_date = datetime.utcnow() - timedelta(days=months_before_archive * 30)
    
    with app.app_context():
        # Find dispatched requests older than 4 months
        requests_to_archive = SampleRequest.query.filter(
            SampleRequest.status == 'Dispatched',
            SampleRequest.date_dispatched < cutoff_date
        ).all()
        
        archived_count = 0
        
        for request in requests_to_archive:
            try:
                # Create archived record
                archived = ArchivedRequest(
                    original_id=request.id,
                    customer_name=request.customer_name,
                    email=request.email,
                    phone=request.phone,
                    company_name=request.company_name,
                    reference=request.reference,
                    street_address=request.street_address,
                    city=request.city,
                    state_province=request.state_province,
                    postal_code=request.postal_code,
                    country=request.country,
                    fabric_selections=request.fabric_selections,
                    additional_notes=request.additional_notes,
                    status=request.status,
                    date_submitted=request.date_submitted,
                    date_dispatched=request.date_dispatched
                )
                
                db.session.add(archived)
                db.session.delete(request)  # Remove from active table (not deleted, just moved)
                archived_count += 1
                
            except Exception as e:
                logger.error(f"Failed to archive request {request.id}: {str(e)}")
                db.session.rollback()
                continue
        
        if archived_count > 0:
            db.session.commit()
            logger.info(f"Successfully archived {archived_count} dispatched requests older than {months_before_archive} months")
        
        return archived_count

def database_health_check():
    """Check database connectivity and basic health"""
    try:
        with app.app_context():
            # Test connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            
            # Get statistics from active table
            total_requests = SampleRequest.query.count()
            outstanding = SampleRequest.query.filter_by(status='Outstanding').count()
            in_progress = SampleRequest.query.filter_by(status='In Progress').count()
            dispatched = SampleRequest.query.filter_by(status='Dispatched').count()
            
            # Get archived statistics
            total_archived = ArchivedRequest.query.count()
            
            logger.info(f"Database health check passed")
            logger.info(f"Active requests: {total_requests}")
            logger.info(f"Outstanding: {outstanding}, In Progress: {in_progress}, Dispatched: {dispatched}")
            logger.info(f"Archived requests: {total_archived}")
            
            return {
                'status': 'healthy',
                'total_active': total_requests,
                'outstanding': outstanding,
                'in_progress': in_progress,
                'dispatched': dispatched,
                'total_archived': total_archived,
                'total_all_time': total_requests + total_archived
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

def retrieve_all_records(search_term=None, include_archived=True):
    """
    Retrieve all records (active and archived) with optional search.
    This ensures bulletproof data retrieval - nothing is ever lost.
    """
    with app.app_context():
        results = {'active': [], 'archived': []}
        
        # Search active records
        query = SampleRequest.query
        if search_term:
            query = query.filter(
                db.or_(
                    SampleRequest.customer_name.contains(search_term),
                    SampleRequest.company_name.contains(search_term),
                    SampleRequest.email.contains(search_term),
                    SampleRequest.reference.contains(search_term)
                )
            )
        results['active'] = query.all()
        
        # Search archived records if requested
        if include_archived:
            archived_query = ArchivedRequest.query
            if search_term:
                archived_query = archived_query.filter(
                    db.or_(
                        ArchivedRequest.customer_name.contains(search_term),
                        ArchivedRequest.company_name.contains(search_term),
                        ArchivedRequest.email.contains(search_term),
                        ArchivedRequest.reference.contains(search_term)
                    )
                )
            results['archived'] = archived_query.all()
        
        return results

if __name__ == "__main__":
    # Run maintenance tasks
    print("Running database maintenance...")
    health = database_health_check()
    print(f"Database health: {health}")
    
    # Archive old dispatched requests
    archived = archive_dispatched_requests()
    print(f"Archived {archived} dispatched requests older than 4 months")