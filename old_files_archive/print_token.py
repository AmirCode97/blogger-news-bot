
import pickle
import base64
import os

if os.path.exists('token_auth_fixed.pickle'):
    with open('token_auth_fixed.pickle', 'rb') as f:
        creds = pickle.load(f)
    pickled = pickle.dumps(creds)
    b64 = base64.b64encode(pickled).decode('utf-8')
    print("---TOKEN_START---")
    print(b64)
    print("---TOKEN_END---")
else:
    print("ERROR: token_auth_fixed.pickle not found.")
