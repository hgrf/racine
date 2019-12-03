from flask import Blueprint

settings = Blueprint('settings', __name__)

from . import views
