#!/usr/bin/env python3
"""
Migration script to add is_taxable column to Transaction model.
This migration will:
1. Add the is_taxable column with default value True
2. Set specific categories like 'Gift', 'Refund', etc. to is_taxable=False
"""

import sqlite3
import os

def migrate_add_is_taxable():
    # Database path
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'db', 'finances.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if is_taxable column already exists
        cursor.execute("PRAGMA table_info([transaction])")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_taxable' in columns:
            print("is_taxable column already exists, skipping migration")
            return
        
        print("Adding is_taxable column to transaction table...")
        
        # Add the is_taxable column with default value True
        cursor.execute("ALTER TABLE [transaction] ADD COLUMN is_taxable BOOLEAN NOT NULL DEFAULT 1")
        
        # Set specific categories to non-taxable
        non_taxable_categories = [
            'Gift', 'gift', 'GIFT',
            'Refund', 'refund', 'REFUND',
            'Insurance Payout', 'insurance payout', 'INSURANCE PAYOUT',
            'Loan', 'loan', 'LOAN',
            'Transfer', 'transfer', 'TRANSFER',
            'Inheritance', 'inheritance', 'INHERITANCE',
            'Insurance Reimbursement', 'insurance reimbursement',
            'Tax Refund', 'tax refund', 'TAX REFUND',
            'Legal Settlement', 'legal settlement',
            'Prize', 'prize', 'PRIZE',
            'Lottery', 'lottery', 'LOTTERY',
            'Gambling', 'gambling', 'GAMBLING'
        ]
        
        # Update existing transactions that should be non-taxable
        for category in non_taxable_categories:
            cursor.execute("""
                UPDATE [transaction] 
                SET is_taxable = 0 
                WHERE transaction_type = 'income' AND category = ?
            """, (category,))
            
            affected_rows = cursor.rowcount
            if affected_rows > 0:
                print(f"  Updated {affected_rows} '{category}' transactions to non-taxable")
        
        # Also check for categories containing certain keywords
        non_taxable_keywords = [
            'gift', 'refund', 'insurance', 'inheritance', 'settlement', 
            'prize', 'lottery', 'gambling', 'transfer'
        ]
        
        for keyword in non_taxable_keywords:
            cursor.execute("""
                UPDATE [transaction] 
                SET is_taxable = 0 
                WHERE transaction_type = 'income' AND LOWER(category) LIKE ?
            """, (f'%{keyword}%',))
            
            affected_rows = cursor.rowcount
            if affected_rows > 0:
                print(f"  Updated {affected_rows} transactions containing '{keyword}' to non-taxable")
        
        # Commit the changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM [transaction] WHERE is_taxable = 0 AND transaction_type = 'income'")
        non_taxable_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM [transaction] WHERE is_taxable = 1 AND transaction_type = 'income'")
        taxable_count = cursor.fetchone()[0]
        
        print(f"\nMigration completed successfully!")
        print(f"Income transactions marked as non-taxable: {non_taxable_count}")
        print(f"Income transactions marked as taxable: {taxable_count}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_add_is_taxable()
