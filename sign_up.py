import requests

# Replace 'http://<Django app URL>' with the base URL of your Django app (e.g., 'http://localhost:8000')
base_url = 'http://127.0.0.1:8000'

# Define the registration endpoint
registration_endpoint = '/accounts/register/'

# Combine the base URL and registration endpoint to form the complete URL
registration_url = base_url + registration_endpoint

# Define the user data for registration
user_data = {
    'username': 'john',
    'email': 'john@example.com',
    'password1': 'MyPassword123',
    'password2': 'MyPassword123'  # Confirm password
}

try:
    # Send a POST request to the registration endpoint with the user data
    response = requests.post(registration_url, data=user_data)
    # Check if the request was successful (status code 200 or 201 for successful creation)
    if response.status_code in (200, 201):
        print("User registration successful!")
        # Print the response content (token or confirmation message)
        print("Response:")
        print(response.text)
    else:
        print(f"User registration failed with status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print("User registration request failed:", e)
