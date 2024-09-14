import requests

BASE_URL = "https://storage.rcs-rds.ro/api/v2"

def get_auth_token(email, password):
    url = f"{BASE_URL}/token"
    headers = {
        "Accept": "*/*",
        "X-Koofr-Password": password,
        "X-Koofr-Email": email
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.headers.get("X-Koofr-Token")
    else:
        return None

def get_user_info(token):
    url = f"{BASE_URL}/user"
    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
