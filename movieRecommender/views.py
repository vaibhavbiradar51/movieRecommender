from .models import *
from flask import Flask, request, session, redirect, url_for, render_template, flash
import re

app = Flask(__name__)
app.jinja_env.filters['zip'] = zip


@app.route("/")
def hello():

    recommendList13 = []
    recommendList14 = []
    recommendList15 = []

    email = session.get('email')
    if email:
        recommendList13 = User(email).getRecommendation13()
        recommendList14 = User(email).getRecommendation14()
        recommendList15 = User(email).getRecommendation15()

    return render_template('layout.html', recommendList13=recommendList13, recommendList14=recommendList14, recommendList15=recommendList15)
    movies = Movie.getAnyMovies()
    print(movies)
    return render_template('layout.html' , movies = movies)

# Admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email != 'admin' or password != 'admin':
            flash('Invalid login.')
        else:
            # if not exist then add admin to database
            User(email).signup('admin', password, is_staff=1)

            session['email'] = email
            session['admin'] = True
            session['staff'] = True
            flash('Logged in.')
            return render_template('admin.html', allUsers=getAllUsersSerialized())

    return render_template('login.html', admin=True)

@app.route('/toggleStaff/<email>', methods=['GET'])
def toggleStaff(email):
    if session.get('admin'):
        User(email).toggle_staff()
        return render_template('admin.html', allUsers=getAllUsersSerialized())
    else:
        flash('Invalid access')
        return redirect(url_for('admin'))

@app.route('/staffOptions', methods=['GET', 'POST'])
def staffOptions():
    return render_template('staffOptions.html')

# (1) Signup
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        emailRegex = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        if len(email) < 1:
            flash('Your email must be at least one character.')
        elif(not re.search(emailRegex, email)):
            flash('Enter a valid email ID.')
        elif len(name) < 1:
            flash('Your name must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif len(password) > 20:
            flash('Your password should not be greater than 20 characters.')
        elif not any(char.isdigit() for char in password):
            flash('Your Password should have at least one number')
        elif not any(char.isupper() for char in password):
            flash('Your Password should have at least one uppercase letter')
        elif not any(char.islower() for char in password):
            flash('Your Password should have at least one lowercase letter')
        elif not User(email).signup(name, password):
            flash('A user with that email already exists.')
        else:
            session['email'] = email
            flash('Logged in.')
            # return redirect(url_for('hello'))
            return redirect(url_for('choosePreference'))

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
            if User(email).isStaffMember():
                session['staff'] = True
            flash('Logged in.')
            return redirect(url_for('hello'))

    return render_template('login.html')

# (2) Logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('staff', None)
    session.pop('admin', None)
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

        userRating = []
        for i in Movielist:
            userRating.append(User(email).getUserRating(i))

        return render_template('addWatchedMovie.html', keyword=Movie, Movielist = Movielist, form = request.form , showfilledform = True, userRating = userRating)

    return render_template('addWatchedMovie.html' , showfilledform = False)

# (5) Search movie
@app.route('/searchMovie', methods=['GET', 'POST'])
def searchMovie():

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

# Movie Details
@app.route('/movieDetails/<int:id>')
def movieDetails(id):
    MovieList, GenreList, ActorList, DirectorList, CountryList = displayMovieDetails(id)
    return render_template('movieDetails.html', MovieList = MovieList, GenreList = GenreList, ActorList = ActorList, DirectorList = DirectorList, CountryList = CountryList)

# (6) Search actor
@app.route('/searchActor', methods=['GET'])
def searchActor():
    return render_template('searchActor.html', users=getAllActorSerialized2())

# (7) Search director
@app.route('/searchDirector', methods=['GET'])
def searchDirector():
    return render_template('searchDirector.html', users=getAllDirectorSerialized2())

# (8) Search for a user
@app.route('/searchUser', methods=['GET'])
def searchUser():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    allUsers = getAllUsersSerialized()

    return render_template('searchUser.html', allUsers=allUsers)

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

@app.route('/changeIsPublic', methods=['POST'])
def changeIsPublic():
    email = session.get('email')
    if not email:
        flash('You must be logged in')
        return redirect(url_for('login'))

    if 'isPublic' in request.form:
        val = 1
    else:
        val = 0
    movieID = request.form['movieId']
    changeIsPublicBackend(val, movieID, email)
    return redirect(url_for('profile', email=email))


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

# Friends Page
@app.route('/friends', methods=['GET', 'POST'])
def friends():
    email = session.get('email')
    if not email:
        flash('You must be logged in to recommend a movie')
        return redirect(url_for('login'))

    friends = User(email).get_friends()
    sendFriendRequests = User(email).send_friend_requests()
    receivedFriendRequests = User(email).received_friend_requests()

    friends = [{'name': friend['u']['name'], 'email': friend['u']['email'], 'id': friend['u'].identity} for friend in friends]
    sendFriendRequests = [{'name': friend['u']['name'], 'email': friend['u']['email'], 'id': friend['u'].identity} for friend in sendFriendRequests]
    receivedFriendRequests = [{'name': friend['u']['name'], 'email': friend['u']['email'], 'id': friend['u'].identity} for friend in receivedFriendRequests]

    return render_template('friends.html', friends=friends, sendFriendRequests=sendFriendRequests, receivedFriendRequests=receivedFriendRequests)

@app.route('/acceptFriendRequest', methods=['POST'])
def acceptFriendRequest():
    email = session.get('email')
    if not email:
        flash('You must be logged in to recommend a movie')
        return redirect(url_for('login'))

    if "acceptfriendRequest" in request.form:
        friendEmail = request.form['acceptfriendRequest']
        user2 = User(friendEmail).find()
        User(email).accept_friend_request(user2)
    elif "rejectfriendRequest" in request.form:
        friendEmail = request.form['rejectfriendRequest']
        user2 = User(friendEmail).find()
        User(email).reject_friend_request(user2)

    return redirect(url_for('friends'))

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

# # (13) GET RECOMMENDATION(based on preference): content based on his preferences and critic movie ratings
# @app.route('/getRecommendation13', methods=['GET'])
# def getRecommendation13():

#     email = session.get('email')
#     if not email:
#         flash('You must be logged in')
#         return redirect(url_for('login'))

#     moviesList = User(email).getRecommendation13()
#     return render_template('displayMovies.html', moviesList=moviesList)

# # (14) GET RECOMMENDATION(based on preference): based on similar users globally
# @app.route('/getRecommendation14', methods=['GET'])
# def getRecommendation14():

#     email = session.get('email')
#     if not email:
#         flash('You must be logged in')
#         return redirect(url_for('login'))

#     moviesList = User(email).getRecommendation14()
#     return render_template('displayMovies.html', moviesList=moviesList)

# # (15) GET RECOMMENDATION(based on preference): based on similar users in my friends
# @app.route('/getRecommendation15', methods=['GET'])
# def getRecommendation15():

#     email = session.get('email')
#     if not email:
#         flash('You must be logged in')
#         return redirect(url_for('login'))

#     moviesList = User(email).getRecommendation15()
#     return render_template('displayMovies.html', moviesList=moviesList)


# (16) Staff create new preference
@app.route('/createPreference', methods=['GET', 'POST'])
def createPreference():

    if not session.get('staff'):
        return redirect(url_for('hello'))

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

    if not session.get('staff'):
        return redirect(url_for('hello'))

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