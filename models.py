from app import db
from datetime import datetime
from sqlalchemy import func

class SampleRequest(db.Model):
    __tablename__ = 'sample_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer information
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(512), nullable=False)  # Supports multiple comma-separated emails
    phone = db.Column(db.String(20), nullable=True)
    company_name = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(100), nullable=True)
    
    # Shipping address
    street_address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state_province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # Request details
    fabric_selections = db.Column(db.Text, nullable=False)  # JSON string of fabric:quantity pairs
    additional_notes = db.Column(db.Text, nullable=True)
    
    # Status and tracking
    status = db.Column(db.String(20), default='Outstanding', nullable=False)  # Outstanding, In Progress, Dispatched
    date_submitted = db.Column(db.DateTime, default=lambda: datetime.utcnow(), nullable=False)
    date_dispatched = db.Column(db.DateTime, nullable=True)
    iliv_email_sent = db.Column(db.Boolean, default=False, nullable=False)  # Track if ILIV email has been sent
    
    def __repr__(self):
        return f'<SampleRequest {self.id}: {self.customer_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'reference': self.reference,
            'street_address': self.street_address,
            'city': self.city,
            'state_province': self.state_province,
            'postal_code': self.postal_code,
            'country': self.country,
            'fabric_selections': self.fabric_selections,
            'additional_notes': self.additional_notes,
            'status': self.status,
            'date_submitted': self.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
            'date_dispatched': self.date_dispatched.strftime('%Y-%m-%d %H:%M:%S') if self.date_dispatched else None
        }

class ArchivedRequest(db.Model):
    """
    Archive table for dispatched requests older than 4 months.
    These records are NEVER deleted and remain permanently accessible.
    """
    __tablename__ = 'archived_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer, nullable=False, index=True)  # Original request ID
    
    # Customer information (preserved from original)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(512), nullable=False)  # Supports multiple comma-separated emails
    phone = db.Column(db.String(20), nullable=True)
    company_name = db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(100), nullable=True)
    
    # Shipping address (preserved from original)
    street_address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state_province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # Request details (preserved from original)
    fabric_selections = db.Column(db.Text, nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)
    
    # Status and tracking (preserved from original)
    status = db.Column(db.String(20), nullable=False)  # Should always be 'Dispatched'
    date_submitted = db.Column(db.DateTime, nullable=False)
    date_dispatched = db.Column(db.DateTime, nullable=False)
    iliv_email_sent = db.Column(db.Boolean, default=False, nullable=False)  # Track if ILIV email was sent before archiving
    
    # Archive metadata
    date_archived = db.Column(db.DateTime, default=lambda: datetime.utcnow(), nullable=False)
    
    def __repr__(self):
        return f'<ArchivedRequest {self.original_id}: {self.customer_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_id': self.original_id,
            'customer_name': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'reference': self.reference,
            'street_address': self.street_address,
            'city': self.city,
            'state_province': self.state_province,
            'postal_code': self.postal_code,
            'country': self.country,
            'fabric_selections': self.fabric_selections,
            'additional_notes': self.additional_notes,
            'status': self.status,
            'date_submitted': self.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
            'date_dispatched': self.date_dispatched.strftime('%Y-%m-%d %H:%M:%S'),
            'date_archived': self.date_archived.strftime('%Y-%m-%d %H:%M:%S')
        }
