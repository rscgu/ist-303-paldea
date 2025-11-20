from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import redis
from redis import Redis
import ldap3
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# create global extenions, but don't attach to app yet!
# bcrypt = Bcrypt()
db  = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
redis = Redis()
oauth = OAuth()
scheduler = BackgroundScheduler()

# Application factory design pattern to avoid a cycle
def create_app():
    app = Flask(__name__)
    app.config.from_object('my_paldea.config.BaseConfig')
  
    # initialize extensions with app
    #bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    oauth.init_app(app)
    login_manager.login_view = 'paldea_app.login'

     # Register OAuth clients
    from my_paldea.paldea_app.views import register_oauth
    register_oauth(app)

    ## Import and register blueprints *after* app is created
    from my_paldea.paldea_app.views import paldea_app, generate_scheduled_reports

    app.register_blueprint(paldea_app)
    
    # Initialize scheduler for scheduled reports
    if not scheduler.running:
        scheduler.start()
        # Schedule report generation to run daily at midnight
        scheduler.add_job(
            func=generate_scheduled_reports,
            trigger=CronTrigger(hour=0, minute=0),
            id='generate_scheduled_reports',
            name='Generate scheduled financial reports',
            replace_existing=True
        )
    #app.register_blueprint(facebook_blueprint)
    #app.register_blueprint(google_blueprint)
    #app.register_blueprint(twitter_blueprint)
    # Register OAuth
    #register_oauth(app)

    # Register Blueprints if needed
    #app.register_blueprint(google_bp, url_prefix='/login')
    #app.register_blueprint(facebook_bp, url_prefix='/login')
    #app.register_blueprint(twitter_bp, url_prefix='/login')
     # Create tables
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        from my_paldea.paldea_app.models import User
        from werkzeug.security import generate_password_hash
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password='admin123', email='admin@example.com')
            db.session.add(admin_user)
            db.session.commit()
        # Update admin password if needed (for compatibility)
        try:
            if admin_user and not admin_user.check_password('admin123'):
                admin_user.pwdhash = generate_password_hash('admin123')
                db.session.commit()
        except AttributeError:
            # If scrypt is not available, recreate the user
            db.session.delete(admin_user)
            db.session.commit()
            admin_user = User(username='admin', password='admin123', email='admin@example.com')
            db.session.add(admin_user)
            db.session.commit()
        #migrate = Migrate(app, db)
    return app
    


