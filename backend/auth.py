from flask import Blueprint, request, jsonify
import requests
import jwt
import datetime
import os
import json
from os.path import expanduser

auth_bp = Blueprint('auth', __name__)
CREDENTIALS_FILE = expanduser('~/.brain_credentials')
SECRET_KEY = os.getenv('JWT_SECRET', 'super-secret-key-for-dev')

login_sessions = {}

def _do_login(email, password):
    try:
        s = requests.Session()
        s.auth = (email, password)
        response = s.post(
            'https://api.worldquantbrain.com/authentication',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        print(f'Auth Status Code: {response.status_code}', flush=True)
        
        if response.status_code == 201:
            wq_token = s.cookies.get('t', '')
            token = jwt.encode({
                'user': email,
                'wq_token': wq_token,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')
            return jsonify({"message": "Login successful", "token": token}), 200
        elif response.status_code == 401:
            if response.headers.get("WWW-Authenticate") == "persona":
                loc = response.headers.get("Location")
                login_sessions[email] = (s, loc)
                return jsonify({"error": "biometrics", "url": f"https://api.worldquantbrain.com{loc}", "email": email}), 401
            try:
                err_data = response.json()
                if 'recaptcha' in err_data:
                    return jsonify({"error": "reCAPTCHA required. You have had too many attempts."}), 401
                return jsonify({"error": f"API Rejected: {err_data.get('detail', 'Unknown 401')}"}), 401
            except:
                return jsonify({"error": f"Invalid WorldQuant credentials. Response: {response.text}"}), 401
        else:
            return jsonify({"error": f"Unexpected error: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/credentials/check', methods=['GET'])
def check_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                creds = json.load(f)
                if isinstance(creds, list) and len(creds) >= 2:
                    return jsonify({"exists": True, "email": creds[0]})
        except Exception:
            pass
    return jsonify({"exists": False})

@auth_bp.route('/login/saved', methods=['POST'])
def login_saved():
    if not os.path.exists(CREDENTIALS_FILE):
        return jsonify({"error": "No saved credentials found"}), 400
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
            email, password = creds[0], creds[1]
        return _do_login(email, password)
    except Exception:
        return jsonify({"error": "Failed to read saved credentials"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    return _do_login(email, password)

@auth_bp.route('/login/biometrics', methods=['POST'])
def login_biometrics():
    data = request.json
    email = data.get('email')
    if email not in login_sessions:
        return jsonify({"error": "No pending biometrics session found. Please try logging in again."}), 400
        
    s, loc = login_sessions[email]
    try:
        try:
            response = s.post(f"https://api.worldquantbrain.com{loc}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            print(f"Biometrics completion status: {response.status_code}")
        except requests.exceptions.ConnectionError as ce:
            print(f"Connection aborted by server: {ce}")
            # Fallback: re-authenticate directly. Since s.auth is set, it will try logging in normally.
            response = s.post('https://api.worldquantbrain.com/authentication', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            print(f"Fallback auth status: {response.status_code}")
        
        wq_token = s.cookies.get('t', '')
        if response.status_code in [200, 201, 204] or wq_token:
            token = jwt.encode({
                'user': email,
                'wq_token': wq_token,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')
            del login_sessions[email]
            return jsonify({"message": "Login successful", "token": token}), 200
        else:
            return jsonify({"error": "Biometrics not completed or failed. Please ensure you completed the scan in your browser."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
