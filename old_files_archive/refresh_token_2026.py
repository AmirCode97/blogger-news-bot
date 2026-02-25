
import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import GOOGLE_CREDENTIALS_FILE

# Scopes needed for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

def generate_new_token():
    print("[INFO] Starting Guest Re-Authentication Flow...")
    
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        print(f"[ERROR] {GOOGLE_CREDENTIALS_FILE} not found!")
        return

    # Run the OAuth Flow
    flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
    # Using a fixed port to make it easier to handle
    creds = flow.run_local_server(port=8080, prompt='consent')

    # Save to pickle
    token_name = 'token_auth_fixed.pickle'
    with open(token_name, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"[OK] Successfully saved new token to {token_name}")

    # Generate Base64 for GitHub Secrets
    with open(token_name, 'rb') as token_file:
        content = token_file.read()
        encoded = base64.b64encode(content).decode('utf-8')
        
    print("\n" + "="*60)
    print(" >>> COPY THIS KEY FOR GITHUB SECRET (BLOGGER_TOKEN_BASE64) <<<")
    print("="*60)
    print(encoded)
    print("="*60 + "\n")
    print("1. Go to your GitHub Repository Settings")
    print("2. Secrets and variables -> Actions")
    print("3. Update 'BLOGGER_TOKEN_BASE64' with the code above.")
    print("4. Re-run your GitHub Action.")

if __name__ == "__main__":
    generate_new_token()
