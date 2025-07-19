from database import db
from datetime import datetime

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    employment_type = db.Column(db.String(10), nullable=False)  # w2 or 1099
    state_code = db.Column(db.String(2), nullable=True)
    city_code = db.Column(db.String(10), nullable=True)
    
    # Monthly allocations
    housing = db.Column(db.Float, default=0)
    food = db.Column(db.Float, default=0)
    transportation = db.Column(db.Float, default=0)
    utilities = db.Column(db.Float, default=0)
    healthcare = db.Column(db.Float, default=0)
    insurance = db.Column(db.Float, default=0)
    entertainment = db.Column(db.Float, default=0)
    personal_care = db.Column(db.Float, default=0)
    shopping = db.Column(db.Float, default=0)
    education = db.Column(db.Float, default=0)
    savings = db.Column(db.Float, default=0)
    emergency_fund = db.Column(db.Float, default=0)
    retirement = db.Column(db.Float, default=0)
    other = db.Column(db.Float, default=0)
    
    # Calculated fields (stored for performance)
    monthly_take_home = db.Column(db.Float, nullable=False)
    monthly_taxes = db.Column(db.Float, nullable=False)
    monthly_loan_payments = db.Column(db.Float, default=0)
    monthly_available = db.Column(db.Float, nullable=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_total_allocated(self):
        """Calculate total monthly allocations"""
        return (self.housing + self.food + self.transportation + self.utilities + 
                self.healthcare + self.insurance + self.entertainment + self.personal_care + 
                self.shopping + self.education + self.savings + self.emergency_fund + 
                self.retirement + self.other)
    
    def get_remaining_budget(self):
        """Calculate remaining unallocated budget"""
        return self.monthly_available - self.get_total_allocated()
    
    def get_allocation_by_category(self, category):
        """Get budget allocation for a specific category"""
        category_map = {
            'Housing': self.housing,
            'Food & Dining': self.food,
            'Transportation': self.transportation,
            'Utilities': self.utilities,
            'Healthcare': self.healthcare,
            'Insurance': self.insurance,
            'Entertainment': self.entertainment,
            'Personal Care': self.personal_care,
            'Shopping': self.shopping,
            'Education': self.education,
            'Savings': self.savings,
            'Emergency Fund': self.emergency_fund,
            'Retirement': self.retirement,
            'Other': self.other
        }
        return category_map.get(category, 0)
    
    def to_dict(self):
        """Convert budget to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'annual_income': self.annual_income,
            'employment_type': self.employment_type,
            'monthly_take_home': self.monthly_take_home,
            'monthly_taxes': self.monthly_taxes,
            'monthly_loan_payments': self.monthly_loan_payments,
            'monthly_available': self.monthly_available,
            'allocations': {
                'housing': self.housing,
                'food': self.food,
                'transportation': self.transportation,
                'utilities': self.utilities,
                'healthcare': self.healthcare,
                'insurance': self.insurance,
                'entertainment': self.entertainment,
                'personal_care': self.personal_care,
                'shopping': self.shopping,
                'education': self.education,
                'savings': self.savings,
                'emergency_fund': self.emergency_fund,
                'retirement': self.retirement,
                'other': self.other
            },
            'total_allocated': self.get_total_allocated(),
            'remaining_budget': self.get_remaining_budget(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
