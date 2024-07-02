from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from . import db
from .models import User, LostItem, FoundItem
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 

# Create a Blueprint for the main routes
main = Blueprint('main', __name__, template_folder='templates')

# Replace with your actual OAuth credentials and callback URLs
google_bp = make_google_blueprint(client_id='your_google_client_id',
                                  client_secret='your_google_client_secret',
                                  redirect_to='main.google_auth')
facebook_bp = make_facebook_blueprint(client_id='your_facebook_client_id',
                                      client_secret='your_facebook_client_secret',
                                      redirect_to='main.facebook_auth')

# Register OAuth blueprints
main.register_blueprint(google_bp, url_prefix='/google_login')
main.register_blueprint(facebook_bp, url_prefix='/facebook_login')

# Home route
@main.route('/')
@main.route('/home')
def home():
    return render_template('index.html')

# Registration route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.register'))

        if existing_email:
            flash('Email address already registered. Please use a different one or login.', 'danger')
            return redirect(url_for('main.register'))

        # If username and email are unique, proceed with registration
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, email=email, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

# Login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=request.form.get('remember', False))
                flash('Logged in successfully.', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Incorrect password.', 'danger')
        else:
            flash('Login Unsuccessful. Username not found.', 'danger')

    return render_template('login.html')

# Logout route
@main.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))

# Google login route
@main.route('/google-auth')
def google_auth():
    if not google.authorized:
        return redirect(url_for('main.google.login'))  # Correct endpoint name here

    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    user_info = resp.json()

    # Check if the user already exists in the database
    user = User.query.filter_by(email=user_info['emails'][0]['value']).first()
    if not user:
        # If not, create a new user
        user = User(username=user_info['displayName'], email=user_info['emails'][0]['value'])
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('main.home'))  # Redirect to the main home page after login

# Facebook login route
@main.route('/facebook-auth')
def facebook_auth():
    if not facebook.authorized:
        return redirect(url_for('main.facebook.login'))  # Correct endpoint name here

    resp = facebook.get('/me?fields=name,email')
    assert resp.ok, resp.text
    user_info = resp.json()

    # Check if the user already exists in the database
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        # If not, create a new user
        user = User(username=user_info['name'], email=user_info['email'])
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('main.home'))  # Redirect to the main home page after login

# Report lost item route
@main.route('/report_lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        description = request.form.get('description')
        location = request.form.get('location')
        photo = request.form.get('photo')  # Handle file upload as needed
        date_lost_str = request.form.get('date_lost')
        date_reported = datetime.strptime(date_lost_str, '%Y-%m-%d') if date_lost_str else datetime.utcnow()

        lost_item = LostItem(description=description, location=location, photo=photo, user_id=current_user.id, date_reported=date_reported)
        db.session.add(lost_item)
        db.session.commit()

        flash('Your lost item report has been created successfully! Thank you for using the app.', 'success')
        return redirect(url_for('main.home'))

    return render_template('report_lost.html')

# Report found items route
@main.route('/report_found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        description = request.form.get('description')
        location = request.form.get('location')
        photo = request.form.get('photo')  # Handle file upload as needed
        date_found_str = request.form.get('date_found')
        date_reported = datetime.strptime(date_found_str, '%Y-%m-%d') if date_found_str else datetime.utcnow()

        found_item = FoundItem(description=description, location=location, photo=photo, user_id=current_user.id, date_reported=date_reported)
        db.session.add(found_item)
        db.session.commit()

        flash('Your found item report has been created successfully! Thank you for using the app.', 'success')
        return redirect(url_for('main.home'))

    return render_template('report_found.html')

# Search route
@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        # Query lost items based on search term
        lost_items = LostItem.query.filter(
            LostItem.description.contains(search_term) |
            LostItem.location.contains(search_term)
        ).all()

        # Query found items based on search term, include user information
        found_items = FoundItem.query.filter(
            FoundItem.description.contains(search_term) |
            FoundItem.location.contains(search_term)
        ).options(db.joinedload(FoundItem.user)).all()

        return render_template('search_results.html',
                               lost_items=lost_items,
                               found_items=found_items,
                               search_term=search_term)

    # If it's a GET request (initial load), render the search form
    return render_template('search.html')

