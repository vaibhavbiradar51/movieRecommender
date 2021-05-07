from py2neo import Graph, Node, Relationship, NodeMatcher
from passlib.hash import bcrypt
from . import config

# url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')


graph = Graph(config.url + '/db/data/', username=config.username, password=config.password)

def addUserFieldReationship(userNode, fieldString, fieldNodeIdList):

    for fieldNodeId in fieldNodeIdList:
        matcher = NodeMatcher(graph)
        x = matcher.get(int(fieldNodeId))

        rel = Relationship(userNode, fieldString + 'Preference', x)
        graph.create(rel)

def getSerializedMovies(movies):
    serializedMovies = []
    for record in movies:
        m = record['m']
        # print(record)
        serializedMovies.append({
            'id': m.identity,
            'title': m['title'],
            'year': m['year'],
            'criticsRating': m['criticsRating'],
            'imageURL': m['imageURL'],
            'isURL': m['isURL'],
        })

    return serializedMovies

def getSerializedMovies2(movies):
    serializedMovies = []
    for record in movies:
        m = record['m']
        r = record['r']
        serializedMovies.append({
            'id': m.identity,
            'title': m['title'],
            'year': m['year'],
            'criticsRating': m['criticsRating'],
            'imageURL': m['imageURL'],
            'isURL': m['isURL'],
            'isPublic': r['isPublic'],
            'userRating': r['rating']
        })

    return serializedMovies


class User:
    def __init__(self, email):
        self.email = email

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("User", email=self.email)).first()

    def signup(self, name, password, is_staff=0):
        if not self.find():
            user = Node('User', email=self.email, name=name, password=bcrypt.encrypt(password), is_staff=is_staff)
            graph.create(user)
            self.id = user.identity
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False
    def deleteOldPreference(self):

        ls1 = ['Genre', 'Country', 'Actor', 'Director']
        ls2 = ['genre', 'country', 'actor', 'director']

        for i in range(len(ls1)):
            query = f'''
            MATCH (u:User)-[r:{ls2[i]}Preference]->(:{ls1[i]})
            WHERE u.email = "{self.email}"
            DELETE r
            '''
            graph.run(query)

    def updatePreferences(self, newGenreList, newCountryList, newActorList, newDirectorList):
        self.deleteOldPreference()
        userNode = self.find()

        addUserFieldReationship(userNode, 'genre', newGenreList)
        addUserFieldReationship(userNode, 'country', newCountryList)
        addUserFieldReationship(userNode, 'actor', newActorList)
        addUserFieldReationship(userNode, 'director', newDirectorList)

    def add_friend(self, user2):
        if self.is_friend(user2):
            return

        user1 = self.find()

        if user1 == user2:
            return

        # if user1.identity > user2.identity:
        #     user1, user2 = user2, user1

        # friendship = Node('Friendship', ID1=user1.identity, ID2=user2.identity)
        # graph.create(friendship)

        friendRequest = Relationship(user1, "friendRequest", user2)
        graph.create(friendRequest)

    def is_friend(self, user2):
        user1 = self.find()
        if user1 == user2:
            return False

        if user1.identity > user2.identity:
            user1, user2 = user2, user1

        matcher = NodeMatcher(graph)
        return len(list(matcher.match("Friendship", ID1=user1.identity, ID2=user2.identity))) > 0

    def delete_friend(self, user2):
        user1 = self.find()
        matcher = NodeMatcher(graph)

        if user1.identity > user2.identity:
            user1, user2 = user2, user1

        # deleting the friend edge
        for x in [user1.identity, user2.identity]:
            query = '''
                MATCH (u1:User)-[f:friend]->(ff:Friendship)
                WHERE id(u1) = %d and ff.ID1 = %d and ff.ID2 = %d
                DELETE f
            ''' % (x, min(user1.identity, user2.identity), max(user1.identity, user2.identity))

            graph.run(query)

        friendship = matcher.match("Friendship", ID1=user1.identity, ID2=user2.identity).first()
        graph.delete(friendship)

    def get_friends(self):
        user = self.find()
        query = '''
            MATCH (u:User)
            MATCH (:Friendship{ID1: %d, ID2:id(u)})
            RETURN u;
        ''' % (user.identity)
        l1 = list(graph.run(query))
        query = '''
            MATCH (u:User)
            MATCH (:Friendship{ID2: %d, ID1:id(u)})
            RETURN u;
        ''' % (user.identity)
        l2 = list(graph.run(query))

        return l1 + l2

    def send_friend_requests(self):
        user = self.find()
        query='''
            MATCH (u1:User)-[f:friendRequest]->(u:User)
            WHERE id(u1) = %d
            RETURN u
        ''' % (user.identity)

        l = list(graph.run(query))
        return l

    def received_friend_requests(self):
        user = self.find()
        query='''
            MATCH (u:User)-[f:friendRequest]->(u2:User)
            WHERE id(u2) = %d
            RETURN u
        ''' % (user.identity)

        l = list(graph.run(query))
        return l

    def accept_friend_request(self, user2):
        if self.is_friend(user2):
            return

        user1 = self.find()

        if user1 == user2:
            return

        # deleting the friendRequest edge
        query = '''
            MATCH (u1:User)-[r:friendRequest]->(u2:User)
            WHERE id(u1) = %d and id(u2) = %d
            DELETE r
        ''' % (user2.identity, user1.identity)

        graph.run(query)

        # creating the friendship node
        if user1.identity > user2.identity:
            user1, user2 = user2, user1

        friendship = Node('Friendship', ID1=user1.identity, ID2=user2.identity)
        graph.create(friendship)

        rel = Relationship(user1, 'friend', friendship)
        graph.create(rel)

        rel = Relationship(user2, 'friend', friendship)
        graph.create(rel)

    def reject_friend_request(self, user2):
        if self.is_friend(user2):
            return

        user1 = self.find()

        if user1 == user2:
            return

        # deleting the friendRequest edge
        query = '''
            MATCH (u1:User)-[r:friendRequest]->(u2:User)
            WHERE id(u1) = %d and id(u2) = %d
            DELETE r
        ''' % (user2.identity, user1.identity)

        graph.run(query)


    def addWatchedMovieRating(self, MovieRatingMap):
        for key,value in MovieRatingMap.items():
            query = '''
                MATCH (a:User), (b:Movie)
                WHERE a.email = '%s' AND id(b) = %s
                MERGE (a)-[r:movieWatched]->(b)
                ON CREATE SET r.rating = %f , r.isPublic = %s
                ON MATCH SET r.rating = %f , r.isPublic = %s
                RETURN r
            '''
            query = query % (self.email , key , value , 1 , value, 1)
            graph.run(query)

    def getPublicWatchedMovieHistory(self):
        query = '''
            MATCH (a:User), (m:Movie)
            WHERE a.email = '%s'
            MATCH (a)-[r:movieWatched]->(m)
            RETURN m, r
        '''
        query = query % (self.email)
        return getSerializedMovies2(graph.run(query))

    def getRecommendedMovies(self, id2):
        id1 = self.find().identity

        query = '''
            MATCH (:Friendship {ID1: %d, ID2: %d})-[:recommends {FromID: %d}]->(m:Movie)
            RETURN m;
        '''
        query = query % (min(id1, id2), max(id1, id2), id2)
        return getSerializedMovies(graph.run(query))

    def recommendMovie(self, movie_id, friendList):
        id1 = self.find().identity
        for id2 in friendList:
            id2 = int(id2)
            query = '''
                MATCH (f:Friendship {ID1: %d, ID2: %d}), (m:Movie)
                WHERE id(m) = %d
                MERGE (f)-[:recommends {FromID: %d}]->(m);
            '''
            query = query % (min(id1, id2), max(id1, id2), movie_id, id1)
            graph.run(query)
        return

    def toggle_staff(self):
        query = '''
            MATCH (u:User)
            WHERE u.email = '%s'
            SET u.is_staff = 1-u.is_staff
        ''' % self.email

        graph.run(query)

    def isStaffMember(self):
        query = '''
            MATCH (u:User)
            WHERE u.email = '%s'
            RETURN u.is_staff as IS_STAFF
        ''' % self.email

        res = graph.run(query)

        for record in res:
            IS_STAFF = record['IS_STAFF']
            if IS_STAFF == 1:
                return True
            else:
                return False


    @staticmethod
    def searchUser(text, email):
        query = '''
            MATCH (u:User)
            WHERE (u.email STARTS WITH '%s'
            OR u.name STARTS WITH '%s')
            AND u.email <> '%s'
            RETURN u;
        ''' % (text, text, email)
        return graph.run(query)

    def getLatest(self):

        query = '''
            MATCH (u1:User {email: "%s"})
            MATCH (m:Movie)
            WHERE NOT EXISTS( (u1)-[:movieWatched]->(m) )
            RETURN m
            ORDER BY m.year DESC
            LIMIT 10
        ''' % (self.email)

        movies = graph.run(query)
        # print(movies)
        return getSerializedMovies(movies)

    def getRecommendation13(self):
        user = self.find()

        query = '''
            MATCH (m:Movie)-[]->()<-[]-(u:User)
            WHERE id(u) = %d AND
            NOT (u)-[:movieWatched]->(m)
            RETURN m, count(*)
            ORDER BY m.criticsRating*count(*) DESC
            LIMIT 10
        ''' % (user.identity)

        movies = graph.run(query)
        # print(movies)
        return getSerializedMovies(movies)


    def getRecommendation14(self):

        user = self.find()
        query = '''
        MATCH (u1:User)-[r:movieWatched]->(m:Movie)
        WHERE id(u1) = %d
        WITH u1, avg(r.rating) AS u1_mean

        MATCH (u1)-[r1:movieWatched]->(m:Movie)<-[r2:movieWatched]-(u2)
        WITH u1, u1_mean, u2, COLLECT({r1: r1, r2: r2}) AS ratings

        MATCH (u2)-[r:movieWatched]->(m:Movie)
        WITH u1, u1_mean, u2, avg(r.rating) AS u2_mean, ratings

        UNWIND ratings AS r

        WITH sum( (r.r1.rating-u1_mean) * (r.r2.rating-u2_mean) ) AS nom,
             sqrt( sum( (r.r1.rating - u1_mean)^2) * sum( (r.r2.rating - u2_mean) ^2)) AS denom,
             u1, u2 WHERE denom <> 0

        WITH u1, u2, nom/denom AS pearson
        ORDER BY pearson DESC LIMIT 10

        MATCH (u2)-[r:movieWatched]->(m:Movie) WHERE NOT EXISTS( (u1)-[:movieWatched]->(m) )

        RETURN m, SUM( pearson * r.rating) AS score
        ORDER BY score DESC LIMIT 10
        ''' % (user.identity)

        movies = graph.run(query)
        return getSerializedMovies(movies)


    def getRecommendation15(self):
        user = self.find()

        query = '''
        MATCH (u1:User)-[r:movieWatched]->(m:Movie)
        WHERE id(u1) = %d
        WITH u1, avg(r.rating) AS u1_mean

        MATCH (u1)-[:friend]->(:Friendship)<-[:friend]-(u2:User)
        MATCH (u1)-[r1:movieWatched]->(m:Movie)<-[r2:movieWatched]-(u2)
        WITH u1, u1_mean, u2, COLLECT({r1: r1, r2: r2}) AS ratings

        MATCH (u2)-[r:movieWatched]->(m:Movie)
        WITH u1, u1_mean, u2, avg(r.rating) AS u2_mean, ratings

        UNWIND ratings AS r

        WITH sum( (r.r1.rating-u1_mean) * (r.r2.rating-u2_mean) ) AS nom,
             sqrt( sum( (r.r1.rating - u1_mean)^2) * sum( (r.r2.rating - u2_mean) ^2)) AS denom,
             u1, u2 WHERE denom <> 0

        WITH u1, u2, nom/denom AS pearson
        ORDER BY pearson DESC LIMIT 10

        MATCH (u1)-[:friend]->(:Friendship)<-[:friend]-(u2:User)
        MATCH (u2)-[r:movieWatched]->(m:Movie) WHERE NOT EXISTS( (u1)-[:movieWatched]->(m) )

        RETURN m, SUM( pearson * r.rating) AS score
        ORDER BY score DESC LIMIT 10
        ''' % (user.identity)

        movies = graph.run(query)
        return getSerializedMovies(movies)

    def getUserRating(self, movieDict):
        user = self.find()

        query = '''
        MATCH (u:User)-[r:movieWatched]->(m:Movie)
        WHERE id(u) = %d and id(m) = %d
        RETURN r.rating
        ''' % (user.identity, movieDict['id'])

        ret = graph.run(query)
        for temp in ret:
            return temp
        return None


def addMovieFieldReationship(movieNode, fieldString, fieldNodeIdList):

    for fieldNodeId in fieldNodeIdList:
        matcher = NodeMatcher(graph)
        x = matcher.get(int(fieldNodeId))

        rel = Relationship(movieNode, 'movie' + fieldString, x)
        graph.create(rel)


class Movie:
    def __init__(self, title, year, criticsRating, imageURL="", isURL=1):
        self.title = title
        self.year = year
        self.criticsRating = criticsRating
        self.imageURL = imageURL
        self.isURL = isURL

    @staticmethod
    def find_by_id(id):
        matcher = NodeMatcher(graph)
        return matcher.get(int(id))

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("Genre", title=self.title, year=self.year, criticsRating=self.criticsRating)).first()

    def add(self, genreIdList, countryIdList, actorIdList, directorIdList):
        movie = Node('Movie', title=self.title, year=self.year, criticsRating=self.criticsRating, imageURL=self.imageURL, isURL=self.isURL)
        graph.create(movie)
        self.id = movie.identity

        addMovieFieldReationship(movie, 'Genre', genreIdList)
        addMovieFieldReationship(movie, 'Country', countryIdList)
        addMovieFieldReationship(movie, 'Actor', actorIdList)
        addMovieFieldReationship(movie, 'Director', directorIdList)

    @staticmethod
    def getAnyMovies():

        # q_list = ("[" + ', '.join(['%s']*len(FieldList)) + "]") % tuple(FieldList)

        query = f'''
            MATCH (m:Movie)
            RETURN m
            LIMIT 10
        '''

        movies = graph.run(query)
        return getSerializedMovies(movies)

    @staticmethod
    def getMostWatched(FieldString, FieldList):

        q_list = ("[" + ', '.join(['%s']*len(FieldList)) + "]") % tuple(FieldList)

        query = f'''
            MATCH (:User)-[:movieWatched]->(m:Movie)-[:movie{FieldString}]->(x:{FieldString})
            WHERE ID(x) IN {q_list}
            RETURN m, COUNT(*)
            ORDER BY COUNT(*) DESC
            LIMIT 10
        '''

        movies = graph.run(query)
        # print(movies)
        return getSerializedMovies(movies)

def changeIsPublicBackend(val, movieID, email):
    val = int(val)
    query = f'''
    MATCH (u:User)-[r:movieWatched]->(m:Movie)
    WHERE id(m) = {movieID} AND u.email = "{email}"
    SET r.isPublic = {val}
    RETURN r
    '''

    graph.run(query)
    # print(r)


def getMovie(title, year, genreIdList, countryIdList, actorIdList, directorIdList):
    query = '''
    MATCH (c:Movie)
    WHERE %s
    RETURN distinct c
    '''
    # print("--------------\n" , query % (Movie) , "\n-------------\n")
    s = 'True'
    if title:
        Movie_mod = title.lower()
        pref_len,suff_len = min(5,len(Movie_mod)) , min(5,len(Movie_mod))
        s += ' and (toLower(c.title) = "%s" or toLower(c.title) starts with "%s" or toLower(c.title) ends with "%s" or toLower(c.title) contains "%s")'%(Movie_mod , Movie_mod[:pref_len] , Movie_mod[-suff_len:] , Movie_mod)
    if year:
        s += ' and c.year = "%s"'%(year)
    for g in genreIdList:
        # print("hii")
        s += ' and exists{ Match (c)-[:movieGenre]->(g:Genre) where id(g) = %s}'%(g)
        # s += ' and (c)-[:movieGenre]->(gen) and id(gen) = %s'%(g)
    for coun in countryIdList:
        s += ' and exists{ Match (c)-[:movieCountry]->(g:Country) where id(g) = %s}'%(coun)
    for actor in actorIdList:
        s += ' and exists{ Match (c)-[:movieActor]->(g:Actor) where id(g) = %s}'%(actor)
    for director in directorIdList:
        s += ' and exists{ Match (c)-[:movieDirector]->(g:Director) where id(g) = %s}'%(director)


    # print(query%(s))
    allMovies = graph.run(query % (s))
    Movielist = []
    for record in allMovies:
        c = record['c']
        Movielist.append({
            'id': c.identity,
            'title': c['title'],
            'year': c['year'],
            'Rating': c['criticsRating'],
            'imageURL': c['imageURL'],
            'isURL': c['isURL'],
        })

    return Movielist

def displayMovieDetails(MovieID):
    query_genre = '''
    Match (c:Movie)-[:movieGenre]->(g:Genre)
    Where id(c) = %s
    Return g
    '''
    allGenres = graph.run(query_genre%(MovieID))
    GenreList = []
    for record in allGenres:
        g = record['g']
        GenreList.append({
            'id': g.identity,
            'genre': g['genre'],
        })

    query_actor = '''
    Match (c:Movie)-[:movieActor]->(g:Actor)
    Where id(c) = %s
    Return g
    '''
    # print("--------------\n" , query % (Actor) , "\n-------------\n")
    allActors = graph.run(query_actor % (MovieID))
    ActorList = []
    for record in allActors:
        c = record['g']
        ActorList.append({
            'id': c.identity,
            'name': c['name'],
        })

    query_director = '''
    Match (c:Movie)-[:movieDirector]->(g:Director)
    Where id(c) = %s
    Return g
    '''
    # print("--------------\n" , query % (Actor) , "\n-------------\n")
    allDirectors = graph.run(query_director % (MovieID))
    DirectorList = []
    for record in allDirectors:
        c = record['g']
        DirectorList.append({
            'id': c.identity,
            'name': c['name'],
        })

    query_country = '''
    Match (c:Movie)-[:movieCountry]->(g:Country)
    Where id(c) = %s
    Return g
    '''
    # print("--------------\n" , query % (Actor) , "\n-------------\n")
    allCountry = graph.run(query_country % (MovieID))
    CountryList = []
    for record in allCountry:
        c = record['g']
        CountryList.append({
            'id': c.identity,
            'country': c['country'],
        })

    query_movie = '''
    Match (c:Movie)
    Where id(c) = %s
    Return c
    '''

    allMovies = graph.run(query_movie % (MovieID))
    MovieList = []
    for record in allMovies:
        c = record['c']
        MovieList.append({
            'id': c.identity,
            'title': c['title'],
            'year': c['year'],
            'Rating': c['criticsRating'],
            'imageURL': c['imageURL'],
            'isURL': c['isURL'],
        })


    return MovieList, GenreList, ActorList, DirectorList, CountryList

def searchMovieusingName(Movie):
    # query = '''
    # MATCH (c:Movie)-[r]->(g)
    # WHERE toLower(c.title) = "%s"
    # RETURN c,g
    # UNION
    # MATCH (c:Movie)-[r]->(g)
    # WHERE toLower(c.title) STARTS WITH '%s'
    # RETURN c,g
    # UNION
    # MATCH (c:Movie)-[r]->(g)
    # WHERE toLower(c.title) ENDS WITH '%s'
    # RETURN c,g
    # UNION
    # MATCH (c:Movie)-[r]->(g)
    # WHERE toLower(c.title) CONTAINS '%s'
    # RETURN c,g
    # '''
    query = '''
    MATCH (c:Movie)
    WHERE toLower(c.title) = "%s"
    RETURN c LIMIT 10
    UNION
    MATCH (c:Movie)
    WHERE toLower(c.title) STARTS WITH '%s'
    RETURN c LIMIT 10
    UNION
    MATCH (c:Movie)
    WHERE toLower(c.title) ENDS WITH '%s'
    RETURN c LIMIT 10
    UNION
    MATCH (c:Movie)
    WHERE toLower(c.title) CONTAINS '%s'
    RETURN c LIMIT 10
    '''
    pref_len,suff_len = min(5,len(Movie)) , min(5,len(Movie))
    Movie_mod = Movie.lower()
    similarMovies = graph.run(query % (Movie_mod , Movie_mod[:pref_len] , Movie_mod[-suff_len:] , Movie_mod.split()[0]))
    Movielist = []

    for record in similarMovies:
        c = record['c']
        # g = record['g']
        # print("type : " , type(c) , " ==== " , type(g))
        Movielist.append({
            'id': c.identity,
            'title': c['title'],
            'year': c['year'],
            'Rating': c['criticsRating'],
            'imageURL': c['imageURL'],
            'isURL': c['isURL'],
        })
    return Movielist

class Genre:
    def __init__(self, genre):
        self.genre = genre

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("Genre", genre=self.genre)).first()

    def add(self):
        if not self.find():
            genreNode = Node('Genre', genre=self.genre)
            graph.create(genreNode)
            self.id = genreNode.identity
            return True
        else:
            return False

def getAllGenreSerialized():
    query = '''
    MATCH (g:Genre)
    RETURN g
    '''

    allGenres = graph.run(query)
    serializedAllGenres = []
    for record in allGenres:
        g = record['g']
        serializedAllGenres.append({
            'id': g.identity,
            'genre': g['genre'],
        })

    return serializedAllGenres

def getUserGenreSerialized(email):
    query = f'''
    MATCH (u:User)-[:genrePreference]->(g:Genre)
    WHERE u.email = "{email}"
    RETURN g
    '''

    userGenres = graph.run(query)
    serializedUserGenres = []
    for record in userGenres:
        g = record['g']
        serializedUserGenres.append({
            'id': g.identity,
            'genre': g['genre'],
        })

    return serializedUserGenres

class Country:
    def __init__(self, country):
        self.country = country

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("Country", country=self.country)).first()

    def add(self):
        if not self.find():
            countryNode = Node('Country', country=self.country)
            graph.create(countryNode)
            self.id = countryNode.identity
            return True
        else:
            return False

def getAllCountrySerialized():
    query = '''
    MATCH (c:Country)
    RETURN c
    '''

    allCountrys = graph.run(query)
    serializedAllCountrys = []
    for record in allCountrys:
        c = record['c']
        serializedAllCountrys.append({
            'id': c.identity,
            'country': c['country'],
        })

    return serializedAllCountrys

def getUserCountrySerialized(email):
    query = f'''
    MATCH (u:User)-[:countryPreference]->(c:Country)
    WHERE u.email = "{email}"
    RETURN c
    '''

    userCountrys = graph.run(query)
    serializedUserCountrys = []
    for record in userCountrys:
        c = record['c']
        serializedUserCountrys.append({
            'id': c.identity,
            'country': c['country'],
        })

    return serializedUserCountrys

class Actor:
    def __init__(self, name):
        self.name = name

    def add(self):
        actorNode = Node('Actor', name=self.name)
        graph.create(actorNode)
        self.id = actorNode.identity
        return

def getActor(Actor):
    query = '''
    MATCH (c:Actor)
    WHERE c.name = "%s"
    RETURN c
    '''
    # print("--------------\n" , query % (Actor) , "\n-------------\n")
    allActors = graph.run(query % (Actor))
    Actorlist = []
    for record in allActors:
        c = record['c']
        Actorlist.append({
            'id': c.identity,
            'name': c['name'],
        })

    return Actorlist

def getAllUsersSerialized():
    query = '''
    MATCH (u:User)
    WHERE u.name <> 'admin'
    RETURN u
    '''

    allUsers = graph.run(query)
    serializedAllUsers = []
    for record in allUsers:
        u = record['u']
        print(u)
        serializedAllUsers.append({
            'id': u.identity,
            'name': u['name'],
            'email': u['email'],
            'is_staff': u['is_staff']
        })

    return serializedAllUsers

def getAllActorSerialized():
    query = '''
    MATCH (a:Actor)
    RETURN a
    '''

    allActors = graph.run(query)
    serializedAllActors = []
    for record in allActors:
        a = record['a']
        serializedAllActors.append({
            'id': a.identity,
            'name': a['name'],
        })

    return serializedAllActors

def getAllActorSerialized2(Actor):
    query = '''
    MATCH (a:Actor),
    (m:Movie)-[:movieActor]->(a)
    WHERE toLower(a.name) CONTAINS '%s'
    WITH m, a
    ORDER BY m.year DESC
    RETURN a, COLLECT({id: ID(m), title: m.title})[0..5] as movies
    LIMIT 100
    ''' % Actor.lower()

    allActors = graph.run(query)
    serializedAllActors = []

    for record in allActors:
        a = record['a']
        mlist = record['movies']
        serializedAllActors.append({
            'id': a.identity,
            'name': a['name'],
            'movieList': mlist
        })

    return serializedAllActors

def getUserActorSerialized(email):
    query = f'''
    MATCH (u:User)-[:actorPreference]->(a:Actor)
    WHERE u.email = "{email}"
    RETURN a
    '''

    userActors = graph.run(query)
    serializedUserActors = []
    for record in userActors:
        a = record['a']
        serializedUserActors.append({
            'id': a.identity,
            'name': a['name'],
        })

    return serializedUserActors

class Director:
    def __init__(self, name):
        self.name = name

    def add(self):
        directorNode = Node('Director', name=self.name)
        graph.create(directorNode)
        self.id = directorNode.identity
        return

def getDirector(Director):
    query = '''
    MATCH (c:Director)
    WHERE c.name = "%s"
    RETURN c
    '''
    # print("--------------\n" , query % (Actor) , "\n-------------\n")
    allDirectors = graph.run(query % (Director))
    Directorslist = []
    for record in allDirectors:
        c = record['c']
        Directorslist.append({
            'id': c.identity,
            'name': c['name'],
        })

    return Directorslist

def getAllDirectorSerialized():
    query = '''
    MATCH (d:Director)
    RETURN d
    '''

    allDirectors = graph.run(query)
    serializedAllDirectors = []
    for record in allDirectors:
        d = record['d']
        serializedAllDirectors.append({
            'id': d.identity,
            'name': d['name'],
        })

    return serializedAllDirectors

def getAllDirectorSerialized2(Director):
    query = '''
    MATCH (d:Director),
    (m:Movie)-[:movieDirector]->(d)
    WHERE toLower(d.name) CONTAINS '%s'
    WITH m, d
    ORDER BY m.year DESC
    RETURN d, COLLECT({id: ID(m), title: m.title})[0..5] as movies
    LIMIT 100
    ''' % Director.lower()

    allDirctors = graph.run(query)
    serializedAllDirctors = []

    for record in allDirctors:
        d = record['d']
        mlist = record['movies']
        serializedAllDirctors.append({
            'id': d.identity,
            'name': d['name'],
            'movieList': mlist
        })

    return serializedAllDirctors

def getUserDirectorSerialized(email):
    query = f'''
    MATCH (u:User)-[:directorPreference]->(d:Director)
    WHERE u.email = "{email}"
    RETURN d
    '''

    userDirectors = graph.run(query)
    serializedUserDirectors = []
    for record in userDirectors:
        d = record['d']
        serializedUserDirectors.append({
            'id': d.identity,
            'name': d['name'],
        })

    return serializedUserDirectors