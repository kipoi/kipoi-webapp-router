"""
Main app view containing the app instance and global variables
"""
import os
from flask import Flask
from flask_cors import CORS


def get_app_base_path():
    """ Get app base path. """
    return os.path.dirname(os.path.realpath(__file__))


def get_instance_folder_path():
    """ Get instance folder path. """
    return os.path.join(get_app_base_path(), 'instance')


app = Flask(__name__,
            instance_path=get_instance_folder_path())
app.config['JSON_SORT_KEYS'] = False
CORS(app)

app.config.from_pyfile('config.py')

from app.routes import bp

app.register_blueprint(bp)

from app.cache import cache

cache.init_app(app)
