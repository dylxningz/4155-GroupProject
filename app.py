from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, get_flashed_messages
import requests
from flask import flash, redirect, url_for
import sys
import subprocess
from models.favorite import Favorite
from dependencies.database import db

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
    
@app.route('/set-flash-message', methods=['POST'])
def set_flash_message():
    data = request.json
    message = data.get('message')
    category = data.get('category', 'info')
    flash(message, category)
    return jsonify({"status": "success"})
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


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'id' not in session:
        flash('You need to be logged in to update your profile.', 'danger')
        return redirect(url_for('login'))

    # Get the form data
    user_id = session['id']
    name = request.form.get('name')
    email = request.form.get('email')

    # Send the data to the FastAPI backend
    response = requests.put(f'http://127.0.0.1:8000/accounts/{user_id}', json={
        'name': name,
        'email': email
    })

    if response.status_code == 200:
        flash('Profile updated successfully!', 'success')
        session['name'] = name
        session['email'] = email
    else:
        flash('Error updating profile. Please try again.', 'danger')

    return redirect(url_for('settings'))

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'id' not in session:
        flash('You need to be logged in to change your password.', 'danger')
        return redirect(url_for('login'))

    # Get the form data
    user_id = session['id']
    current_password = request.form.get('current-password')
    new_password = request.form.get('new-password')
    confirm_password = request.form.get('confirm-password')

    # Check if the new password and confirm password match
    if new_password != confirm_password:
        flash('New password and confirm password do not match.', 'danger')
        return redirect(url_for('settings'))

    # Send the data to the FastAPI backend for password change
    response = requests.post(f'http://127.0.0.1:8000/accounts/{user_id}/change-password', json={
        'current_password': current_password,
        'new_password': new_password
    })

    if response.status_code == 200:
        flash('Password changed successfully!', 'success')
    else:
        flash('Error changing password. Please try again.', 'danger')

    return redirect(url_for('settings'))

@app.route('/update-notifications', methods=['POST'])
def update_notifications():
    if 'id' not in session:
        flash('You need to be logged in to update notifications.', 'danger')
        return redirect(url_for('login'))

    # Handle the notification preferences here (mocking it in this case)
    email_notifications = request.form.get('email-notifications') == 'on'
    # Assume backend handles notifications (you can customize this as needed)
    flash('Notification preferences updated!', 'success')

    return redirect(url_for('settings'))

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
@app.route('/conversations')
def conversations():
    user_id = session.get('id')
    if not user_id:
        flash('You need to be logged in to view conversations.', 'danger')
        return redirect(url_for('login'))

    response = requests.get(f'http://127.0.0.1:8000/conversations/?user_id={user_id}')
    
    if response.status_code == 200:
        conversations = response.json()
        return render_template('conversations.html', conversations=conversations)
    else:
        flash('Failed to retrieve conversations. Please try again.', 'danger')
        return redirect(url_for('dashboard'))
    
@app.route('/start-conversation', methods=['GET', 'POST'])
def start_conversation():
    if request.method == 'POST':
        participant_2 = request.form.get('participant_2')
        price = request.form.get('price')
        participant_1 = session.get('id')  # The logged-in user ID

        if not all([participant_1, participant_2, price]):
            flash('Participant and price must be provided.', 'danger')
            return redirect(url_for('start_conversation'))

        conversation_data = {
            'participant_1': participant_1,
            'participant_2': participant_2,
            'price': float(price)
        }

        print(f"Form data sent: {conversation_data}")  # Debug log

        response = requests.post('http://127.0.0.1:8000/conversations', json=conversation_data)

        if response.status_code == 201:
            flash('Conversation started successfully!', 'success')
            return redirect(url_for('conversations'))
        else:
            print(f"Error: {response.status_code}, {response.text}")  # Debug log for response
            flash('Failed to start conversation. Please try again.', 'danger')

    return render_template('start_conversation.html')

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        # Handle form submission for review creation
        user_id = session.get('id')
        content = request.form.get('content')
        rating = request.form.get('rating')

        if not user_id or not content or not rating:
            flash('All fields must be filled out to submit a review.', 'danger')
            return redirect(url_for('reviews'))

        review_data = {
            'user_id': user_id,
            'content': content,
            'rating': int(rating)
        }

        response = requests.post('http://127.0.0.1:8000/reviews', json=review_data)

        if response.status_code == 201:
            flash('Review submitted successfully!', 'success')
        else:
            flash('Failed to submit the review. Please try again.', 'danger')

    return render_template('reviews.html')

@app.route('/submit-review', methods=['POST'])
def submit_review():
    user_id = session.get('id')
    content = request.form.get('content')
    rating = request.form.get('rating')

    if not user_id or not content or not rating:
        flash('All fields must be filled out to submit a review.', 'danger')
        return redirect(url_for('reviews'))

    review_data = {
        'user_id': user_id,
        'content': content,
        'rating': int(rating)
    }

    response = requests.post('http://127.0.0.1:8000/reviews', json=review_data)

    if response.status_code == 201:
        flash('Review submitted successfully!', 'success')
    else:
        flash('Failed to submit the review. Please try again.', 'danger')

    return redirect(url_for('reviews'))

@app.route('/favorite', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get('user_id')
    item_id = data.get('item_id')

    existing_favorite = Favorite.query.filter_by(user_id=user_id, item_id=item_id).first()
    if existing_favorite:
        return jsonify({"message": "Item already favorited"}), 409

    new_favorite = Favorite(user_id=user_id, item_id=item_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Item favorited successfully"}), 201

if __name__ == '__main__':
    subprocess.Popen([sys.executable, "api.py"])
    app.run(debug=True)