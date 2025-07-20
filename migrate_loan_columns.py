#!/usr/bin/env python3
"""
Migration script to add new loan management columns to existing database
Run this script to add the enhanced loan features to your existing loans
"""

import os
import sqlite3
from datetime import datetime

def migrate_loan_columns():
    """Add new columns to the loan table"""
    # Get the database path
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'db', 'finances.db')
    
    print(f"Migrating database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Error: Database file not found!")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check what columns already exist
        cursor.execute("PRAGMA table_info(loan)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # List of new columns to add
        new_columns = {
            'target_payoff_months': 'INTEGER',
            'current_month_paid': 'REAL DEFAULT 0.0',
            'last_payment_date': 'DATE',
            'auto_payment_enabled': 'BOOLEAN DEFAULT 0'
        }
        
        # Add missing columns
        columns_added = 0
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE loan ADD COLUMN {column_name} {column_type}"
                    print(f"Adding column: {sql}")
                    cursor.execute(sql)
                    columns_added += 1
                    print(f"✓ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"✗ Error adding column {column_name}: {e}")
            else:
                print(f"⚠ Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the new structure
        cursor.execute("PRAGMA table_info(loan)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"\nFinal columns: {final_columns}")
        
        # Show current loans
        cursor.execute("SELECT id, name, balance, interest_rate FROM loan")
        loans = cursor.fetchall()
        print(f"\nFound {len(loans)} existing loans:")
        for loan in loans:
            print(f"  - {loan[1]}: ${loan[2]:,.2f} at {loan[3]:.2f}% APR")
        
        conn.close()
        
        print(f"\n✅ Migration completed successfully! Added {columns_added} new columns.")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Starting loan table migration...")
    success = migrate_loan_columns()
    
    if success:
        print("\n🎉 Migration completed! You can now use the enhanced loan features.")
        print("💡 New features include:")
        print("   - APR-based payment calculations")
        print("   - Custom payoff timelines")
        print("   - Interactive payment tracking")
        print("   - Dynamic recalculation")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
