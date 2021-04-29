from .models import *
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('layout.html')

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

# (2) Logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('Logged out.')
    return redirect(url_for('hello'))

# (3) Choose Preference
@app.route('/choosePreference', methods=['GET', 'POST'])
def choosePreference():

    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if request.method == 'POST':
        genreIdList = request.form.getlist('genre')
        countryIdList = request.form.getlist('country')
        actorIdList = request.form.getlist('actor')
        directorIdList = request.form.getlist('director')

        User(email).updatePreferences(genreIdList, countryIdList, actorIdList, directorIdList)
        return redirect(url_for('hello'))

    return render_template('choosePreference.html', allGenres=getAllGenreSerialized(),
                            allCountries=getAllCountrySerialized(), allActors=getAllActorSerialized(),
                            allDirectors=getAllDirectorSerialized(), userGenres=getUserGenreSerialized(email),
                            userCountries=getUserCountrySerialized(email), userActors=getUserActorSerialized(email),
                            userDirectors=getUserDirectorSerialized(email))

# (4) Add a Watched Movie
@app.route("/handleWatchedMovie", methods = ['POST', 'GET'])
def handleWatchedMovie():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))
    if request.method == 'POST':
        # //add to db also
        Movieselected = request.form.getlist('selectedMovie')
        MovieRatingMap = {}
        for mov in Movieselected:
            val = request.form[mov]
            if val == '':
                val = 0
            else:
                val = float(val)
            MovieRatingMap[int(mov)] = val
        User(email).addWatchedMovieRating(MovieRatingMap )
        if request.form['Submit'] == 'Submit':
            return redirect(url_for('hello'))
        elif request.form['Submit'] == 'Submit and add Another':
            return redirect(url_for('addWatchedMovie'))
    return redirect(url_for('addWatchedMovie'))

@app.route('/addWatchedMovie', methods=['GET', 'POST'])
def addWatchedMovie():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))
    if request.method == 'POST':
        Movie = request.form['Movie']
        Movielist = searchMovieusingName(Movie)
        return render_template('addWatchedMovie.html', keyword=Movie, Movielist = Movielist, form = request.form , showfilledform = True)

    return render_template('addWatchedMovie.html' , showfilledform = False)

# (5) Search movie
@app.route('/searchMovie', methods=['GET', 'POST'])
def searchMovie():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        # criticsRating = request.form['criticsRating']
        genreIdList = request.form.getlist('genre')
        countryIdList = request.form.getlist('country')
        actorIdList = request.form.getlist('actor')
        directorIdList = request.form.getlist('director')

        Movielist = getMovie(title, year, genreIdList, countryIdList, actorIdList, directorIdList)
        # Movie(title, year).add(genreIdList, countryIdList, actorIdList, directorIdList)
        # return redirect(url_for('createMovie'))

        return render_template('displayMovie.html', Movielist = Movielist)
        # print(request.form.getlist('genre'))
    
    return render_template('searchMovie.html', genres=getAllGenreSerialized(),
                            countries=getAllCountrySerialized(), actors=getAllActorSerialized(),
                            directors=getAllDirectorSerialized())

# (6) Search actor
@app.route('/searchActor', methods=['GET', 'POST'])
def searchActor():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if request.method == 'POST':
        Actor = request.form['Actor']
        Actorlist = getActor(Actor)
        return render_template('displayName.html', mylist = Actorlist, name="Actor")
        # print(request.form.getlist('genre'))

    return render_template('searchActor.html')

# (7) Search director
@app.route('/searchDirector', methods=['GET', 'POST'])
def searchDirector():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if request.method == 'POST':
        Director = request.form['Director']
        Directorslist = getDirector(Director)
        return render_template('displayName.html', mylist = Directorslist, name="Directors")
        # print(request.form.getlist('genre'))

    return render_template('searchDirector.html')


# (8) Search for a user
@app.route('/searchUser', methods=['GET', 'POST'])
def searchUser():
    email = session.get('email')

    if request.method == 'POST':
        if 'title' in request.form:
            title = request.form['title']
            users = User.searchUser(title, email)
        else:
            if email is None:
                return render_template('searchUser.html')
            users = User(email).get_friends()

        return render_template('displayUserList.html', users=[{'name': user['u']['name'], 'email': user['u']['email'], 'id': user['u'].identity} for user in users])

    return render_template('searchUser.html')

# (8) User Details
@app.route('/profile/<email>', methods=['GET'])
def profile(email):
    cur_email = session.get('email')

    user = User(email).find()
    if user is None:
        flash("Not a valid user")
        return redirect(url_for('hello'))

    movies_watched_public = User(email).getPublicWatchedMovieHistory()

    if not cur_email:
        # FILL MOVIE WATCHED HISTORY
        return render_template('profile.html', name=user['name'], email=user['email'], movies_watched_public=movies_watched_public)
    else:
        isFriend = User(cur_email).is_friend(user)

        if isFriend:
            movies_recommended = User(cur_email).getRecommendedMovies(user.identity)
            preferences = {}
        else:
            preferences = {
                'Actor': [a['name'] for a in getUserActorSerialized(email)],
                'Director': [a['name'] for a in getUserDirectorSerialized(email)],
                'Genre': [a['genre'] for a in getUserGenreSerialized(email)],
                'Country': [a['country'] for a in getUserCountrySerialized(email)]
            }
            movies_recommended = []

        return render_template('profile.html', name=user['name'], email=user['email'], movies_watched_public=movies_watched_public, isFriend=isFriend, movies_recommended=movies_recommended, preferences=preferences)


# (9) Add Friend
@app.route('/addFriend', methods=['POST'])
def addFriend():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if 'email' in request.form:
        email2 = request.form['email']
        user2 = User(email2).find()

        User(email).add_friend(user2)
        return redirect(url_for('profile', email=email2))

# (9) Delete Friend
@app.route('/deleteFriend', methods=['POST'])
def deleteFriend():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if 'email' in request.form:
        email2 = request.form['email']
        user2 = User(email2).find()

        User(email).delete_friend(user2)
        return redirect(url_for('profile', email=email2))


# (9) Recommend a movie to friend
@app.route('/recommendMovie/<int:id>', methods=['GET', 'POST'])
def recommendMovie(id):
    email = session.get('email')
    if not email:
        flash('You must be logged in to recommend a movie')
        return redirect(url_for('login'))

    if request.method == 'GET':
        friends_list = User(email).get_friends()
        friends = [{'name': friend['u']['name'], 'email': friend['u']['email'], 'id': friend['u'].identity} for friend in friends_list]

        movie = Movie.find_by_id(id)

        return render_template('userMovie.html', movie=movie, friends=friends)
    else:
        friends_list = request.form.getlist('chosenFriends')
        print(friends_list)
        User(email).recommendMovie(id, friends_list)
        return redirect(url_for('profile', email=email))


# (12) GET DETAILS: most watched movies
@app.route('/getMostWatchedMovies', methods=['GET', 'POST'])
def getMostWatchedMovies():

    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if request.method == 'POST':

        if 'genre' in request.form:
            genreIdList = request.form.getlist('genre')
            moviesList = Movie.getMostWatched('Genre', genreIdList)

        elif 'country' in request.form:
            countryIdList = request.form.getlist('country')
            moviesList = Movie.getMostWatched('Country', countryIdList)

        return render_template('displayMovies.html', moviesList=moviesList)

    return render_template('getMostWatchedMovies.html', genres=getAllGenreSerialized(),
                            countries=getAllCountrySerialized())

# (13) GET RECOMMENDATION(based on preference): content based on his preferences and critic movie ratings
@app.route('/getRecommendation13', methods=['GET'])
def getRecommendation13():

    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    moviesList = User(email).getRecommendation13()
    return render_template('displayMovies.html', moviesList=moviesList)

# (14) GET RECOMMENDATION(based on preference): based on similar users globally
@app.route('/getRecommendation14', methods=['GET'])
def getRecommendation14():

    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    moviesList = User(email).getRecommendation14()
    return render_template('displayMovies.html', moviesList=moviesList)

# (15) GET RECOMMENDATION(based on preference): based on similar users in my friends
@app.route('/getRecommendation15', methods=['GET'])
def getRecommendation15():

    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    moviesList = User(email).getRecommendation15()
    return render_template('displayMovies.html', moviesList=moviesList)


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
        title = request.form['title']
        year = request.form['year']
        criticsRating = request.form['criticsRating']
        genreIdList = request.form.getlist('genre')
        countryIdList = request.form.getlist('country')
        actorIdList = request.form.getlist('actor')
        directorIdList = request.form.getlist('director')

        Movie(title, year, criticsRating).add(genreIdList, countryIdList, actorIdList, directorIdList)
        return redirect(url_for('createMovie'))

    return render_template('createMovie.html', genres=getAllGenreSerialized(),
                            countries=getAllCountrySerialized(), actors=getAllActorSerialized(),
                            directors=getAllDirectorSerialized())