# all packages
from flask import Flask, render_template, request, redirect, url_for, flash, session
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import os
import webbrowser

# Flask starting
app = Flask(__name__)
app.config['upload folder'] = 'uploads'
app.secret_key = 'your_secret_key'  # Required for session

# Store user details in memory
users = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        psw = request.form['password']
        
        if email in users and users[email]['password'] == psw:
            session['email'] = email  # Store email in session
            return redirect(url_for('prediction'))  # Changed to redirect instead of render_template
        else:
            return render_template('login.html', msg='Invalid Credentials. Please register if you haven\'t already.')
    return render_template('login.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        pws = request.form['psw']
        cpws = request.form['cpsw']
        
        if pws == cpws:
            if email in users:
                return render_template('registration.html', msg='Email already registered')
            
            # Store user details in memory
            users[email] = {
                'name': name,
                'password': pws
            }
            
            # Add success message to session
            session['registration_success'] = True
            return redirect(url_for('login'))
        else:
            return render_template('registration.html', msg='Passwords do not match')
            
    return render_template('registration.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/load", methods=['GET', 'POST'])
def load():
    if request.method == 'POST':
        file = request.files['file']
        filetype = os.path.splitext(file.filename)[1]
        if filetype == '.csv':
            path = os.path.join(app.config['upload folder'], file.filename)
            file.save(path)
            return render_template('load.html', msg='File uploaded successfully')
        return render_template('load.html', msg='Invalid file type')
    return render_template('load.html')

@app.route("/view")
def view():
    try:
        file = os.listdir(app.config['upload folder'])
        path = os.path.join(app.config['upload folder'], file[0])
        global df
        df = pd.read_csv(path)
        return render_template('view.html', col_name=df.columns.values, row_val=list(df.values.tolist()))
    except (IndexError, FileNotFoundError):
        return render_template('view.html', msg='No file uploaded yet')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        # Get form data
        data = [
            float(request.form['age']),
            float(request.form['sex']),
            float(request.form['cp']),
            float(request.form['trestbps']),
            float(request.form['chol']),
            float(request.form['fbs']),
            float(request.form['restecg']),
            float(request.form['thalach']),
            float(request.form['exang']),
            float(request.form['oldpeak']),
            float(request.form['slope']),
            float(request.form['ca']),
            float(request.form['thal'])
        ]
        
        # Make prediction
        prediction = model.predict([data])[0]
        probability = model.predict_proba([data])[0][1] * 100
        
        if prediction == 1:
            result = "High risk of heart disease"
        else:
            result = "Low risk of heart disease"
            
        msg = f"{result}\nConfidence: {probability:.1f}%"
        return render_template('prediction.html', msg=msg)
    return render_template('prediction.html')

# Add this new route after your existing routes
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to home page
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    # Open browser after Flask starts
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True, port=5000)