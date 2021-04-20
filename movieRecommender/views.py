from .models import User
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if len(email) < 1:
            flash('Your email must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif not User(email).signup(password):
            flash('A user with that email already exists.')
        else:
            session['email'] = email
            flash('Logged in.')
            return redirect(url_for('hello'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print(email, password)

        if not User(email).verify_password(password):
            flash('Invalid login.')
        else:
            session['email'] = email
            flash('Logged in.')
            return redirect(url_for('hello'))

    return render_template('login.html')
