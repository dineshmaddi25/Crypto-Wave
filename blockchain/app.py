from flask import Flask, render_template, flash, redirect, url_for, session, request
from passlib.hash import sha256_crypt
from functools import wraps
import time
import sqlite3

from sqllite import Table
from blockchain import Block, Blockchain
from forms import RegisterForm, SendMoneyForm, BuyForm

app = Flask(__name__)

# Configure SQLite3
app.config['DATABASE'] = 'C:\\Users\\dines\\blockchain\\crypto.db'


# Wrap to define if the user is currently logged in from session
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login.", "danger")
            return redirect(url_for('login'))
    return wrap

# Login the user by updating session
def log_in_user(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')

# Registration page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    # If form is submitted
    if request.method == 'POST' and form.validate():
        # Collect form data
        username = form.username.data
        email = form.email.data
        name = form.name.data

        # Make sure user does not already exist
        if not users.isnewuser(username):
            # Add the user to SQLite3 and log them in
            password = sha256_crypt.encrypt(form.password.data)
            users.insert(name, email, username, password)
            log_in_user(username)
            flash('You are now registered and logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)

# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():

    # If form is submitted
    if request.method == 'POST':
        # Collect form data
        username = request.form['username']
        password_candidate = request.form['password']

        # Access users table to get the user's actual password
        users = Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        if user:
            accPass = user.get('password')

            # If the password entered matches the actual password
            if sha256_crypt.verify(password_candidate, accPass):
                # Log in the user and redirect to Dashboard page
                log_in_user(username)
                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                # If the passwords do not match
                flash('Invalid password', 'danger')
                return redirect(url_for('login'))
        else:
            # If the username is not found
            flash('Username not found', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Transaction page
@app.route("/transaction", methods=['GET', 'POST'])
@is_logged_in
def transaction():
    form = SendMoneyForm(request.form)
    table_instance = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    balance = table_instance.get_balance(session.get('username'))

    # If form is submitted
    if request.method == 'POST':
        try:
            # Attempt to execute the transaction
            table_instance.send_money(session.get('username'), form.username.data, form.amount.data)
            flash("Money Sent!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('transaction'))

    return render_template('transaction.html', balance=balance, form=form, page='transaction')

# Buy page
@app.route("/buy", methods=['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyForm(request.form)
    table_instance = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    balance = table_instance.get_balance(session.get('username'))

    if request.method == 'POST':
        # Attempt to buy amount
        try:
            table_instance.send_money("BANK", session.get('username'), form.amount.data)
            flash("Purchase Successful!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('dashboard'))

    return render_template('buy.html', balance=balance, form=form, page='buy')

# Logout the user. Ends current session
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout success", "success")
    return redirect(url_for('login'))

# Dashboard page
@app.route("/dashboard")
@is_logged_in
def dashboard():
    table_instance = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    balance = table_instance.get_balance(session.get('username'))
    blockchain = table_instance.get_blockchain().chain
    ct = time.strftime("%I:%M %p")
    return render_template('dashboard.html', balance=balance, session=session, ct=ct, blockchain=blockchain, page='dashboard')

# Index page
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

# Run app
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
