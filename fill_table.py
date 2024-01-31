import requests
import random

# Replace 'http://<Django app URL>' with the base URL of your Django app (e.g., 'http://localhost:8000')
base_url = 'http://127.0.0.1:8000/datatb/product/'

# Define the endpoint URL
endpoint_url = 'add'

url = base_url + endpoint_url

# Generate random values for the input fields
random_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
random_info = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
random_price = random.randint(1, 100)

# Define the form data with random values
form_data = {
    'name': random_name,
    'info': random_info,
    'price': random_price
}

# Define the headers with cookies
headers = {
    'Cookie': 'csrftoken=5vvs6151ScRQGpdMlKAf8FAFERO67MmK; sessionid=c35o5m7xkymbjdtcu9k916f8jfj2f8x7'
}

try:
    response = requests.post(url, headers=headers, data=form_data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Request successful!")
        # Process the response data as needed
        print("Response:")
        print(response.text)

    else:
        print(f"Request failed with status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
