# api/index.py
import os
import json
import time
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

# ENV variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "quickbooks")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "tokens")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION]

@app.route('/')
def home():
    return '✅ Flask backend running on Vercel with MongoDB!'

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

    # Save tokens in MongoDB with realm_id as identifier
    collection.update_one(
        {"realm_id": realm_id},
        {"$set": {**tokens, "realm_id": realm_id}},
        upsert=True
    )

    return jsonify({"status": "✅ Tokens saved to MongoDB", "realm_id": realm_id})

