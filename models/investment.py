from datetime import datetime
from database import db

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    cost_basis = db.Column(db.Float, nullable=False)  # Price per share when purchased
    current_price = db.Column(db.Float, nullable=False)
    investment_type = db.Column(db.String(50), nullable=False)  # 'stock', 'etf', 'mutual_fund', 'crypto', 'bond'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Investment {self.id}: {self.symbol} {self.shares} shares>'
    
    def total_cost(self):
        """Total amount invested"""
        return self.shares * self.cost_basis
    
    def current_value(self):
        """Current market value"""
        return self.shares * self.current_price
    
    def gain_loss(self):
        """Gain or loss amount"""
        return self.current_value() - self.total_cost()
    
    def gain_loss_percentage(self):
        """Gain or loss percentage"""
        if self.total_cost() == 0:
            return 0
        return (self.gain_loss() / self.total_cost()) * 100
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'shares': self.shares,
            'cost_basis': self.cost_basis,
            'current_price': self.current_price,
            'investment_type': self.investment_type,
            'total_cost': self.total_cost(),
            'current_value': self.current_value(),
            'gain_loss': self.gain_loss(),
            'gain_loss_percentage': self.gain_loss_percentage(),
            'updated_at': self.updated_at.isoformat()
        }
