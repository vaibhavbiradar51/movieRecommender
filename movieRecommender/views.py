from .models import *
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# (1) Signup
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if len(email) < 1:
            flash('Your email must be at least one character.')
        elif len(name) < 1:
            flash('Your name must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif not User(email).signup(name, password):
            flash('A user with that email already exists.')
        else:
            session['email'] = email
            flash('Logged in.')
            return redirect(url_for('hello'))

    return render_template('signup.html')

# (2) Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not User(email).verify_password(password):
            flash('Invalid login.')
        else:
            session['email'] = email
            flash('Logged in.')
            return redirect(url_for('hello'))

    return render_template('login.html')

# (8) Search for a user
@app.route('/searchUser', methods=['GET', 'POST'])
def searchUser():
    if request.method == 'POST':
        if 'title' in request.form:
            title = request.form['title']
            users = User.searchUser(title)
        else:
            users = User(session.get('email')).get_friends()

        return render_template('displayUsers.html', users=users)

    return render_template('searchUser.html')


# (16) Staff create new preference
@app.route('/createPreference', methods=['GET', 'POST'])
def createPreference():
    if request.method == 'POST':
        if 'genre' in request.form:
            genre = request.form['genre']
            if len(genre) < 1:
                flash('Genre must be atleast 1 character')
            elif not Genre(genre).add():
                flash('Genre already exists')
            else:
                return redirect(url_for('createPreference'))

        elif 'country' in request.form:
            country = request.form['country']
            if len(country) < 1:
                flash('Country of Origin must be atleast 1 character')
            elif not Country(country).add():
                flash('Country already exists')
            else:
                return redirect(url_for('createPreference'))

        elif 'actor' in request.form:
            actor = request.form['actor']
            if len(actor) < 1:
                flash('Actor Name must be atleast 1 character')
            else:
                Actor(actor).add()
                return redirect(url_for('createPreference'))

        elif 'director' in request.form:
            director = request.form['director']
            if len(director) < 1:
                flash('Director Name must be atleast 1 character')
            else:
                Director(director).add()
                return redirect(url_for('createPreference'))

    return render_template('createPreference.html')


# (17) Creating New Movie
@app.route('/createMovie', methods=['GET', 'POST'])
def createMovie():
    if request.method == 'POST':
        print(request.form)
        print(request.form.getlist('genre'))

    return render_template('createMovie.html', genres=getAllGenreSerialized(),
                            countries=getAllCountrySerialized(), actors=getAllActorSerialized(),
                            directors=getAllDirectorSerialized())