#!/usr/bin/env python3
"""
PIN Update System - Final Version
Simple, reliable PIN generation and repository updates
"""

import os
import requests
import base64
import json
import random
from datetime import datetime

def main():
    # Required environment variables
    github_token = os.environ.get('GH_TOKEN')
    pastebin_api_key = os.environ.get('PASTEBIN_API_KEY')
    shortener_api_key = os.environ.get('SHORTENER_API_KEY')
    target_repo = os.environ.get('TARGET_REPO', 'sandy2k25/wbn1')
    target_file = os.environ.get('TARGET_FILE', 'index.html')
    
    # Validate required variables
    if not all([github_token, pastebin_api_key, shortener_api_key]):
        print("Missing required environment variables")
        exit(1)
    
    print("Environment variables validated successfully")
    
    # Generate PIN
    pin_code = str(random.randint(1000, 9999))
    print(f"Generated PIN: {pin_code}")
    
    # Create Pastebin paste
    print("Creating Pastebin paste...")
    pastebin_data = {
        'api_dev_key': pastebin_api_key,
        'api_option': 'paste',
        'api_paste_code': f'Your PIN: {pin_code}',
        'api_paste_name': f'PIN Code {pin_code}',
        'api_paste_expire_date': '1D',
        'api_paste_private': '1'
    }
    
    try:
        response = requests.post('https://pastebin.com/api/api_post.php', data=pastebin_data, timeout=30)
        if response.status_code == 422:
