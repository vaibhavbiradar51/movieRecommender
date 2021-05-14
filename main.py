from movieRecommender import app
import os


if __name__ == '__main__':
  


  app.secret_key = os.urandom(24)
  app.run(host='boomsi.azurewebsites.net',port=8000, debug=True)           
