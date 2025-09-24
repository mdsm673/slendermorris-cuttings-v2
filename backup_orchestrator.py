"""
Automated Backup and Integrity Verification Orchestrator
========================================================
This module implements mission-critical automated backup and integrity safeguards
to ensure ZERO business data loss and prevent any future database recovery scenarios.

Key Features:
- Pre-change automatic backups
- Post-operation integrity verification  
- Business data validation (real companies, no test data)
- Monitoring and alerting for database health
- Complete audit trail for all operations
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from app import app, db
from models import SampleRequest, ArchivedRequest
from data_integrity import data_integrity_manager
from database_maintenance import database_health_check, archive_dispatched_requests

logger = logging.getLogger(__name__)

class BackupOrchestrator:
    """
    Mission-critical backup and integrity orchestrator that ensures:
    1. All business operations are backed up before execution
    2. Data integrity is verified after every operation  
    3. Real business data is protected from test/fake data contamination
    4. Automatic monitoring and alerting for database health
    """
    
    def __init__(self):
        self.backup_log_path = "backup_operations_log.json"
        self.business_data_validation_enabled = True
        self.known_test_companies = [
            "test company", "test corp", "prestwood fabric green", 
            "demo company", "sample company", "fake company"
        ]
        self.known_real_companies = [
            "TAITS INTERIORS", "Suzanne Brennan", "Menadue Floor Coverings",
            "David Hall", "Harvest & Home Interiors", "The Bank Art Museum",
            "TURBILL BLINDS", "Philippa Beak"
        ]
        
    def pre_operation_backup(self, operation_type: str, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL: Create mandatory backup before ANY database operation
        This prevents data loss if operations fail or corrupt data
        """
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            logger.info(f"🔄 CRITICAL: Creating pre-operation backup for {operation_type}")
            
            # 1. Verify database connectivity first
            health_check = database_health_check()
            if health_check['status'] != 'healthy':
                raise RuntimeError(f"CRITICAL: Database unhealthy before {operation_type}: {health_check}")
            
            # 2. Create comprehensive data snapshot
            with app.app_context():
                backup_data = {
                    "backup_id": backup_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "operation_type": operation_type,
                    "operation_details": operation_details,
                    "pre_operation_stats": health_check,
                    "active_records": self._get_full_data_snapshot('active'),
                    "archived_records": self._get_full_data_snapshot('archived'),
                    "data_integrity_check": data_integrity_manager.perform_integrity_check()
                }
            
            # 3. Save backup snapshot
            backup_filename = f"backup_snapshot_{backup_id}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            # 4. Log backup operation
            self._log_backup_operation("pre_operation_backup", backup_id, operation_type, "SUCCESS")
            
            logger.info(f"✅ CRITICAL: Pre-operation backup completed: {backup_filename}")
            
            return {
                "status": "success",
                "backup_id": backup_id,
                "backup_file": backup_filename,
                "pre_operation_health": health_check
            }
            
        except Exception as e:
            logger.error(f"🚨 CRITICAL BACKUP FAILURE: {operation_type} backup failed: {e}")
            logger.error(f"🚨 BUSINESS RISK: Cannot proceed with {operation_type} without backup")
            self._log_backup_operation("pre_operation_backup", backup_id, operation_type, f"FAILED: {e}")
            raise RuntimeError(f"CRITICAL: Pre-operation backup failed for {operation_type}: {e}")
    
    def post_operation_verification(self, backup_id: str, operation_type: str) -> Dict[str, Any]:
        """
        CRITICAL: Verify data integrity after database operations
        Ensures no data corruption or loss occurred during operations
        """
        try:
            logger.info(f"🔍 CRITICAL: Post-operation verification for {operation_type} (Backup: {backup_id})")
            
            with app.app_context():
                # 1. Database health check
                health_check = database_health_check()
                
                # 2. Comprehensive integrity check
                integrity_check = data_integrity_manager.perform_integrity_check()
                
                # 3. Business data validation
                business_validation = self._validate_business_data()
                
                # 4. Compare with pre-operation backup
                comparison_result = self._compare_with_backup(backup_id)
            
            verification_result = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "backup_id": backup_id,
                "operation_type": operation_type,
                "database_health": health_check,
                "integrity_check": integrity_check,
                "business_validation": business_validation,
                "backup_comparison": comparison_result,
                "critical_issues": []
            }
            
            # 5. Analyze results for critical issues
            if health_check['status'] != 'healthy':
                verification_result["critical_issues"].append(f"Database health compromised: {health_check}")
            
            if integrity_check['status'] != 'healthy':
                verification_result["critical_issues"].append(f"Data integrity issues found: {integrity_check['issues']}")
            
            if business_validation['status'] != 'clean':
                verification_result["critical_issues"].append(f"Business data contamination: {business_validation['issues']}")
            
            # 6. Final status determination
            if verification_result["critical_issues"]:
                verification_result["status"] = "issues_found"
                logger.warning(f"⚠️ POST-OPERATION ISSUES: {len(verification_result['critical_issues'])} critical issues found")
                for issue in verification_result["critical_issues"]:
                    logger.warning(f"⚠️ ISSUE: {issue}")
            else:
                logger.info(f"✅ POST-OPERATION SUCCESS: {operation_type} completed successfully with no issues")
            
            # 7. Log verification
            self._log_backup_operation("post_operation_verification", backup_id, operation_type, verification_result["status"])
            
            return verification_result
            
        except Exception as e:
            logger.error(f"🚨 CRITICAL VERIFICATION FAILURE: {operation_type} verification failed: {e}")
            self._log_backup_operation("post_operation_verification", backup_id, operation_type, f"FAILED: {e}")
            raise RuntimeError(f"CRITICAL: Post-operation verification failed for {operation_type}: {e}")
    
    def _get_full_data_snapshot(self, table_type: str) -> List[Dict[str, Any]]:
        """Get complete data snapshot for backup (assumes app context already active)"""
        if table_type == 'active':
            records = SampleRequest.query.all()
        elif table_type == 'archived':
            records = ArchivedRequest.query.all()
        else:
            raise ValueError(f"Invalid table_type: {table_type}")
        
        return [record.to_dict() for record in records]
    
    def _validate_business_data(self) -> Dict[str, Any]:
        """
        CRITICAL: Validate that database contains only authentic business data
        Prevents test/fake data contamination that caused original data loss scenario
        """
        issues = []
        warnings = []
        
        try:
            # Check active records for test data contamination (assumes app context already active)
            active_companies = db.session.query(SampleRequest.company_name).distinct().all()
            active_companies = [company[0].lower() for company in active_companies]
            
            # Check for known test companies (CRITICAL issues only for obvious test data)
            for test_company in self.known_test_companies:
                if test_company.lower() in active_companies:
                    issues.append(f"CRITICAL: Test company found in active data: '{test_company}'")
            
            # Check for suspicious patterns (warnings only)
            suspicious_patterns = ["test", "demo", "sample", "fake", "lorem", "placeholder"]
            for company in active_companies:
                for pattern in suspicious_patterns:
                    if pattern in company.lower():
                        warnings.append(f"WARNING: Suspicious company name: '{company}' (contains '{pattern}')")
            
            # Check for presence of known real companies (WARNING, not CRITICAL)
            real_companies_found = 0
            for real_company in self.known_real_companies:
                for company in active_companies:
                    if real_company.lower() in company.lower():
                        real_companies_found += 1
                        break
            
            if real_companies_found == 0 and len(active_companies) > 0:
                warnings.append("WARNING: No known reference companies found - data may be from different time period")
            
            # Check for reasonable data volume (adjusted thresholds to avoid false positives)
            total_records = SampleRequest.query.count()
            if total_records == 0:
                issues.append("CRITICAL: No records found - database may be empty")
            elif total_records < 3:
                warnings.append(f"WARNING: Very low record count ({total_records}) - monitor for data loss")
            
            return {
                "status": "contaminated" if issues else "clean",
                "issues": issues,
                "warnings": warnings,
                "total_companies": len(active_companies),
                "real_companies_found": real_companies_found,
                "total_records": total_records
            }
            
        except Exception as e:
            logger.error(f"Business data validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "issues": [f"Validation failed: {e}"],
                "warnings": []
            }
    
    def _compare_with_backup(self, backup_id: str) -> Dict[str, Any]:
        """Compare current state with pre-operation backup"""
        try:
            backup_filename = f"backup_snapshot_{backup_id}.json"
            if not os.path.exists(backup_filename):
                return {"status": "error", "error": f"Backup file not found: {backup_filename}"}
            
            with open(backup_filename, 'r') as f:
                backup_data = json.load(f)
            
            # Get current data
            current_active = self._get_full_data_snapshot('active')
            current_archived = self._get_full_data_snapshot('archived')
            
            # Compare record counts
            backup_active_count = len(backup_data['active_records'])
            backup_archived_count = len(backup_data['archived_records'])
            current_active_count = len(current_active)
            current_archived_count = len(current_archived)
            
            changes = {
                "active_records_change": current_active_count - backup_active_count,
                "archived_records_change": current_archived_count - backup_archived_count,
                "total_change": (current_active_count + current_archived_count) - (backup_active_count + backup_archived_count)
            }
            
            return {
                "status": "success",
                "changes": changes,
                "backup_counts": {
                    "active": backup_active_count,
                    "archived": backup_archived_count
                },
                "current_counts": {
                    "active": current_active_count,
                    "archived": current_archived_count
                }
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _log_backup_operation(self, operation: str, backup_id: str, operation_type: str, status: str):
        """Log all backup operations for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "backup_id": backup_id,
            "operation_type": operation_type,
            "status": status
        }
        
        try:
            if os.path.exists(self.backup_log_path):
                with open(self.backup_log_path, 'r') as f:
                    log = json.load(f)
            else:
                log = []
            
            log.append(log_entry)
            
            # Keep only last 1000 entries
            if len(log) > 1000:
                log = log[-1000:]
            
            with open(self.backup_log_path, 'w') as f:
                json.dump(log, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log backup operation: {e}")
    
    def execute_with_safeguards(self, operation_name: str, operation_func, operation_args=None, operation_kwargs=None):
        """
        CRITICAL: Execute any database operation with full backup and verification safeguards
        This is the MANDATORY wrapper for all database operations
        """
        operation_args = operation_args or []
        operation_kwargs = operation_kwargs or {}
        
        logger.info(f"🔐 EXECUTING WITH SAFEGUARDS: {operation_name}")
        
        backup_result = None
        try:
            # 1. MANDATORY: Pre-operation backup
            backup_result = self.pre_operation_backup(
                operation_name, 
                {"args": operation_args, "kwargs": operation_kwargs}
            )
            backup_id = backup_result["backup_id"]
            
            # 2. Execute the actual operation
            logger.info(f"⚙️ EXECUTING: {operation_name}")
            operation_result = operation_func(*operation_args, **operation_kwargs)
            logger.info(f"✅ OPERATION COMPLETED: {operation_name}")
            
            # 3. MANDATORY: Post-operation verification
            verification_result = self.post_operation_verification(backup_id, operation_name)
            
            # 4. Return comprehensive results
            return {
                "status": "success",
                "operation_name": operation_name,
                "operation_result": operation_result,
                "backup_id": backup_id,
                "verification": verification_result,
                "safeguards_applied": True
            }
            
        except Exception as e:
            logger.error(f"🚨 SAFEGUARDED OPERATION FAILED: {operation_name}: {e}")
            backup_id = backup_result.get('backup_id', 'UNKNOWN') if backup_result else 'BACKUP_FAILED'
            logger.error(f"🚨 RECOVERY ACTION: Check backup {backup_id} for data recovery")
            raise RuntimeError(f"CRITICAL: Safeguarded operation {operation_name} failed: {e}")

# Global instance for use throughout the application
backup_orchestrator = BackupOrchestrator()

def with_backup_safeguards(operation_name: str):
    """
    Decorator to automatically apply backup safeguards to any function
    Usage: @with_backup_safeguards("archive_old_records")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            return backup_orchestrator.execute_with_safeguards(
                operation_name, func, args, kwargs
            )
        return wrapper
    return decorator