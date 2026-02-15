# login.py

from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import os

# Step 1: Load the environment variables from the .env file
load_dotenv()

# Step 2: Get the credentials from .env
api_key = os.getenv("API_KEY")
client_code = os.getenv("CLIENT_CODE")
password = os.getenv("CLIENT_PASSWORD")
totp = os.getenv("TOTP")

# Step 3: Initialize SmartConnect with your API key
obj = SmartConnect(api_key=api_key)

# Step 4: Try to generate a session (login)
try:
    data = obj.generateSession(client_code, password, totp)
    refresh_token = data['data']['refreshToken']
    print(" Login Successful!")
    print("Client Code:", client_code)
    print("Feed Token:", obj.getfeedToken())
    print("Refresh Token:", refresh_token)

except Exception as e:
    print("Login Failed!")
    print("Error:", e)