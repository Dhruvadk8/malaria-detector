import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)
db = SQLAlchemy()


class User(db.Model):
    """User model for storing user details."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Detection(db.Model):
    """Model for storing malaria detection results."""
    __tablename__ = 'detections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    result = db.Column(db.String(200), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    heatmap_path = db.Column(db.String(200), nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    parasite_stage = db.Column(db.String(100), nullable=True)
    stage_confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def image_url(self):
        if self.image_path:
            return self.image_path
        if self.heatmap_path:
            return self.heatmap_path
        return '/static/images/th.jpeg'

    @property
    def stage_badge_class(self):
        stage = self.parasite_stage or ''
        if not stage or 'Uninfected' in stage or 'Healthy' in stage:
            return 'bg-success'
        if 'Ring' in stage:
            return 'bg-info text-dark'
        if 'Trophozoite' in stage:
            return 'bg-warning text-dark'
        if 'Schizont' in stage:
            return 'bg-danger'
        if 'Gametocyte' in stage:
            return 'bg-primary'
        return 'bg-secondary'

    def __repr__(self):
        return f'<Detection {self.id} - {self.result} ({self.parasite_stage})>'
