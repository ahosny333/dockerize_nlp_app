from flask import Flask, request, render_template, jsonify,url_for, flash,redirect
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from extensions import db
from models import User
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load API key from environment
API_KEY = os.getenv('API_KEY')
db_url = os.getenv('DB_URL')
secret_key = os.getenv('secret_key')
print(db_url)
print(API_KEY)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

# Initialize the database with the Flask app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create the database tables
with app.app_context():
    db.create_all()

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Route to redirect unauthorized users

# Load the user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
@login_required  # Protect this route
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Call the MeaningCloud API
        response = requests.post(
            'https://api.meaningcloud.com/sentiment-2.1',
            data={'key': API_KEY, 'url': url, 'lang': 'en'}
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to contact MeaningCloud API"}), 500

        api_response = response.json()
        # print(api_response)
        # Extract meaningful fields
        result = {
            "score_tag": api_response.get("score_tag", "NONE"),
            "agreement": api_response.get("agreement", "UNKNOWN"),
            "subjectivity": api_response.get("subjectivity", "UNKNOWN"),
            "confidence": api_response.get("confidence", 0),
            "irony": api_response.get("irony", "UNKNOWN"),
        }

        return jsonify(result)
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            login_user(user)  # Log the user in
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')  # Get the next page from the query string
            return redirect(next_page or url_for('index'))  # Redirect to the next page or home
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate input
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
        else:
            # Create a new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)  # Hash the password
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required  # Protect this route
def logout():
    logout_user()  # Log the user out
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
