''' To handle the user requests for registration and login'''
import ldap3
import flask_dance
from flask import g,Blueprint, render_template,request,flash,redirect, url_for, session, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from my_paldea import db,login_manager,bcrypt
from my_paldea.utlities import get_ldap_connection
from authlib.integrations.flask_client import OAuth
from my_paldea.paldea_app.models import User, RegistrationForm,LoginForm
from my_paldea.paldea_app.models import RegistrationForm, LoginForm
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
def home():
    return render_template('home.html')

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
        email = form.email.data
        password = form.password.data

        # --- Try local DB login first ---
        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.checkpw(password.encode(), user.password_hash):
                session["user_id"] = user.id
                flash("Logged in successfully (local)!", "success")
                return redirect(url_for("paldea_app.dashboard"))
            else:
                flash("Invalid password for local account", "danger")
                return render_template("login.html", form=form)

        # --- If no local user, try LDAP ---
        try:
            ldap_server = Server("ldap://your-ldap-server.com", get_info=ALL)
            ldap_conn = Connection(
                ldap_server,
                user=f"uid={email},ou=users,dc=example,dc=com",  # adjust DN to your LDAP
                password=password
            )
            if ldap_conn.bind():  # successful LDAP login
                session["user_email"] = email
                flash("Logged in successfully (LDAP)!", "success")
                return redirect(url_for("paldea_app.dashboard"))
            else:
                flash("Invalid LDAP credentials", "danger")
        except Exception as e:
            flash(f"LDAP error: {str(e)}", "danger")

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

        except ldap3.INVALID_CREDENTIALS:
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
    
