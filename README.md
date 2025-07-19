# Personal Finance Tracker

A comprehensive personal finance management web application built with Python Flask. Track your income, expenses, investments, loans, and calculate tax obligations all in one place.

## Features

### 📊 Dashboard
- Real-time overview of your financial health
- Net worth calculation
- Visual charts for spending analysis
- Quick action buttons for common tasks

### 💰 Transaction Management
- Add income and expense transactions
- Categorize transactions for better organization
- Filter by date range, category, or type
- View detailed transaction history

### 💳 Loans & Credit Cards
- Track all your debts in one place
- Monitor credit card utilization
- Calculate payoff timelines
- Debt avalanche and snowball strategies

### 📈 Investment Portfolio
- Track stocks, ETFs, mutual funds, crypto, and more
- Real-time gain/loss calculations
- Portfolio allocation visualization
- Performance metrics and analytics

### 🧮 Tax Calculator
- Estimate federal tax obligations
- Support for W-2 employees and 1099 contractors
- Calculate quarterly payment estimates
- Tax planning recommendations

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Bootstrap Icons

## Installation

1. **Clone or download the project**
   ```bash
   cd flask_finance
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:5000` in your web browser.

## Project Structure

```
flask_finance/
├── app.py                 # Main Flask application
├── database.py           # Database configuration
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── models/              # Database models
│   ├── transaction.py   # Transaction model
│   ├── loan.py         # Loan/credit card model
│   └── investment.py   # Investment model
├── templates/           # HTML templates
│   ├── base.html       # Base template with navigation
│   ├── dashboard.html  # Dashboard page
│   ├── transactions.html # Transaction management
│   ├── loans.html      # Loan tracking
│   ├── investments.html # Investment portfolio
│   └── taxes.html      # Tax calculator
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── main.js     # JavaScript functionality
├── utils/              # Utility modules
│   └── tax_calculator.py # Tax calculation logic
└── db/                 # Database files (auto-created)
    └── finances.db     # SQLite database
```

## Usage Guide

### Adding Transactions
1. Go to the Transactions page
2. Click "Add Transaction"
3. Fill in amount, date, category, and type (income/expense)
4. Optionally add a description
5. Click "Add Transaction"

### Tracking Loans
1. Navigate to Loans & Credit page
2. Click "Add Loan/Credit Card"
3. Enter loan details including balance, interest rate, and minimum payment
4. View payoff strategies and timelines

### Managing Investments
1. Go to Investments page
2. Click "Add Investment"
3. Enter symbol, shares, cost basis, and current price
4. Track portfolio performance and allocation

### Tax Calculations
1. Visit the Tax Calculator page
2. Enter your annual income
3. Select employment type (W-2 or 1099)
4. View detailed tax breakdown and recommendations

## Features in Detail

### Dashboard Metrics
- **Total Income**: Sum of all income transactions
- **Total Expenses**: Sum of all expense transactions
- **Net Balance**: Income minus expenses
- **Net Worth**: Balance plus investments minus debts

### Smart Categorization
The app suggests categories based on transaction type and learns from your input patterns.

### Investment Tracking
- Automatic gain/loss calculations
- Portfolio diversification metrics
- Performance comparisons

### Tax Planning Tools
- 2024 federal tax brackets
- Self-employment tax calculations
- Quarterly payment estimates
- Withholding recommendations

## Dark Mode
Toggle between light and dark themes using the moon/sun icon in the navigation bar. Your preference is saved locally.

## Data Storage
All data is stored locally in an SQLite database. No data is sent to external servers, ensuring your financial information remains private.

## Customization

### Adding New Categories
Transaction categories are automatically learned from user input, but you can modify the suggested categories in the JavaScript file.

### Modifying Tax Brackets
Update the tax brackets in `utils/tax_calculator.py` for different tax years or jurisdictions.

### Styling Changes
Customize the appearance by modifying `static/css/style.css`.

## Security Notes

1. **Change the secret key** in production:
   ```python
   app.config['SECRET_KEY'] = 'your-secure-random-key-here'
   ```

2. **Database security**: The SQLite database is stored locally. For production use, consider PostgreSQL or MySQL with proper access controls.

3. **HTTPS**: Use HTTPS in production to encrypt data transmission.

## Troubleshooting

### Database Issues
If you encounter database errors, delete the `db/finances.db` file and restart the app to recreate the database.

### Missing Dependencies
Ensure all packages are installed:
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

## Future Enhancements

- [ ] CSV import/export functionality
- [ ] Multi-user support with authentication
- [ ] Budget planning and tracking
- [ ] Bill reminders and notifications
- [ ] Integration with financial APIs
- [ ] Mobile responsive improvements
- [ ] Backup and restore functionality

## Contributing

This is a personal project template. Feel free to fork and modify according to your needs.

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please check the troubleshooting section above or create an issue in the project repository.

---

**Disclaimer**: This application is for personal financial tracking and educational purposes. Tax calculations are estimates based on 2024 federal tax brackets. Always consult with a qualified tax professional for official tax advice.
