from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Use absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(basedir, 'db')
os.makedirs(db_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_dir, "finances.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from database import db
db.init_app(app)

# Import models after db initialization
from models.transaction import Transaction
from models.loan import Loan
from models.investment import Investment
from models.budget import Budget
from models.account import Account
from utils.tax_calculator import TaxCalculator

# Create tables
def init_db():
    with app.app_context():
        db.create_all()

# Ensure database is initialized when the app starts
try:
    init_db()
except Exception as e:
    print(f"Database initialization will be attempted on first request: {e}")

# Initialize database when running as main module
if __name__ == '__main__':
    init_db()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Get summary data
    transactions = Transaction.query.all()
    loans = Loan.query.all()
    investments = Investment.query.all()
    active_budget = Budget.query.filter_by(is_active=True).first()
    
    # Calculate monthly totals (current month)
    from datetime import datetime, timedelta
    current_month = datetime.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    # Get current month transactions
    monthly_transactions = Transaction.query.filter(
        Transaction.date >= current_month.date(),
        Transaction.date < next_month.date()
    ).all()
    
    monthly_income = sum(t.amount for t in monthly_transactions if t.transaction_type == 'income')
    monthly_expenses = sum(t.amount for t in monthly_transactions if t.transaction_type == 'expense')
    monthly_net_balance = monthly_income - monthly_expenses
    
    # Calculate tax amount for this month based on income and budget info
    monthly_tax_amount = 0
    if active_budget and monthly_income > 0:
        try:
            calculator = TaxCalculator()
            # Calculate what percentage of annual income this month's income represents
            income_percentage = monthly_income / (active_budget.annual_income / 12)
            # Apply that percentage to the monthly tax estimate
            monthly_tax_amount = active_budget.monthly_taxes * income_percentage
        except Exception as e:
            print(f"Error calculating monthly tax amount: {e}")
            monthly_tax_amount = 0
    
    # Calculate all-time totals for net worth calculation
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_balance = total_income - total_expenses
    
    # Calculate debt summary
    total_debt = sum(loan.balance for loan in loans)
    
    # Calculate investment summary
    total_invested = sum(inv.shares * inv.cost_basis for inv in investments)
    current_portfolio_value = sum(inv.shares * inv.current_price for inv in investments)
    portfolio_gain_loss = current_portfolio_value - total_invested
    
    # Net worth calculation
    net_worth = net_balance + current_portfolio_value - total_debt
    
    # Tax cost breakdown (if budget exists, get estimated tax info)
    tax_breakdown = None
    if active_budget:
        try:
            calculator = TaxCalculator()
            tax_info = calculator.calculate_taxes(
                active_budget.annual_income, 
                active_budget.employment_type, 
                'single',  # Default filing status for now
                active_budget.state_code, 
                active_budget.city_code
            )
            tax_breakdown = {
                'annual_income': active_budget.annual_income,
                'monthly_taxes': active_budget.monthly_taxes,
                'tax_details': {
                    'federal_income': tax_info.get('federal_income_tax', 0),
                    'federal_payroll': tax_info.get('payroll_taxes', {}).get('total_payroll', 0) if active_budget.employment_type == 'w2' else 0,
                    'self_employment': tax_info.get('self_employment_tax', 0) if active_budget.employment_type == '1099' else 0,
                    'state_tax': tax_info.get('state_tax_info', {}).get('state_tax', 0),
                    'local_tax': tax_info.get('local_tax_info', {}).get('local_tax', 0),
                    'total_annual': tax_info.get('total_tax_owed', 0)
                },
                'state_name': tax_info.get('state_tax_info', {}).get('state_name', 'No State Tax'),
                'city_name': tax_info.get('local_tax_info', {}).get('city_name', 'No Local Tax'),
                'effective_rate': tax_info.get('effective_tax_rate', 0)
            }
        except Exception as e:
            print(f"Error calculating tax breakdown: {e}")
            tax_breakdown = None

    # Budget vs Actual Analysis
    budget_analysis = None
    if active_budget:
        # Use the monthly transactions we already calculated above
        monthly_expense_transactions = [t for t in monthly_transactions if t.transaction_type == 'expense']
        
        # Calculate actual spending by category
        actual_spending = {}
        for transaction in monthly_expense_transactions:
            category = transaction.category
            if category not in actual_spending:
                actual_spending[category] = 0
            actual_spending[category] += transaction.amount
        
        # Map categories to budget categories (comprehensive mapping)
        category_mapping = {
            'Housing': [
                'Housing', 'Rent', 'Mortgage', 'Property Tax', 'Home Insurance', 
                'Home Maintenance', 'HOA', 'Property Management', 'Renter\'s Insurance'
            ],
            'Food & Dining': [
                'Food & Dining', 'Food', 'Groceries', 'Restaurants', 'Dining', 'Coffee', 
                'Takeout', 'Fast Food', 'Delivery', 'Lunch', 'Dinner', 'Breakfast',
                'Snacks', 'Alcohol', 'Beer', 'Wine', 'Drinks', 'Cafe', 'Bar'
            ],
            'Transportation': [
                'Transportation', 'Gas', 'Gasoline', 'Fuel', 'Car Payment', 
                'Auto Payment', 'Public Transit', 'Car Insurance', 'Auto Insurance',
                'Uber/Lyft', 'Uber', 'Lyft', 'Taxi', 'Car Maintenance', 'Auto Repair',
                'Oil Change', 'Tires', 'Registration', 'Parking', 'Tolls',
                'Bus', 'Train', 'Subway', 'Metro'
            ],
            'Utilities': [
                'Utilities', 'Electric', 'Electricity', 'Gas', 'Natural Gas', 'Water', 
                'Sewer', 'Internet', 'Phone', 'Cell Phone', 'Mobile', 'Cable', 'TV',
                'Trash', 'Garbage', 'Recycling', 'WiFi', 'Broadband'
            ],
            'Healthcare': [
                'Healthcare', 'Medical', 'Doctor', 'Dental', 'Dentist', 'Pharmacy', 
                'Health Insurance', 'Vision', 'Eye Care', 'Prescription', 'Medicine',
                'Hospital', 'Clinic', 'Therapy', 'Mental Health', 'Counseling'
            ],
            'Entertainment': [
                'Entertainment', 'Movies', 'Theater', 'Cinema', 'Games', 'Gaming',
                'Subscriptions', 'Netflix', 'Spotify', 'Streaming', 'Hobbies', 
                'Sports', 'Concert', 'Event', 'Books', 'Music', 'TV', 'Video Games'
            ],
            'Shopping': [
                'Shopping', 'Clothing', 'Clothes', 'Electronics', 'Online Shopping',
                'Amazon', 'Home Goods', 'Furniture', 'Appliances', 'Tools', 'Gifts',
                'Department Store', 'Retail'
            ],
            'Personal Care': [
                'Personal Care', 'Beauty', 'Cosmetics', 'Haircut', 'Hair', 'Salon',
                'Spa', 'Massage', 'Gym', 'Fitness', 'Workout', 'Health Club',
                'Personal Training', 'Yoga'
            ],
            'Education': [
                'Education', 'Tuition', 'School', 'Books', 'Textbooks', 'Courses',
                'Training', 'Online Course', 'Certification', 'Workshop', 'Seminar'
            ],
            'Insurance': [
                'Insurance', 'Life Insurance', 'Disability Insurance', 
                'Umbrella Insurance', 'Home Insurance', 'Renters Insurance'
            ]
        }
        
        # Track which transaction categories were mapped
        mapped_categories = set()
        budget_vs_actual = {}
        for budget_category, expense_categories in category_mapping.items():
            budget_amount = active_budget.get_allocation_by_category(budget_category)
            actual_amount = 0
            
            # Check for exact matches (case-insensitive)
            for transaction_category, amount in actual_spending.items():
                transaction_category_lower = transaction_category.lower()
                
                # Check if transaction category matches any mapped category (case-insensitive)
                for mapped_category in expense_categories:
                    if (transaction_category_lower == mapped_category.lower() or 
                        mapped_category.lower() in transaction_category_lower or
                        transaction_category_lower in mapped_category.lower()):
                        actual_amount += amount
                        mapped_categories.add(transaction_category)
                        break  # Don't double-count if multiple matches
            
            budget_vs_actual[budget_category] = {
                'budget': budget_amount,
                'actual': actual_amount,
                'remaining': budget_amount - actual_amount,
                'percentage_used': (actual_amount / budget_amount * 100) if budget_amount > 0 else 0
            }
        
        # Find unmapped spending (categories that don't fit into budget categories)
        unmapped_spending = {}
        total_unmapped = 0
        for transaction_category, amount in actual_spending.items():
            if transaction_category not in mapped_categories:
                unmapped_spending[transaction_category] = amount
                total_unmapped += amount
        
        budget_analysis = {
            'active_budget': active_budget,
            'budget_vs_actual': budget_vs_actual,
            'total_budgeted': active_budget.get_total_allocated(),
            'total_spent': sum(actual_spending.values()),
            'budget_remaining': active_budget.get_total_allocated() - sum(actual_spending.values()),
            'unmapped_spending': unmapped_spending,
            'total_unmapped': total_unmapped
        }
    
    # Get active accounts for transaction form
    accounts = Account.query.filter_by(is_active=True).order_by(Account.name).all()
    
    return render_template('dashboard.html',
                         # Monthly stats (for top summary cards)
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         monthly_net_balance=monthly_net_balance,
                         monthly_tax_amount=monthly_tax_amount,
                         # All-time stats (for net worth calculation)
                         total_income=total_income,
                         total_expenses=total_expenses,
                         net_balance=net_balance,
                         total_debt=total_debt,
                         total_invested=total_invested,
                         current_portfolio_value=current_portfolio_value,
                         portfolio_gain_loss=portfolio_gain_loss,
                         net_worth=net_worth,
                         transactions=transactions[:10],  # Recent transactions
                         loans=loans,
                         investments=investments,
                         accounts=accounts,
                         budget_analysis=budget_analysis,
                         tax_breakdown=tax_breakdown,
                         date=date)

@app.route('/transactions')
def transactions():
    # Get filter parameters
    category_filter = request.args.get('category', '')
    type_filter = request.args.get('type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Build query
    query = Transaction.query
    
    if category_filter:
        query = query.filter(Transaction.category.ilike(f'%{category_filter}%'))
    if type_filter:
        query = query.filter(Transaction.transaction_type == type_filter)
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Transaction.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Get active accounts for transaction form
    accounts = Account.query.filter_by(is_active=True).order_by(Account.name).all()
    
    return render_template('transactions.html', 
                         transactions=transactions, 
                         categories=categories,
                         accounts=accounts,
                         current_filters={
                             'category': category_filter,
                             'type': type_filter,
                             'start_date': start_date,
                             'end_date': end_date
                         },
                         date=date)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        # Handle category selection (dropdown or custom)
        use_custom = request.form.get('use_custom') == 'on'
        if use_custom:
            category = request.form.get('custom_category', '').strip()
        else:
            category = request.form.get('category', '').strip()
        
        if not category:
            category = 'Other'
        
        # Handle account selection
        account_id = request.form.get('account_id')
        if account_id and account_id != '':
            account_id = int(account_id)
        else:
            account_id = None
        
        transaction = Transaction(
            amount=float(request.form['amount']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            category=category,
            description=request.form.get('description', ''),
            transaction_type=request.form['transaction_type'],
            account_id=account_id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding transaction: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting transaction: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))

@app.route('/loans')
def loans():
    loans = Loan.query.all()
    return render_template('loans.html', loans=loans)

@app.route('/add_loan', methods=['POST'])
def add_loan():
    try:
        loan = Loan(
            name=request.form['name'],
            balance=float(request.form['balance']),
            interest_rate=float(request.form['interest_rate']),
            minimum_payment=float(request.form['minimum_payment']),
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date(),
            loan_type=request.form['loan_type']
        )
        db.session.add(loan)
        db.session.commit()
        flash('Loan added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding loan: {str(e)}', 'error')
    
    return redirect(url_for('loans'))

@app.route('/delete_loan/<int:loan_id>', methods=['POST'])
def delete_loan(loan_id):
    try:
        loan = Loan.query.get_or_404(loan_id)
        db.session.delete(loan)
        db.session.commit()
        flash('Loan deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting loan: {str(e)}', 'error')
    
    return redirect(url_for('loans'))

@app.route('/investments')
def investments():
    investments = Investment.query.all()
    return render_template('investments.html', investments=investments)

@app.route('/add_investment', methods=['POST'])
def add_investment():
    try:
        investment = Investment(
            symbol=request.form['symbol'],
            name=request.form['name'],
            shares=float(request.form['shares']),
            cost_basis=float(request.form['cost_basis']),
            current_price=float(request.form['current_price']),
            investment_type=request.form['investment_type']
        )
        db.session.add(investment)
        db.session.commit()
        flash('Investment added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding investment: {str(e)}', 'error')
    
    return redirect(url_for('investments'))

@app.route('/delete_investment/<int:investment_id>', methods=['POST'])
def delete_investment(investment_id):
    try:
        investment = Investment.query.get_or_404(investment_id)
        db.session.delete(investment)
        db.session.commit()
        flash('Investment deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting investment: {str(e)}', 'error')
    
    return redirect(url_for('investments'))

@app.route('/taxes')
def taxes():
    calculator = TaxCalculator()
    states = calculator.get_state_list()
    return render_template('taxes.html', states=states)

@app.route('/budget')
def budget():
    # Get existing data for budget calculations
    loans = Loan.query.all()
    
    # Calculate total monthly debt payments
    total_monthly_debt = sum(loan.minimum_payment for loan in loans)
    
    # Get recent transactions to analyze spending patterns
    recent_transactions = Transaction.query.filter(
        Transaction.transaction_type == 'expense'
    ).order_by(Transaction.date.desc()).limit(100).all()
    
    # Analyze spending categories
    category_spending = {}
    for transaction in recent_transactions:
        category = transaction.category or 'Other'
        category_spending[category] = category_spending.get(category, 0) + transaction.amount
    
    return render_template('budget.html', 
                         loans=loans,
                         total_monthly_debt=total_monthly_debt,
                         category_spending=category_spending)

@app.route('/calculate_budget', methods=['POST'])
def calculate_budget():
    try:
        # Get form data
        annual_income = float(request.form['annual_income'])
        employment_type = request.form['employment_type']
        filing_status = request.form.get('filing_status', 'single')
        state_code = request.form.get('state_code', '')
        city_code = request.form.get('city_code', '')
        
        # Budget allocations (percentages)
        housing_percent = float(request.form.get('housing_percent', 30)) / 100
        transportation_percent = float(request.form.get('transportation_percent', 15)) / 100
        food_percent = float(request.form.get('food_percent', 12)) / 100
        utilities_percent = float(request.form.get('utilities_percent', 8)) / 100
        healthcare_percent = float(request.form.get('healthcare_percent', 5)) / 100
        entertainment_percent = float(request.form.get('entertainment_percent', 5)) / 100
        savings_percent = float(request.form.get('savings_percent', 20)) / 100
        other_percent = float(request.form.get('other_percent', 5)) / 100
        
        # Calculate taxes
        calculator = TaxCalculator()
        if not state_code:
            state_code = None
        if not city_code:
            city_code = None
            
        tax_info = calculator.calculate_taxes(annual_income, employment_type, filing_status, state_code, city_code)
        
        # Calculate take-home income
        monthly_gross = annual_income / 12
        monthly_taxes = tax_info['total_tax_owed'] / 12
        monthly_net = monthly_gross - monthly_taxes
        
        # Get loan data
        loans = Loan.query.all()
        total_monthly_debt = sum(loan.minimum_payment for loan in loans)
        
        # Calculate available for allocation after debt payments
        available_for_budget = monthly_net - total_monthly_debt
        
        # Calculate budget allocations
        budget_breakdown = {
            'housing': available_for_budget * housing_percent,
            'transportation': available_for_budget * transportation_percent,
            'food': available_for_budget * food_percent,
            'utilities': available_for_budget * utilities_percent,
            'healthcare': available_for_budget * healthcare_percent,
            'entertainment': available_for_budget * entertainment_percent,
            'savings': available_for_budget * savings_percent,
            'other': available_for_budget * other_percent
        }
        
        # Prepare results
        budget_result = {
            'annual_income': annual_income,
            'monthly_gross': monthly_gross,
            'monthly_taxes': monthly_taxes,
            'monthly_net': monthly_net,
            'monthly_debt': total_monthly_debt,
            'available_for_budget': available_for_budget,
            'budget_breakdown': budget_breakdown,
            'tax_info': tax_info,
            'loans': loans,
            'percentages': {
                'housing': housing_percent * 100,
                'transportation': transportation_percent * 100,
                'food': food_percent * 100,
                'utilities': utilities_percent * 100,
                'healthcare': healthcare_percent * 100,
                'entertainment': entertainment_percent * 100,
                'savings': savings_percent * 100,
                'other': other_percent * 100
            }
        }
        
        # Get states and cities for form
        states = calculator.get_state_list()
        cities = calculator.get_cities_for_state(state_code) if state_code else []
        
        return render_template('budget.html',
                             budget_result=budget_result,
                             annual_income=annual_income,
                             employment_type=employment_type,
                             filing_status=filing_status,
                             selected_state=state_code,
                             selected_city=city_code,
                             states=states,
                             cities=cities,
                             loans=loans,
                             total_monthly_debt=total_monthly_debt)
                             
    except Exception as e:
        flash(f'Error calculating budget: {str(e)}', 'error')
        return redirect(url_for('budget'))

@app.route('/save_budget', methods=['POST'])
def save_budget():
    try:
        # Get form data
        budget_name = request.form.get('budget_name', 'My Budget Plan')
        annual_income = float(request.form['annual_income'])
        employment_type = request.form['employment_type']
        state_code = request.form.get('state_code') or None
        city_code = request.form.get('city_code') or None
        
        # Get allocation amounts (not percentages)
        housing = float(request.form.get('housing', 0))
        food = float(request.form.get('food', 0))
        transportation = float(request.form.get('transportation', 0))
        utilities = float(request.form.get('utilities', 0))
        healthcare = float(request.form.get('healthcare', 0))
        insurance = float(request.form.get('insurance', 0))
        entertainment = float(request.form.get('entertainment', 0))
        personal_care = float(request.form.get('personal_care', 0))
        shopping = float(request.form.get('shopping', 0))
        education = float(request.form.get('education', 0))
        savings = float(request.form.get('savings', 0))
        emergency_fund = float(request.form.get('emergency_fund', 0))
        retirement = float(request.form.get('retirement', 0))
        other = float(request.form.get('other', 0))
        
        # Calculate derived values
        monthly_take_home = float(request.form.get('monthly_take_home', 0))
        monthly_taxes = float(request.form.get('monthly_taxes', 0))
        monthly_loan_payments = float(request.form.get('monthly_loan_payments', 0))
        monthly_available = float(request.form.get('monthly_available', 0))
        
        # Deactivate previous active budgets
        Budget.query.filter_by(is_active=True).update({'is_active': False})
        
        # Create new budget
        budget = Budget(
            name=budget_name,
            annual_income=annual_income,
            employment_type=employment_type,
            state_code=state_code,
            city_code=city_code,
            housing=housing,
            food=food,
            transportation=transportation,
            utilities=utilities,
            healthcare=healthcare,
            insurance=insurance,
            entertainment=entertainment,
            personal_care=personal_care,
            shopping=shopping,
            education=education,
            savings=savings,
            emergency_fund=emergency_fund,
            retirement=retirement,
            other=other,
            monthly_take_home=monthly_take_home,
            monthly_taxes=monthly_taxes,
            monthly_loan_payments=monthly_loan_payments,
            monthly_available=monthly_available,
            is_active=True
        )
        
        db.session.add(budget)
        db.session.commit()
        
        flash('Budget plan saved successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Error saving budget: {str(e)}', 'error')
        return redirect(url_for('budget'))

@app.route('/calculate_taxes', methods=['POST'])
def calculate_taxes():
    try:
        annual_income = float(request.form['annual_income'])
        employment_type = request.form['employment_type']
        filing_status = request.form.get('filing_status', 'single')
        state_code = request.form.get('state_code', '')
        city_code = request.form.get('city_code', '')
        
        # Convert empty strings to None
        if not state_code:
            state_code = None
        if not city_code:
            city_code = None
            
        calculator = TaxCalculator()
        tax_info = calculator.calculate_taxes(annual_income, employment_type, filing_status, state_code, city_code)
        
        # Get lists for form dropdowns
        states = calculator.get_state_list()
        cities = calculator.get_cities_for_state(state_code) if state_code else []
        
        return render_template('taxes.html', 
                             tax_info=tax_info, 
                             annual_income=annual_income, 
                             employment_type=employment_type,
                             filing_status=filing_status,
                             selected_state=state_code,
                             selected_city=city_code,
                             states=states,
                             cities=cities)
    except Exception as e:
        flash(f'Error calculating taxes: {str(e)}', 'error')
        return redirect(url_for('taxes'))

@app.route('/api/chart_data')
def chart_data():
    chart_type = request.args.get('type', 'spending_by_category')
    
    if chart_type == 'spending_by_category':
        # Get spending by category
        categories = db.session.query(
            Transaction.category,
            db.func.sum(Transaction.amount)
        ).filter(Transaction.transaction_type == 'expense').group_by(Transaction.category).all()
        
        return jsonify({
            'labels': [cat[0] for cat in categories],
            'data': [float(cat[1]) for cat in categories]
        })
    
    elif chart_type == 'income_vs_expenses':
        # Monthly income vs expenses
        monthly_data = db.session.query(
            db.func.strftime('%Y-%m', Transaction.date).label('month'),
            Transaction.transaction_type,
            db.func.sum(Transaction.amount)
        ).group_by('month', Transaction.transaction_type).all()
        
        months = []
        income_data = []
        expense_data = []
        
        for month, trans_type, amount in monthly_data:
            if month not in months:
                months.append(month)
                income_data.append(0)
                expense_data.append(0)
            
            idx = months.index(month)
            if trans_type == 'income':
                income_data[idx] = float(amount)
            else:
                expense_data[idx] = float(amount)
        
        return jsonify({
            'labels': months,
            'income': income_data,
            'expenses': expense_data
        })
    
    return jsonify({'error': 'Invalid chart type'})

@app.route('/api/cities/<state_code>')
def get_cities_for_state(state_code):
    calculator = TaxCalculator()
    cities = calculator.get_cities_for_state(state_code)
    return jsonify(cities)

@app.route('/api/category_mapping')
def get_category_mapping():
    """API endpoint to view current category mapping for debugging"""
    category_mapping = {
        'Housing': [
            'Housing', 'Rent', 'Mortgage', 'Property Tax', 'Home Insurance', 
            'Home Maintenance', 'HOA', 'Property Management', 'Renter\'s Insurance'
        ],
        'Food & Dining': [
            'Food & Dining', 'Food', 'Groceries', 'Restaurants', 'Dining', 'Coffee', 
            'Takeout', 'Fast Food', 'Delivery', 'Lunch', 'Dinner', 'Breakfast',
            'Snacks', 'Alcohol', 'Beer', 'Wine', 'Drinks', 'Cafe', 'Bar'
        ],
        'Transportation': [
            'Transportation', 'Gas', 'Gasoline', 'Fuel', 'Car Payment', 
            'Auto Payment', 'Public Transit', 'Car Insurance', 'Auto Insurance',
            'Uber/Lyft', 'Uber', 'Lyft', 'Taxi', 'Car Maintenance', 'Auto Repair',
            'Oil Change', 'Tires', 'Registration', 'Parking', 'Tolls',
            'Bus', 'Train', 'Subway', 'Metro'
        ],
        'Utilities': [
            'Utilities', 'Electric', 'Electricity', 'Gas', 'Natural Gas', 'Water', 
            'Sewer', 'Internet', 'Phone', 'Cell Phone', 'Mobile', 'Cable', 'TV',
            'Trash', 'Garbage', 'Recycling', 'WiFi', 'Broadband'
        ],
        'Healthcare': [
            'Healthcare', 'Medical', 'Doctor', 'Dental', 'Dentist', 'Pharmacy', 
            'Health Insurance', 'Vision', 'Eye Care', 'Prescription', 'Medicine',
            'Hospital', 'Clinic', 'Therapy', 'Mental Health', 'Counseling'
        ],
        'Entertainment': [
            'Entertainment', 'Movies', 'Theater', 'Cinema', 'Games', 'Gaming',
            'Subscriptions', 'Netflix', 'Spotify', 'Streaming', 'Hobbies', 
            'Sports', 'Concert', 'Event', 'Books', 'Music', 'TV', 'Video Games'
        ],
        'Shopping': [
            'Shopping', 'Clothing', 'Clothes', 'Electronics', 'Online Shopping',
            'Amazon', 'Home Goods', 'Furniture', 'Appliances', 'Tools', 'Gifts',
            'Department Store', 'Retail'
        ],
        'Personal Care': [
            'Personal Care', 'Beauty', 'Cosmetics', 'Haircut', 'Hair', 'Salon',
            'Spa', 'Massage', 'Gym', 'Fitness', 'Workout', 'Health Club',
            'Personal Training', 'Yoga'
        ],
        'Education': [
            'Education', 'Tuition', 'School', 'Books', 'Textbooks', 'Courses',
            'Training', 'Online Course', 'Certification', 'Workshop', 'Seminar'
        ],
        'Insurance': [
            'Insurance', 'Life Insurance', 'Disability Insurance', 
            'Umbrella Insurance', 'Home Insurance', 'Renters Insurance'
        ]
    }
    
    return jsonify(category_mapping)

@app.route('/api/transaction_categories')
def get_transaction_categories():
    """API endpoint to view all current transaction categories"""
    categories = db.session.query(
        Transaction.category,
        db.func.count(Transaction.id).label('count'),
        db.func.sum(Transaction.amount).label('total')
    ).filter(Transaction.transaction_type == 'expense').group_by(Transaction.category).all()
    
    result = []
    for cat, count, total in categories:
        result.append({
            'category': cat,
            'transaction_count': count,
            'total_amount': float(total)
        })
    
    return jsonify(result)

# Account Management Routes
@app.route('/accounts')
def accounts():
    accounts = Account.query.filter_by(is_active=True).order_by(Account.name).all()
    
    # Calculate total balances by account type
    checking_total = sum(acc.current_balance for acc in accounts if acc.account_type == 'checking')
    savings_total = sum(acc.current_balance for acc in accounts if acc.account_type == 'savings')
    credit_total = sum(acc.current_balance for acc in accounts if acc.account_type == 'credit')
    investment_total = sum(acc.current_balance for acc in accounts if acc.account_type == 'investment')
    cash_total = sum(acc.current_balance for acc in accounts if acc.account_type == 'cash')
    
    # Calculate reconciliation vs transactions
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    calculated_net = total_income - total_expenses
    
    # Account-based net worth
    account_net_worth = Account.get_net_worth()
    
    # Difference between transaction-based and account-based calculations
    reconciliation_difference = account_net_worth - calculated_net
    
    # Get unbalanced accounts
    unbalanced_accounts = [acc for acc in accounts if not acc.is_balanced()]
    
    return render_template('accounts.html',
                         accounts=accounts,
                         checking_total=checking_total,
                         savings_total=savings_total,
                         credit_total=credit_total,
                         investment_total=investment_total,
                         cash_total=cash_total,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         calculated_net=calculated_net,
                         account_net_worth=account_net_worth,
                         reconciliation_difference=reconciliation_difference,
                         unbalanced_accounts=unbalanced_accounts)

@app.route('/add_account', methods=['POST'])
def add_account():
    try:
        name = request.form['name']
        account_type = request.form['account_type']
        bank_name = request.form.get('bank_name', '')
        account_number = request.form.get('account_number', '')
        current_balance = float(request.form['current_balance'])
        initial_balance = float(request.form.get('initial_balance', current_balance))
        
        account = Account(
            name=name,
            account_type=account_type,
            bank_name=bank_name,
            account_number=account_number,
            current_balance=current_balance,
            initial_balance=initial_balance
        )
        
        db.session.add(account)
        db.session.commit()
        
        flash(f'Account "{name}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding account: {str(e)}', 'error')
    
    return redirect(url_for('accounts'))

@app.route('/update_account_balance', methods=['POST'])
def update_account_balance():
    try:
        account_id = int(request.form['account_id'])
        new_balance = float(request.form['current_balance'])
        
        account = Account.query.get_or_404(account_id)
        account.current_balance = new_balance
        account.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Balance updated for "{account.name}"', 'success')
    except Exception as e:
        flash(f'Error updating balance: {str(e)}', 'error')
    
    return redirect(url_for('accounts'))

@app.route('/delete_account/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    try:
        account = Account.query.get_or_404(account_id)
        
        # Check if account has transactions
        if account.transactions:
            # Soft delete - mark as inactive instead of deleting
            account.is_active = False
            flash(f'Account "{account.name}" has been deactivated (has transaction history)', 'warning')
        else:
            # Hard delete if no transactions
            db.session.delete(account)
            flash(f'Account "{account.name}" has been deleted', 'success')
        
        db.session.commit()
        
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'error')
    
    return redirect(url_for('accounts'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
