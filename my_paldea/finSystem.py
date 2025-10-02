from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import smtplib
from email.message import EmailMessage
from twilio.rest import Client


    # ------------------- Database Setup -------------------
def init_db(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users(
                 username TEXT PRIMARY KEY,
                 password TEXT NOT NULL,
                 email TEXT,
                 phone TEXT,
                 security_key TEXT
                 )''')
        conn.commit()
        conn.close()

    # ------------------- Helper Functions -------------------
def send_email_code(self, email, code):
    EMAIL_ADDRESS = session.get('smtp_email')
    EMAIL_PASSWORD = session.get('smtp_password')
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        flash("Email credentials missing! Configure them first.")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Your 2FA Code'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content(f'Your 2FA code is: {code}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def send_sms_code(self, phone, code):
    ACCOUNT_SID = session.get('twilio_sid')
    AUTH_TOKEN = session.get('twilio_auth')
    FROM_PHONE = session.get('twilio_from')
    if not ACCOUNT_SID or not AUTH_TOKEN or not FROM_PHONE:
        flash("Twilio credentials missing! Configure them first.")
        return

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=f"Your 2FA code is: {code}",
        from_=FROM_PHONE,
        to=phone
    )

def generate_2fa_code(self):
    return str(random.randint(100000, 999999))

# ------------------- Credential Configuration -------------------
@app.route('/configure', methods=['GET','POST'])
def configure(self):
    if request.method == 'POST':
        session['smtp_email'] = request.form['smtp_email']
        session['smtp_password'] = request.form['smtp_password']
        session['twilio_sid'] = request.form['twilio_sid']
        session['twilio_auth'] = request.form['twilio_auth']
        session['twilio_from'] = request.form['twilio_from']
        flash("Credentials configured successfully!")
        return redirect(url_for('login'))
    return render__template('configure.html')

class FincialSystem():
    def __init__(self, finInterm, finMarkets, finAssets):
        self.finInterm = finInterm
        self.finMarkets = finMarkets
        self.finAssets = finAssets

    def trans_resources(self):
        pass
    def manage_risk(self):
        pass
    def clear_payment(self):
        pass
    def set_payment(self):
        pass
    def pool_shares(self):
        pass
    def subdivide_shares(self):
        pass
    def provide_information(self):
        pass
    def set_up_authentication(self):
        pass
    def create_db_schema(self):
        pass
    def add_income_transaction(self):
        pass
    def add_expense_transaction(self):
        pass



    