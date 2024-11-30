from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, get_flashed_messages
import requests
from flask import flash, redirect, url_for
import sys
import subprocess
from utilities.utils import login_required
from models.favorite import Favorite
from dependencies.database import db
import logging

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

@app.route('/test-redirect')
def test_redirect():
    return redirect(url_for('verify_email'))

@app.route('/set-session', methods=['POST'])
def set_session():
    data = request.json

    if 'id' in data and 'email' in data and 'name' in data:
        session['id'] = data['id']  
        session['email'] = data['email']  
        session['name'] = data['name'] 
        session['username'] = data['email'].split('@')[0] 

        return jsonify({"message": "Session data set successfully"})
    else:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-session')
def test_session():
    return jsonify(dict(session))

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'GET':
        return render_template("verify_email.html")

    email = request.form.get('email')
    code = request.form.get('code')

    if not email or not code:
        flash('Email and verification code are required.', 'danger')
        return redirect(url_for('verify_email'))

    try:
        response = requests.post(
            'http://127.0.0.1:8000/accounts/verify',
            params={'email': email, 'code': code}
        )

        if response.status_code == 200:
            flash('Email verified successfully!', 'success')
            return redirect(url_for('login'))
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except ValueError:
                error_detail = 'Unexpected response from the server.'
            flash(f"Verification failed: {error_detail}", 'danger')
            return redirect(url_for('verify_email'))

    except requests.exceptions.RequestException as e:
        flash(f"Failed to connect to the verification service: {str(e)}", 'danger')
        return redirect(url_for('verify_email'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Handle POST request (form submission logic)
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check for valid email domain
        if not email.endswith("@charlotte.edu"):
            flash("Only @charlotte.edu emails are allowed.", "danger")
            return redirect(url_for("signup"))

        # Send signup data to FastAPI
        try:
            response = requests.post(
                "http://127.0.0.1:8000/accounts/",
                json={"name": name, "email": email, "password": password},
            )

            # Handle FastAPI response
            if response.status_code == 200:
                flash("Sign-up successful! Check your email for the verification code.", "success")
                return redirect(url_for("verify_email", email=email))
            else:
                # Show detailed error from FastAPI or a default error
                flash(response.json().get("detail", "Sign-up failed. Please try again."), "danger")
                return redirect(url_for("signup"))

        except requests.exceptions.RequestException as e:
            # Handle connection errors or FastAPI being down
            flash(f"Failed to connect to the signup service: {str(e)}", "danger")
            return redirect(url_for("signup"))

    # Handle GET request (display signup form with potential error flashes)
    error = request.args.get("error")
    if error == "password_mismatch":
        flash("Passwords do not match!", "danger")
    elif error == "invalid_email":
        flash("Please use a @charlotte.edu email address.", "danger")
    elif error == "submission_failed":
        flash("Form submission failed. Please try again.", "danger")

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()
        email = request.form.get('email')
        password = request.form.get('password')

        try:
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
                flash(f"Welcome {session['username']}, you have been successfully logged in.", "success")
                return redirect(url_for('dashboard'))

            elif response.status_code == 403:
                flash('Your email is not verified. Please verify your email to log in.', 'warning')
                return redirect(url_for('verify_email', email=email))

            else:
                flash('Login failed: Wrong email and/or password.', 'danger')
                return redirect(url_for('login'))

        except requests.exceptions.RequestException as e:
            flash('An error occurred while connecting to the authentication service. Please try again.', 'danger')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An unexpected error occurred. Please try again later.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
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

    user_id = session['id']
    name = request.form.get('name')
    email = request.form.get('email')

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

    user_id = session['id']
    current_password = request.form.get('current-password')
    new_password = request.form.get('new-password')
    confirm_password = request.form.get('confirm-password')

    if new_password != confirm_password:
        flash('New password and confirm password do not match.', 'danger')
        return redirect(url_for('settings'))

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

    email_notifications = request.form.get('email-notifications') == 'on'
    flash('Notification preferences updated!', 'success')

    return redirect(url_for('settings'))

@app.route('/create-item', methods=['GET', 'POST'])
@login_required
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

    return render_template('itemcreate.html')

@app.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

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
@login_required
def delete_item(item_id):
    response = requests.delete(f'http://127.0.0.1:8000/listings/{item_id}')
    if response.status_code == 204:
        flash('Item deleted successfully!', 'success')
    else:
        flash('Failed to delete item. Please try again.', 'danger')

    return redirect(url_for('items'))

@app.route('/items')
def items():
    response = requests.get('http://127.0.0.1:8000/listings')
    listings = response.json() if response.status_code == 200 else []
    return render_template('items.html', listings=listings)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    return render_template('item.html')

@app.route('/userProfile')
def userProfile():
    return render_template('userProfile.html')

@app.route('/api/signup', methods=['POST'])
def user_signup():
    pass

@app.route('/api/login', methods=['GET'])
def user_login():
    pass

@app.route('/listings')
def get_listings():
    response = requests.get('http://127.0.0.1:8000/listings')
    return jsonify(response.json())

@app.route('/listings/<int:item_id>')
def get_listing(item_id):
    response = requests.get(f'http://127.0.0.1:8000/listings/{item_id}')
    return jsonify(response.json())

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
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

@app.route('/start-conversation', methods=['POST'])
@login_required
def start_conversation():
    if 'id' not in session:
        flash('You need to be logged in to start a conversation.', 'danger')
        return redirect(url_for('login'))

    participant_1 = session['id']
    participant_2 = request.json.get('participant_2')
    item_id = request.json.get('item_id')
    response = requests.get(f'http://127.0.0.1:8000/conversations/check', params={
        'user_1': participant_1,
        'user_2': participant_2,
        'item_id': item_id
    })

    if response.status_code == 200:
        conversation = response.json()
        if conversation.get('id'):
            flash('Conversation already exists. Redirecting to chat...', 'info')
            return redirect(url_for('chat', conversation_id=conversation['id']))
        else:
            flash('No existing conversation found, creating new one...', 'info')
    else:
        flash('Failed to check for existing conversation.', 'danger')

    response = requests.post('http://127.0.0.1:8000/conversations', json={
        'participant_1': participant_1,
        'participant_2': participant_2,
        'item_id': item_id
    })
    if response.status_code == 201:
        conversation = response.json()
        flash('Conversation started successfully!', 'success')
        return redirect(url_for('chat', conversation_id=conversation['id']))
    else:
        flash('Failed to start conversation. Please try again.', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))

@app.route('/chat/<int:conversation_id>')
@login_required
def chat(conversation_id):
    if 'id' not in session:
        flash('You need to log in to view this chat.', 'danger')
        return redirect(url_for('login'))

    response = requests.get(f'http://127.0.0.1:8000/conversations/{conversation_id}')
    if response.status_code != 200:
        flash('Conversation not found.', 'danger')
        return redirect(url_for('items'))

    conversation = response.json()

    other_user_id = (
        conversation['participant_1']
        if conversation['participant_1'] != session['id']
        else conversation['participant_2']
    )

    other_user_response = requests.get(f'http://127.0.0.1:8000/accounts/{other_user_id}')
    if other_user_response.status_code != 200:
        other_user_name = 'Unknown'
        flash('Could not fetch the other user\'s details.', 'warning')
    else:
        other_user_name = other_user_response.json()['name']

    item_id = conversation.get('item_id')

    seller_id = (
        conversation['participant_1'] if conversation['participant_1'] != session['id'] else conversation['participant_2']
    )

    return render_template(
        'chat.html',
        conversation_id=conversation_id,
        other_user_name=other_user_name,
        seller_id=seller_id,
        item_id=item_id
    )

@app.route('/conversations')
@login_required
def conversations():
    if 'id' not in session:
        flash('You need to be logged in to view conversations.', 'danger')
        return redirect(url_for('login'))
    return render_template('conversations.html', user_id=session['id'])

@app.route('/favorite', methods=['POST'])
@login_required
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

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_id = session.get('id')

    if not user_id:
        flash('You need to be logged in to delete your account.', 'danger')
        return redirect(url_for('login'))

    try:
        # Send delete request to FastAPI
        response = requests.delete(f'http://127.0.0.1:8000/accounts/{user_id}')
        
        if response.status_code == 204:  # Successful deletion
            session.clear()  # Clear the session
            flash('Your account has been deleted successfully.', 'success')
            return redirect(url_for('index'))  # Redirect to the index page
        else:
            # Handle failed deletion response
            error_message = response.json().get('detail', 'Failed to delete your account.')
            flash(error_message, 'danger')
    except requests.exceptions.RequestException as e:
        # Handle API connection errors
        flash(f"An error occurred: {str(e)}", 'danger')

    # Redirect back to settings if deletion fails
    return redirect(url_for('settings'))

if __name__ == '__main__':
    subprocess.Popen([sys.executable, "api.py"])
    app.run(debug=True)
