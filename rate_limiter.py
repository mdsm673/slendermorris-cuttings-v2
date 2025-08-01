"""Rate limiting functionality to prevent abuse"""
from flask import request, jsonify, flash, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
import time

# Simple in-memory rate limiting (in production, use Redis)
request_counts = {}

def get_client_ip():
    """Get the real client IP address"""
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Handle proxy
        ip = forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

def rate_limit(max_requests=5, window_seconds=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = get_client_ip()
            now = time.time()
            
            # Clean old entries
            global request_counts
            request_counts = {k: v for k, v in request_counts.items() 
                            if now - v['first_request'] < window_seconds}
            
            # Check rate limit
            if ip in request_counts:
                count = request_counts[ip]['count']
                first_request = request_counts[ip]['first_request']
                
                if now - first_request < window_seconds:
                    if count >= max_requests:
                        return jsonify({
                            'success': False, 
                            'message': 'Too many requests. Please try again later.'
                        }), 429
                    request_counts[ip]['count'] += 1
                else:
                    # Reset window
                    request_counts[ip] = {'count': 1, 'first_request': now}
            else:
                request_counts[ip] = {'count': 1, 'first_request': now}
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit_login(max_attempts=5, lockout_minutes=15):
    """Special rate limiting for login attempts"""
    login_attempts = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = get_client_ip()
            now = datetime.now()
            
            # Check if IP is locked out
            if ip in login_attempts:
                attempts = login_attempts[ip]['attempts']
                last_attempt = login_attempts[ip]['last_attempt']
                
                # Check lockout
                if attempts >= max_attempts:
                    lockout_time = last_attempt + timedelta(minutes=lockout_minutes)
                    if now < lockout_time:
                        remaining = int((lockout_time - now).total_seconds() / 60)
                        flash(f'Too many failed login attempts. Please try again in {remaining} minutes.', 'error')
                        return redirect(url_for('admin_login'))
                    else:
                        # Reset after lockout period
                        login_attempts[ip] = {'attempts': 0, 'last_attempt': now}
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def record_failed_login(ip):
    """Record a failed login attempt"""
    now = datetime.now()
    if ip not in login_attempts:
        login_attempts[ip] = {'attempts': 1, 'last_attempt': now}
    else:
        login_attempts[ip]['attempts'] += 1
        login_attempts[ip]['last_attempt'] = now

def reset_login_attempts(ip):
    """Reset login attempts after successful login"""
    if ip in login_attempts:
        del login_attempts[ip]

# Global storage for rate limiting
login_attempts = {}