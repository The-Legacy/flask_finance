#!/usr/bin/env python3
"""
Database migration script to add account_id column to transactions table
and create the accounts table.
"""

import sqlite3
import os

def migrate_database():
    # Path to database
    db_path = os.path.join(os.path.dirname(__file__), 'db', 'finances.db')
    
    print(f"Migrating database at: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if account table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='account';
        """)
        
        account_table_exists = cursor.fetchone() is not None
        
        if not account_table_exists:
            print("Creating accounts table...")
            cursor.execute("""
                CREATE TABLE account (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    account_type VARCHAR(50) NOT NULL,
                    bank_name VARCHAR(100),
                    account_number VARCHAR(50),
                    current_balance FLOAT NOT NULL DEFAULT 0.0,
                    initial_balance FLOAT NOT NULL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✓ Accounts table created")
        else:
            print("✓ Accounts table already exists")
        
        # Check if account_id column exists in transaction table
        cursor.execute('PRAGMA table_info("transaction");')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'account_id' not in columns:
            print("Adding account_id column to transactions table...")
            cursor.execute('''
                ALTER TABLE "transaction" 
                ADD COLUMN account_id INTEGER 
                REFERENCES account(id);
            ''')
            print("✓ account_id column added to transactions")
        else:
            print("✓ account_id column already exists in transactions")
        
        # Commit changes
        conn.commit()
        print("✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
