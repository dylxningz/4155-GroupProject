from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for sign-up page
@app.route('/signup')
def signup():
    return render_template('signup.html')

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

@app.route('/items')
def items():
    return render_template('items.html')

@app.route('/item')
def item():
    return render_template('item.html')

if __name__ == '__main__':
    app.run(debug=True)