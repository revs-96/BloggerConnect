import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Base model for SQLAlchemy
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database URI
# Example URI: postgresql://username:password@localhost:5432/BlogConnectDB
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:admin123@db:5432/BlogConnectDB"  # change localhost to db
)

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize the app with the extensions
db.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from BloggerConnect.models import User
    return User.query.get(int(user_id))

# Context processor to make theme available to all templates
@app.context_processor
def inject_theme():
    from flask_login import current_user
    if current_user.is_authenticated:
        return {'user_theme': current_user.theme_preference}
    return {'user_theme': 'dark'}  # Default theme for non-authenticated users

# App context for DB creation and seeding
with app.app_context():
    from BloggerConnect import models  # Ensure models are imported
    db.create_all()

    # Optional: load initial data
    from BloggerConnect.init_data import initialize_sample_data
    initialize_sample_data()

# Import routes after app and db setup
from BloggerConnect import routes
