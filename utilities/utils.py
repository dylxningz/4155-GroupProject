from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:  # Check if 'id' exists in the session
            flash('You need to log in to access this page.', 'danger')
            return redirect(url_for('login'))  # Redirect to the login route
        return f(*args, **kwargs)
    return decorated_function