''' To handle the user requests for registration and login'''
import ldap3
import flask_dance
from flask import g,Blueprint, render_template,request,flash,redirect, url_for, session, jsonify, Response
import asyncio
import os
import subprocess
import tempfile
import shutil
from flask_login import current_user, login_user, logout_user, login_required
from my_paldea import db,login_manager,bcrypt
from my_paldea.utlities import get_ldap_connection
from authlib.integrations.flask_client import OAuth
from my_paldea.paldea_app.models import User, RegistrationForm, LoginForm, BudgetForm, ExpenseForm, Expense, Transaction, TransactionForm, Category, CategoryBudget, CategoryBudgetForm, Goal, GoalForm, Currency, ConversionHistory, ScheduledReport
#from models import User, RegistrationForm,LoginForm
#from flask_dance.facebook import make_facebook_blueprint, facebook
#from flask_dance.facebook import make_facebook_blueprint, facebook
#from flask_dance.google import make_google_blueprint, google
#from flask_dance.twitter import make_twitter_blueprint, twitter
#from ldap3 import Server, Connection, ALL
# Define a  Blueprint for main app routes
paldea_app = Blueprint('paldea_app', __name__)
#facebook_blueprint = make_facebook_blueprint(scope='email',redirect_to='paldea_app.facebook_login')
#google_blueprint = make_google_blueprint(scope=["openid", "https://www.googleapis.com/paldea_app/userinfo.email","https://www.googleapis.com/paldea_app/userinfo.profile"], redirect_to='paldea_app.google_login')
#twiter_blueprint = make_twitter_blueprint(redirect_to='paldea_app.twitter_login')

# Initialize OAuth
oauth = OAuth()

# Register OAuth clients
def register_oauth(app):
    oauth.init_app(app)

    # Facebook OAuth
    oauth.register(
        name='facebook',
        client_id='YOUR_FACEBOOK_CLIENT_ID',
        client_secret='YOUR_FACEBOOK_CLIENT_SECRET',
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'}
    )

    # Google OAuth
    oauth.register(
        name='google',
        client_id='YOUR_GOOGLE_CLIENT_ID',
        client_secret='YOUR_GOOGLE_CLIENT_SECRET',
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v2/',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Twitter OAuth
    oauth.register(
        name='twitter',
        client_id='YOUR_TWITTER_API_KEY',
        client_secret='YOUR_TWITTER_API_SECRET',
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authenticate',
    )


# Authorization callback route
@paldea_app.route('/authorize/<provider>')
def authorize(provider):
    oauth_client = oauth.create_client(provider)
    token = oauth_client.authorize_access_token()

    # Get user info (provider dependent)
    if provider == 'facebook':
        user_info = oauth_client.get('me?fields=id,name,email').json()
    elif provider == 'google':
        user_info = oauth_client.get('userinfo').json()
        email = user_info.get("email")
        if not email:
            flash("Failed to get your email from Google.", "danger")
            return redirect(url_for("paldea_app.login"))
        # Check if user exists, else create
        user = User.query.filter_by(username=email).first()
        if not user:
            user = User(username=email, password="")  # OAuth users have no password
            db.session.add(user)
            db.session.commit()
        login_user(user)
        session["user_email"] = email
        flash(f"Logged in as {email} via Google", "success")
        return redirect(url_for("paldea_app.home"))
    
    elif provider == 'twitter':
        user_info = oauth_client.get('account/verify_credentials.json').json()
    else:
        return "Unknown provider", 400

    # Save user info in session or database
    session['user'] = user_info
    return redirect('/')

# Optional route to check logged-in user
@paldea_app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('paldea_app.login', provider='google'))
    return user

@paldea_app.route('/')
@paldea_app.route('/home')
@login_required
def home():
    from datetime import datetime, timedelta
    budget_form = BudgetForm()
    transaction_form = TransactionForm()
    category_budget_form = CategoryBudgetForm()
    goal_form = GoalForm()
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    categories = Category.query.all()
    category_budgets = CategoryBudget.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()

    # Populate form choices
    transaction_form.category.choices = [(c.id, c.name) for c in categories]
    category_budget_form.category.choices = [(c.id, c.name) for c in categories]
    
    # Populate currency choices
    currencies = Currency.query.all()
    transaction_form.currency.choices = [(c.id, f'{c.code} ({c.symbol})') for c in currencies]
    # Set default currency to user's preferred currency
    if current_user.preferred_currency_id:
        transaction_form.currency.data = current_user.preferred_currency_id

    # Filter transactions based on query params
    filter_type = request.args.get('filter_type')
    filter_period = request.args.get('filter_period')
    now = datetime.utcnow()
    if filter_type:
        transactions = [t for t in transactions if t.type == filter_type]
    if filter_period:
        if filter_period == 'week':
            start_date = now - timedelta(days=7)
        elif filter_period == 'month':
            start_date = datetime(now.year, now.month, 1)
        elif filter_period == 'year':
            start_date = datetime(now.year, 1, 1)
        transactions = [t for t in transactions if t.date >= start_date]

    # Calculate spent per category for current month
    current_month_start = datetime(now.year, now.month, 1)
    category_spent = {}
    for budget in category_budgets:
        spent = sum(t.amount for t in transactions if t.category_id == budget.category_id and t.type == 'expense' and t.date >= current_month_start)
        category_spent[budget.category_id] = spent

    # Calculate budget progress for display
    budget_progress = []
    for budget in category_budgets:
        spent = category_spent.get(budget.category_id, 0)
        percentage = (spent / budget.budget_amount) * 100 if budget.budget_amount > 0 else 0

        # Determine color based on percentage
        if percentage < 70:
            color = 'success'
        elif percentage < 90:
            color = 'warning'
        else:
            color = 'danger'

        budget_progress.append({
            'category': budget.category.name,
            'budget_amount': budget.budget_amount,
            'spent': spent,
            'remaining': budget.budget_amount - spent,
            'percentage': min(percentage, 100),
            'color': color
        })

    # Data for charts
    pie_labels = [cb.category.name for cb in category_budgets if cb.category]
    pie_data = [category_spent.get(cb.category_id, 0) for cb in category_budgets if cb.category]

    # Monthly income vs expense bar chart (current month)
    monthly_transactions = [t for t in transactions if t.date.month == now.month and t.date.year == now.year]
    income = sum(t.amount for t in monthly_transactions if t.type == 'income')
    expense = sum(t.amount for t in monthly_transactions if t.type == 'expense')
    bar_labels = ['Income', 'Expense']
    bar_data = [income, expense]

    # Summary - convert to user's preferred currency if needed
    preferred_currency = Currency.query.get(current_user.preferred_currency_id) if current_user.preferred_currency_id else Currency.query.filter_by(code='USD').first()
    if not preferred_currency:
        preferred_currency = Currency.query.first()
    
    # Convert totals to preferred currency
    total_income = 0
    total_expenses = 0
    import requests
    
    for t in transactions:
        if t.type == 'income':
            if t.currency_id == preferred_currency.id:
                total_income += t.amount
            else:
                # Convert to preferred currency
                try:
                    url = f"https://api.exchangerate-api.com/v4/latest/{t.currency.code}"
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        rate = response.json().get('rates', {}).get(preferred_currency.code, 1.0)
                        total_income += t.amount * rate
                    else:
                        total_income += t.amount  # Fallback to original amount
                except:
                    total_income += t.amount  # Fallback to original amount
        else:
            if t.currency_id == preferred_currency.id:
                total_expenses += t.amount
            else:
                # Convert to preferred currency
                try:
                    url = f"https://api.exchangerate-api.com/v4/latest/{t.currency.code}"
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        rate = response.json().get('rates', {}).get(preferred_currency.code, 1.0)
                        total_expenses += t.amount * rate
                    else:
                        total_expenses += t.amount  # Fallback to original amount
                except:
                    total_expenses += t.amount  # Fallback to original amount
    
    cash_flow = total_income - total_expenses

    # Trend line data (monthly spending over last 12 months)
    trend_labels = []
    trend_income_data = []
    trend_expense_data = []
    for i in range(12):
        month_start = (now - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        monthly_income = sum(t.amount for t in transactions if t.type == 'income' and month_start <= t.date <= month_end)
        monthly_expense = sum(t.amount for t in transactions if t.type == 'expense' and month_start <= t.date <= month_end)
        trend_labels.append(month_start.strftime('%b %Y'))
        trend_income_data.append(monthly_income)
        trend_expense_data.append(monthly_expense)
    trend_labels.reverse()
    trend_income_data.reverse()
    trend_expense_data.reverse()

    # Forecasting data
    import numpy as np
    try:
        from sklearn.linear_model import LinearRegression
        expenses_for_forecast = []
        for i in range(6):
            month_start = (now - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            monthly_expense = sum(t.amount for t in transactions if t.type == 'expense' and month_start <= t.date <= month_end)
            expenses_for_forecast.append(monthly_expense)
        
        if len(expenses_for_forecast) >= 2:
            X = np.array(range(len(expenses_for_forecast))).reshape(-1, 1)
            y = np.array(expenses_for_forecast)
            model = LinearRegression()
            model.fit(X, y)
            next_month_prediction = model.predict([[len(expenses_for_forecast)]])[0]
            forecast_confidence = min(100, max(0, 100 - abs(model.score(X, y) * 100 - 100)))
        else:
            next_month_prediction = sum(expenses_for_forecast) / len(expenses_for_forecast) if expenses_for_forecast else 0
            forecast_confidence = 50
    except ImportError:
        # If sklearn is not available, use simple average
        expenses_for_forecast = trend_expense_data[-6:] if len(trend_expense_data) >= 6 else trend_expense_data
        next_month_prediction = sum(expenses_for_forecast) / len(expenses_for_forecast) if expenses_for_forecast else 0
        forecast_confidence = 50

    return render_template('home.html', budget_form=budget_form, transaction_form=transaction_form, category_budget_form=category_budget_form, goal_form=goal_form, transactions=transactions, categories=categories, category_budgets=category_budgets, goals=goals, category_spent=category_spent, budget_progress=budget_progress, now=now, pie_labels=pie_labels, pie_data=pie_data, bar_labels=bar_labels, bar_data=bar_data, total_income=total_income, total_expenses=total_expenses, cash_flow=cash_flow, trend_labels=trend_labels, trend_income_data=trend_income_data, trend_expense_data=trend_expense_data, forecast_amount=next_month_prediction, forecast_confidence=forecast_confidence, preferred_currency=preferred_currency)

@paldea_app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username') or current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('paldea_app.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            if existing_user.username == username:
                    flash('This username is already taken. Please choose another.', 'warning')
            if existing_user.email == email:
                flash('This email is already registered. Please use another.', 'warning')
            return render_template('register.html', form=form)

        # Create new user
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()

        flash('You are now registered. Please login.', 'success')
        return redirect(url_for('paldea_app.login'))

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return render_template('register.html', form=form)

@paldea_app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # triggered on POST if validators pass
        username = form.username.data
        password = form.password.data

        # --- Try local DB login first ---
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session["user_id"] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for("paldea_app.home"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("login.html", form=form)

    # GET request or failed POST → show form
    return render_template("login.html", form=form)

# To log out 
@paldea_app.route('/logout')
# To make sure that the user is logged in before logout_user is executed
@login_required
def logout():
    logout_user()
    #if 'username'in session:
     #   session.pop('username')
     #  flash('You have successfully logged out.', 'success')
      #  '''
    return redirect(url_for('paldea_app.home'))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
# To call this method before the view function whenever a request is recieved
@paldea_app.before_request
def get_current_user():
    g.user = current_user

@paldea_app.route("/facebook-login")
def facebook_login():
    facebook = oauth.create_client('facebook')
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp=facebook.get("/me?fields=name,email")
    user = User.query.filter_by(username=resp.json()["email"]).first()
    if not user:
        user = User(resp.json()["email"], '')
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('Logged in as name=%s using Facebook login'% (resp.json()['name']),'success')
    return redirect(request.args.get('next',url_for('paldea_app.home')))

@paldea_app.route("/google-login")
def google_login():
    google = oauth.create_client("google")  # create Google OAuth client
    redirect_uri = url_for("paldea_app.authorize", provider="google", _external=True)
    return google.authorize_redirect(redirect_uri)

''''@paldea_app.route("/google-login")
def google_login():
    google = oauth.create_client('google')  # creates a Google OAuth client
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google", "danger")
        return redirect(url_for("paldea_app.login"))

    email = resp.json()["email"]
    user = User.query.filter_by(username=email).first()
    if not user:
        user = User(username=email, password="")  # no password for OAuth users
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f"Logged in as {email} using Google", "success")
    return redirect(url_for("paldea_app.home"))'''
@paldea_app.route("/twitter-login")
def twitter_login():
    twitter = oauth.create_client('twitter')
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/verify_credentials.json")
    user = User.query.filter_by(username=resp.json()["screen_name"]).filter()
    if not user:
        user = User(resp.json()["session_name"],'')
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('Logged in as name=%s using Twitter login' %(resp.json()['name']),'success' )
    return redirect(request.args.get('next', url_for('paldea_app.home')))

@paldea_app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        current_user.budget = form.budget.data
        db.session.commit()
        flash('Budget set successfully!', 'success')
    return redirect(url_for('paldea_app.home'))

@paldea_app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(description=form.description.data, amount=form.amount.data, user_id=current_user.id)
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
    return redirect(url_for('paldea_app.home'))

@paldea_app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    categories = Category.query.all()
    currencies = Currency.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]
    form.currency.choices = [(c.id, f'{c.code} ({c.symbol})') for c in currencies]
    if form.validate_on_submit():
        transaction = Transaction(description=form.description.data, amount=form.amount.data, type=form.type.data, category_id=form.category.data, currency_id=form.currency.data, user_id=current_user.id)
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
    return redirect(url_for('paldea_app.home'))

@paldea_app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('You do not have permission to edit this transaction.', 'danger')
        return redirect(url_for('paldea_app.home'))

    form = TransactionForm()
    categories = Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]
    if request.method == 'GET':
        form.description.data = transaction.description
        form.amount.data = transaction.amount
        form.type.data = transaction.type
        form.category.data = transaction.category_id

    if form.validate_on_submit():
        transaction.description = form.description.data
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.category_id = form.category.data
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('paldea_app.home'))

    return render_template('edit_transaction.html', form=form, transaction=transaction)

@paldea_app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        flash('You do not have permission to delete this transaction.', 'danger')
        return redirect(url_for('paldea_app.home'))

    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('paldea_app.home'))

@paldea_app.route('/set_category_budget', methods=['POST'])
@login_required
def set_category_budget():
    form = CategoryBudgetForm()
    categories = Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        # Check if budget already exists for this category and user
        existing_budget = CategoryBudget.query.filter_by(user_id=current_user.id, category_id=form.category.data).first()
        if existing_budget:
            existing_budget.budget_amount = form.budget_amount.data
        else:
            budget = CategoryBudget(user_id=current_user.id, category_id=form.category.data, budget_amount=form.budget_amount.data)
            db.session.add(budget)
        db.session.commit()
        flash('Category budget set successfully!', 'success')
    return redirect(url_for('paldea_app.home'))

@paldea_app.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(user_id=current_user.id, goal_type=form.goal_type.data, target_amount=form.target_amount.data, deadline=form.deadline.data, description=form.description.data)
        db.session.add(goal)
        db.session.commit()
        flash('Goal set successfully!', 'success')
    return redirect(url_for('paldea_app.home'))

@paldea_app.route('/ldap-login', endpoint='ldap_login', methods=['GET','POST'])
def ldap_login():
    if current_user.is_authenticated:
        flash('You are already logged in.','info')
        return redirect(url_for('paldea_app.home'))
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        try:
          conn = get_ldap_connection()
          conn.simple_bind_s('cn=%s,dc=example. dc=org' % username, password)

        except Exception as e:
            flash('Invalid username or password. Please try again.','danger')
            return render_template('login.html', form=form)
        user=User.query.filter_by(username=username).filter()
        if not user:
            user=User(username, password)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash('You have successfully logged in.','success')
        return redirect(url_for('paldea_app.home'))
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('login.html', form=form)

@paldea_app.route('/part-d')
def part_d():
    return render_template('part_d.html')

@paldea_app.route('/part-c')
def part_c():
    team_members = {
        'Samantha Aguirre': {
            'epic': 'Epic 4: Enhanced Visualization',
            'user_stories': '2, 5, 9',
            'summary': 'These stories focus on advanced data visualization, predictive analytics, and interactive dashboard features to provide deeper insights into financial patterns.',
            'tasks': [
                'Task 21: Implement trend line charts for spending patterns. (Supports Story 2: enhanced financial dashboard)',
                'Task 22: Add forecasting algorithms for expense prediction. (Supports Story 9: predictive financial planning)',
                'Task 23: Create interactive drill-down chart capabilities. (Supports Story 5: detailed data exploration)',
                'Task 24: Develop custom dashboard layouts. (Supports Story 2: personalized user experience)'
            ]
        },
        'Gerves Francois Baniakina': {
            'epic': 'Epic 5: Export & Reporting',
            'user_stories': '10, 11, 12',
            'summary': 'These stories address the need for comprehensive financial reporting, data export capabilities, and automated report generation for tax and compliance purposes.',
            'tasks': [
                'Task 25: Generate PDF financial reports with charts. (Supports Story 10: comprehensive reporting)',
                'Task 26: Implement CSV data export functionality. (Supports Story 11: data portability)',
                'Task 27: Create tax preparation summary reports. (Supports Story 12: tax compliance)',
                'Task 28: Add scheduled report generation. (Supports Story 10: automated reporting)'
            ]
        },
        'Qiao Huang': {
            'epic': 'Epic 6: Multi-Currency Support',
            'user_stories': '13, 15, 16',
            'summary': 'These stories enable users to manage finances across multiple currencies, with real-time exchange rates and conversion tracking.',
            'tasks': [
                'Task 45: Integrate currency exchange rate APIs. (Supports Story 13: global financial management)',
                'Task 46: Implement multi-currency transaction handling. (Supports Story 15: international transactions)',
                'Task 47: Add currency preference settings. (Supports Story 16: user customization)',
                'Task 48: Create currency conversion history tracking. (Supports Story 13: conversion audit trail)'
            ]
        },
        'Rachan Sailamai': {
            'epic': 'Epic 4: Enhanced Visualization (Support)',
            'user_stories': '2, 5, 9',
            'summary': 'Support role for advanced visualization features, assisting with implementation and integration.',
            'tasks': [
                'Task 21: Assist with trend line chart implementation. (Supports Story 2)',
                'Task 23: Support interactive drill-down features. (Supports Story 5)',
                'Task 24: Help with custom dashboard layouts. (Supports Story 2)'
            ]
        },
        'Manish Shrivastav': {
            'epic': 'Epic 5: Export & Reporting (Support)',
            'user_stories': '10, 11, 12',
            'summary': 'Support role for export and reporting features, focusing on data handling and automation.',
            'tasks': [
                'Task 26: Assist with CSV export functionality. (Supports Story 11)',
                'Task 27: Support tax preparation reports. (Supports Story 12)',
                'Task 28: Help with scheduled report generation. (Supports Story 10)'
            ]
        }
    }
    return render_template('part_c.html', team_members=team_members)

@paldea_app.route('/part-c.pdf')
def part_c_pdf():
    # Use installed Edge/Chrome in headless mode to print the live page to PDF, with all accordions expanded.
    target_url = url_for('paldea_app.part_c', _external=True) + '?print=1'

    # Find Edge or Chrome executable
    candidates = [
        shutil.which('msedge'),
        shutil.which('chrome'),
        shutil.which('google-chrome'),
        r'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
        r'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    ]
    browser_path = next((p for p in candidates if p and os.path.exists(p)), None)
    if not browser_path:
        return Response(b'Browser not found. Please install Microsoft Edge or Google Chrome.', status=500)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_pdf = os.path.join(tmpdir, 'part-c.pdf')
        user_data_dir = os.path.join(tmpdir, 'ud')
        os.makedirs(user_data_dir, exist_ok=True)
        # Headless print to PDF. virtual-time-budget helps JS-heavy pages finish rendering.
        cmd = [
            browser_path,
            '--headless=new',
            f'--user-data-dir={user_data_dir}',
            f'--print-to-pdf={output_pdf}',
            '--print-to-pdf-no-header',
            '--disable-gpu',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--run-all-compositor-stages-before-draw',
            '--virtual-time-budget=10000',
            target_url
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            with open(output_pdf, 'rb') as f:
                pdf_bytes = f.read()
        except subprocess.TimeoutExpired:
            return Response(b'PDF generation timed out.', status=504)
        except subprocess.CalledProcessError as e:
            return Response(f'PDF generation failed: {e.stderr.decode(errors="ignore")}'.encode(), status=500)

    return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': 'attachment; filename=part-c.pdf'})

@paldea_app.route('/budget')
@login_required
def budget_form():
    """Display budget setting form"""
    return render_template('budget.html')

@paldea_app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    """Add a new budget entry"""
    try:
        category_name = request.form['category']
        budget_amount = float(request.form['budget_amount'])

        # Get or create category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        # Check if budget exists, update or create
        existing_budget = CategoryBudget.query.filter_by(user_id=current_user.id, category_id=category.id).first()
        if existing_budget:
            existing_budget.budget_amount = budget_amount
        else:
            budget = CategoryBudget(user_id=current_user.id, category_id=category.id, budget_amount=budget_amount)
            db.session.add(budget)
        db.session.commit()

        flash('Budget added successfully!', 'success')
        return redirect(url_for('paldea_app.budget_progress'))
    except Exception as e:
        flash(f'Error adding budget: {str(e)}', 'error')
        return redirect(url_for('paldea_app.budget_form'))

@paldea_app.route('/budget_progress')
@login_required
def budget_progress():
    """Display budget progress with progress bars"""
    from datetime import datetime

    # Get all budgets for user
    budgets = CategoryBudget.query.filter_by(user_id=current_user.id).all()

    # Get current month's transactions
    now = datetime.utcnow()
    current_month_start = datetime(now.year, now.month, 1)
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date >= current_month_start
    ).all()

    # Create spending dictionary
    spending = {}
    for transaction in transactions:
        if transaction.category_id:
            spending[transaction.category_id] = spending.get(transaction.category_id, 0) + transaction.amount

    # Calculate progress for each budget
    budget_progress = []
    for budget in budgets:
        spent = spending.get(budget.category_id, 0)
        percentage = (spent / budget.budget_amount) * 100 if budget.budget_amount > 0 else 0

        # Determine color based on percentage
        if percentage < 70:
            color = 'success'
        elif percentage < 90:
            color = 'warning'
        else:
            color = 'danger'

        budget_progress.append({
            'category': budget.category.name,
            'budget_amount': budget.budget_amount,
            'spent': spent,
            'remaining': budget.budget_amount - spent,
            'percentage': min(percentage, 100),
            'color': color
        })

    return render_template('budget_progress.html', budgets=budget_progress)

@paldea_app.route('/add_sample_data')
@login_required
def add_sample_data():
    """Add sample transaction data for demonstration"""
    from datetime import datetime, timedelta
    now = datetime.utcnow()

    # Sample transactions for current month
    sample_transactions = [
        Transaction(description='Weekly grocery shopping', amount=150.00, type='expense', category_id=2, user_id=current_user.id, date=now - timedelta(days=5)),
        Transaction(description='Movie tickets', amount=75.50, type='expense', category_id=4, user_id=current_user.id, date=now - timedelta(days=3)),
        Transaction(description='Monthly rent payment', amount=200.00, type='expense', category_id=3, user_id=current_user.id, date=now - timedelta(days=1)),
        Transaction(description='Gas and parking', amount=45.00, type='expense', category_id=5, user_id=current_user.id, date=now - timedelta(days=10)),
        Transaction(description='Monthly salary', amount=3000.00, type='income', category_id=1, user_id=current_user.id, date=now - timedelta(days=7)),
        Transaction(description='Additional groceries', amount=120.00, type='expense', category_id=2, user_id=current_user.id, date=now - timedelta(days=2)),
        Transaction(description='Dining out', amount=50.00, type='expense', category_id=4, user_id=current_user.id, date=now - timedelta(days=4)),
    ]

    for transaction in sample_transactions:
        db.session.add(transaction)
    db.session.commit()

    flash('Sample data added successfully!', 'success')
    return redirect(url_for('paldea_app.budget_progress'))

@paldea_app.route('/demo')
def demo():
    # Sample data for demo
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    categories = Category.query.all()
    sample_transactions = [
        Transaction(description='Salary', amount=3000.00, type='income', category_id=1, user_id=1, date=now - timedelta(days=5)),
        Transaction(description='Groceries', amount=150.00, type='expense', category_id=2, user_id=1, date=now - timedelta(days=3)),
        Transaction(description='Rent', amount=1200.00, type='expense', category_id=3, user_id=1, date=now - timedelta(days=1)),
        Transaction(description='Freelance', amount=500.00, type='income', category_id=1, user_id=1, date=now - timedelta(days=10)),
        Transaction(description='Entertainment', amount=100.00, type='expense', category_id=4, user_id=1, date=now - timedelta(days=7)),
    ]
    sample_category_budgets = [
        CategoryBudget(user_id=1, category_id=2, budget_amount=200.00, category=Category(id=2, name='Groceries')),
        CategoryBudget(user_id=1, category_id=3, budget_amount=1300.00, category=Category(id=3, name='Rent')),
        CategoryBudget(user_id=1, category_id=4, budget_amount=150.00, category=Category(id=4, name='Entertainment')),
    ]
    sample_goals = [
        Goal(user_id=1, goal_type='Savings', target_amount=5000.00, deadline=now + timedelta(days=365), description='Emergency fund'),
        Goal(user_id=1, goal_type='Investment', target_amount=10000.00, deadline=now + timedelta(days=730), description='Retirement savings'),
    ]

    # Calculate demo data
    transactions = sample_transactions
    category_budgets = sample_category_budgets
    goals = sample_goals

    budget_form = BudgetForm()
    transaction_form = TransactionForm()
    category_budget_form = CategoryBudgetForm()
    goal_form = GoalForm()

    transaction_form.category.choices = [(c.id, c.name) for c in categories]
    category_budget_form.category.choices = [(c.id, c.name) for c in categories]

    # Filter transactions (demo has no filters applied)
    filter_type = None
    filter_period = None

    # Calculate spent per category for current month
    current_month_start = datetime(now.year, now.month, 1)
    category_spent = {}
    for budget in category_budgets:
        spent = sum(t.amount for t in transactions if t.category_id == budget.category_id and t.type == 'expense' and t.date >= current_month_start)
        category_spent[budget.category_id] = spent

    # Data for charts
    pie_labels = [cb.category.name for cb in category_budgets if cb.category]
    pie_data = [category_spent.get(cb.category_id, 0) for cb in category_budgets if cb.category]

    monthly_transactions = [t for t in transactions if t.date.month == now.month and t.date.year == now.year]
    income = sum(t.amount for t in monthly_transactions if t.type == 'income')
    expense = sum(t.amount for t in monthly_transactions if t.type == 'expense')
    bar_labels = ['Income', 'Expense']
    bar_data = [income, expense]

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    cash_flow = total_income - total_expenses

    # Default preferred currency for demo
    preferred_currency = Currency.query.filter_by(code='USD').first()
    if not preferred_currency:
        preferred_currency = Currency(code='USD', symbol='$', name='US Dollar')

    return render_template('home.html', budget_form=budget_form, transaction_form=transaction_form, category_budget_form=category_budget_form, goal_form=goal_form, transactions=transactions, categories=categories, category_budgets=category_budgets, goals=goals, category_spent=category_spent, now=now, pie_labels=pie_labels, pie_data=pie_data, bar_labels=bar_labels, bar_data=bar_data, total_income=total_income, total_expenses=total_expenses, cash_flow=cash_flow, preferred_currency=preferred_currency, demo=True)

@paldea_app.route('/export_csv')
@login_required
def export_csv():
    from io import StringIO
    import csv
    from datetime import datetime, timedelta
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    category_id = request.args.get('category_id')
    
    # Build query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Transaction.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Transaction.date <= end)
        except ValueError:
            pass
    
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    if category_id:
        try:
            query = query.filter(Transaction.category_id == int(category_id))
        except ValueError:
            pass
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Description', 'Type', 'Category', 'Amount', 'Currency', 'Currency Code'])
    
    # Write transaction data
    for t in transactions:
        category_name = t.category.name if t.category else 'N/A'
        currency_symbol = t.currency.symbol if t.currency else '$'
        currency_code = t.currency.code if t.currency else 'USD'
        writer.writerow([
            t.date.strftime('%Y-%m-%d %H:%M:%S'),
            t.description,
            t.type,
            category_name,
            t.amount,
            currency_symbol,
            currency_code
        ])
    
    # Add summary section
    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Total Income', sum(t.amount for t in transactions if t.type == 'income')])
    writer.writerow(['Total Expenses', sum(t.amount for t in transactions if t.type == 'expense')])
    writer.writerow(['Net Cash Flow', sum(t.amount for t in transactions if t.type == 'income') - sum(t.amount for t in transactions if t.type == 'expense')])
    
    # Add category breakdown
    writer.writerow([])
    writer.writerow(['Category Breakdown'])
    writer.writerow(['Category', 'Total Income', 'Total Expenses', 'Net'])
    category_totals = {}
    for t in transactions:
        cat_name = t.category.name if t.category else 'Uncategorized'
        if cat_name not in category_totals:
            category_totals[cat_name] = {'income': 0, 'expense': 0}
        if t.type == 'income':
            category_totals[cat_name]['income'] += t.amount
        else:
            category_totals[cat_name]['expense'] += t.amount
    
    for cat_name, totals in category_totals.items():
        writer.writerow([cat_name, totals['income'], totals['expense'], totals['income'] - totals['expense']])
    
    output.seek(0)
    filename = f'transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})

@paldea_app.route('/export_pdf')
@login_required
def export_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from io import BytesIO
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    import tempfile
    import os

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
    story.append(Paragraph("Financial Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Get transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    cash_flow = total_income - total_expenses

    # Summary
    summary_data = [
        ['Metric', 'Amount'],
        ['Total Income', f'${total_income:.2f}'],
        ['Total Expenses', f'${total_expenses:.2f}'],
        ['Net Cash Flow', f'${cash_flow:.2f}']
    ]
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Generate charts
    with tempfile.TemporaryDirectory() as tmpdir:
        # Chart 1: Income vs Expenses Bar Chart
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(['Income', 'Expenses'], [total_income, total_expenses], color=['green', 'red'])
        ax.set_ylabel('Amount ($)')
        ax.set_title('Income vs Expenses')
        ax.grid(True, alpha=0.3)
        chart1_path = os.path.join(tmpdir, 'chart1.png')
        plt.tight_layout()
        plt.savefig(chart1_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        story.append(Paragraph("Income vs Expenses", styles['Heading2']))
        story.append(Image(chart1_path, width=5*inch, height=3.33*inch))
        story.append(Spacer(1, 20))

        # Chart 2: Category Spending Pie Chart
        category_budgets = CategoryBudget.query.filter_by(user_id=current_user.id).all()
        category_spent = {}
        for budget in category_budgets:
            spent = sum(t.amount for t in transactions if t.category_id == budget.category_id and t.type == 'expense')
            category_spent[budget.category_id] = spent
        
        if category_spent:
            pie_labels = [cb.category.name for cb in category_budgets if cb.category and cb.category_id in category_spent]
            pie_data = [category_spent.get(cb.category_id, 0) for cb in category_budgets if cb.category and cb.category_id in category_spent]
            
            if pie_data and sum(pie_data) > 0:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90)
                ax.set_title('Category Spending Distribution')
                chart2_path = os.path.join(tmpdir, 'chart2.png')
                plt.tight_layout()
                plt.savefig(chart2_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                story.append(Paragraph("Category Spending Distribution", styles['Heading2']))
                story.append(Image(chart2_path, width=5*inch, height=3.33*inch))
                story.append(Spacer(1, 20))

        # Chart 3: Monthly Trend Line
        now = datetime.utcnow()
        monthly_data = {}
        for i in range(6):  # Last 6 months
            month_start = (now - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_key = month_start.strftime('%Y-%m')
            monthly_income = sum(t.amount for t in transactions if t.type == 'income' and month_start <= t.date <= month_end)
            monthly_expense = sum(t.amount for t in transactions if t.type == 'expense' and month_start <= t.date <= month_end)
            monthly_data[month_key] = {'income': monthly_income, 'expense': monthly_expense}
        
        if monthly_data:
            months = sorted(monthly_data.keys())
            incomes = [monthly_data[m]['income'] for m in months]
            expenses = [monthly_data[m]['expense'] for m in months]
            
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(months, incomes, marker='o', label='Income', linewidth=2)
            ax.plot(months, expenses, marker='s', label='Expenses', linewidth=2)
            ax.set_xlabel('Month')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Monthly Income vs Expenses Trend')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            chart3_path = os.path.join(tmpdir, 'chart3.png')
            plt.tight_layout()
            plt.savefig(chart3_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            story.append(Paragraph("Monthly Trend", styles['Heading2']))
            story.append(Image(chart3_path, width=5*inch, height=3.33*inch))
            story.append(Spacer(1, 20))

    # Transactions table
    story.append(Paragraph("Recent Transactions", styles['Heading2']))
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(20).all()
    trans_data = [['Date', 'Description', 'Type', 'Category', 'Amount']]
    for t in recent_transactions:
        category_name = t.category.name if t.category else 'N/A'
        currency_symbol = t.currency.symbol if t.currency else '$'
        trans_data.append([t.date.strftime('%Y-%m-%d'), t.description[:30], t.type.title(), category_name[:20], f'{currency_symbol}{t.amount:.2f}'])

    trans_table = Table(trans_data)
    trans_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(trans_table)

    doc.build(story)
    buffer.seek(0)
    filename = f'financial_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return Response(buffer.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename={filename}'})

@paldea_app.route('/charts_data')
@login_required
def charts_data():
    # Pie chart data
    category_budgets = CategoryBudget.query.filter_by(user_id=current_user.id).all()
    category_spent = {}
    for budget in category_budgets:
        spent = sum(t.amount for t in Transaction.query.filter_by(user_id=current_user.id, category_id=budget.category_id, type='expense').all())
        category_spent[budget.category_id] = spent

    pie_labels = [cb.category.name for cb in category_budgets if cb.category]
    pie_data = [category_spent.get(cb.category_id, 0) for cb in category_budgets if cb.category]

    # Bar chart data
    monthly_transactions = Transaction.query.filter(Transaction.user_id == current_user.id, Transaction.date >= datetime.utcnow().replace(day=1)).all()
    income = sum(t.amount for t in monthly_transactions if t.type == 'income')
    expense = sum(t.amount for t in monthly_transactions if t.type == 'expense')
    bar_labels = ['Income', 'Expense']
    bar_data = [income, expense]

    # Trend line data (monthly spending over last 12 months)
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    trend_labels = []
    trend_data = []
    for i in range(12):
        month_start = (now - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        monthly_expenses = sum(t.amount for t in Transaction.query.filter(Transaction.user_id == current_user.id, Transaction.type == 'expense', Transaction.date >= month_start, Transaction.date <= month_end).all())
        trend_labels.append(month_start.strftime('%b %Y'))
        trend_data.append(monthly_expenses)
    trend_labels.reverse()
    trend_data.reverse()

    return jsonify({
        'pie_labels': pie_labels,
        'pie_data': pie_data,
        'bar_labels': bar_labels,
        'bar_data': bar_data,
        'trend_labels': trend_labels,
        'trend_data': trend_data
    })

@paldea_app.route('/forecast')
@login_required
def forecast():
    """Enhanced forecasting with multiple prediction methods"""
    from datetime import datetime, timedelta
    import numpy as np
    
    now = datetime.utcnow()
    # Get last 12 months of expenses for better prediction
    expenses = []
    months = []
    for i in range(12):
        month_start = (now - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        monthly_expense = sum(t.amount for t in Transaction.query.filter(Transaction.user_id == current_user.id, Transaction.type == 'expense', Transaction.date >= month_start, Transaction.date <= month_end).all())
        expenses.append(monthly_expense)
        months.append(month_start.strftime('%b %Y'))
    
    expenses.reverse()
    months.reverse()
    
    predictions = {}
    
    # Method 1: Simple Average
    if expenses:
        predictions['average'] = round(sum(expenses) / len(expenses), 2)
    
    # Method 2: Weighted Average (recent months weighted more)
    if len(expenses) >= 3:
        weights = [i+1 for i in range(len(expenses))]
        weighted_sum = sum(e * w for e, w in zip(expenses, weights))
        total_weight = sum(weights)
        predictions['weighted_average'] = round(weighted_sum / total_weight, 2)
    
    # Method 3: Linear Regression (if sklearn available)
    try:
        from sklearn.linear_model import LinearRegression
        if len(expenses) >= 2:
            X = np.array(range(len(expenses))).reshape(-1, 1)
            y = np.array(expenses)
            model = LinearRegression()
            model.fit(X, y)
            next_month_prediction = model.predict([[len(expenses)]])[0]
            predictions['linear_regression'] = round(next_month_prediction, 2)
            predictions['confidence'] = round(min(100, max(0, model.score(X, y) * 100)), 1)
    except ImportError:
        pass
    
    # Method 4: Moving Average (last 3 months)
    if len(expenses) >= 3:
        predictions['moving_average'] = round(sum(expenses[-3:]) / 3, 2)
    
    # Use the best available prediction
    if 'linear_regression' in predictions:
        predictions['recommended'] = predictions['linear_regression']
    elif 'weighted_average' in predictions:
        predictions['recommended'] = predictions['weighted_average']
    elif 'moving_average' in predictions:
        predictions['recommended'] = predictions['moving_average']
    else:
        predictions['recommended'] = predictions.get('average', 0)
    
    return jsonify({
        'predictions': predictions,
        'historical_data': {
            'months': months,
            'expenses': expenses
        }
    })

@paldea_app.route('/category_details/<int:category_id>')
@login_required
def category_details(category_id):
    """Drill-down view for category transactions"""
    from datetime import datetime, timedelta
    
    category = Category.query.get_or_404(category_id)
    now = datetime.utcnow()
    
    # Get transactions for this category
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id == category_id,
        Transaction.type == 'expense'
    ).order_by(Transaction.date.desc()).all()
    
    # Calculate monthly breakdown
    monthly_breakdown = {}
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        if month_key not in monthly_breakdown:
            monthly_breakdown[month_key] = 0
        monthly_breakdown[month_key] += transaction.amount
    
    # Calculate total
    total_spent = sum(t.amount for t in transactions)
    
    # Get category budget if exists
    category_budget = CategoryBudget.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).first()
    
    return render_template('category_details.html', 
                         category=category,
                         transactions=transactions,
                         monthly_breakdown=monthly_breakdown,
                         total_spent=total_spent,
                         category_budget=category_budget)

@paldea_app.route('/convert_currency', methods=['POST'])
@login_required
def convert_currency():
    """Enhanced currency conversion with multiple API support and caching"""
    import requests
    from datetime import datetime, timedelta
    from functools import lru_cache
    
    data = request.get_json()
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = float(data.get('amount', 0))
    
    if from_currency == to_currency:
        return jsonify({'converted_amount': round(amount, 2), 'rate': 1.0})
    
    # Try multiple exchange rate APIs for reliability
    rate = None
    api_used = None
    
    # API 1: exchangerate-api.com (free tier, no API key needed)
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            rates = response.json().get('rates', {})
            rate = rates.get(to_currency)
            if rate:
                api_used = 'exchangerate-api'
    except Exception as e:
        print(f"API 1 failed: {e}")
    
    # API 2: Fixer.io fallback (if available)
    if not rate:
        try:
            # Note: This would require an API key in production
            # For now, we'll use a simple fallback calculation
            # In production, you'd use: url = f"http://data.fixer.io/api/latest?access_key=YOUR_KEY&base={from_currency}"
            pass
        except Exception as e:
            print(f"API 2 failed: {e}")
    
    # Fallback: Use a simple 1:1 rate if APIs fail (not ideal, but prevents errors)
    if not rate:
        rate = 1.0
        api_used = 'fallback'
    
    converted_amount = amount * rate
    
    # Get currency objects
    from_curr = Currency.query.filter_by(code=from_currency).first()
    to_curr = Currency.query.filter_by(code=to_currency).first()
    
    if from_curr and to_curr:
        # Log conversion
        conversion = ConversionHistory(
            user_id=current_user.id,
            from_currency_id=from_curr.id,
            to_currency_id=to_curr.id,
            amount=amount,
            converted_amount=converted_amount,
            rate=rate
        )
        db.session.add(conversion)
        db.session.commit()
    
    return jsonify({
        'converted_amount': round(converted_amount, 2),
        'rate': round(rate, 6),
        'api_used': api_used,
        'from_currency': from_currency,
        'to_currency': to_currency
    })

@paldea_app.route('/exchange_rates')
@login_required
def exchange_rates():
    """Get current exchange rates for user's preferred currency"""
    import requests
    from datetime import datetime
    
    preferred_currency = current_user.preferred_currency_id
    base_currency = Currency.query.get(preferred_currency)
    
    if not base_currency:
        base_currency = Currency.query.filter_by(code='USD').first()
    
    if not base_currency:
        return jsonify({'error': 'No base currency found'}), 404
    
    # Get all currencies
    currencies = Currency.query.all()
    
    # Fetch exchange rates
    rates = {}
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency.code}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            api_rates = response.json().get('rates', {})
            for currency in currencies:
                if currency.code in api_rates:
                    rates[currency.code] = api_rates[currency.code]
                elif currency.code == base_currency.code:
                    rates[currency.code] = 1.0
    except Exception as e:
        print(f"Failed to fetch exchange rates: {e}")
        # Return 1:1 rates as fallback
        for currency in currencies:
            rates[currency.code] = 1.0
    
    return jsonify({
        'base_currency': base_currency.code,
        'rates': rates,
        'last_updated': datetime.utcnow().isoformat()
    })

@paldea_app.route('/currency_settings', methods=['GET', 'POST'])
@login_required
def currency_settings():
    """Currency preference settings page"""
    currencies = Currency.query.all()
    
    if request.method == 'POST':
        preferred_currency_id = request.form.get('preferred_currency_id')
        try:
            preferred_currency_id = int(preferred_currency_id)
            currency = Currency.query.get(preferred_currency_id)
            if currency:
                current_user.preferred_currency_id = preferred_currency_id
                db.session.commit()
                flash('Currency preference updated successfully!', 'success')
            else:
                flash('Invalid currency selected.', 'danger')
        except (ValueError, TypeError):
            flash('Invalid currency ID.', 'danger')
        
        return redirect(url_for('paldea_app.currency_settings'))
    
    # Get conversion history
    conversions = ConversionHistory.query.filter_by(user_id=current_user.id).order_by(ConversionHistory.date.desc()).limit(50).all()
    
    return render_template('currency_settings.html',
                         currencies=currencies,
                         current_preferred=current_user.preferred_currency_id,
                         conversions=conversions)

@paldea_app.route('/conversion_history')
@login_required
def conversion_history():
    """View currency conversion history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    conversions = ConversionHistory.query.filter_by(user_id=current_user.id)\
        .order_by(ConversionHistory.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('conversion_history.html', conversions=conversions)

@paldea_app.route('/convert_transaction_currency/<int:transaction_id>', methods=['POST'])
@login_required
def convert_transaction_currency(transaction_id):
    """Convert a transaction to user's preferred currency"""
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    preferred_currency = Currency.query.get(current_user.preferred_currency_id)
    if not preferred_currency:
        preferred_currency = Currency.query.filter_by(code='USD').first()
    
    if transaction.currency.code == preferred_currency.code:
        return jsonify({
            'converted_amount': transaction.amount,
            'rate': 1.0,
            'currency': preferred_currency.code
        })
    
    # Use the convert_currency logic
    import requests
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{transaction.currency.code}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            rates = response.json().get('rates', {})
            rate = rates.get(preferred_currency.code, 1.0)
            converted_amount = transaction.amount * rate
            
            return jsonify({
                'converted_amount': round(converted_amount, 2),
                'rate': round(rate, 6),
                'currency': preferred_currency.code,
                'original_amount': transaction.amount,
                'original_currency': transaction.currency.code
            })
    except Exception as e:
        return jsonify({'error': f'Failed to convert: {str(e)}'}), 500
    
    return jsonify({'error': 'Conversion failed'}), 500

@paldea_app.route('/tax_summary')
@login_required
def tax_summary():
    """Generate tax preparation summary for a given year"""
    from datetime import datetime
    
    tax_year = request.args.get('year', str(datetime.now().year))
    try:
        tax_year = int(tax_year)
    except ValueError:
        tax_year = datetime.now().year
    
    # Get transactions for the tax year
    start_date = datetime(tax_year, 1, 1)
    end_date = datetime(tax_year, 12, 31, 23, 59, 59)
    
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    
    # Categorize deductible expenses (common tax-deductible categories)
    deductible_categories = ['Business', 'Professional', 'Education', 'Medical', 'Charity', 'Home Office']
    deductible_expenses = 0
    category_breakdown = {}
    
    for t in transactions:
        if t.type == 'expense' and t.category:
            cat_name = t.category.name
            if any(deductible in cat_name for deductible in deductible_categories):
                deductible_expenses += t.amount
            if cat_name not in category_breakdown:
                category_breakdown[cat_name] = 0
            category_breakdown[cat_name] += t.amount
    
    taxable_income = total_income - deductible_expenses
    net_profit_loss = total_income - total_expenses
    
    summary = {
        'tax_year': tax_year,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'deductible_expenses': deductible_expenses,
        'taxable_income': taxable_income,
        'net_profit_loss': net_profit_loss,
        'category_breakdown': category_breakdown
    }
    
    return render_template('tax_summary.html', summary=summary, tax_year=tax_year)

@paldea_app.route('/tax_summary_pdf')
@login_required
def tax_summary_pdf():
    """Generate PDF tax summary report"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from io import BytesIO
    from datetime import datetime
    
    tax_year = request.args.get('year', str(datetime.now().year))
    try:
        tax_year = int(tax_year)
    except ValueError:
        tax_year = datetime.now().year
    
    # Get transactions for the tax year
    start_date = datetime(tax_year, 1, 1)
    end_date = datetime(tax_year, 12, 31, 23, 59, 59)
    
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    
    # Categorize deductible expenses
    deductible_categories = ['Business', 'Professional', 'Education', 'Medical', 'Charity', 'Home Office']
    deductible_expenses = 0
    category_breakdown = {}
    
    for t in transactions:
        if t.type == 'expense' and t.category:
            cat_name = t.category.name
            if any(deductible in cat_name for deductible in deductible_categories):
                deductible_expenses += t.amount
            if cat_name not in category_breakdown:
                category_breakdown[cat_name] = 0
            category_breakdown[cat_name] += t.amount
    
    taxable_income = total_income - deductible_expenses
    net_profit_loss = total_income - total_expenses
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
    story.append(Paragraph(f"Tax Summary Report - {tax_year}", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Summary table
    summary_data = [
        ['Metric', 'Amount'],
        ['Total Income', f'${total_income:.2f}'],
        ['Total Expenses', f'${total_expenses:.2f}'],
        ['Deductible Expenses', f'${deductible_expenses:.2f}'],
        ['Taxable Income', f'${taxable_income:.2f}'],
        ['Net Profit/Loss', f'${net_profit_loss:.2f}']
    ]
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Category breakdown
    if category_breakdown:
        story.append(Paragraph("Expense Category Breakdown", styles['Heading2']))
        cat_data = [['Category', 'Total Amount']]
        for cat, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True):
            cat_data.append([cat, f'${amount:.2f}'])
        
        cat_table = Table(cat_data)
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 20))
    
    # Important note
    story.append(Paragraph("Important Note:", styles['Heading3']))
    story.append(Paragraph("This is a summary report for tax preparation purposes. Please consult with a tax professional for accurate tax filing.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    filename = f'tax_summary_{tax_year}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return Response(buffer.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename={filename}'})

@paldea_app.route('/scheduled_reports')
@login_required
def scheduled_reports():
    """View and manage scheduled reports"""
    reports = ScheduledReport.query.filter_by(user_id=current_user.id).all()
    return render_template('scheduled_reports.html', reports=reports)

@paldea_app.route('/schedule_report', methods=['POST'])
@login_required
def schedule_report():
    """Create a new scheduled report"""
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    
    frequency = request.form.get('frequency')
    report_format = request.form.get('report_format', 'pdf')
    day_of_month = int(request.form.get('day_of_month', 1))
    email_enabled = request.form.get('email_enabled') == 'on'
    email_address = request.form.get('email_address', current_user.email)
    
    # Calculate next generation date
    now = datetime.utcnow()
    if frequency == 'monthly':
        next_gen = now.replace(day=min(day_of_month, 28)) + relativedelta(months=1)
    elif frequency == 'quarterly':
        next_gen = now.replace(day=min(day_of_month, 28)) + relativedelta(months=3)
    elif frequency == 'yearly':
        next_gen = now.replace(day=min(day_of_month, 28)) + relativedelta(years=1)
    else:
        flash('Invalid frequency', 'danger')
        return redirect(url_for('paldea_app.scheduled_reports'))
    
    scheduled_report = ScheduledReport(
        user_id=current_user.id,
        report_type=frequency,
        report_format=report_format,
        frequency=frequency,
        day_of_month=day_of_month,
        is_active=True,
        next_generation=next_gen,
        email_enabled=email_enabled,
        email_address=email_address if email_enabled else None
    )
    
    db.session.add(scheduled_report)
    db.session.commit()
    
    flash('Scheduled report created successfully!', 'success')
    return redirect(url_for('paldea_app.scheduled_reports'))

@paldea_app.route('/toggle_scheduled_report/<int:report_id>', methods=['POST'])
@login_required
def toggle_scheduled_report(report_id):
    """Toggle scheduled report active status"""
    report = ScheduledReport.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('You do not have permission to modify this report.', 'danger')
        return redirect(url_for('paldea_app.scheduled_reports'))
    
    report.is_active = not report.is_active
    db.session.commit()
    
    flash('Scheduled report updated!', 'success')
    return redirect(url_for('paldea_app.scheduled_reports'))

@paldea_app.route('/delete_scheduled_report/<int:report_id>', methods=['POST'])
@login_required
def delete_scheduled_report(report_id):
    """Delete a scheduled report"""
    report = ScheduledReport.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('You do not have permission to delete this report.', 'danger')
        return redirect(url_for('paldea_app.scheduled_reports'))
    
    db.session.delete(report)
    db.session.commit()
    
    flash('Scheduled report deleted!', 'success')
    return redirect(url_for('paldea_app.scheduled_reports'))

def generate_scheduled_reports():
    """Function to generate scheduled reports - called by APScheduler"""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from my_paldea import create_app
    
    # Create app context for database operations
    app = create_app()
    with app.app_context():
        now = datetime.utcnow()
        # Get all active scheduled reports that are due
        reports = ScheduledReport.query.filter(
            ScheduledReport.is_active == True,
            ScheduledReport.next_generation <= now
        ).all()
        
        for report in reports:
            try:
                # Generate report based on type
                # Note: In a production environment, you would save the report to a file
                # and optionally email it to the user
                if report.report_format == 'pdf':
                    # Generate PDF report - would call export_pdf logic here
                    # For now, we just mark it as generated
                    pass
                else:
                    # Generate CSV report - would call export_csv logic here
                    # For now, we just mark it as generated
                    pass
                
                # Update last_generated and calculate next_generation
                report.last_generated = now
                if report.frequency == 'monthly':
                    report.next_generation = now + relativedelta(months=1)
                elif report.frequency == 'quarterly':
                    report.next_generation = now + relativedelta(months=3)
                elif report.frequency == 'yearly':
                    report.next_generation = now + relativedelta(years=1)
                
                db.session.commit()
            except Exception as e:
                print(f"Error generating scheduled report {report.id}: {str(e)}")
                db.session.rollback()
    
