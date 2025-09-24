"""
Database Connectivity Monitoring and Alerting System
Provides continuous monitoring, health checks, and alert notifications for database connectivity
"""

import os
import time
import json
import logging
import smtplib
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, DatabaseError

# Import application components
from app import app, db
from config import Config

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class HealthMetrics:
    """Database health metrics data structure"""
    timestamp: str
    connectivity_status: str
    response_time_ms: float
    connection_count: int
    error_message: Optional[str] = None
    query_success: bool = True
    pool_info: Optional[Dict] = None

@dataclass
class AlertConfig:
    """Alert configuration and thresholds"""
    max_response_time_ms: float = 5000  # 5 seconds
    max_failed_checks: int = 3  # Alert after 3 consecutive failures
    check_interval_seconds: int = 60  # Check every minute
    alert_cooldown_minutes: int = 15  # Don't spam alerts
    
    # Email alert settings
    enable_email_alerts: bool = True
    alert_recipients: Optional[List[str]] = None
    smtp_settings: Optional[Dict] = None
    
    def __post_init__(self):
        if self.alert_recipients is None:
            self.alert_recipients = [
                "orders@slendermorris.com",
                "slendermorris@gmail.com"
            ]
        
        if self.smtp_settings is None:
            self.smtp_settings = {
                'host': Config.SMTP_HOST or 'smtp.gmail.com',
                'port': Config.SMTP_PORT or 587,
                'username': Config.SMTP_USERNAME,
                'password': Config.SMTP_PASSWORD
            }

class DatabaseMonitor:
    """
    Comprehensive database connectivity monitoring and alerting system
    """
    
    def __init__(self, config: Optional[AlertConfig] = None):
        self.config = config or AlertConfig()
        self.health_history: List[HealthMetrics] = []
        self.consecutive_failures = 0
        self.last_alert_time: Optional[datetime] = None
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Validate SMTP configuration at startup
        self._validate_smtp_config()
        
        logger.info("🔍 Database Monitor initialized")
    
    def _validate_smtp_config(self):
        """Validate SMTP configuration for email alerts"""
        if self.config.enable_email_alerts:
            smtp_config = self.config.smtp_settings or {}
            username = smtp_config.get('username')
            
            if not username:
                logger.warning("⚠️ SMTP_USERNAME not configured - email alerts will be disabled")
                self.config.enable_email_alerts = False
            else:
                logger.info(f"📧 Email alerts enabled - notifications will be sent to {len(self.config.alert_recipients or [])} recipients")
        else:
            logger.info("📧 Email alerts disabled in configuration")
    
    def add_alert_callback(self, callback: Callable):
        """Add custom alert callback function"""
        self.alert_callbacks.append(callback)
        logger.info(f"Alert callback added: {callback.__name__}")
    
    def check_database_health(self) -> HealthMetrics:
        """
        Perform comprehensive database health check
        Returns health metrics with detailed status information
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            with app.app_context():
                # Test basic connectivity with engine-agnostic query
                with db.engine.connect() as connection:
                    # Execute engine-agnostic test query
                    result = connection.execute(text('SELECT 1 as health_check'))
                    test_result = result.fetchone()
                    
                    if not test_result or test_result[0] != 1:
                        raise RuntimeError("Database health check query failed")
                
                # Get connection pool information (if available)
                try:
                    pool_info = {
                        'pool_size': getattr(db.engine.pool, 'size', lambda: 0)(),
                        'checked_in': getattr(db.engine.pool, 'checkedin', lambda: 0)(),
                        'checked_out': getattr(db.engine.pool, 'checkedout', lambda: 0)(),
                        'overflow': getattr(db.engine.pool, 'overflow', lambda: 0)(),
                        'invalid': getattr(db.engine.pool, 'invalid', lambda: 0)()
                    }
                except Exception:
                    pool_info = {'status': 'pool_info_unavailable'}
                
                # Calculate response time
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Check table accessibility with engine-agnostic queries (empty tables are OK)
                with db.engine.connect() as connection:
                    # Check sample_requests table exists and is accessible
                    try:
                        result = connection.execute(text("SELECT 1 FROM sample_requests LIMIT 1"))
                        result.fetchone()  # Don't require rows, just table access
                    except Exception as e:
                        if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
                            raise RuntimeError("Critical table 'sample_requests' does not exist")
                        # Table exists but might be empty - that's OK
                    
                    # Check archived_requests table exists and is accessible
                    try:
                        result = connection.execute(text("SELECT 1 FROM archived_requests LIMIT 1"))
                        result.fetchone()  # Don't require rows, just table access
                    except Exception as e:
                        if "no such table" in str(e).lower() or "doesn't exist" in str(e).lower():
                            raise RuntimeError("Critical table 'archived_requests' does not exist")
                        # Table exists but might be empty - that's OK
                    
                    connection_count = int(pool_info.get('checked_out', 0)) if pool_info else 0
                
                # Create successful health metrics
                metrics = HealthMetrics(
                    timestamp=timestamp,
                    connectivity_status="healthy",
                    response_time_ms=response_time,
                    connection_count=connection_count,
                    query_success=True,
                    pool_info=pool_info
                )
                
                # Reset failure counter on success
                self.consecutive_failures = 0
                
                logger.debug(f"✅ Database health check passed: {response_time:.2f}ms")
                return metrics
                
        except (OperationalError, DatabaseError, RuntimeError) as e:
            response_time = (time.time() - start_time) * 1000
            
            # Create failure health metrics
            metrics = HealthMetrics(
                timestamp=timestamp,
                connectivity_status="failed",
                response_time_ms=response_time,
                connection_count=0,
                error_message=str(e),
                query_success=False
            )
            
            # Increment failure counter
            self.consecutive_failures += 1
            
            logger.error(f"❌ Database health check failed: {e}")
            return metrics
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            # Create error health metrics
            metrics = HealthMetrics(
                timestamp=timestamp,
                connectivity_status="error",
                response_time_ms=response_time,
                connection_count=0,
                error_message=f"Unexpected error: {str(e)}",
                query_success=False
            )
            
            self.consecutive_failures += 1
            
            logger.error(f"🚨 Database health check error: {e}")
            return metrics
    
    def evaluate_alert_conditions(self, metrics: HealthMetrics) -> bool:
        """
        Evaluate if alert conditions are met based on current metrics
        Returns True if alert should be triggered
        """
        alert_conditions = []
        
        # Check response time threshold
        if metrics.response_time_ms > self.config.max_response_time_ms:
            alert_conditions.append(f"High response time: {metrics.response_time_ms:.2f}ms > {self.config.max_response_time_ms}ms")
        
        # Check consecutive failures
        if self.consecutive_failures >= self.config.max_failed_checks:
            alert_conditions.append(f"Consecutive failures: {self.consecutive_failures} >= {self.config.max_failed_checks}")
        
        # Check connectivity status
        if metrics.connectivity_status in ['failed', 'error']:
            alert_conditions.append(f"Database connectivity: {metrics.connectivity_status}")
        
        # Check alert cooldown
        if self.last_alert_time:
            cooldown_end = self.last_alert_time + timedelta(minutes=self.config.alert_cooldown_minutes)
            if datetime.now() < cooldown_end:
                logger.debug(f"Alert suppressed - cooldown active until {cooldown_end}")
                return False
        
        if alert_conditions:
            logger.warning(f"🚨 Alert conditions met: {', '.join(alert_conditions)}")
            return True
            
        return False
    
    def send_email_alert(self, metrics: HealthMetrics, alert_conditions: List[str]):
        """Send email alert notification"""
        try:
            if not self.config.enable_email_alerts or not self.config.smtp_settings or not self.config.smtp_settings.get('username'):
                logger.warning("Email alerts disabled or SMTP not configured")
                return
            
            # Create email content
            subject = "🚨 CRITICAL: Database Connectivity Alert - Slender Morris Furnishings"
            
            body = f"""
CRITICAL DATABASE ALERT
========================

System: Slender Morris Furnishings - Fabric Cutting Request System
Time: {metrics.timestamp}
Environment: {'PRODUCTION' if Config.is_production else 'DEVELOPMENT'}

ALERT CONDITIONS:
{chr(10).join(['• ' + condition for condition in alert_conditions])}

DATABASE METRICS:
• Status: {metrics.connectivity_status}
• Response Time: {metrics.response_time_ms:.2f}ms
• Consecutive Failures: {self.consecutive_failures}
• Query Success: {metrics.query_success}
• Error: {metrics.error_message or 'None'}

CONNECTION POOL INFO:
{json.dumps(metrics.pool_info or {}, indent=2) if metrics.pool_info else 'Not available'}

IMMEDIATE ACTIONS REQUIRED:
1. Check database connectivity and server status
2. Review application logs for error details
3. Verify DATABASE_URL configuration
4. Check network connectivity to database server
5. Contact system administrator if issue persists

ESCALATION:
If this is a production system, escalate immediately:
• Primary: orders@slendermorris.com
• Secondary: slendermorris@gmail.com

System Status Dashboard: Check Replit console for additional details

This is an automated alert from the database monitoring system.
Do not reply to this email.
            """
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_settings['username']
            recipients = self.config.alert_recipients or []
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            smtp_config = self.config.smtp_settings or {}
            with smtplib.SMTP(smtp_config.get('host', 'smtp.gmail.com'), smtp_config.get('port', 587)) as server:
                server.starttls()
                server.login(smtp_config.get('username', ''), smtp_config.get('password', ''))
                server.send_message(msg)
            
            logger.info(f"📧 Alert email sent to {len(recipients)} recipients")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")
    
    def trigger_alert(self, metrics: HealthMetrics):
        """
        Trigger alert notifications based on health metrics
        """
        alert_conditions = []
        
        # Determine alert conditions
        if metrics.response_time_ms > self.config.max_response_time_ms:
            alert_conditions.append(f"High response time: {metrics.response_time_ms:.2f}ms")
        
        if self.consecutive_failures >= self.config.max_failed_checks:
            alert_conditions.append(f"{self.consecutive_failures} consecutive failures")
        
        if metrics.connectivity_status in ['failed', 'error']:
            alert_conditions.append(f"Database {metrics.connectivity_status}")
        
        # Log alert
        logger.critical(f"🚨 DATABASE ALERT TRIGGERED: {', '.join(alert_conditions)}")
        
        # Send email notification
        self.send_email_alert(metrics, alert_conditions)
        
        # Execute custom alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(metrics, alert_conditions)
            except Exception as e:
                logger.error(f"Alert callback {callback.__name__} failed: {e}")
        
        # Update last alert time
        self.last_alert_time = datetime.now()
        
        # Log to monitoring history
        self.log_alert_event(metrics, alert_conditions)
    
    def log_alert_event(self, metrics: HealthMetrics, alert_conditions: List[str]):
        """Log alert event to monitoring history"""
        alert_event = {
            'timestamp': metrics.timestamp,
            'event_type': 'alert_triggered',
            'conditions': alert_conditions,
            'metrics': asdict(metrics),
            'consecutive_failures': self.consecutive_failures,
            'environment': 'PRODUCTION' if Config.is_production else 'DEVELOPMENT'
        }
        
        # Write to alert log file in writable directory
        alert_log_file = '/tmp/database_alerts.json'
        try:
            
            # Read existing alerts
            alerts = []
            if os.path.exists(alert_log_file):
                with open(alert_log_file, 'r') as f:
                    alerts = json.load(f)
            
            # Add new alert
            alerts.append(alert_event)
            
            # Keep only last 100 alerts
            alerts = alerts[-100:]
            
            # Write back to file
            with open(alert_log_file, 'w') as f:
                json.dump(alerts, f, indent=2, default=str)
            
            logger.info(f"Alert event logged to {alert_log_file}")
            
        except Exception as e:
            logger.debug(f"Could not log alert event to {alert_log_file}: {e}")
            # Don't fail monitoring for file write issues
    
    def store_health_metrics(self, metrics: HealthMetrics):
        """Store health metrics in monitoring history"""
        self.health_history.append(metrics)
        
        # Keep only last 1000 metrics (about 16 hours at 1-minute intervals)
        if len(self.health_history) > 1000:
            self.health_history = self.health_history[-1000:]
        
        # Write to health log file in writable directory
        health_log_file = '/tmp/database_health.json'
        try:
            
            # Write latest metrics to file
            health_data = {
                'last_updated': datetime.now().isoformat(),
                'total_checks': len(self.health_history),
                'latest_metrics': asdict(metrics),
                'consecutive_failures': self.consecutive_failures,
                'monitoring_active': self.monitoring_active
            }
            
            with open(health_log_file, 'w') as f:
                json.dump(health_data, f, indent=2, default=str)
            
        except Exception as e:
            logger.debug(f"Could not store health metrics to {health_log_file}: {e}")
            # Don't fail monitoring for file write issues
    
    def get_health_summary(self) -> Dict:
        """Get summary of database health status"""
        if not self.health_history:
            return {
                'status': 'no_data',
                'message': 'No health data available'
            }
        
        latest = self.health_history[-1]
        recent_checks = self.health_history[-10:]  # Last 10 checks
        
        # Calculate success rate
        successful_checks = sum(1 for check in recent_checks if check.query_success)
        success_rate = (successful_checks / len(recent_checks)) * 100
        
        # Calculate average response time
        avg_response_time = sum(check.response_time_ms for check in recent_checks if check.query_success) / max(successful_checks, 1)
        
        return {
            'status': latest.connectivity_status,
            'last_check': latest.timestamp,
            'response_time_ms': latest.response_time_ms,
            'success_rate_percent': round(success_rate, 1),
            'avg_response_time_ms': round(avg_response_time, 2),
            'consecutive_failures': self.consecutive_failures,
            'total_checks': len(self.health_history),
            'monitoring_active': self.monitoring_active,
            'pool_status': latest.pool_info
        }
    
    def monitoring_loop(self):
        """Main monitoring loop - runs in separate thread"""
        logger.info("🔄 Database monitoring loop started")
        
        while self.monitoring_active:
            try:
                # Perform health check
                metrics = self.check_database_health()
                
                # Store metrics
                self.store_health_metrics(metrics)
                
                # Check if alert should be triggered
                if self.evaluate_alert_conditions(metrics):
                    self.trigger_alert(metrics)
                
                # Log status
                status_emoji = "✅" if metrics.connectivity_status == "healthy" else "❌"
                logger.info(f"{status_emoji} Database check: {metrics.connectivity_status}, {metrics.response_time_ms:.2f}ms")
                
            except Exception as e:
                logger.error(f"🚨 Monitoring loop error: {e}")
            
            # Wait for next check
            time.sleep(self.config.check_interval_seconds)
        
        logger.info("🛑 Database monitoring loop stopped")
    
    def start_monitoring(self):
        """Start continuous database monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🟢 Database monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous database monitoring"""
        if not self.monitoring_active:
            logger.warning("Monitoring not active")
            return
        
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("🔴 Database monitoring stopped")

# Global monitor instance with singleton pattern
database_monitor = None
_monitor_lock = threading.Lock()

def get_monitor_status() -> Dict:
    """Get current monitoring status for external access"""
    global database_monitor
    if database_monitor is None:
        return {'status': 'not_initialized', 'message': 'Monitor not started'}
    return database_monitor.get_health_summary()

def start_database_monitoring():
    """Start database monitoring (for external access) - inter-process singleton"""
    global database_monitor
    
    # Inter-process lock using file system
    lock_file = '/tmp/database_monitor.lock'
    
    with _monitor_lock:
        if database_monitor is not None and database_monitor.monitoring_active:
            logger.info("🔍 Database monitoring already active in this process - skipping")
            return
        
        # Atomic inter-process lock to prevent duplicate monitors
        try:
            current_pid = os.getpid()
            
            # Try to atomically create lock file (fails if exists)
            try:
                lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                # Immediately write PID and flush to prevent empty file race condition
                with os.fdopen(lock_fd, 'w') as f:
                    f.write(str(current_pid))
                    f.flush()  # Ensure PID is written before any other process can read
                    os.fsync(f.fileno())  # Force write to disk
                logger.info(f"🔍 Acquired monitoring lock (PID: {current_pid})")
                
            except FileExistsError:
                # Lock file exists - enter TRUE indefinite blocking until exclusive ownership
                logger.info(f"🔍 Lock file exists, entering indefinite blocking wait for exclusive ownership")
                
                # Indefinite blocking - only exit when we have exclusive lock or confirmed active monitor
                while True:
                    try:
                        time.sleep(0.1)  # Brief wait between attempts
                        
                        with open(lock_file, 'r') as f:
                            content = f.read().strip()
                            
                        if not content:
                            # File is empty, another process may be writing - continue waiting
                            logger.debug("🔍 Lock file empty, waiting for PID to be written...")
                            continue
                            
                        existing_pid = int(content)
                        
                        # Check if the existing process is still running
                        try:
                            os.kill(existing_pid, 0)  # Signal 0 just checks existence
                            logger.info(f"🔍 Database monitoring confirmed running in process {existing_pid} - this worker will exit")
                            return  # EXIT FUNCTION - another monitor is already running
                        except (OSError, ProcessLookupError):
                            # Stale lock - process no longer exists, claim it
                            logger.info(f"🔍 Found stale lock (PID: {existing_pid}), claiming exclusive ownership")
                            os.remove(lock_file)
                            
                            # Atomically claim the lock
                            lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                            with os.fdopen(lock_fd, 'w') as f:
                                f.write(str(current_pid))
                                f.flush()
                                os.fsync(f.fileno())
                            logger.info(f"🔍 Successfully claimed exclusive monitoring lock (PID: {current_pid})")
                            break  # EXIT LOOP - we now have the lock, proceed to start monitor
                            
                    except (ValueError, FileNotFoundError):
                        # File disappeared or corrupted - try to claim it
                        logger.debug("🔍 Lock file disappeared/corrupted, attempting to claim...")
                        try:
                            lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                            with os.fdopen(lock_fd, 'w') as f:
                                f.write(str(current_pid))
                                f.flush()
                                os.fsync(f.fileno())
                            logger.info(f"🔍 Successfully claimed exclusive monitoring lock after file disappeared (PID: {current_pid})")
                            break  # EXIT LOOP - we now have the lock, proceed to start monitor
                        except FileExistsError:
                            # Another process created it, continue waiting
                            logger.debug("🔍 Another process claimed lock, continuing to wait...")
                            continue
                    except Exception as e:
                        # Any other error - continue waiting
                        logger.debug(f"🔍 Error during indefinite wait: {e}, continuing...")
                        continue
            
            # If we got here, we have the lock - start monitoring
            database_monitor = DatabaseMonitor()
            database_monitor.start_monitoring()
            logger.info(f"🔍 Database monitoring instance created and started (PID: {current_pid})")
            
        except Exception as e:
            logger.error(f"Failed to create inter-process monitoring lock: {e}")
            # Fall back to process-local monitoring if file locking fails
            database_monitor = DatabaseMonitor()
            database_monitor.start_monitoring()
            logger.info("🔍 Database monitoring started with process-local fallback")

def stop_database_monitoring():
    """Stop database monitoring (for external access)"""
    global database_monitor
    if database_monitor is not None:
        database_monitor.stop_monitoring()

def force_health_check() -> HealthMetrics:
    """Force immediate health check (for external access)"""
    global database_monitor
    if database_monitor is None:
        raise RuntimeError("Monitor not initialized")
    return database_monitor.check_database_health()

if __name__ == "__main__":
    # CLI interface for monitoring
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            logger.info("Starting database monitoring from CLI")
            start_database_monitoring()
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Stopping monitoring...")
                stop_database_monitoring()
                
        elif command == "check":
            logger.info("Performing single health check")
            metrics = force_health_check()
            print(json.dumps(asdict(metrics), indent=2, default=str))
            
        elif command == "status":
            logger.info("Getting monitoring status")
            status = get_monitor_status()
            print(json.dumps(status, indent=2, default=str))
            
        else:
            print("Usage: python database_monitor.py [start|check|status]")
    else:
        print("Database Monitor - Available commands:")
        print("  start  - Start continuous monitoring")
        print("  check  - Perform single health check")
        print("  status - Get current monitoring status")