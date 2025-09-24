# 🚨 DISASTER RECOVERY DOCUMENTATION
## Slender Morris Furnishings - Fabric Cutting Request System

---

## 📋 QUICK REFERENCE EMERGENCY CONTACTS

**IMMEDIATE ESCALATION (Data Loss Detected)**
- **Primary Contact**: orders@slendermorris.com  
- **Secondary Contact**: slendermorris@gmail.com
- **Database Platform**: Replit PostgreSQL (Neon-backed)
- **System Administrator**: Contact via Replit support for database infrastructure issues

---

## 🚨 EMERGENCY RESPONSE PROCEDURES

### STEP 1: IMMEDIATE ASSESSMENT (First 5 Minutes)
1. **Stop all operations** - Do not make any changes to database or system
2. **Document the incident**:
   - Time of discovery: ________________
   - Who discovered it: ________________  
   - What was observed: ________________
   - Last known good state: ________________

3. **Check system status**:
   ```bash
   # Verify application is running
   ps aux | grep gunicorn
   
   # Check database connectivity 
   python3 -c "from app import app, db; from sqlalchemy import text; import app as app_module; with app.app_context(): db.session.execute(text('SELECT 1'))"
   ```

### STEP 2: DAMAGE ASSESSMENT (Next 10 Minutes)
1. **Check recent logs**:
   ```bash
   # Check application logs for errors
   tail -100 /var/log/application.log
   
   # Look for database connection issues
   grep -i "database\|error\|fail" /var/log/application.log
   ```

2. **Verify data integrity**:
   ```bash
   # Run integrity check
   python3 -c "from data_integrity import data_integrity_manager; print(data_integrity_manager.perform_integrity_check())"
   ```

3. **Check backup status**:
   ```bash
   # List recent backups
   ls -la backup_snapshot_*.json | tail -5
   
   # Check backup orchestrator logs
   tail -50 data_audit_log.json
   ```

### STEP 3: RECOVERY DECISION (Next 5 Minutes)
**Choose appropriate recovery method based on assessment:**

- **Minor data corruption** → Go to [Data Validation & Repair](#data-validation--repair)
- **Recent data loss (< 24 hours)** → Go to [Recent Backup Recovery](#recent-backup-recovery)  
- **Major data loss** → Go to [Full Database Recovery](#full-database-recovery)
- **System compromise** → Go to [Security Incident Response](#security-incident-response)

---

## 🔄 RECOVERY PROCEDURES

### Recent Backup Recovery
**Use this when recent data is lost but system integrity is intact**

1. **Identify latest backup**:
   ```bash
   # Find most recent backup
   ls -la backup_snapshot_*.json | tail -1
   
   # Verify backup integrity
   python3 -c "
   import json
   with open('backup_snapshot_YYYYMMDD_HHMMSS_XXX.json', 'r') as f:
       data = json.load(f)
       print(f'Active records: {len(data[\"active_records\"])}')
       print(f'Archived records: {len(data[\"archived_records\"])}')
   "
   ```

2. **Create pre-recovery backup**:
   ```bash
   # Backup current state before recovery
   python3 -c "
   from backup_orchestrator import backup_orchestrator
   backup_id = backup_orchestrator.pre_operation_backup('emergency_recovery')
   print(f'Pre-recovery backup: {backup_id}')
   "
   ```

3. **Restore from backup**:
   ```bash
   # Use data integrity manager for recovery
   python3 -c "
   from data_integrity import data_integrity_manager
   result = data_integrity_manager.restore_from_backup('backup_snapshot_YYYYMMDD_HHMMSS_XXX.json')
   print(f'Recovery result: {result}')
   "
   ```

4. **Verify recovery**:
   ```bash
   # Run comprehensive integrity check
   python3 -c "
   from data_integrity import data_integrity_manager
   check = data_integrity_manager.perform_integrity_check()
   print(f'Post-recovery integrity: {check}')
   "
   ```

### Full Database Recovery
**Use this for major data loss or database corruption**

1. **Access Replit Database Rollback**:
   - Go to Replit Database pane
   - Click "Rollback" tab
   - Select appropriate checkpoint (usually within last 24 hours)
   - Review checkpoint details and affected data
   - Execute rollback with full system restore

2. **Post-rollback verification**:
   ```bash
   # Restart application after rollback
   pkill -f gunicorn
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   
   # Verify database connectivity and initialization
   python3 -c "from app import setup_application; setup_application()"
   
   # Run full integrity check
   python3 -c "
   from data_integrity import data_integrity_manager
   check = data_integrity_manager.perform_integrity_check()
   print(f'Rollback verification: {check}')
   "
   ```

3. **Business data validation**:
   ```bash
   # Validate business records are present
   python3 -c "
   from backup_orchestrator import backup_orchestrator
   validation = backup_orchestrator._validate_business_data()
   print(f'Business data status: {validation}')
   "
   ```

### Data Validation & Repair
**Use this for minor corruption or integrity issues**

1. **Run automated repair**:
   ```bash
   # Attempt automated data repair
   python3 -c "
   from database_maintenance import run_data_maintenance, archive_old_records
   
   # Archive old dispatched records
   archived = archive_old_records()
   print(f'Archived records: {archived}')
   
   # Run maintenance
   maintenance = run_data_maintenance()
   print(f'Maintenance result: {maintenance}')
   "
   ```

2. **Manual data validation**:
   ```bash
   # Check for duplicate records
   python3 -c "
   from models import SampleRequest
   from app import app, db
   with app.app_context():
       duplicates = db.session.query(SampleRequest.email, db.func.count()).group_by(SampleRequest.email).having(db.func.count() > 1).all()
       print(f'Potential duplicates: {duplicates}')
   "
   
   # Check for missing required fields
   python3 -c "
   from models import SampleRequest
   from app import app, db
   with app.app_context():
       incomplete = SampleRequest.query.filter(
           (SampleRequest.company_name == None) | 
           (SampleRequest.email == None)
       ).all()
       print(f'Incomplete records: {len(incomplete)}')
   "
   ```

### Security Incident Response
**Use this if data compromise is suspected**

1. **Immediate security measures**:
   ```bash
   # Change admin password immediately
   python3 -c "
   from werkzeug.security import generate_password_hash
   new_hash = generate_password_hash('NEW_SECURE_PASSWORD_HERE')
   print(f'New password hash: {new_hash}')
   # Update ADMIN_PASSWORD environment variable
   "
   
   # Review recent login attempts
   tail -100 /var/log/application.log | grep -i "login\|auth\|admin"
   ```

2. **Audit trail review**:
   ```bash
   # Check audit logs for suspicious activity
   cat data_audit_log.json | grep -A5 -B5 "$(date +%Y-%m-%d)"
   
   # Look for recent database operations
   grep -i "backup\|restore\|delete" data_audit_log.json | tail -20
   ```

3. **System hardening**:
   - Reset all API keys and secrets
   - Review and update access controls
   - Enable additional logging
   - Contact Replit support for infrastructure review

---

## 🔍 DATA VALIDATION CHECKLIST

### Business Data Validation
After any recovery, verify these critical business requirements:

**✅ Customer Records**
- [ ] All company names are present and properly formatted
- [ ] Email addresses are valid and not duplicated inappropriately  
- [ ] Phone numbers are present where expected
- [ ] Shipping addresses are complete

**✅ Fabric Cutting Data**
- [ ] Fabric selections are preserved (no truncation)
- [ ] Special requests and notes are intact
- [ ] Reference numbers are unique and present

**✅ Order Status Integrity**
- [ ] Status progression is logical (Outstanding → In Progress → Dispatched)
- [ ] Date stamps are present and reasonable
- [ ] ILIV email tracking is preserved

**✅ System Functionality**
- [ ] Admin login works with correct password
- [ ] New cutting requests can be submitted
- [ ] Status changes trigger appropriate emails
- [ ] Search functionality works across all fields
- [ ] Archive system functions properly

### Technical Validation Commands
```bash
# Verify database schema
python3 -c "
from app import app, db
from models import SampleRequest, ArchivedRequest
with app.app_context():
    print('Sample requests table:', db.engine.has_table('sample_requests'))
    print('Archived requests table:', db.engine.has_table('archived_requests'))
    print('Total active records:', SampleRequest.query.count())
    print('Total archived records:', ArchivedRequest.query.count())
"

# Check email functionality
python3 -c "
import smtplib
from email.mime.text import MIMEText
# Test SMTP connection without sending
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
print('SMTP connection successful')
server.quit()
"

# Verify backup system
python3 -c "
from backup_orchestrator import backup_orchestrator
test_backup = backup_orchestrator.pre_operation_backup('validation_test')
print(f'Backup system functional: {test_backup}')
"
```

---

## 📊 MONITORING & EARLY WARNING SIGNS

### Critical Alerts to Monitor
1. **Database connectivity failures** → Check immediately
2. **Backup creation failures** → Investigate within 1 hour  
3. **Data integrity check failures** → Review within 30 minutes
4. **Unexpected low record counts** → Validate immediately
5. **SMTP email failures** → Check configuration within 2 hours

### Daily Health Checks
Run these commands daily to catch issues early:

```bash
# Daily health check script
echo "=== DAILY SYSTEM HEALTH CHECK ==="
echo "Date: $(date)"
echo ""

# Database connectivity
python3 -c "from app import app, db; from sqlalchemy import text; with app.app_context(): result = db.session.execute(text('SELECT 1')); print('✅ Database:', 'Connected' if result.fetchone() else '❌ Failed')"

# Record counts
python3 -c "
from models import SampleRequest, ArchivedRequest
from app import app, db
with app.app_context():
    active = SampleRequest.query.count()
    archived = ArchivedRequest.query.count()
    print(f'📊 Active records: {active}')
    print(f'📦 Archived records: {archived}')
    print(f'📈 Total records: {active + archived}')
"

# Recent backups
echo "💾 Recent backups:"
ls -la backup_snapshot_*.json | tail -3

# System status
echo "🟢 Application status:"
ps aux | grep gunicorn | grep -v grep || echo "❌ Application not running"

echo ""
echo "=== HEALTH CHECK COMPLETE ==="
```

---

## 📝 INCIDENT DOCUMENTATION TEMPLATE

**For every data incident, complete this documentation:**

```
INCIDENT REPORT: DR-YYYY-MM-DD-XXX

SUMMARY:
- Date/Time: _______________
- Reporter: _______________
- Impact Level: [ ] Low [ ] Medium [ ] High [ ] Critical
- Estimated Data Loss: _______________

TIMELINE:
- Issue Discovered: _______________
- Response Started: _______________
- Recovery Initiated: _______________
- Resolution Completed: _______________
- Total Downtime: _______________

ROOT CAUSE:
_______________

RECOVERY ACTIONS TAKEN:
1. _______________
2. _______________
3. _______________

DATA VALIDATED:
- [ ] Customer records verified
- [ ] Fabric cutting data confirmed  
- [ ] System functionality tested
- [ ] Email notifications working

PREVENTIVE MEASURES:
_______________

LESSONS LEARNED:
_______________

SIGN-OFF:
- Administrator: _______________ Date: _______________
- Business Owner: _______________ Date: _______________
```

---

## 🔧 SYSTEM RECOVERY TOOLS

### Key Scripts & Commands
```bash
# Emergency database reset (EXTREME CAUTION)
python3 -c "
from app import app, db
from models import SampleRequest, ArchivedRequest
with app.app_context():
    # This will DROP all data - use only in extreme emergencies
    # db.drop_all()
    # db.create_all()
    print('Database reset complete')
"

# Backup verification
python3 -c "
import json, os
backups = [f for f in os.listdir('.') if f.startswith('backup_snapshot_')]
for backup in sorted(backups)[-5:]:
    with open(backup, 'r') as f:
        data = json.load(f)
        print(f'{backup}: {len(data[\"active_records\"])} active, {len(data[\"archived_records\"])} archived')
"

# Quick data export (for manual backup)
python3 -c "
import csv
from datetime import datetime
from models import SampleRequest
from app import app, db
with app.app_context():
    records = SampleRequest.query.all()
    with open(f'emergency_export_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'Email', 'Status', 'Created', 'Fabrics'])
        for r in records:
            writer.writerow([r.company_name, r.email, r.status, r.date_created, r.fabric_cuttings])
    print(f'Emergency export complete: {len(records)} records')
"
```

---

## 📚 APPENDIX: SYSTEM ARCHITECTURE

### Database Tables
- **sample_requests**: Active cutting requests (primary business data)
- **archived_requests**: Dispatched requests older than 4 months
- Both tables contain identical schema for seamless archiving

### Backup Strategy
- **Automated backups**: Created before any risky operation
- **Manual backups**: Available via backup_orchestrator tool
- **Platform backups**: Replit automatic checkpoints (24-hour retention)
- **Archive protection**: Dispatched records automatically archived, never deleted

### Recovery Capabilities
1. **Granular backup recovery** (specific operations)
2. **Full database rollback** (Replit checkpoints)
3. **Automated data repair** (integrity validation)
4. **Manual data restoration** (CSV import/export)

---

**🔴 REMEMBER: In any data emergency, preservation is priority #1. Always backup current state before attempting recovery!**

---

*Document Version: 1.0*  
*Last Updated: September 24, 2025*  
*Next Review Date: December 24, 2025*