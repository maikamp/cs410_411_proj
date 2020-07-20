from flask import Flask
from .config import Config
import os
os.environ.setdefault('PYPANDOC_PANDOC', '/usr/local/bin/pandoc')

app = Flask(__name__)
app.config.from_object(Config)

from acubed_svr import routes