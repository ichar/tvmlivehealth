from flask import Blueprint

scenario = Blueprint('scenario', __name__)

from . import views
