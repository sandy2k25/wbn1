#!/usr/bin/env python3

import os
import requests
import base64
import json
import random
from datetime import datetime
import time

class PinUpdater:
    def __init__(self):
        self.github_token = os.environ.get('HUB_TOKEN')
        self.pastebin_api_key = os.environ.get('PASTEBIN_API_KEY')
        self.shortener_api_key = os.environ.get('SHORTENER_API_KEY')
        self.target_repo = os.environ.get('TARGET_REPO', 'sandy2k25/wbn1')
        self.target_file = os.environ.get('TARGET_FILE', 'index.html')
        
        self.github_api_base = "https://api.github.com"
        
        self.validate_environment()
    
    def validate_environment(self):
        """Validate required environment variables."""
        required_vars = {
            'GITHUB_TOKEN': self.github_token,
            'PASTEBIN_API_KEY': self.pastebin_api_key,
            'SHORTENER_API_KEY': self.shortener_api_key
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            exit(1)
        
        print("✅ Environment variables validated successfully")
    
    def generate_pin(self):
        """Generate a random 4-digit PIN."""
