from flask import Flask, request, render_template, jsonify
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from extensions import db
from models import User

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load API key from environment
API_KEY = os.getenv('API_KEY')
db_url = os.getenv('DB_URL')
print(db_url)
print(API_KEY)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
