# Flask app goes here 
# api/index.py
import os
import json
import time
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from requests.auth import HTTPBasicAuth

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

@app.route('/')
def home():
    return '✅ Flask backend running on Vercel!'

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    realm_id = request.args.get('realmId')

    if not code:
        return '❌ Missing auth code.', 400

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    res = requests.post(TOKEN_URL, data=data, headers=headers, auth=auth)

    if res.status_code != 200:
        return f'❌ Token exchange failed.\n\n{res.text}', 500

    tokens = res.json()
    tokens['expires_at'] = time.time() + tokens.get('expires_in', 3600)

    return jsonify(tokens)

# if __name__ == '__main__':
#     # Only runs if testing locally
#     app.run(port=8000)
