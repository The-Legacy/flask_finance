from datetime import datetime
from database import db

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    original_amount = db.Column(db.Float)
    interest_rate = db.Column(db.Float, nullable=False)  # Annual percentage rate
    minimum_payment = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)  # 'credit_card', 'mortgage', 'auto', 'personal', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Loan {self.id}: {self.name} ${self.balance}>'
    
    def monthly_interest_payment(self):
        """Calculate monthly interest payment"""
        monthly_rate = self.interest_rate / 100 / 12
        return self.balance * monthly_rate
    
    def effective_minimum_payment(self):
        """Calculate the effective minimum payment (can't be more than balance)"""
        return min(self.minimum_payment, self.balance)
    
    def is_overpaid(self):
        """Check if minimum payment is higher than balance"""
        return self.minimum_payment > self.balance
    
    def credit_utilization(self, credit_limit=None):
        """Calculate credit utilization percentage for credit cards"""
        if self.loan_type == 'credit_card' and credit_limit:
            return (self.balance / credit_limit) * 100
        return None
    
    def payoff_time_months(self):
        """Estimate months to pay off with minimum payments"""
        effective_payment = self.effective_minimum_payment()
        
        if effective_payment <= self.monthly_interest_payment():
            return None  # Will never pay off
        
        monthly_rate = self.interest_rate / 100 / 12
        if monthly_rate == 0:
            return self.balance / effective_payment
        
        # Formula for loan payoff time
        import math
        numerator = -math.log(1 - (monthly_rate * self.balance / effective_payment))
        denominator = math.log(1 + monthly_rate)
        return numerator / denominator
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'balance': self.balance,
            'interest_rate': self.interest_rate,
            'minimum_payment': self.minimum_payment,
            'due_date': self.due_date.isoformat(),
            'loan_type': self.loan_type,
            'monthly_interest': self.monthly_interest_payment(),
            'payoff_months': self.payoff_time_months()
        }
