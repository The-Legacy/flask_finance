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
    
    # New fields for enhanced loan management
    target_payoff_months = db.Column(db.Integer)  # User-selected payoff timeline
    current_month_paid = db.Column(db.Float, default=0.0)  # Amount paid this month
    last_payment_date = db.Column(db.Date)  # Track when last payment was made
    auto_payment_enabled = db.Column(db.Boolean, default=False)  # For automatic payments
    
    # Enhanced tracking fields
    total_interest_paid = db.Column(db.Float, default=0.0)  # Total interest paid over loan life
    total_payments_made = db.Column(db.Float, default=0.0)  # Total amount paid towards loan
    payment_count = db.Column(db.Integer, default=0)  # Number of payments made
    
    def __repr__(self):
        return f'<Loan {self.id}: {self.name} ${self.balance}>'
    
    def monthly_interest_payment(self):
        """Calculate monthly interest payment based on current balance"""
        monthly_rate = self.interest_rate / 100 / 12
        return self.balance * monthly_rate
    
    def calculate_monthly_payment(self, payoff_months=None):
        """
        Calculate required monthly payment based on payoff timeline
        This is the primary payment calculation method
        """
        if self.balance <= 0:
            return 0
            
        # Use target payoff months if set, otherwise use default
        months = payoff_months or self.target_payoff_months
        if not months or months <= 0:
            # Default to reasonable payoff times based on loan type
            if self.loan_type == 'credit_card':
                months = 24  # 2 years for credit cards
            elif self.loan_type == 'auto':
                months = 60  # 5 years for auto loans
            elif self.loan_type == 'mortgage':
                months = 360  # 30 years for mortgages
            elif self.loan_type == 'student':
                months = 120  # 10 years for student loans
            else:
                months = 60  # 5 years default
        
        monthly_rate = self.interest_rate / 100 / 12
        
        # If no interest rate, just divide balance by months
        if monthly_rate == 0:
            return max(self.balance / months, self.effective_minimum_payment())
        
        # Standard loan payment formula: PMT = PV * (r * (1+r)^n) / ((1+r)^n - 1)
        numerator = self.balance * monthly_rate * ((1 + monthly_rate) ** months)
        denominator = ((1 + monthly_rate) ** months) - 1
        calculated_payment = numerator / denominator
        
        # Ensure payment is at least the effective minimum required (capped at balance)
        return max(calculated_payment, self.effective_minimum_payment())
    
    def calculate_interest_breakdown(self, payment_amount=None):
        """
        Calculate how much of a payment goes to interest vs principal
        Returns tuple: (interest_portion, principal_portion)
        """
        if payment_amount is None:
            payment_amount = self.calculate_monthly_payment()
            
        interest_portion = self.monthly_interest_payment()
        principal_portion = max(0, payment_amount - interest_portion)
        
        # If payment is less than balance, cap principal at remaining balance
        if principal_portion > self.balance:
            principal_portion = self.balance
            
        return interest_portion, principal_portion
    
    def calculate_payoff_summary(self, extra_payment=0):
        """
        Calculate full payoff summary with current terms
        Returns dict with payoff details
        """
        if self.balance <= 0:
            return {
                'months_remaining': 0,
                'total_payments': 0,
                'total_interest': 0,
                'monthly_payment': 0,
                'monthly_interest': 0,
                'monthly_principal': 0
            }
        
        monthly_payment = self.calculate_monthly_payment() + extra_payment
        monthly_rate = self.interest_rate / 100 / 12
        
        if monthly_payment <= self.monthly_interest_payment():
            return None  # Payment too low - will never pay off
        
        # Calculate payoff time with current payment
        if monthly_rate == 0:
            months = max(1, int(self.balance / monthly_payment))
        else:
            import math
            try:
                numerator = -math.log(1 - (monthly_rate * self.balance / monthly_payment))
                denominator = math.log(1 + monthly_rate)
                months = max(1, int(math.ceil(numerator / denominator)))
            except (ValueError, ZeroDivisionError):
                return None
        
        total_payments = monthly_payment * months
        total_interest = total_payments - self.balance
        interest_portion, principal_portion = self.calculate_interest_breakdown(monthly_payment)
        
        return {
            'months_remaining': months,
            'total_payments': total_payments,
            'total_interest': total_interest + self.total_interest_paid,  # Include already paid interest
            'monthly_payment': monthly_payment,
            'monthly_interest': interest_portion,
            'monthly_principal': principal_portion,
            'payoff_date': self.calculate_payoff_date(months)
        }
    
    def calculate_payoff_date(self, months_remaining):
        """Calculate the date when loan will be paid off"""
        from datetime import date, timedelta
        import calendar
        
        current_date = date.today()
        target_date = current_date
        
        for _ in range(months_remaining):
            # Move to next month
            if target_date.month == 12:
                target_date = target_date.replace(year=target_date.year + 1, month=1)
            else:
                target_date = target_date.replace(month=target_date.month + 1)
        
        return target_date
    
    def effective_minimum_payment(self):
        """Calculate the effective minimum payment (can't be more than balance)"""
        return min(self.minimum_payment, self.balance)
    
    def apr_based_payment(self, target_payoff_years=None):
        """
        Legacy method - now uses calculate_monthly_payment
        Maintained for backward compatibility
        """
        if target_payoff_years:
            return self.calculate_monthly_payment(target_payoff_years * 12)
        return self.calculate_monthly_payment()
    
    def required_monthly_payment(self):
        """Get the required monthly payment (calculated or minimum)"""
        return self.calculate_monthly_payment()
    
    def remaining_payment_this_month(self):
        """Calculate how much more is needed to meet this month's payment requirement"""
        required = self.required_monthly_payment()
        remaining = max(0, required - self.current_month_paid)
        return remaining
    
    def is_current_month_satisfied(self):
        """Check if this month's payment requirement has been met"""
        return self.current_month_paid >= self.required_monthly_payment()
    
    def make_payment(self, amount, payment_date=None, account_id=None):
        """
        Make a payment on this loan and track interest vs principal
        Returns dict with payment details and updated loan status
        """
        from datetime import date
        if payment_date is None:
            payment_date = date.today()
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
            
        if amount > self.balance:
            amount = self.balance  # Can't pay more than balance
        
        # Calculate interest and principal portions
        interest_portion, principal_portion = self.calculate_interest_breakdown(amount)
        
        # Handle month rollover for payment tracking
        if (self.last_payment_date is None or 
            payment_date.month != self.last_payment_date.month or 
            payment_date.year != self.last_payment_date.year):
            # New month, reset current month payment tracking
            self.current_month_paid = 0.0
        
        # Update payment tracking
        old_balance = self.balance
        self.current_month_paid += amount
        self.last_payment_date = payment_date
        self.total_payments_made += amount
        self.total_interest_paid += interest_portion
        self.payment_count += 1
        
        # Apply payment to balance
        self.balance = max(0, self.balance - principal_portion)
        actual_principal_applied = old_balance - self.balance
        
        # Calculate if overpaid this month
        required_monthly = self.calculate_monthly_payment()
        overpaid_amount = max(0, self.current_month_paid - required_monthly)
        months_ahead = 0
        
        if overpaid_amount > 0 and required_monthly > 0:
            months_ahead = int(overpaid_amount // required_monthly)
        
        # Return detailed payment info
        payment_details = {
            'payment_amount': amount,
            'interest_portion': interest_portion,
            'principal_portion': actual_principal_applied,
            'new_balance': self.balance,
            'overpaid_amount': overpaid_amount,
            'months_ahead': months_ahead,
            'current_month_paid': self.current_month_paid,
            'remaining_payment_this_month': self.remaining_payment_this_month(),
            'is_month_satisfied': self.is_current_month_satisfied(),
            'estimated_payoff_months': self.recalculate_payoff_timeline(),
            'account_id': account_id
        }
        
        return payment_details
    
    def recalculate_payoff_timeline(self):
        """
        Recalculate payoff timeline based on current balance and payment schedule
        Returns new estimated payoff months
        """
        if self.balance <= 0:
            return 0
        
        monthly_rate = self.interest_rate / 100 / 12
        monthly_payment = self.required_monthly_payment()
        
        if monthly_payment <= self.monthly_interest_payment():
            return None  # Will never pay off
        
        if monthly_rate == 0:
            return max(1, int(self.balance / monthly_payment))
        
        # Calculate remaining months with current payment amount
        import math
        try:
            numerator = -math.log(1 - (monthly_rate * self.balance / monthly_payment))
            denominator = math.log(1 + monthly_rate)
            return max(1, int(numerator / denominator))
        except (ValueError, ZeroDivisionError):
            return None
    
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
        payoff_summary = self.calculate_payoff_summary()
        return {
            'id': self.id,
            'name': self.name,
            'balance': self.balance,
            'original_amount': self.original_amount,
            'interest_rate': self.interest_rate,
            'minimum_payment': self.minimum_payment,
            'due_date': self.due_date.isoformat(),
            'loan_type': self.loan_type,
            'target_payoff_months': self.target_payoff_months,
            
            # Payment calculations
            'monthly_payment': self.calculate_monthly_payment(),
            'monthly_interest': self.monthly_interest_payment(),
            'required_monthly_payment': self.required_monthly_payment(),
            
            # Current month tracking
            'current_month_paid': self.current_month_paid,
            'remaining_payment_this_month': self.remaining_payment_this_month(),
            'is_current_month_satisfied': self.is_current_month_satisfied(),
            
            # Historical tracking
            'total_interest_paid': self.total_interest_paid,
            'total_payments_made': self.total_payments_made,
            'payment_count': self.payment_count,
            
            # Payoff projections
            'payoff_summary': payoff_summary,
            'estimated_payoff_months': self.recalculate_payoff_timeline() if payoff_summary else None,
            'payoff_date': payoff_summary['payoff_date'].isoformat() if payoff_summary else None
        }
