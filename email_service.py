import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import logging

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

Thank you for your fabric sample request. We have received your order and will process it shortly.

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
3. Fabric samples will be prepared and dispatched
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
Request submitted: {datetime.now().strftime('%d %B %Y at %I:%M %p')}
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
    
    subject = f"New Fabric Sample Request #{request_id} - Action Required"
    
    email_body = f"""
NEW FABRIC SAMPLE REQUEST RECEIVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Request ID: #{request_id}
Submitted: {datetime.now().strftime('%d %B %Y at %I:%M %p')}

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
2. Prepare fabric samples
3. Update status to "In Progress"
4. Dispatch samples and mark as "Dispatched"

View full details: [Admin Dashboard Link]

This is an automated notification from the Fabric Sample Ordering System.
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