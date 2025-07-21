#!/usr/bin/env python3
"""
GitHub Actions script to automatically update PIN codes and shortened links.
This script:
1. Generates a random 4-digit PIN code
2. Creates a Pastebin paste with the PIN (24-hour expiration)
3. Creates a shortened URL from the Pastebin link
4. Updates the target repository file with new values
"""

import os
import sys
import json
import random
import requests
import re
from datetime import datetime
from urllib.parse import urlencode

class PinUpdater:
    def __init__(self):
        # Environment variables and configuration
        self.pastebin_api_key = os.getenv('PASTEBIN_API_KEY')
        self.pastebin_user_key = os.getenv('PASTEBIN_USER_KEY', '')
        self.shortener_api_key = os.getenv('SHORTENER_API_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Target repository and file
        self.target_repo = os.getenv('TARGET_REPO', 'sandy2k25/wbn1')
        self.target_file = os.getenv('TARGET_FILE', 'index.html')
        
        # API endpoints
        self.pastebin_api_url = 'https://pastebin.com/api/api_post.php'
        self.github_api_base = 'https://api.github.com'
        
        # Validate required environment variables
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate that all required environment variables are set."""
        required_vars = {
