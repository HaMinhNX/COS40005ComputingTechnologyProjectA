
import requests
import json

base_url = "http://127.0.0.1:8001/api"

# Login
login_data = {"username": "doctor1", "password": "123"}
response = requests.post(f"{base_url}/login", json=login_data)
print(f"Login status: {response.status_code}")
data = response.json()
token = data.get("access_token")
print(f"Token: {token[:10]}...")

# Get patients
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{base_url}/patients", headers=headers)
print(f"Get patients status: {response.status_code}")
if response.status_code != 200:
    print(f"Error detail: {response.json()}")
else:
    print("Success!")
