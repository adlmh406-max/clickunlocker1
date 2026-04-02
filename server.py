# server.py - الموجود عندك
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
KEYS_FILE = 'keys.json'

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(keys, f, indent=4)

@app.route('/verify-key', methods=['POST'])
def verify_key():
    try:
        data = request.get_json()
        key = data.get('key')
        hwid = data.get('hwid')
        
        print(f"📝 Key: {key}")
        print(f"🖥️ HWID: {hwid}")
        
        keys = load_keys()
        
        if key not in keys:
            return jsonify({"status": "invalid"})
        
        license_data = keys[key]
        
        expiry = license_data.get('expiry')
        if expiry:
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
            if expiry_date < datetime.now():
                return jsonify({"status": "expired"})
        
        saved_hwid = license_data.get('hwid')
        if saved_hwid and saved_hwid != hwid:
            return jsonify({"status": "wrong_device"})
        
        if not saved_hwid:
            license_data['hwid'] = hwid
            license_data['activated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_keys(keys)
            print(f"✅ Key activated")
        
        return jsonify({"status": "valid"})
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error"})

@app.route('/')
def index():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)