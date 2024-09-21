import requests

base_url = "http://127.0.0.1:8000"

def create(name, age, email, password):
    url = f"{base_url}/accounts/"
    data = {
        "name": name,
        "age": age,
        "email": email,
        "password": password
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"Added Account: {response.json()}")
        return response.json()
    else:
        print(f"Failed to Add Account: {response.status_code}")
        return None


def read_all():
    url = f"{base_url}/accounts/"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"All Customer Accounts: {response.json()}")
        return response.json()
    else:
        print(f"Failed to Get All Accounts: {response.status_code}")
        return None


def read_one(account_id):
    url = f"{base_url}/accounts/{account_id}"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Customer Account: {response.json()}")
        return response.json()
    else:
        print(f"Failed to Get Account: {response.status_code}")
        return None

def read_by_email(email):
    url = f"{base_url}/accounts/{email}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None


def update(account_id, name=None, age=None, email=None, password=None):
    url = f"{base_url}/accounts/{account_id}"
    new_data = {}
    if name is not None:
        new_data["name"] = name
    if age is not None:
        new_data["age"] = age
    if email is not None:
        new_data["email"] = email
    if password is not None:
        new_data["password"] = password
    response = requests.put(url, json=new_data)
    if response == 200:
        print(f"Account Info Updated: {response.json()}")
        return response.json()
    else:
        print(f"Failed to Update Account Info: {response.status_code}")
        return None


def delete(account_id):
    url = f"{base_url}/accounts/{account_id}"
    response = requests.delete(url)
    if response == 200:
        print(f"Deleted Account: {response.json()}")
        return response.json()
    else:
        print(f"Failed to Delete Account: {response.status_code}")
        return None
