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
from my_paldea.paldea_app.models import User, RegistrationForm,LoginForm, BudgetForm, ExpenseForm, Expense, Transaction, TransactionForm, Category, CategoryBudget, CategoryBudgetForm, Goal, GoalForm
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

    # Summary
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    cash_flow = total_income - total_expenses

    return render_template('home.html', budget_form=budget_form, transaction_form=transaction_form, category_budget_form=category_budget_form, goal_form=goal_form, transactions=transactions, categories=categories, category_budgets=category_budgets, goals=goals, category_spent=category_spent, budget_progress=budget_progress, now=now, pie_labels=pie_labels, pie_data=pie_data, bar_labels=bar_labels, bar_data=bar_data, total_income=total_income, total_expenses=total_expenses, cash_flow=cash_flow)

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
    form.category.choices = [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        transaction = Transaction(description=form.description.data, amount=form.amount.data, type=form.type.data, category_id=form.category.data, user_id=current_user.id)
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

@paldea_app.route('/part-c')
def part_c():
    team_members = {
        'Gerves Francois Baniakina': {
            'epic': 'Epic 1: Core Transaction Management',
            'user_stories': '1, 6, 7',
            'summary': 'These stories describe the need for a unified system where users can record and categorize both income and expense transactions without relying on multiple services.',
            'tasks': [
                'Task 1: Set up user authentication (login, register). (Supports Story 1: unified financial system with no extra signups)',
                'Task 2: Create database schema (users, transactions, categories). (Foundation for Stories 6 & 7)',
                'Task 3: Implement "Add income transaction" form. (Supports Story 6: income tracker)',
                'Task 4: Implement "Add expense transaction" form. (Supports Story 7: expense tracker)'
            ]
        },
        'Samantha Aguirre': {
            'epic': 'Epic 1.2: Core Transaction Management Continued',
            'user_stories': '1, 6, 7',
            'summary': 'These stories describe the need for a unified system where users can record and categorize both income and expense transactions without relying on multiple services.',
            'tasks': [
                'Task 5: Categorize transactions by income/expense type. (Supports Stories 6 & 7)',
                'Task 6: Display transactions in a list view. (Supports Stories 6 & 7)',
                'Task 7: Implement delete/edit transaction functionality. (Enhances Stories 6 & 7 usability)'
            ]
        },
        'Qiao Huang': {
            'epic': 'Epic 2: Budgeting & Alerts',
            'user_stories': '3, 4, 14',
            'summary': 'These stories address monthly and annual financial planning, user-defined savings goals, and system alerts when overspending.',
            'tasks': [
                'Task 8: Monthly Budget Feature - Allows users to set spending limits for different expense categories. Users select a category and enter a dollar amount. System stores these budget limits in the database. User interaction: Simple form with dropdown menu for category selection, text input for budget amount, save button. Technical requirements: Database table for user_id, category, budget_amount, time_period; form validation; backend route.',
                'Task 9: Progress Bar Implementation - Calculates percentage of budget used based on transaction data. Displays visual progress bar showing spending vs. limit. Shows dollar amounts (spent, remaining, total). How it works: Query database for transactions in selected category for current month, sum amounts, calculate percentage. Display progress bar filled to that percentage. Visual elements: Progress bar (CSS/Bootstrap), text showing "$X of $Y spent", "$Z remaining", color coding (green <70%, yellow 70-90%, red >90%).'
            ]
        },
        'Rachan Sailamai': {
            'epic': 'Epic 2.2: Budgeting & Alerts Continued',
            'user_stories': '3, 4, 14',
            'summary': 'These stories address monthly and annual financial planning, user-defined savings goals, and system alerts when overspending.',
            'tasks': [
                'Task 10: Show alert when budget is exceeded. (Directly supports Story 4: alerts for overspending)',
                'Task 11: Create goal-setting form for savings/investments/loans. (Supports Story 14: annual financial targets)',
                'Task 12: Implement progress markers toward goals. (Supports Story 14: tracking goal achievement)'
            ]
        },
        'Manish Shrivastav': {
            'epic': 'Epic 3: Visualization & Reporting',
            'user_stories': '2, 5',
            'summary': 'These stories highlight the need for financial summaries, filters, and visualizations to help users interpret their financial data.',
            'tasks': [
                'Task 13: Integrate Chart.js for category spending pie chart. (Supports Story 2: financial dashboard, Story 5: custom filters with summaries)',
                'Task 14: Add monthly income vs. expense bar chart. (Supports Story 2: monthly budget & summaries)',
                'Task 15: Implement filters by date (week, month, year). (Supports Story 5: trace financial progress over time)',
                'Task 16: Generate summary dashboard (income, expenses, cash flow). (Supports Story 2: accessible financial dashboard)'
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

    return render_template('home.html', budget_form=budget_form, transaction_form=transaction_form, category_budget_form=category_budget_form, goal_form=goal_form, transactions=transactions, categories=categories, category_budgets=category_budgets, goals=goals, category_spent=category_spent, now=now, pie_labels=pie_labels, pie_data=pie_data, bar_labels=bar_labels, bar_data=bar_data, total_income=total_income, total_expenses=total_expenses, cash_flow=cash_flow, demo=True)
    
