#!/usr/bin/env python3
"""
Migration script to add enhanced loan tracking fields to existing database
Run this script to update your database schema with the new loan columns
"""

import os
import sqlite3
from datetime import datetime

def migrate_loan_table():
    # Get the database path
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'db', 'finances.db')
    
    print(f"Migrating database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database...")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(loan)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current loan table columns: {columns}")
        
        # List of new columns to add
        new_columns = [
            ('total_interest_paid', 'REAL DEFAULT 0.0'),
            ('total_payments_made', 'REAL DEFAULT 0.0'),
            ('payment_count', 'INTEGER DEFAULT 0')
        ]
        
        # Add missing columns
        for col_name, col_definition in new_columns:
            if col_name not in columns:
                try:
                    sql = f"ALTER TABLE loan ADD COLUMN {col_name} {col_definition}"
                    print(f"Adding column: {sql}")
                    cursor.execute(sql)
                    print(f"✓ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ Error adding column {col_name}: {e}")
            else:
                print(f"✓ Column {col_name} already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify final table structure
        cursor.execute("PRAGMA table_info(loan)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"Final loan table columns: {final_columns}")
        
        conn.close()
        print("✓ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting loan table migration...")
    success = migrate_loan_table()
    if success:
        print("Migration completed. You can now run the application.")
    else:
        print("Migration failed. Please check the errors above.")
