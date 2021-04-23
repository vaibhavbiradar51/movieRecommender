from py2neo import Graph, Node, Relationship, NodeMatcher
from passlib.hash import bcrypt
from . import config

# url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')


graph = Graph(config.url + '/db/data/', username=config.username, password=config.password)

class User:
    def __init__(self, email):
        self.email = email

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("User", email=self.email)).first()

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

    def get_friends(self):
        user = self.find()
        matcher = NodeMatcher(graph)
        return list(matcher.match("Friendship", ID1=user.identity)) + list(matcher.match("Friendship", ID2=user.identity))

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

    @staticmethod
    def searchUser(text):
        query = '''
            MATCH (u:User)
            WHERE u.email STARTS WITH '%s'
            OR u.name STARTS WITH '%s'
            RETURN u;
        ''' % (text, text)
        return graph.run(query)


def addMovieFieldReationship(movieNode, fieldString, fieldNodeIdList):

    for fieldNodeId in fieldNodeIdList:
        matcher = NodeMatcher(graph)
        x = matcher.get(int(fieldNodeId))
        print(x)
        print(type(x))

        rel = Relationship(movieNode, 'movie' + fieldString, x)
        graph.create(rel)


class Movie:
    def __init__(self, title, year, criticsRating):
        self.title = title
        self.year = year
        self.criticsRating = criticsRating

    def find(self):
        matcher = NodeMatcher(graph)
        return (matcher.match("Genre", genre=self.genre)).first()

    def add(self, genreIdList, countryIdList, actorIdList, directorIdList):
        movie = Node('Movie', title=self.title, year=self.year, criticsRating=self.criticsRating)
        graph.create(movie)
        self.id = movie.identity

        addMovieFieldReationship(movie, 'Genre', genreIdList)
        addMovieFieldReationship(movie, 'Country', countryIdList)
        addMovieFieldReationship(movie, 'Actor', actorIdList)
        addMovieFieldReationship(movie, 'Director', directorIdList)

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
    query = '''
    MATCH (u:User)-[:genrePreference]->(g:Genre)
    WHERE u.email = {e}
    RETURN g
    '''

    userGenres = graph.run(query, e=email)
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

# def getUserCountrySerialized(email):
#     query = '''
#     MATCH (u:User)-[:countryPreference]->(g:Country)
#     WHERE u.email = {e}
#     RETURN g
#     '''

#     userGenres = graph.run(query, e=email)
#     serializedUserGenres = []
#     for record in userGenres:
#         g = record['g']
#         serializedUserGenres.append({
#             'id': g.identity,
#             'genre': g['genre'],
#         })

#     return serializedUserGenres

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