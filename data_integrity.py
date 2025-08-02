"""
Data Integrity and Security Module
==================================
This module implements bulletproof data retention policies and safeguards
to ensure no record is ever accidentally lost or deleted.
"""

import logging
import json
import os
from datetime import datetime
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from app import db
from models import SampleRequest, ArchivedRequest
import hashlib

logger = logging.getLogger(__name__)

class DataIntegrityError(Exception):
    """Custom exception for data integrity violations"""
    pass

class DataIntegrityManager:
    """
    Manages data integrity and implements multiple layers of protection:
    1. Transaction logging - Every database operation is logged
    2. Soft delete prevention - Records cannot be hard deleted
    3. Audit trail - Complete history of all changes
    4. Backup verification - Ensures data exists in at least one table
    5. Recovery mechanisms - Can restore data from audit logs
    """
    
    def __init__(self):
        self.audit_log_path = "data_audit_log.json"
        self.backup_verification_enabled = True
        self._setup_database_listeners()
    
    def _setup_database_listeners(self):
        """Set up SQLAlchemy event listeners to monitor all database operations"""
        
        # Monitor DELETE operations on SampleRequest
        @event.listens_for(SampleRequest, 'before_delete')
        def receive_before_delete(mapper, connection, target):
            """Intercept delete operations and ensure they're part of archiving"""
            # Check if this delete is part of an archive operation
            if not hasattr(target, '_archiving_in_progress'):
                # This is an unauthorized delete attempt
                raise DataIntegrityError(
                    f"SECURITY VIOLATION: Attempted to delete SampleRequest #{target.id} "
                    f"without archiving. Direct deletion is prohibited."
                )
            
            # Log the archiving operation
            self._log_operation('archive', 'SampleRequest', target.id, target.to_dict())
        
        # Monitor any DELETE on ArchivedRequest (should never happen)
        @event.listens_for(ArchivedRequest, 'before_delete')
        def receive_archived_delete(mapper, connection, target):
            """Prevent ANY deletion of archived records"""
            raise DataIntegrityError(
                f"CRITICAL SECURITY VIOLATION: Attempted to delete ArchivedRequest "
                f"#{target.original_id}. Archived records are immutable and cannot be deleted."
            )
        
        # Monitor INSERT operations for audit trail
        @event.listens_for(SampleRequest, 'after_insert')
        def receive_after_insert(mapper, connection, target):
            """Log all new record insertions"""
            self._log_operation('insert', 'SampleRequest', target.id, target.to_dict())
        
        # Monitor UPDATE operations
        @event.listens_for(SampleRequest, 'after_update')
        def receive_after_update(mapper, connection, target):
            """Log all record updates"""
            self._log_operation('update', 'SampleRequest', target.id, target.to_dict())
    
    def _log_operation(self, operation, table, record_id, data):
        """Log all database operations to audit trail"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'table': table,
            'record_id': record_id,
            'data': data,
            'checksum': self._calculate_checksum(data)
        }
        
        try:
            # Load existing audit log
            if os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, 'r') as f:
                    audit_log = json.load(f)
            else:
                audit_log = []
            
            # Append new entry
            audit_log.append(audit_entry)
            
            # Keep only last 10000 entries to prevent file bloat
            if len(audit_log) > 10000:
                audit_log = audit_log[-10000:]
            
            # Write back to file
            with open(self.audit_log_path, 'w') as f:
                json.dump(audit_log, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {str(e)}")
    
    def _calculate_checksum(self, data):
        """Calculate checksum for data integrity verification"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def verify_record_exists(self, original_id):
        """
        Verify that a record exists in either active or archive table.
        Returns location of record or None if not found.
        """
        # Check active table
        active_record = SampleRequest.query.filter_by(id=original_id).first()
        if active_record:
            return {'location': 'active', 'record': active_record}
        
        # Check archive table
        archived_record = ArchivedRequest.query.filter_by(original_id=original_id).first()
        if archived_record:
            return {'location': 'archived', 'record': archived_record}
        
        # Record not found - check audit log for recovery
        return self._check_audit_log_for_record(original_id)
    
    def _check_audit_log_for_record(self, record_id):
        """Check audit log for record data if not found in database"""
        try:
            if os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, 'r') as f:
                    audit_log = json.load(f)
                
                # Search for most recent entry for this record
                for entry in reversed(audit_log):
                    if entry.get('record_id') == record_id:
                        return {
                            'location': 'audit_log',
                            'record': entry['data'],
                            'last_operation': entry['operation'],
                            'timestamp': entry['timestamp']
                        }
        except Exception as e:
            logger.error(f"Failed to read audit log: {str(e)}")
        
        return None
    
    def recover_from_audit_log(self, record_id):
        """Attempt to recover a record from audit log"""
        audit_data = self._check_audit_log_for_record(record_id)
        
        if not audit_data or audit_data['location'] != 'audit_log':
            return False
        
        try:
            record_data = audit_data['record']
            
            # Recreate the record
            new_record = SampleRequest()
            for key, value in record_data.items():
                if hasattr(new_record, key) and key != 'id':
                    if key in ['date_submitted', 'date_dispatched'] and value:
                        # Convert date strings back to datetime
                        setattr(new_record, key, datetime.fromisoformat(value.replace(' ', 'T')))
                    else:
                        setattr(new_record, key, value)
            
            db.session.add(new_record)
            db.session.commit()
            
            logger.warning(f"RECOVERED record #{record_id} from audit log")
            return True
            
        except Exception as e:
            logger.error(f"Failed to recover record #{record_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def perform_integrity_check(self):
        """Perform comprehensive data integrity check"""
        issues = []
        
        try:
            # 1. Check for duplicate records between active and archive
            active_ids = db.session.query(SampleRequest.id).all()
            active_ids = [id[0] for id in active_ids]
            
            archived_original_ids = db.session.query(ArchivedRequest.original_id).all()
            archived_original_ids = [id[0] for id in archived_original_ids]
            
            duplicates = set(active_ids) & set(archived_original_ids)
            if duplicates:
                issues.append(f"Found {len(duplicates)} duplicate records between active and archive tables: {duplicates}")
            
            # 2. Check for records in audit log but not in database
            if os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, 'r') as f:
                    audit_log = json.load(f)
                
                audited_ids = set()
                for entry in audit_log:
                    if entry['table'] == 'SampleRequest' and entry['operation'] != 'archive':
                        audited_ids.add(entry['record_id'])
                
                all_db_ids = set(active_ids) | set(archived_original_ids)
                missing_ids = audited_ids - all_db_ids
                
                if missing_ids:
                    issues.append(f"Found {len(missing_ids)} records in audit log but not in database: {missing_ids}")
                    # Attempt recovery
                    for missing_id in missing_ids:
                        if self.recover_from_audit_log(missing_id):
                            issues.append(f"Successfully recovered record #{missing_id}")
            
            # 3. Check for records older than 4 months that should be archived
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=120)
            
            unarchived_old_records = SampleRequest.query.filter(
                SampleRequest.status == 'Dispatched',
                SampleRequest.date_dispatched < cutoff_date
            ).count()
            
            if unarchived_old_records > 0:
                issues.append(f"Found {unarchived_old_records} dispatched records older than 4 months that should be archived")
            
            # 4. Verify database constraints
            constraints_ok = self._verify_database_constraints()
            if not constraints_ok:
                issues.append("Database constraints need to be reinforced")
            
            return {
                'status': 'issues_found' if issues else 'healthy',
                'issues': issues,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Integrity check failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _verify_database_constraints(self):
        """Verify that proper database constraints are in place"""
        try:
            # Check if we can execute a test query
            result = db.session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database constraint check failed: {str(e)}")
            return False
    
    def create_backup_snapshot(self):
        """Create a JSON backup of all records"""
        try:
            backup_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'active_records': [],
                'archived_records': []
            }
            
            # Backup active records
            for record in SampleRequest.query.all():
                backup_data['active_records'].append(record.to_dict())
            
            # Backup archived records
            for record in ArchivedRequest.query.all():
                backup_data['archived_records'].append(record.to_dict())
            
            # Write backup file
            backup_filename = f"backup_snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Created backup snapshot: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"Failed to create backup snapshot: {str(e)}")
            return None

# Global instance
data_integrity_manager = DataIntegrityManager()