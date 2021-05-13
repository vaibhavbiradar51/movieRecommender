from movieRecommender import app
import os

app.secret_key = os.urandom(24)
app.run(host="boomsi.azurewebsites.net",debug=True)           
