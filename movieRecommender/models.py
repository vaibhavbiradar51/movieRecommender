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

class Movie:
    def __init__(self, title, year, criticsRating):
        self.title = title
        self.year = year
        self.criticsRating = criticsRating

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

class Actor:
    def __init__(self, name):
        self.name = name

    def add(self):
        actorNode = Node('Actor', name=self.name)
        graph.create(actorNode)
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

class Director:
    def __init__(self, name):
        self.name = name

    def add(self):
        directorNode = Node('Director', name=self.name)
        graph.create(directorNode)
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