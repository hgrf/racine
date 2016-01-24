from flask import Blueprint

printdata = Blueprint('printdata', __name__)

from . import views