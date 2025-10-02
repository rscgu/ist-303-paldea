from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import redis
from redis import Redis
import ldap3

# create global extenions, but don't attach to app yet!
# bcrypt = Bcrypt()
db  = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
redis = Redis()
oauth = OAuth()

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
    from my_paldea.paldea_app.views import paldea_app

    app.register_blueprint(paldea_app)
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
        #migrate = Migrate(app, db)
    return app
    


