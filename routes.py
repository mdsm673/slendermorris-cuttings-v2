import json
import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import SampleRequest

# No longer needed - fabric cuttings are now text inputs

# Admin credentials (in production, this should be in environment variables)
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))

@app.route('/')
def index():
    """Customer-facing form for fabric sample requests"""
    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])
def submit_request():
    """Handle fabric sample request submission"""
    try:
        # Get form data
        customer_name = request.form.get('customer_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company_name = request.form.get('company_name', '').strip()
        
        # Address fields
        street_address = request.form.get('street_address', '').strip()
        city = request.form.get('city', '').strip()
        state_province = request.form.get('state_province', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        country = request.form.get('country', '').strip()
        
        additional_notes = request.form.get('additional_notes', '').strip()
        
        # Validate required fields (including company_name now)
        if not all([customer_name, email, company_name, street_address, city, state_province, postal_code, country]):
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
        
        # Get fabric cuttings from text inputs
        fabric_cuttings = []
        for i in range(1, 6):
            cutting = request.form.get(f'fabric_cutting_{i}', '').strip()
            if cutting:
                fabric_cuttings.append(cutting)
        
        if not fabric_cuttings:
            return jsonify({'success': False, 'message': 'Please enter at least one fabric cutting.'})
        
        # Create new sample request
        sample_request = SampleRequest(
            customer_name=customer_name,
            email=email,
            phone=phone,
            company_name=company_name,
            street_address=street_address,
            city=city,
            state_province=state_province,
            postal_code=postal_code,
            country=country,
            fabric_selections=json.dumps(fabric_cuttings),
            additional_notes=additional_notes
        )
        
        db.session.add(sample_request)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Thank you, {customer_name}! Your fabric sample request has been submitted successfully. You will receive a confirmation email shortly.',
            'request_id': sample_request.id
        })
        
    except Exception as e:
        app.logger.error(f"Error submitting request: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while submitting your request. Please try again.'})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_authenticated'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password. Please try again.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard for managing sample requests"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'date_submitted')
    sort_order = request.args.get('order', 'desc')
    
    # Build query
    query = SampleRequest.query
    
    if status_filter:
        query = query.filter(SampleRequest.status == status_filter)
    
    # Apply sorting
    if sort_by == 'date_submitted':
        if sort_order == 'desc':
            query = query.order_by(SampleRequest.date_submitted.desc())
        else:
            query = query.order_by(SampleRequest.date_submitted.asc())
    elif sort_by == 'customer_name':
        if sort_order == 'desc':
            query = query.order_by(SampleRequest.customer_name.desc())
        else:
            query = query.order_by(SampleRequest.customer_name.asc())
    elif sort_by == 'status':
        if sort_order == 'desc':
            query = query.order_by(SampleRequest.status.desc())
        else:
            query = query.order_by(SampleRequest.status.asc())
    
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
                         sort_order=sort_order)

@app.route('/admin/request/<int:request_id>')
def request_details(request_id):
    """View detailed information for a specific request"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    sample_request = SampleRequest.query.get_or_404(request_id)
    fabric_selections = json.loads(sample_request.fabric_selections)
    
    return render_template('request_details.html', 
                         request=sample_request, 
                         fabric_selections=fabric_selections)

@app.route('/admin/update_status/<int:request_id>', methods=['POST'])
def update_status(request_id):
    """Update the status of a sample request"""
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        sample_request = SampleRequest.query.get_or_404(request_id)
        json_data = request.get_json()
        if not json_data:
            return jsonify({'success': False, 'message': 'No JSON data received'})
            
        new_status = json_data.get('status')
        
        if new_status not in ['Outstanding', 'In Progress', 'Dispatched']:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        sample_request.status = new_status
        
        # Set dispatch date if status is changed to Dispatched
        if new_status == 'Dispatched' and sample_request.date_dispatched is None:
            sample_request.date_dispatched = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Status updated to {new_status}',
            'date_dispatched': sample_request.date_dispatched.strftime('%Y-%m-%d %H:%M:%S') if sample_request.date_dispatched else None
        })
        
    except Exception as e:
        app.logger.error(f"Error updating status: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating status'})



@app.route('/admin/logout')
def admin_logout():
    """Logout admin user"""
    session.pop('admin_authenticated', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
