#!/usr/bin/env python3
"""
Database migration script to add ILIV email tracking columns.
Run this once to add the new columns to existing database.
"""

from app import app, db
from sqlalchemy import text

def add_iliv_columns():
    """Add ILIV email tracking columns to sample_requests table"""
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sample_requests' 
                AND column_name IN ('iliv_email_sent', 'iliv_email_sent_date')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'iliv_email_sent' not in existing_columns:
                print("Adding iliv_email_sent column...")
                db.session.execute(text("""
                    ALTER TABLE sample_requests 
                    ADD COLUMN iliv_email_sent BOOLEAN DEFAULT FALSE NOT NULL
                """))
                
            if 'iliv_email_sent_date' not in existing_columns:
                print("Adding iliv_email_sent_date column...")
                db.session.execute(text("""
                    ALTER TABLE sample_requests 
                    ADD COLUMN iliv_email_sent_date TIMESTAMP
                """))
                
            db.session.commit()
            print("✓ ILIV email tracking columns added successfully!")
            
        except Exception as e:
            print(f"Error adding columns: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_iliv_columns()