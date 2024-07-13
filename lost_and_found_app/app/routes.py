from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from . import db
from .models import User, LostItem, FoundItem
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 
from werkzeug.utils import secure_filename
import os

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
         return redirect(url_for('main.profile'))  # Redirect to profile if already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=request.form.get('remember', False))
                flash('Logged in successfully.', 'success')
                return redirect(url_for('main.profile'))  # Redirect to profile if already logged in
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
    return redirect(url_for('main.profile'))  # Redirect to profile if login is succesiful


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
    return redirect(url_for('main.profile'))  # Redirect to profile if login is succesiful


@main.route('/profile')
@login_required  # Ensures user must be logged in to access this route
def profile():
     # Fetch user details from the database using current_user.id
    user = User.query.get(current_user.id)
    if user:
        return render_template('profile.html', user=user)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('main.home'))  # Redirect to home or another page if user is not found


# Report lost item route
@main.route('/report_lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        # Debugging statements for form data
        print("Received POST request for reporting lost item")
        description = request.form.get('description')
        location = request.form.get('location')
        date_lost_str = request.form.get('date_lost')
        print(f"Description: {description}, Location: {location}, Date Lost: {date_lost_str}")

        date_reported = datetime.strptime(date_lost_str, '%Y-%m-%d') if date_lost_str else datetime.utcnow()
        print(f"Date Reported: {date_reported}")

        photo = request.files['photo']
        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('static/uploads', filename)
            print(f"Photo received: {photo}")
            print(f"Photo path: {photo_path}")  # Debugging statement
            try:
                photo.save(photo_path)
                print("Photo saved successfully")
                photo_url = url_for('static', filename=f'uploads/{filename}')
                print(f"Photo URL: {photo_url}")
            except Exception as e:
                print(f"Error saving photo: {e}")
        else:
            photo_path = None
            photo_url = None
            print("No photo received")

        try:
            lost_item = LostItem(description=description, location=location, photo=photo_path, user_id=current_user.id, date_reported=date_reported)
            db.session.add(lost_item)
            db.session.commit()
            print("Lost item added to the database successfully")
        except Exception as e:
            print(f"Error adding lost item to the database: {e}")

        flash('Your lost item report has been created successfully! Thank you for using the app.', 'success')
        return redirect(url_for('main.profile'))

    print("GET request for reporting lost item")
    return render_template('report_lost.html')


# Report found items route
@main.route('/report_found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        # Debugging statements for form data
        print("Received POST request for reporting found item")
        description = request.form.get('description')
        location = request.form.get('location')
        date_found_str = request.form.get('date_found')
        print(f"Description: {description}, Location: {location}, Date Found: {date_found_str}")

        date_reported = datetime.strptime(date_found_str, '%Y-%m-%d') if date_found_str else datetime.utcnow()
        print(f"Date Reported: {date_reported}")

        photo = request.files['photo']
        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('static/uploads', filename)
            print(f"Photo received: {photo}")
            print(f"Photo path: {photo_path}")  # Debugging statement
            try:
                photo.save(photo_path)
                print("Photo saved successfully")
                photo_url = url_for('static', filename=f'uploads/{filename}')
                print(f"Photo URL: {photo_url}")
            except Exception as e:
                print(f"Error saving photo: {e}")
        else:
            photo_path = None
            photo_url = None
            print("No photo received")

        try:
            found_item = FoundItem(description=description, location=location, photo=photo_path, user_id=current_user.id, date_reported=date_reported)
            db.session.add(found_item)
            db.session.commit()
            print("Found item added to the database successfully")
        except Exception as e:
            print(f"Error adding found item to the database: {e}")

        flash('Your found item report has been created successfully! Thank you for using the app.', 'success')
        return redirect(url_for('main.profile'))

    print("GET request for reporting found item")
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

