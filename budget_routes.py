from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transactions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            transaction_type TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create budgets table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            budget_amount REAL NOT NULL,
            time_period TEXT DEFAULT 'monthly',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Budget routes
@app.route('/budget')
def budget_form():
    """Display budget setting form"""
    return render_template('budget.html')

@app.route('/add_budget', methods=['POST'])
def add_budget():
    """Add a new budget entry"""
    try:
        category = request.form['category']
        budget_amount = float(request.form['budget_amount'])
        user_id = 1  # For demo purposes, using user_id = 1
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO budgets (user_id, category, budget_amount) VALUES (?, ?, ?)',
            (user_id, category, budget_amount)
        )
        conn.commit()
        conn.close()
        
        flash('Budget added successfully!', 'success')
        return redirect(url_for('budget_progress'))
    except Exception as e:
        flash(f'Error adding budget: {str(e)}', 'error')
        return redirect(url_for('budget_form'))

@app.route('/budget_progress')
def budget_progress():
    """Display budget progress with progress bars"""
    conn = get_db_connection()
    
    # Get all budgets for user
    budgets = conn.execute(
        'SELECT * FROM budgets WHERE user_id = ?', (1,)
    ).fetchall()
    
    # Get current month's transactions
    current_month = datetime.now().strftime('%Y-%m')
    transactions = conn.execute(
        '''SELECT category, SUM(amount) as total_spent 
           FROM transactions 
           WHERE user_id = ? AND date LIKE ? AND transaction_type = 'expense'
           GROUP BY category''',
        (1, f'{current_month}%')
    ).fetchall()
    
    # Create spending dictionary
    spending = {row['category']: row['total_spent'] for row in transactions}
    
    # Calculate progress for each budget
    budget_progress = []
    for budget in budgets:
        spent = spending.get(budget['category'], 0)
        percentage = (spent / budget['budget_amount']) * 100 if budget['budget_amount'] > 0 else 0
        
        # Determine color based on percentage
        if percentage < 70:
            color = 'success'
        elif percentage < 90:
            color = 'warning'
        else:
            color = 'danger'
        
        budget_progress.append({
            'category': budget['category'],
            'budget_amount': budget['budget_amount'],
            'spent': spent,
            'remaining': budget['budget_amount'] - spent,
            'percentage': min(percentage, 100),
            'color': color
        })
    
    conn.close()
    return render_template('budget_progress.html', budgets=budget_progress)

@app.route('/add_sample_data')
def add_sample_data():
    """Add sample transaction data for demonstration"""
    conn = get_db_connection()
    
    # Sample transactions for current month
    sample_transactions = [
        (1, 150.00, 'Groceries', 'Weekly grocery shopping', 'expense'),
        (1, 75.50, 'Entertainment', 'Movie tickets', 'expense'),
        (1, 200.00, 'Rent', 'Monthly rent payment', 'expense'),
        (1, 45.00, 'Transportation', 'Gas and parking', 'expense'),
        (1, 3000.00, 'Salary', 'Monthly salary', 'income'),
        (1, 120.00, 'Groceries', 'Additional groceries', 'expense'),
        (1, 50.00, 'Entertainment', 'Dining out', 'expense'),
    ]
    
    for transaction in sample_transactions:
        conn.execute(
            '''INSERT INTO transactions (user_id, amount, category, description, transaction_type)
               VALUES (?, ?, ?, ?, ?)''',
            transaction
        )
    
    conn.commit()
    conn.close()
    
    flash('Sample data added successfully!', 'success')
    return redirect(url_for('budget_progress'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
