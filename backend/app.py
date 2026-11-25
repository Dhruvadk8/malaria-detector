import os
import logging
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from backend.models import db, User
from backend.api import api
from backend.routes import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

jwt = JWTManager()
csrf = CSRFProtect()
migrate = Migrate()

@jwt.user_lookup_loader
def user_lookup_loader(_jwt_header, jwt_data):
    identity = jwt_data.get("sub")
    if isinstance(identity, dict):
        identity = identity.get("id")
    try:
        if identity is not None:
            return User.query.get(int(identity))
    except (ValueError, TypeError):
        pass
    return None

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '24')
    
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'malaria.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    
    upload_folder = os.path.join(app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    csrf.exempt(api)
    
    with app.app_context():
        db.create_all()
        
    app.register_blueprint(api)
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
