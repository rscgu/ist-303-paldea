'''Model to store the user details'''
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, PasswordField,SubmitField, FloatField, DateField, SelectField
from wtforms.validators import InputRequired, EqualTo, Length, Email
from my_paldea import db
from datetime import datetime

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150),nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    pwdhash = db.Column(db.String(256), nullable=False)
    budget = db.Column(db.Float, default=0.0)  # Monthly budget
    expenses = db.relationship('Expense', backref='user', lazy=True)

    def __init__(self, username, password, email):
        self.username = username
        if password:
            self.pwdhash = generate_password_hash(password, method='pbkdf2:sha256')
        else:
            self.pwdhash = ''
        self.email = email

    def get_total_expenses(self):
        return sum(expense.amount for expense in self.expenses)

    def is_budget_exceeded(self):
        return self.get_total_expenses() > self.budget if self.budget > 0 else False

    def check_password(self, password):
        return check_password_hash(self.pwdhash,password)
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)
    def __repr__(self):
        return '<User %d>' % self.id

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class CategoryBudget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    budget_amount = db.Column(db.Float, nullable=False)
    time_period = db.Column(db.String(20), default='monthly')  # 'monthly', 'yearly', etc.

    user = db.relationship('User', backref='category_budgets')
    category = db.relationship('Category', backref='budgets')

    def __repr__(self):
        return f'<CategoryBudget {self.category.name}: ${self.budget_amount} ({self.time_period})>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category = db.relationship('Category', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.description}: ${self.amount} ({self.type})>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Expense {self.description}: ${self.amount}>'

class BudgetForm(FlaskForm):
    budget = FloatField('Monthly Budget', validators=[InputRequired()])
    submit = SubmitField('Set Budget')

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[InputRequired(), Length(min=1, max=200)])
    amount = FloatField('Amount', validators=[InputRequired()])
    submit = SubmitField('Add Expense')

class TransactionForm(FlaskForm):
    description = StringField('Description', validators=[InputRequired(), Length(min=1, max=200)])
    amount = FloatField('Amount', validators=[InputRequired()])
    type = SelectField('Type', choices=[('income', 'Income'), ('expense', 'Expense')], validators=[InputRequired()])
    category = SelectField('Category', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Add Transaction')

class CategoryBudgetForm(FlaskForm):
    category = SelectField('Category', coerce=int, validators=[InputRequired()])
    budget_amount = FloatField('Budget Amount', validators=[InputRequired()])
    submit = SubmitField('Set Category Budget')

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # 'savings', 'investments', 'loans'
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Goal {self.goal_type}: ${self.target_amount}>'

class GoalForm(FlaskForm):
    goal_type = SelectField('Goal Type', choices=[('savings', 'Savings'), ('investments', 'Investments'), ('loans', 'Loans')], validators=[InputRequired()])
    target_amount = FloatField('Target Amount', validators=[InputRequired()])
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[InputRequired()])
    description = StringField('Description', validators=[Length(max=200)])
    submit = SubmitField('Set Goal')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    #PasswordField = PasswordField('Password', [InputRequired(), EqualTo('confirm',message='Passwords must match')])
    #confirm = PasswordField('Confirm Password', [InputRequired()])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


