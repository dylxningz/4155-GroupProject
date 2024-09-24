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

@app.route('/api/signup', methods=['POST'])
def user_signup():
    pass

if __name__ == '__main__':
    app.run(debug=True)