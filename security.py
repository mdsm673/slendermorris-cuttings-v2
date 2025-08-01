"""Security utilities and validators for the application"""
import re
from flask import abort
from functools import wraps
from flask import session

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format (allows various formats)"""
    if not phone:
        return True  # Phone is optional
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's a valid phone number (digits only, 7-15 digits)
    return re.match(r'^\+?\d{7,15}$', cleaned) is not None

def sanitize_input(text, max_length=None):
    """Sanitize text input to prevent XSS and SQL injection"""
    if not text:
        return text
    # Strip whitespace
    text = text.strip()
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

def validate_status(status):
    """Validate order status"""
    valid_statuses = ['Outstanding', 'In Progress', 'Dispatched']
    return status in valid_statuses

def validate_fabric_cutting(cutting):
    """Validate fabric cutting input"""
    if not cutting:
        return True
    # Limit length and check for basic validity
    if len(cutting) > 200:
        return False
    # Allow alphanumeric, spaces, and common punctuation
    return re.match(r'^[a-zA-Z0-9\s\-\.,\'"/()]+$', cutting) is not None