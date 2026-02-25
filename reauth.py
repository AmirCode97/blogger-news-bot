
import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']
GOOGLE_CREDENTIALS_FILE = 'credentials.json'

def re_authenticate():
    print("="*60)
    print("RE-AUTHENTICATION STARTED")
    print("="*60)
    print("A browser window should open shortly. Please login and grant permission.")
    
    flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080, prompt='consent')
    
    # Save the new token locally
    with open('token_auth_fixed.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    # Generate the base64 for GitHub
    pickled = pickle.dumps(creds)
    b64 = base64.b64encode(pickled).decode('utf-8')
    
    print("\n" + "="*60)
    print("SUCCESS! LOCAL TOKEN UPDATED")
    print("="*60)
    print("\nNow, follow these steps to fix GitHub Actions:")
    print("1. Go to your GitHub Repository: AmirCode97/blogger-news-bot")
    print("2. Go to Settings -> Secrets and variables -> Actions")
    print("3. Find the secret named: BLOGGER_TOKEN_BASE64")
    print("4. Click Edit and paste the code below:")
    print("\n" + b64 + "\n")
    print("="*60)
    print("Once updated, GitHub Actions will work again.")

if __name__ == "__main__":
    re_authenticate()
