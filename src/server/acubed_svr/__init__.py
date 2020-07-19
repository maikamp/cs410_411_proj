from flask import Flask
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

from acubed_svr import routes