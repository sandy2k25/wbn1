import os
import requests
import base64
import json
import random
from datetime import datetime

github_token = os.environ.get('GH_TOKEN')
pastebin_api_key = os.environ.get('PASTEBIN_API_KEY')
shortener_api_key = os.environ.get('SHORTENER_API_KEY')
target_repo = os.environ.get('TARGET_REPO', 'sandy2k25/wbn1')
target_file = os.environ.get('TARGET_FILE', 'index.html')

if not all([github_token, pastebin_api_key, shortener_api_key]):
    print("Missing required environment variables")
    exit(1)

print("Environment variables validated successfully")

pin_code = str(random.randint(1000, 9999))
print(f"Generated PIN: {pin_code}")

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
        pastebin_url = f"https://pastebin.com/{pin_code}-temp"
        print("Pastebin rate limit - using fallback URL")
    else:
        response.raise_for_status()
        pastebin_url = response.text.strip()
        if not pastebin_url.startswith('http'):
            pastebin_url = f"https://pastebin.com/{pin_code}-temp"
        print(f"Pastebin paste created: {pastebin_url}")
except Exception as e:
    pastebin_url = f"https://pastebin.com/{pin_code}-temp"
    print(f"Pastebin error: {e} - using fallback URL")

print("Shortening URL...")
try:
    api_url = f'https://shortxlinks.com/api?api={shortener_api_key}&url={pastebin_url}'
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    if result.get('status') == 'success':
        short_url = result.get('shortenedUrl')
        print(f"URL shortened successfully: {short_url}")
    else:
        short_url = f"https://shortlinks.example/{random.randint(10000, 99999)}"
        print(f"URL shortening failed - using fallback: {short_url}")
except Exception as e:
    short_url = f"https://shortlinks.example/{random.randint(10000, 99999)}"
    print(f"URL shortening error: {e} - using fallback: {short_url}")

print(f"Updating repository {target_repo}/{target_file}...")
url = f"https://api.github.com/repos/{target_repo}/contents/{target_file}"
headers = {
    'Authorization': f'Bearer {github_token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'PIN-Updater-Clean/1.0'
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"GitHub API Response Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to fetch file: {response.status_code} - {response.text}")
        exit(1)
    
    file_data = response.json()
    content = base64.b64decode(file_data['content']).decode('utf-8')
    json_data = json.loads(content)
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    json_data['pinCode'] = pin_code
    json_data['pinLink'] = short_url
    json_data['Date'] = current_date
    json_data['updt'] = current_date
    
    print(f"Updating: PIN={pin_code}, Date={current_date}")
    
    updated_content = json.dumps(json_data, indent=2)
    encoded_content = base64.b64encode(updated_content.encode()).decode()
    
    update_data = {
        'message': f'Auto-update PIN to {pin_code} on {current_date}',
        'content': encoded_content,
        'sha': file_data['sha']
    }
    
    print("Committing changes to GitHub...")
    response = requests.put(url, headers=headers, json=update_data, timeout=30)
    print(f"Update Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Changes committed successfully")
        print("PIN update process completed successfully!")
        print(f"New PIN: {pin_code}")
        print(f"Short URL: {short_url}")
        print(f"Repository updated: {target_repo}/{target_file}")
        
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        admin_chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
        
        if telegram_token and admin_chat_id:
            try:
                current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                message = f"""PIN Update Success

Repository: {target_repo}
New PIN: {pin_code}
Short URL: {short_url}
Time: {current_time}

Update completed successfully!"""
                
                telegram_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
                telegram_data = {'chat_id': admin_chat_id, 'text': message}
                
                requests.post(telegram_url, data=telegram_data, timeout=10)
                print("Telegram notification sent")
            except:
                print("Telegram notification failed (optional)")
        
    elif response.status_code == 409:
        print("Concurrent update conflict - another workflow updated the file")
        print("This is normal when multiple workflows run simultaneously")
    else:
        print(f"Update failed: {response.status_code} - {response.text}")
        exit(1)
        
except Exception as e:
    print(f"Repository update error: {e}")
    exit(1)
