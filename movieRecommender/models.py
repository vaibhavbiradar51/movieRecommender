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
        return len(matcher.match("User", email=self.email))

    def signup(self, password):
        if not self.find():
            user = Node('User', email=self.email, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            print("here")
            # return bcrypt.verify(password, user['password'])
            return True
        else:
            return False