from flask import Flask, render_template, request, jsonify
import requests
from flask import flash, redirect, url_for

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Signup data: name={name}, email={email}, password={password}")  # Debugging

        # Make a request to FastAPI's sign-up endpoint
        response = requests.post('http://127.0.0.1:8000/accounts', json={
            'name': name,
            'email': email,
            'password': password
        })

        # Debugging: Print the response status and data
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 201:
            flash('Sign-up successful! Please log in.')
            return redirect(url_for('login'))  # Redirect to login page
        else:
            flash('Sign-up failed. Please try again.')
            print(f"Error details: {response.json()}")  # Print the error details for debugging

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Send the login data to FastAPI (with plain text password)
        response = requests.post('http://127.0.0.1:8000/accounts/login', data={
            'username': email,
            'password': password
        })

        if response.status_code == 200:
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials.')
            print(f"Error: {response.text}")

    return render_template('login.html')

# Route for user dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route for user profile
@app.route('/userProfile')
def userProfile():
    return render_template('userProfile.html')

# Route for user settings
@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/api/signup', methods=['POST'])
def user_signup():
    pass

@app.route('/api/login', methods=['GET'])
def user_login():
    pass

# Route for rendering the items list page
@app.route('/items')
def items():
    return render_template('items.html')

# Route for fetching all listings (to be used by the front-end in items.html)
@app.route('/listings')
def get_listings():
    # Assuming you're making a request to the FastAPI backend here
    response = requests.get('http://127.0.0.1:8000/listings')
    return jsonify(response.json())

@app.route('/create-item', methods=['GET', 'POST'])
def create_item():
    if request.method == 'POST':
        # Extract form data
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        # Prepare the data to be sent to FastAPI
        formData = {
            'title': title,
            'description': description,
            'price': float(price),
            'user_id': 1  # Replace with actual user ID
        }

        # Send the data to FastAPI's /listings endpoint
        response = requests.post('http://127.0.0.1:8000/listings', json=formData)

        if response.status_code == 201:
            flash('Listing created successfully!', 'success')
            return redirect(url_for('items'))  # Redirect to the items page
        else:
            flash('Failed to create listing. Please try again.', 'danger')

    return render_template('itemcreate.html')


# Route for rendering the item detail page
@app.route('/item/<int:item_id>')
def item_detail(item_id):
    return render_template('item.html')

# Route for fetching a single listing by ID (to be used by the front-end in item.html)
@app.route('/listings/<int:item_id>')
def get_listing(item_id):
    # Assuming you're making a request to the FastAPI backend here
    response = requests.get(f'http://127.0.0.1:8000/listings/{item_id}')
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)