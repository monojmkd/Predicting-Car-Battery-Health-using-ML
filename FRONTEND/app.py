from flask import Flask, render_template, url_for, redirect, request, jsonify, session, flash
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from tensorflow.keras.losses import MeanSquaredError
import pandas as pd
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong, random secret key

# Database connection
mydb = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='toor',
    database='electric_vehicle'
)
mycur = mydb.cursor()

# Dataset paths
DATASETS = {
    'dataset1': 'Arranged_TripA01.xlsx',
    'dataset2': 'bat_charge(4).csv'
}

# Models and preprocessing setup
scaler = MinMaxScaler(feature_range=(0, 1))

# Routes
@app.route('/')
def index():
    username = session.get('username', None)
    return render_template('index.html', username=username)

@app.route('/about')
def about():
    username = session.get('username', None)
    return render_template('about.html', username=username)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        address = request.form['address']

        if password != confirmpassword:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('registration'))

        # Check if user already exists
        sql = 'SELECT * FROM users WHERE email = %s'
        mycur.execute(sql, (email,))
        if mycur.fetchone():
            flash('User already registered!', 'warning')
            return redirect(url_for('registration'))

        # Insert new user
        sql = 'INSERT INTO users (name, email, password, address) VALUES (%s, %s, %s, %s)'
        mycur.execute(sql, (name, email, password, address))
        mydb.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        sql = 'SELECT * FROM users WHERE email = %s'
        mycur.execute(sql, (email,))
        user = mycur.fetchone()

        if user and user[3] == password:  # Assuming password is in column 4
            session['logged_in'] = True
            session['username'] = user[1]  # Assuming name is in column 2
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/viewdata', methods=['GET', 'POST'])
def viewdata():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    selected_dataset = request.form.get('dataset', None)
    selected_table = None

    if selected_dataset:
        file_path = DATASETS.get(selected_dataset)
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        selected_table = df.to_html(classes='table table-striped', index=False)

    return render_template('viewdata.html', selected_dataset=selected_dataset, selected_table=selected_table, username=session['username'])

@app.route('/algo', methods=['GET', 'POST'])
def algo():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    selected_algorithm = request.form.get('algorithm', None)
    r2_score_value = None

    algorithms_results = {
        'CNN': {'r2_score': 0.83497},
        'SVR': {'r2_score': 0.99599},
        'FNN': {'r2_score': 0.33411},
        'RBF_SVR': {'r2_score': 0.99599},
        'Random Forest': {'r2_score': 0.99734},
        'XGBoost': {'r2_score': 0.99736},
        'LSTM': {'r2_score': 0.99976},
        'DNN': {'r2_score': 0.81}
    }

    if selected_algorithm:
        r2_score_value = algorithms_results[selected_algorithm]['r2_score']

    return render_template('algo.html', algorithms=algorithms_results.keys(), selected_algorithm=selected_algorithm, r2_score_value=r2_score_value, username=session['username'])

@app.route('/prediction1', methods=['GET', 'POST'])
def prediction1():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    msg = None
    if request.method == 'POST':
        # Prediction logic here
        pass

    return render_template('prediction1.html', msg=msg, username=session['username'])

@app.route('/prediction2', methods=['GET', 'POST'])
def prediction2():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            minutes = int(request.form['minutes'])
            # Prediction logic here
            pass
        except ValueError:
            flash('Invalid input. Please enter a valid number.', 'danger')

    return render_template('prediction2.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
