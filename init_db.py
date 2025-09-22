#!/usr/bin/env python3
"""
Database initialization script for production deployments.
Run this once after deployment to create database tables.
"""
import os
import sys
from app import app, db

def init_production_database():
    """Initialize database tables for production deployment"""
    with app.app_context():
        # Import models to register them
        import models
        
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Initialize data integrity manager
        try:
            from data_integrity import data_integrity_manager
            print("Data integrity manager initialized")
        except Exception as e:
            print(f"Warning: Data integrity manager initialization failed: {e}")

if __name__ == "__main__":
    print("Initializing production database...")
    init_production_database()
    print("Database initialization complete!")