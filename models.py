from app import db
from datetime import datetime
from sqlalchemy import func

class SampleRequest(db.Model):
    __tablename__ = 'sample_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer information
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)
    
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
    
    def __repr__(self):
        return f'<SampleRequest {self.id}: {self.customer_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
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
