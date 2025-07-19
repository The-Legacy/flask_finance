from database import db
from datetime import datetime

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # checking, savings, credit, investment, cash
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))  # Store last 4 digits for identification
    current_balance = db.Column(db.Float, nullable=False, default=0.0)
    initial_balance = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with transactions
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    
    def __repr__(self):
        return f'<Account {self.name}: ${self.current_balance:.2f}>'
    
    def get_calculated_balance(self):
        """Calculate balance based on transactions starting from initial balance"""
        if not self.transactions:
            return self.initial_balance
        
        balance = self.initial_balance
        for transaction in self.transactions:
            if transaction.transaction_type == 'income':
                balance += transaction.amount
            else:  # expense
                balance -= transaction.amount
        
        return balance
    
    def get_balance_difference(self):
        """Get the difference between actual and calculated balance"""
        calculated = self.get_calculated_balance()
        return self.current_balance - calculated
    
    def is_balanced(self, tolerance=0.01):
        """Check if account balance matches calculated balance within tolerance"""
        return abs(self.get_balance_difference()) <= tolerance
    
    def get_transaction_count(self):
        """Get the number of transactions for this account"""
        return len(self.transactions)
    
    @staticmethod
    def get_total_assets():
        """Get total value of asset accounts (checking, savings, cash, investment)"""
        asset_types = ['checking', 'savings', 'cash', 'investment']
        return db.session.query(db.func.sum(Account.current_balance)).filter(
            Account.account_type.in_(asset_types),
            Account.is_active == True
        ).scalar() or 0.0
    
    @staticmethod
    def get_total_liabilities():
        """Get total value of liability accounts (credit cards, loans)"""
        liability_types = ['credit', 'loan']
        return db.session.query(db.func.sum(Account.current_balance)).filter(
            Account.account_type.in_(liability_types),
            Account.is_active == True
        ).scalar() or 0.0
    
    @staticmethod
    def get_net_worth():
        """Calculate net worth from account balances"""
        return Account.get_total_assets() - Account.get_total_liabilities()
