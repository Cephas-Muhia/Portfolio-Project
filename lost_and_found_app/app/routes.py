from flask import Blueprint, render_template, request, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

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

@main.route('/')
@main.route('/home')
def home():
    return render_template('index.html')

@main.route('/register')
def register():
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form submission
        email = request.form.get('email')
        password = request.form.get('password')

        # Example: Check login credentials (replace with your logic)
        if email == 'user@example.com' and password == 'password':
            # Example: Redirect to home page after successful login
            return redirect(url_for('main.home'))
        else:
            # Example: Handle invalid login (redirect to login page with message)
            return redirect(url_for('main.login'))

    # GET request: Render the login form
    return render_template('login.html')
@main.route('/facebook-login', methods=['GET', 'POST'])
def facebook_login():
    # Implementation of your Facebook login logic
    return render_template('facebook_login.html')
@main.route('/google-login', methods=['GET', 'POST'])
def google_login():
    if request.method == 'POST':
        # Handle form submission (if needed for Google login form)
        pass
        # Replace with your Google login logic if necessary

    # GET request: Render the Google login form
    return render_template('google_login.html')  

@main.route('/report_lost')
def report_lost():
    return render_template('report_lost.html')

@main.route('/report_found')
def report_found():
    return render_template('report_found.html')

@main.route('/search')
def search():
    return render_template('search.html')

@main.route('/google_auth')
def google_auth():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    return f'You are {resp.json()["displayName"]} on Google'

@main.route('/facebook_auth')
def facebook_auth():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/me?fields=name,email')
    assert resp.ok, resp.text
    return f'You are {resp.json()["name"]} on Facebook'

