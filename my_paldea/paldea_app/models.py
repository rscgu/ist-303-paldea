'''Model to store the user details'''
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import InputRequired, EqualTo, Length, Email
from my_paldea import db

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150),nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    pwdhash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.pwdhash = generate_password_hash(password)
        self.email = email

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
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    #PasswordField = PasswordField('Password', [InputRequired(), EqualTo('confirm',message='Passwords must match')])
    #confirm = PasswordField('Confirm Password', [InputRequired()])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')
class LoginForm(FlaskForm):
    # email = StringField('Email', validators=[InputRequired(), Email()])
    #username = StringField('Username', [InputRequired()])
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    #PasswordField = PasswordField('Password', [InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


