#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
import sqlite3

def migrate_payment_columns():
    """Add missing columns to payments table"""
    print("=== Migrating Payment Table ===\n")
    
    app = create_app()
    
    with app.app_context():
        # Get database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"Database path: {db_path}")
        
        try:
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if columns exist
            cursor.execute("PRAGMA table_info(payments)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing columns: {columns}")
            
            # Add missing columns
            if 'catatan_user' not in columns:
                cursor.execute("ALTER TABLE payments ADD COLUMN catatan_user TEXT")
                print("✓ Added catatan_user column")
            else:
                print("✓ catatan_user column already exists")
            
            if 'catatan_admin' not in columns:
                cursor.execute("ALTER TABLE payments ADD COLUMN catatan_admin TEXT")
                print("✓ Added catatan_admin column")
            else:
                print("✓ catatan_admin column already exists")
            
            # Commit changes
            conn.commit()
            conn.close()
            
            print("\n=== Migration Complete ===")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    migrate_payment_columns()