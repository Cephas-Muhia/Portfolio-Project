import os
from flask import Flask, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
