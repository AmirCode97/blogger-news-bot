
import os
import pickle
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def check_auth():
    print("Checking Blogger Authentication...")
    creds = None
    
    # Try loading from file
    if os.path.exists('token_auth_fixed.pickle'):
        print("Found token_auth_fixed.pickle")
        with open('token_auth_fixed.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds:
        print("No local token found.")
        return
    
    print(f"Token Valid: {creds.valid}")
    print(f"Token Expired: {creds.expired}")
    if creds.refresh_token:
        print("Refresh token exists.")
    else:
        print("No refresh token!")

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("Attempting to refresh token...")
            try:
                creds.refresh(Request())
                print("Token refreshed successfully!")
                with open('token_auth_fixed.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                
                # Update base64 for GitHub
                pickled = pickle.dumps(creds)
                b64 = base64.b64encode(pickled).decode('utf-8')
                print("\nSUCCESS! New BLOGGER_TOKEN_BASE64 for GitHub:")
                print("="*40)
                print(b64)
                print("="*40)
            except Exception as e:
                print(f"Refresh failed: {e}")
                print("\nCRITICAL: You need to re-authenticate manually.")
        else:
            print("Token is invalid and cannot be refreshed.")

if __name__ == "__main__":
    check_auth()
