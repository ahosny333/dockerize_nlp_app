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

        # Fetch the article content from the URL
        try:
            article_response = requests.get(url)
            article_response.raise_for_status()
            article_text = article_response.text
        except requests.RequestException as e:
            return jsonify({"error": f"Failed to fetch the article: {e}"}), 500

        # Call Hugging Face Inference API for sentiment analysis
        api_url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        payload = {"inputs": article_text,
		  "options": {"truncation": True}
		  }
        max_characters = 1300  # Adjust this value as needed
        if len(article_text) > max_characters:
            article_text = article_text[:max_characters]
            payload["inputs"] = article_text
        
        response = requests.post(api_url, headers=headers, json=payload)
        print(response.status_code)
        print(response.text)
        if response.status_code != 200:
            return jsonify({"error": "Failed to contact Hugging Face API", "status": response.status_code}), 500

        api_response = response.json()

        # Process the API response. Typically, the response is a list with one dict.
        if isinstance(api_response, list) and len(api_response) > 0:
            predictions = api_response[0]  # Extract the inner list for a single input
            # You can then decide how to use these predictions:
            negative = next((p for p in predictions if p["label"] == "NEGATIVE"), {})
            positive = next((p for p in predictions if p["label"] == "POSITIVE"), {})
            # For example:
            result = {
            "negative_score": negative.get("score", 0),
            "positive_score": positive.get("score", 0)
            }
        else:
            sentiment_result = {}
            result = {
            "negative_score": negative.get("score", 0),
            "positive_score": positive.get("score", 0)
            }


        # Build result similar to your MeaningCloud output if needed.
        #result = {
        #    "label": sentiment_result.get("label", "UNKNOWN"),
        #    "score": sentiment_result.get("score", 0)
        #}

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
