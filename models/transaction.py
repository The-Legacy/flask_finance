from datetime import datetime
from database import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    is_taxable = db.Column(db.Boolean, nullable=False, default=True)  # Whether income is taxable (gifts, refunds, etc. are not)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)  # Made nullable for existing data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.transaction_type} ${self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'category': self.category,
            'description': self.description,
            'transaction_type': self.transaction_type,
            'is_taxable': self.is_taxable,
            'created_at': self.created_at.isoformat()
        }
