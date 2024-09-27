# app.py
from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Secret key for session management
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in the filesystem
Session(app)

# Schwab OAuth configuration
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'sNk6C2navgsc9hUU'
AUTHORIZATION_BASE_URL = 'https://api.schwab.com/oauth/authorize'
TOKEN_URL = 'https://api.schwab.com/oauth/token'
REDIRECT_URI = 'https://878a-100-36-156-86.ngrok-free.app/callback'

@app.route('/')
def home():
    return 'Welcome to the Schwab OAuth Integration!'

@app.route('/login')
def login():
    authorization_url = f"{AUTHORIZATION_BASE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Error: No code received', 400

    # Exchange the code for an access token
    token_response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    token_response_data = token_response.json()
    if 'access_token' not in token_response_data:
        return 'Error: No access token received', 400

    # Store the access token in the session
    session['access_token'] = token_response_data['access_token']
    return 'OAuth flow completed successfully!'

if __name__ == "__main__":
    app.run(port=8000)  # Make sure the port matches your ngrok setup
