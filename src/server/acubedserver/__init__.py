from Flask import Flask
from config import Config


app = Flask(__name__)
  app.config.from_object(Config)

from acubedserver import routes
