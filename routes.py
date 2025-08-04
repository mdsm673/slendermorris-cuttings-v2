import json
import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response, abort
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import SampleRequest, ArchivedRequest
from email_service import send_confirmation_email, send_admin_notification, send_dispatch_notification
from security import validate_email, validate_phone, sanitize_input, require_admin, validate_status, validate_fabric_cutting
from rate_limiter import rate_limit, rate_limit_login, record_failed_login, reset_login_attempts, get_client_ip

# No longer needed - fabric cuttings are now text inputs

# Admin credentials (in production, this should be in environment variables)
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get("ADMIN_PASSWORD", "Matthew1234"))

@app.route('/')
def index():
    """Customer-facing form for fabric sample requests"""
    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)  # 5 requests per 5 minutes
def submit_request():
    """Handle fabric sample request submission"""
    try:
        # Get and sanitize form data
        company_customer_name = sanitize_input(request.form.get('company_customer_name', ''), 100)
        email = sanitize_input(request.form.get('email', ''), 120)
        phone = sanitize_input(request.form.get('phone', ''), 20)
        reference = sanitize_input(request.form.get('reference', ''), 100)
        
        # Address fields
        street_address = sanitize_input(request.form.get('street_address', ''), 200)
        city = sanitize_input(request.form.get('city', ''), 100)
        state_province = sanitize_input(request.form.get('state_province', ''), 100)
        postal_code = sanitize_input(request.form.get('postal_code', ''), 20)
        country = sanitize_input(request.form.get('country', ''), 100)
        
        additional_notes = sanitize_input(request.form.get('additional_notes', ''), 1000)
        
        # Validate required fields
        if not all([company_customer_name, email, street_address, city, state_province, postal_code, country]):
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Please enter a valid email address.'})
        
        # Validate phone format if provided
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Please enter a valid phone number.'})
        
        # Get and validate fabric cuttings from text inputs
        fabric_cuttings = []
        for i in range(1, 6):
            cutting = sanitize_input(request.form.get(f'fabric_cutting_{i}', ''), 200)
            if cutting:
                if not validate_fabric_cutting(cutting):
                    return jsonify({'success': False, 'message': f'Invalid fabric cutting entry: {cutting[:50]}...'})
                fabric_cuttings.append(cutting)
        
        if not fabric_cuttings:
            return jsonify({'success': False, 'message': 'Please enter at least one fabric cutting.'})
        
        # Create new sample request
        sample_request = SampleRequest()
        sample_request.customer_name = company_customer_name
        sample_request.email = email
        sample_request.phone = phone
        sample_request.company_name = company_customer_name
        sample_request.reference = reference
        sample_request.street_address = street_address
        sample_request.city = city
        sample_request.state_province = state_province
        sample_request.postal_code = postal_code
        sample_request.country = country
        sample_request.fabric_selections = json.dumps(fabric_cuttings)
        sample_request.additional_notes = additional_notes
        
        db.session.add(sample_request)
        db.session.commit()
        
        # Prepare data for email
        customer_email_data = {
            'company_name': company_customer_name,
            'customer_name': company_customer_name,
            'email': email,
            'phone': phone,
            'reference': reference,
            'street_address': street_address,
            'city': city,
            'state_province': state_province,
            'postal_code': postal_code,
            'country': country,
            'additional_notes': additional_notes
        }
        
        # Send confirmation email to customer and internal team
        email_sent = send_confirmation_email(customer_email_data, fabric_cuttings)
        
        # Send admin notification
        admin_email_sent = send_admin_notification(customer_email_data, fabric_cuttings, sample_request.id)
        
        # Log email status
        if email_sent:
            app.logger.info(f"Confirmation email sent for request #{sample_request.id}")
        else:
            app.logger.warning(f"Failed to send confirmation email for request #{sample_request.id}")
            
        if admin_email_sent:
            app.logger.info(f"Admin notification sent for request #{sample_request.id}")
        else:
            app.logger.warning(f"Failed to send admin notification for request #{sample_request.id}")
        
        return jsonify({
            'success': True, 
            'message': f'Thank you, {company_customer_name}! Your fabric cutting request has been submitted successfully. You will receive a confirmation email shortly.',
            'request_id': sample_request.id
        })
        
    except Exception as e:
        app.logger.error(f"Error submitting request: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while submitting your request. Please try again.'})

@app.route('/admin/login', methods=['GET', 'POST'])
@rate_limit_login(max_attempts=5, lockout_minutes=15)
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        ip = get_client_ip()
        
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_authenticated'] = True
            session.permanent = True  # Make session permanent
            app.permanent_session_lifetime = timedelta(hours=2)  # 2 hour session
            reset_login_attempts(ip)
            app.logger.info(f"Successful admin login from IP: {ip}")
            return redirect(url_for('admin_dashboard'))
        else:
            record_failed_login(ip)
            app.logger.warning(f"Failed admin login attempt from IP: {ip}")
            flash('Invalid password. Please try again.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
@require_admin
def admin_dashboard():
    """Admin dashboard for managing sample requests"""
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'date_submitted')
    sort_order = request.args.get('order', 'desc')
    search_term = request.args.get('search', '').strip()
    
    # Build query
    query = SampleRequest.query
    
    # Apply search filter if provided
    if search_term:
        # Search across all text fields
        search_pattern = f'%{search_term}%'
        query = query.filter(
            db.or_(
                SampleRequest.customer_name.ilike(search_pattern),
                SampleRequest.email.ilike(search_pattern),
                SampleRequest.phone.ilike(search_pattern),
                SampleRequest.company_name.ilike(search_pattern),
                SampleRequest.reference.ilike(search_pattern),
                SampleRequest.street_address.ilike(search_pattern),
                SampleRequest.city.ilike(search_pattern),
                SampleRequest.state_province.ilike(search_pattern),
                SampleRequest.postal_code.ilike(search_pattern),
                SampleRequest.country.ilike(search_pattern),
                SampleRequest.additional_notes.ilike(search_pattern),
                SampleRequest.fabric_selections.ilike(search_pattern),  # This searches the JSON string
                SampleRequest.status.ilike(search_pattern)
            )
        )
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter(SampleRequest.status == status_filter)
    
    # Apply sorting - Always prioritize Outstanding orders first
    # Use CASE statement to ensure Outstanding appears before Dispatched
    from sqlalchemy import case
    
    status_order = case(
        (SampleRequest.status == 'Outstanding', 1),
        (SampleRequest.status == 'In Progress', 2),
        (SampleRequest.status == 'Dispatched', 3),
        else_=4
    )
    
    if sort_by == 'date_submitted':
        if sort_order == 'desc':
            query = query.order_by(status_order, SampleRequest.date_submitted.desc())
        else:
            query = query.order_by(status_order, SampleRequest.date_submitted.asc())
    elif sort_by == 'customer_name':
        if sort_order == 'desc':
            query = query.order_by(status_order, SampleRequest.customer_name.desc())
        else:
            query = query.order_by(status_order, SampleRequest.customer_name.asc())
    elif sort_by == 'status':
        # When sorting by status, still use custom order but date as secondary sort
        if sort_order == 'desc':
            query = query.order_by(status_order.desc(), SampleRequest.date_submitted.desc())
        else:
            query = query.order_by(status_order, SampleRequest.date_submitted.desc())
    
    requests = query.all()
    
    # Parse fabric cuttings for each request for template display
    for req in requests:
        try:
            req.parsed_fabric_cuttings = json.loads(req.fabric_selections)
        except (json.JSONDecodeError, TypeError):
            req.parsed_fabric_cuttings = []
    
    return render_template('admin_dashboard.html', 
                         requests=requests, 
                         status_filter=status_filter,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         search_term=search_term)

@app.route('/admin/request/<int:request_id>')
@require_admin
def request_details(request_id):
    """View detailed information for a specific request"""
    
    sample_request = SampleRequest.query.get_or_404(request_id)
    fabric_selections = json.loads(sample_request.fabric_selections)
    
    return render_template('request_details.html', 
                         request=sample_request, 
                         fabric_selections=fabric_selections)

@app.route('/admin/update_status/<int:request_id>', methods=['POST'])
@require_admin
def update_status(request_id):
    """Update the status of a sample request"""
    
    try:
        sample_request = SampleRequest.query.get_or_404(request_id)
        json_data = request.get_json()
        if not json_data:
            return jsonify({'success': False, 'message': 'No JSON data received'})
            
        new_status = json_data.get('status')
        
        if not validate_status(new_status):
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        sample_request.status = new_status
        
        # Set dispatch date if status is changed to Dispatched
        if new_status == 'Dispatched' and sample_request.date_dispatched is None:
            sample_request.date_dispatched = datetime.utcnow()
        
        db.session.commit()
        
        # Send dispatch notification email if status changed to Dispatched
        if new_status == 'Dispatched':
            email_sent = send_dispatch_notification(sample_request)
            if email_sent:
                app.logger.info(f"Dispatch notification sent for request #{sample_request.id}")
            else:
                app.logger.warning(f"Failed to send dispatch notification for request #{sample_request.id}")
        
        return jsonify({
            'success': True, 
            'message': f'Status updated to {new_status}',
            'date_dispatched': sample_request.date_dispatched.strftime('%Y-%m-%d %H:%M:%S') if sample_request.date_dispatched else None
        })
        
    except Exception as e:
        app.logger.error(f"Error updating status: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating status'})



# Delete functionality has been removed from the system

@app.route('/admin/archived')
@require_admin
def archived_requests():
    """View archived requests (dispatched and older than 4 months)"""
    
    search_term = request.args.get('search', '').strip()
    
    # Build query for archived requests
    query = ArchivedRequest.query
    
    # Apply comprehensive search if provided
    if search_term:
        # Search across all text fields
        search_pattern = f'%{search_term}%'
        query = query.filter(
            db.or_(
                ArchivedRequest.customer_name.ilike(search_pattern),
                ArchivedRequest.email.ilike(search_pattern),
                ArchivedRequest.phone.ilike(search_pattern),
                ArchivedRequest.company_name.ilike(search_pattern),
                ArchivedRequest.reference.ilike(search_pattern),
                ArchivedRequest.street_address.ilike(search_pattern),
                ArchivedRequest.city.ilike(search_pattern),
                ArchivedRequest.state_province.ilike(search_pattern),
                ArchivedRequest.postal_code.ilike(search_pattern),
                ArchivedRequest.country.ilike(search_pattern),
                ArchivedRequest.additional_notes.ilike(search_pattern),
                ArchivedRequest.fabric_selections.ilike(search_pattern),  # This searches the JSON string
                ArchivedRequest.status.ilike(search_pattern)
            )
        )
    
    # Order by date archived (newest first)
    requests = query.order_by(ArchivedRequest.date_archived.desc()).all()
    
    # Parse fabric cuttings for display
    for req in requests:
        try:
            req.parsed_fabric_cuttings = json.loads(req.fabric_selections)
        except (json.JSONDecodeError, TypeError):
            req.parsed_fabric_cuttings = []
    
    return render_template('archived_requests.html', 
                         requests=requests,
                         search_term=search_term)

@app.route('/admin/archived/<int:request_id>')
@require_admin
def archived_request_details(request_id):
    """View detailed information for an archived request"""
    
    archived_request = ArchivedRequest.query.get_or_404(request_id)
    fabric_selections = json.loads(archived_request.fabric_selections)
    
    return render_template('archived_request_details.html', 
                         request=archived_request, 
                         fabric_selections=fabric_selections)

@app.route('/admin/archive_old_requests', methods=['POST'])
@require_admin
def manual_archive_requests():
    """Manually trigger archiving of old dispatched requests"""
    from database_maintenance import archive_dispatched_requests
    
    try:
        archived_count = archive_dispatched_requests()
        if archived_count > 0:
            flash(f'Successfully archived {archived_count} dispatched requests older than 4 months.', 'success')
        else:
            flash('No requests to archive. Only dispatched requests older than 4 months are archived.', 'info')
        
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        app.logger.error(f"Error archiving requests: {str(e)}")
        flash('Error occurred while archiving requests. Please check logs.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/data_integrity', methods=['GET', 'POST'])
@require_admin
def data_integrity_check():
    """Run data integrity check and recovery"""
    from data_integrity import data_integrity_manager
    from database_recovery import emergency_recovery
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'integrity_check':
            result = data_integrity_manager.perform_integrity_check()
            flash(f"Integrity check completed: {result['status']}", 'info')
            if result.get('issues'):
                for issue in result['issues']:
                    flash(issue, 'warning')
        
        elif action == 'recovery_scan':
            result = emergency_recovery.perform_full_recovery_scan()
            flash(f"Recovery scan completed: {result['recovered_from_audit']} records recovered", 'success')
            if result.get('issues_found'):
                for issue in result['issues_found']:
                    flash(issue, 'warning')
        
        elif action == 'backup_snapshot':
            filename = data_integrity_manager.create_backup_snapshot()
            if filename:
                flash(f"Backup created: {filename}", 'success')
            else:
                flash("Backup creation failed", 'error')
        
        return redirect(url_for('data_integrity_check'))
    
    # Get current integrity status
    integrity_status = data_integrity_manager.perform_integrity_check()
    
    return render_template('data_integrity.html', integrity_status=integrity_status)

@app.route('/admin/email_iliv/<int:request_id>', methods=['POST'])
@require_admin
def email_iliv(request_id):
    """Send fabric cutting request email to ILIV suppliers"""
    app.logger.info(f"ILIV email endpoint called for request #{request_id}")
    try:
        # Get the request
        sample_request = SampleRequest.query.get_or_404(request_id)
        app.logger.info(f"Found sample request #{request_id}")
        
        # Get custom email body from request if provided
        json_data = request.get_json()
        custom_body = json_data.get('email_body') if json_data else None
        app.logger.info(f"Custom body provided: {bool(custom_body)}")
        
        # Send the email using the email service
        from email_service import send_iliv_fabric_request
        success = send_iliv_fabric_request(sample_request, custom_body)
        
        if success:
            app.logger.info(f"ILIV email sent successfully for request #{request_id}")
            return jsonify({
                'success': True,
                'message': 'Email sent successfully to ILIV'
            })
        else:
            app.logger.error(f"Failed to send ILIV email for request #{request_id}")
            return jsonify({
                'success': False,
                'message': 'Failed to send email. Please try again.'
            })
            
    except Exception as e:
        app.logger.error(f"Error sending ILIV email for request #{request_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        })

@app.route('/admin/logout')
@require_admin
def admin_logout():
    """Logout admin user"""
    session.clear()  # Clear entire session for security
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
