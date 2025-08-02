# Deployment Guide

## Pre-Deployment Checklist

✅ **Database Security**
- Bulletproof data retention implemented
- Audit logging active
- Recovery mechanisms tested
- Backup systems operational

✅ **Application Security**
- Rate limiting configured
- Session security hardened
- Input validation comprehensive
- Security headers enabled

✅ **Email Configuration**
- SMTP settings configured
- Test emails sent successfully
- Sydney timezone configured

✅ **Data Integrity**
- Archive system tested
- Recovery tools functional
- No delete functionality exists
- All records permanently retained

## Required Environment Variables

```bash
DATABASE_URL=postgresql://...
SESSION_SECRET=<secure-random-string>
ADMIN_PASSWORD=Matthew1234
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<email>
SMTP_PASSWORD=<app-password>
```

## Deployment Steps

1. **Deploy via Replit Deployments**
   - Click the Deploy button in Replit
   - Replit will handle building and hosting automatically

2. **Post-Deployment Verification**
   - Test customer form submission
   - Verify email notifications
   - Check admin dashboard access
   - Run data integrity check
   - Test archive functionality

3. **Monitoring**
   - Check Data Integrity page weekly
   - Review audit logs monthly
   - Create backup snapshots monthly
   - Monitor email delivery rates

## Production URL

Once deployed, the application will be available at:
- `https://<your-app-name>.replit.app`
- Or your custom domain if configured

## Support

For any deployment issues:
1. Check application logs
2. Run data integrity check
3. Review audit logs
4. Contact Replit support if needed