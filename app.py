from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB Atlas connection URI
mongo_uri = "mongodb+srv://sreevidya111003:1234@cluster0.oucbvsu.mongodb.net/"
client = MongoClient(mongo_uri)
db = client["TS"]
users_collection = db["user"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        existing_user = users_collection.find_one({'email': request.form['email']})
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            msg='Invalid email'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$',password):
            msg='Password should contain 8 to 15 characters with at least one lowercase letter, one uppercase letter, one numeric digit, and one special character'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        elif existing_user is None:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users_collection.insert_one({'username': username, 'password': hashed_password,'email':email})
            return redirect(url_for('login'))
        return 'User already exists!'
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = users_collection.find_one({'email': request.form['email']})
        if login_user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
                session['email'] = request.form['email']
                return redirect(url_for('dashboard'))
        return 'Invalid username/password combination'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
