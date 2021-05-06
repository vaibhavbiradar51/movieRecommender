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
        serializedMovies.append({
            'id': m.identity,
            'title': m['title'],
            'year': m['year'],
            'criticsRating': m['criticsRating'],
        })

    return serializedMovies


class User:
    def __init__(self, email):
        self.email = email

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("User", email=self.email)).first()

    @staticmethod
    def find_by_id(id):
        query = '''
        MATCH (m:Movie)
        WHERE id(m) = %d
        RETURN m
        ''' % id

        movies = getSerializedMovies(graph.run(query))
        return movies[0]

    def signup(self, name, password):
        if not self.find():
            user = Node('User', email=self.email, name=name, password=bcrypt.encrypt(password))
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

        if user1.identity > user2.identity:
            user1, user2 = user2, user1

        friendship = Node('Friendship', ID1=user1.identity, ID2=user2.identity)
        graph.create(friendship)

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

    def addWatchedMovieRating(self, MovieRatingMap):
        for key,value in MovieRatingMap.items():
            query = '''
                MATCH (a:User), (b:Movie)
                WHERE a.email = '%s' AND id(b) = %s
                MERGE (a)-[r:movieWatched]->(b)
                ON CREATE SET r.Rating = %s , r.IsPublic = %s
                ON MATCH SET r.Rating = %s , r.IsPublic = %s
                RETURN r
            '''
            query = query % (self.email , key , value , 1 , value, 1)
            graph.run(query)

    def getPublicWatchedMovieHistory(self):
        query = '''
            MATCH (a:User), (m:Movie)
            WHERE a.email = '%s'
            MATCH (a)-[r:movieWatched]->(m)
            RETURN m
        '''
        query = query % (self.email)
        return getSerializedMovies(graph.run(query))

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

    def getRecommendation13(self):
        query = '''
        MATCH (m:Movie)
        RETURN m
        LIMIT 10
        '''
        movies = graph.run(query)
        return getSerializedMovies(movies)


    def getRecommendation14(self):
        query = '''
        MATCH (m:Movie)
        RETURN m
        LIMIT 10
        '''

        movies = graph.run(query)
        return getSerializedMovies(movies)


    def getRecommendation15(self):
        query = '''
        MATCH (m:Movie)
        RETURN m
        LIMIT 10
        '''

        movies = graph.run(query)
        return getSerializedMovies(movies)


def addMovieFieldReationship(movieNode, fieldString, fieldNodeIdList):

    for fieldNodeId in fieldNodeIdList:
        matcher = NodeMatcher(graph)
        x = matcher.get(int(fieldNodeId))

        rel = Relationship(movieNode, 'movie' + fieldString, x)
        graph.create(rel)


class Movie:
    def __init__(self, title, year, criticsRating):
        self.title = title
        self.year = year
        self.criticsRating = criticsRating

    @staticmethod
    def find_by_id(id):
        matcher = NodeMatcher(graph)
        return matcher.get(int(id))

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("Genre", title=self.title, year=self.year, criticsRating=self.criticsRating)).first()

    def add(self, genreIdList, countryIdList, actorIdList, directorIdList):
        movie = Node('Movie', title=self.title, year=self.year, criticsRating=self.criticsRating)
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
        return getSerializedMovies(movies)

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
    RETURN c
    UNION
    MATCH (c:Movie)
    WHERE toLower(c.title) STARTS WITH '%s'
    RETURN c
    UNION
    MATCH (c:Movie)
    WHERE toLower(c.title) ENDS WITH '%s'
    RETURN c
    UNION
    MATCH (c:Movie)
    WHERE toLower(c.title) CONTAINS '%s'
    RETURN c
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