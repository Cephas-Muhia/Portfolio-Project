# app/models.py

from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    date_lost = db.Column(db.DateTime, nullable=False)  
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('lost_items', lazy=True))

class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('found_items', lazy=True))

