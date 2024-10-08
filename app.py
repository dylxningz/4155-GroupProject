from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, get_flashed_messages
import requests
from flask import flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

@app.route('/set-session', methods=['POST'])
def set_session():
    data = request.json

    if 'id' in data and 'email' in data and 'name' in data:
        session['id'] = data['id']  
        session['email'] = data['email']  
        session['name'] = data['name'] 
        session['username'] = data['email'].split('@')[0] 

        print(f"Session data set: id={session['id']}, name={session['name']}, email={session['email']}")
        return jsonify({"message": "Session data set successfully"})
    else:
        print(f"Error: 'id', 'email', or 'name' not found in session data")
        return jsonify({"error": "Missing session data"}), 400
    
@app.route('/get-session', methods=['GET'])
def get_session():
    if 'id' in session:  
        return jsonify({
            "id": session['id'],  
            "email": session['email']  
        })
    else:
        return jsonify({"error": "No user session found"}), 400
# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test-session')
def test_session():
    return jsonify(dict(session))

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
        session.clear()  
        email = request.form.get('email')
        password = request.form.get('password')

        response = requests.post('http://127.0.0.1:8000/accounts/login', data={
            'username': email,
            'password': password
        })

        if response.status_code == 200:
            data = response.json()
            session['email'] = data['email']
            session['name'] = data['name']
            session['id'] = data['id']
            session['username'] = email.split('@')[0]
            
            print(f"Session after login: {dict(session)}")
            
            flash(f"Welcome {session['username']}, you have been successfully logged in.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed: Wrong email and/or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    messages = get_flashed_messages(with_categories=True)
    
    return render_template('dashboard.html', user_id=session.get('id'))

# Route for creating a new item (listing)
@app.route('/create-item', methods=['GET', 'POST'])
def create_item():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        user_id = session.get('id')

        if not user_id:
            flash('You need to be logged in to create a listing.', 'danger')
            return redirect(url_for('login'))

        formData = {
            'title': title,
            'description': description,
            'price': float(price),
            'user_id': user_id
        }

        response = requests.post('http://127.0.0.1:8000/listings', json=formData)

        if response.status_code == 201:
            flash('Listing created successfully!', 'success')
            return redirect(url_for('items'))
        else:
            flash('Failed to create listing. Please try again.', 'danger')
            print(f"Error from FastAPI: {response.json()}")  # Debugging

    return render_template('itemcreate.html')

@app.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        # Update the item with the new data
        formData = {
            'title': title,
            'description': description,
            'price': float(price)
        }

        response = requests.put(f'http://127.0.0.1:8000/listings/{item_id}', json=formData)

        if response.status_code == 200:
            flash('Item updated successfully!', 'success')
            return redirect(url_for('items'))
        else:
            flash('Failed to update item. Please try again.', 'danger')

    response = requests.get(f'http://127.0.0.1:8000/listings/{item_id}')
    if response.status_code == 200:
        item = response.json()
        return render_template('itemedit.html', item=item)
    else:
        flash('Item not found.', 'danger')
        return redirect(url_for('items'))

@app.route('/delete-item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    response = requests.delete(f'http://127.0.0.1:8000/listings/{item_id}')
    if response.status_code == 204:
        flash('Item deleted successfully!', 'success')
    else:
        flash('Failed to delete item. Please try again.', 'danger')

    return redirect(url_for('items'))


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