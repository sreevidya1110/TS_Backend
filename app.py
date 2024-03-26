from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt
import re
import os
import summary
import document_to_text
import docx
import io

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        error=''
        existing_user = users_collection.find_one({'email': request.form['email']})
        name=request.form['name']
        password = request.form['password']
        cpassword=request.form['cpassword']
        email = request.form['email']
        if not name or not  password or not email:
            error='Please fill all the fields'
            return render_template('signup.html',error=error)
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            error='Invalid email'
            return render_template('signup.html',error=error)
        if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$',password):
            error='Password should contain 8 to 15 characters with at least one lowercase letter, one uppercase letter, one numeric digit, and one special character'
            return render_template('signup.html',error=error)
        
        if cpassword!=password:
            error='Passwords do not match'
            return render_template('signup.html',error=error)
        if existing_user:
            error='User already exists'
            return render_template('signup.html',error=error)
        summary=[]
        summaryt=[]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({'name': name, 'password': hashed_password,'email':email,'summary':summary,'summaryt':summaryt})
        return render_template('login.html')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        error=''
        email=request.form['email']
        password=request.form['password']
        if not email or not password:
            error='Enter all fields'
            return render_template('login.html',error=error)
        login_user = users_collection.find_one({'email':email})
        if login_user:
            if bcrypt.checkpw(password.encode('utf-8'), login_user['password']):
                session['email']=login_user['email']
                print("hello")
                summary_title=login_user['summaryt']
                summary_history=login_user['summary']
                return render_template('summarize.html',error=summary_title,msg=summary_history,email=session['email'])
                
        error='Invalid email/password combination'
        return render_template('login.html',error=error)
    return render_template('login.html')


@app.route('/summarize-w',methods=['GET','POST'])
def summarize():
    if request.method=='POST':
        file=request.files['document']
        error=''
        error4=''
        if file.filename=='':
            print("kite")
            error=summary.generate_summary(request.form['text'])
            error4=request.form['text']
        else:
            
            converted_text=document_to_text.extract_text_from_docx(file)
            error=summary.generate_summary(converted_text)
            error4=converted_text
        error1=error.split("<n>")
        error2=''
        for i in error1:
            if i=="<n>":
                continue
            else:
                error2=error2+" "+i
        return render_template('summarize-w.html',summary=error2,input=error4)
    return render_template('summarize-w.html')

@app.route('/summarize',methods=['POST'])
def history():
    if request.method=='POST':
        print("hi")
        email=session['email']
        file=request.files['document']
        error=''
        error4=''
        if file.filename=='':
            print("kite")
            error=summary.generate_summary(request.form['text'])
            error4=request.form['text']
        else:
            
            converted_text=document_to_text.extract_text_from_docx(file)
            error=summary.generate_summary(converted_text)
            error4=converted_text
        
        error1=error.split("<n>")
        error2=''
        for i in error1:
            if i=="<n>":
                continue
            else:
                error2=error2+" "+i
        history_user=users_collection.find_one({'email':email})
        summary_list=history_user['summary']
        summary_title=history_user['summaryt']
        summary_list.append(error2)
        error3=''
        for i in range(0,10):
            error3=error3+error2[i]
        summary_title.append(error3+"...")
        query={'email':email}
        new_values={'$set':{'summary':summary_list,'summaryt':summary_title}}
        cursor=users_collection.update_one(query,new_values)
        return render_template('summarize.html',summary=error2,input=error4)
    
        

    
@app.route('/logout')
def logout():
    session.pop('email', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
