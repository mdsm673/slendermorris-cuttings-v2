import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import logging
import json
from zoneinfo import ZoneInfo

def send_confirmation_email(customer_data, fabric_cuttings):
    """Send confirmation email to customer and internal team"""
    
    # SMTP Configuration from environment variables
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    # Debug logging
    logging.info(f"SMTP Host: {smtp_host}")
    logging.info(f"SMTP Port: {smtp_port}")
    logging.info(f"SMTP Username: {smtp_username}")
    logging.info(f"SMTP Password: {'Set' if smtp_password else 'Not set'}")
    
    if not smtp_host or not smtp_username or not smtp_password:
        logging.error(f"SMTP configuration missing - Host: {smtp_host}, Username: {smtp_username}, Password: {'Set' if smtp_password else 'Not set'}")
        return False
    
    # Email content
    subject = "Slender Morris - Your Fabric Cuttings Request has been Lodged"
    
    # Create email body
    email_body = f"""
Dear {customer_data.get('company_name', customer_data.get('customer_name', 'Valued Customer'))},

Thank you for your fabric cutting request. We have received your order and will process it shortly.

REQUEST DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Customer Information:
• Company/Name: {customer_data.get('company_name', customer_data.get('customer_name', 'Not provided'))}
• Email: {customer_data.get('email', 'Not provided')}
• Phone: {customer_data.get('phone', 'Not provided')}
• Reference: {customer_data.get('reference', 'Not provided')}

Shipping Address:
• Street: {customer_data.get('street_address', 'Not provided')}
• Suburb: {customer_data.get('city', 'Not provided')}
• State: {customer_data.get('state_province', 'Not provided')}
• Postal Code: {customer_data.get('postal_code', 'Not provided')}
• Country: {customer_data.get('country', 'Not provided')}

Fabric Cuttings Requested:
{chr(10).join([f"• {cutting}" for cutting in fabric_cuttings if cutting.strip()])}

Additional Notes:
{customer_data.get('additional_notes', 'None')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT HAPPENS NEXT:
1. Your request has been logged in our system
2. Our team will review your requirements
3. Fabric cutting will be prepared and dispatched
4. You will receive a tracking notification once shipped

If you have any questions or need to make changes to your request, please contact us:
📧 Email: orders@slendermorris.com
📞 Phone: Available during business hours

Thank you for choosing Slender Morris Furnishings.

Best regards,
The Slender Morris Team
Since 1948

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated confirmation email.
Request submitted: {datetime.now(ZoneInfo('Australia/Sydney')).strftime('%d %B %Y')}
"""

    # Email recipients
    customer_email = customer_data.get('email')
    internal_emails = ['orders@slendermorris.com', 'slendermorris@gmail.com']
    
    all_recipients = [customer_email] + internal_emails if customer_email else internal_emails
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send email to each recipient
        for recipient in all_recipients:
            if recipient and recipient.strip():
                msg = EmailMessage()
                msg['From'] = smtp_username
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.set_content(email_body)
                
                # Send the email
                server.send_message(msg)
                logging.info(f"Confirmation email sent to {recipient}")
        
        server.quit()
        return True
        
    except Exception as e:
        logging.error(f"Failed to send confirmation email: {str(e)}")
        return False

def send_admin_notification(customer_data, fabric_cuttings, request_id):
    """Send notification email to admin team about new request"""
    
    # SMTP Configuration
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_host or not smtp_username or not smtp_password:
        logging.error("SMTP configuration missing")
        return False
    
    subject = f"New Fabric Cutting Request #{request_id} - Action Required"
    
    email_body = f"""
NEW FABRIC CUTTING REQUEST RECEIVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Request ID: #{request_id}
Submitted: {datetime.now(tz=ZoneInfo('Australia/Sydney')).strftime('%d %B %Y')}

CUSTOMER DETAILS:
• Company/Name: {customer_data.get('company_name', customer_data.get('customer_name', 'Not provided'))}
• Email: {customer_data.get('email', 'Not provided')}
• Phone: {customer_data.get('phone', 'Not provided')}
• Reference: {customer_data.get('reference', 'Not provided')}

SHIPPING ADDRESS:
{customer_data.get('street_address', 'Not provided')}
{customer_data.get('city', 'Not provided')}, {customer_data.get('state_province', 'Not provided')} {customer_data.get('postal_code', 'Not provided')}
{customer_data.get('country', 'Not provided')}

FABRIC CUTTINGS REQUESTED:
{chr(10).join([f"• {cutting}" for cutting in fabric_cuttings if cutting.strip()])}

ADDITIONAL NOTES:
{customer_data.get('additional_notes', 'None')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT ACTIONS:
1. Review request in admin dashboard
2. Prepare fabric cutting
3. Update status to "In Progress"
4. Dispatch cutting and mark as "Dispatched"

View full details: [Admin Dashboard Link]

This is an automated notification from the Fabric Cutting Ordering System.
"""

    try:
        # Send to internal team only
        internal_emails = ['orders@slendermorris.com', 'slendermorris@gmail.com']
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        for recipient in internal_emails:
            msg = EmailMessage()
            msg['From'] = smtp_username
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.set_content(email_body)
            
            server.send_message(msg)
            logging.info(f"Admin notification sent to {recipient}")
        
        server.quit()
        return True
        
    except Exception as e:
        logging.error(f"Failed to send admin notification: {str(e)}")
        return False

def send_dispatch_notification(sample_request):
    """Send dispatch notification to customer and internal team"""
    
    # SMTP Configuration
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_host or not smtp_username or not smtp_password:
        logging.error("SMTP configuration missing for dispatch notification")
        return False
    
    # Parse fabric selections
    try:
        fabric_cuttings = json.loads(sample_request.fabric_selections)
    except:
        fabric_cuttings = []
    
    # Email content
    subject = f"Your Fabric Cutting Order #{sample_request.id} Has Been Dispatched"
    
    email_body = f"""
Dear {sample_request.company_name or sample_request.customer_name or 'Valued Customer'},

Great news! Your fabric cutting order has been dispatched.

ORDER DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Order Number: #{sample_request.id}
Dispatch Date: {datetime.now(tz=ZoneInfo('Australia/Sydney')).strftime('%d %B %Y')}

FABRIC CUTTINGS DISPATCHED:
{chr(10).join([f"• {cutting}" for cutting in fabric_cuttings if cutting.strip()])}

SHIPPING TO:
{sample_request.street_address}
{sample_request.city}, {sample_request.state_province} {sample_request.postal_code}
{sample_request.country}

WHAT TO EXPECT:
• Your fabric cuttings have been carefully prepared and packaged
• You should receive your order within 3-5 business days
• Track your shipment using the order number provided

If you have any questions about your order, please contact us:
📧 Email: orders@slendermorris.com
📞 Phone: Available during business hours

Thank you for choosing Slender Morris Furnishings.

Best regards,
The Slender Morris Team
Since 1948

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated dispatch confirmation.
"""
    
    # Recipients - customer email + internal emails
    recipients = []
    if sample_request.email:
        recipients.append(sample_request.email)
    recipients.extend(['orders@slendermorris.com', 'slendermorris@gmail.com'])
    
    success = True
    try:
        # Create SMTP connection
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send email to each recipient
        for recipient in recipients:
            if recipient and recipient.strip():
                msg = EmailMessage()
                msg['From'] = smtp_username
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.set_content(email_body)
                
                # Send the email
                server.send_message(msg)
                logging.info(f"Dispatch notification sent to {recipient}")
        
        server.quit()
        return True
        
    except Exception as e:
        logging.error(f"Failed to send dispatch notification: {str(e)}")
        return False

def send_iliv_fabric_request(sample_request, custom_body=None):
    """Send fabric cutting request email to ILIV suppliers"""
    
    # SMTP Configuration from environment variables
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_host or not smtp_username or not smtp_password:
        logging.error("SMTP configuration missing for ILIV email")
        return False
    
    # Parse fabric selections
    try:
        fabric_list = json.loads(sample_request.fabric_selections)
        if isinstance(fabric_list, list):
            fabric_bullets = '\n'.join([f"- {fabric.strip()}" for fabric in fabric_list if fabric.strip()])
        else:
            fabric_bullets = "- No fabrics specified"
    except (json.JSONDecodeError, TypeError):
        fabric_bullets = "- No fabrics specified"
    
    # Email content
    subject = "[ATT: Juris] - Cuttings Request - Slender Morris"
    
    # Use custom body if provided, otherwise use default template
    if custom_body:
        email_body = custom_body
    else:
        email_body = f"""Hi Juris

Please send us the following cuttings:
{fabric_bullets}

Please send the order confirmation to: ORDERS@SLENDERMORRIS.COM (NOT this email address)

Thanks
Matthew & Neville - Slender Morris"""
    
    # Recipients - always send to these 4 addresses
    recipients = [
        'orders@slendermorris.com',
        'slendermorris@gmail.com', 
        'export@iliv.co.uk',
        'jurijs_peremots@smd-textiles.co.uk'
    ]
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            
            for recipient in recipients:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = smtp_username
                msg['To'] = recipient
                msg.set_content(email_body)
                
                server.send_message(msg)
                logging.info(f"ILIV email sent to {recipient}")
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to send ILIV email: {str(e)}")
        return False