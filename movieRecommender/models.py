from py2neo import Graph, Node, Relationship, NodeMatcher
from passlib.hash import bcrypt
import os

# url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')
url = "http://localhost:7474"
username = "neo4j"
password = "pulkit@neo4j"

graph = Graph(url + '/db/data/', username=username, password=password)

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
        else:
            return False

    def get_friends(self):
        user = self.find()
        matcher = NodeMatcher(graph)
        return list(matcher.match("Friendship", ID1=user.identity)) + list(matcher.match("Friendship", ID2=user.identity))

    @staticmethod
    def searchUser(text):
        matcher = NodeMatcher(graph)
        return list(matcher.match("User", email__startwith=text)) + list(matcher.match("User", name__startswith=text))

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

class Director:
    def __init__(self, name):
        self.name = name

    def add(self):
        directorNode = Node('Director', name=self.name)
        graph.create(directorNode)
        return

def getActor(Actor):
    query = '''
    MATCH (c:Actor)
    WHERE c.name = %s
    RETURN c
    '''
    print("--------------\n" , query % (Actor) , "\n-------------\n")
    allActors = graph.run(query % (Actor))
    Actorlist = []
    for record in allCountrys:
        c = record['c']
        Actorlist.append({
            'id': c.identity,
            'name': c['name'],
        })

    return Actorlist