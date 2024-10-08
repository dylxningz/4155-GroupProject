from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, get_flashed_messages
import requests
from flask import flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

@app.route('/set-session', methods=['POST'])
def set_session():
    data = request.get_json()

    # Debugging: Check what data is received
    print(f"Data received: {data}")

    if 'email' not in data:
        return jsonify({'message': 'Email not provided'}), 400  # Return error if email is missing

    session['email'] = data['email']  # Set the session with the user's email
    session['username'] = data['email'].split('@')[0]  # Extract username from email
    return jsonify({'message': 'Session set'}), 200
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

        response = requests.post('http://127.0.0.1:8000/accounts', json={
            'name': name,
            'email': email,
            'password': password
        })

        if response.status_code == 201:
            flash('Sign-up successful! Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Sign-up failed. Please try again.')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Send the login data to FastAPI
        response = requests.post('http://127.0.0.1:8000/accounts/login', data={
            'username': email,
            'password': password
        })

        if response.status_code == 200:
            data = response.json()
            session['email'] = data['email']
            session['username'] = email.split('@')[0]  # Username from email

            # Set the flash message before redirecting
            flash(f"Welcome {session['username']}, you have been successfully logged in.", "success")
            print("Flash message before redirect:", get_flashed_messages(with_categories=True))  # Debugging

            return redirect(url_for('dashboard'))  
        else:
            flash('Login failed: Wrong email and/or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    messages = get_flashed_messages(with_categories=True)
    print("Flash messages:", messages)
    print("Current session data:", session.get('email'), session.get('username'))  # Debugging: Check session data
    
    return render_template('dashboard.html')

# Route for creating a new item (listing)
@app.route('/create-item', methods=['GET', 'POST'])
def create_item():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        # Send data to FastAPI
        formData = {
            'title': title,
            'description': description,
            'price': float(price),
            'user_id': 1  # Replace with actual user ID or fetch from session
        }
        response = requests.post('http://127.0.0.1:8000/listings', json=formData)

        if response.status_code == 201:
            flash('Listing created successfully!', 'success')
            return redirect(url_for('items'))
        else:
            flash('Failed to create listing. Please try again.')

    return render_template('itemcreate.html')

# Route for displaying all items (listings)
@app.route('/items')
def items():
    # Fetch listings from FastAPI
    response = requests.get('http://127.0.0.1:8000/listings')
    listings = response.json() if response.status_code == 200 else []
    return render_template('items.html', listings=listings)

# Route for item details
@app.route('/item/<int:item_id>')
def item_detail(item_id):
    return render_template('item.html')

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



# Route for fetching all listings (to be used by the front-end in items.html)
@app.route('/listings')
def get_listings():
    # Assuming you're making a request to the FastAPI backend here
    response = requests.get('http://127.0.0.1:8000/listings')
    return jsonify(response.json())



# Route for fetching a single listing by ID (to be used by the front-end in item.html)
@app.route('/listings/<int:item_id>')
def get_listing(item_id):
    # Assuming you're making a request to the FastAPI backend here
    response = requests.get(f'http://127.0.0.1:8000/listings/{item_id}')
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)