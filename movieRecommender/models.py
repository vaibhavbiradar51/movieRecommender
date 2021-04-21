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
            return True
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