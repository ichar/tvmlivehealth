from flask import Blueprint

appbot = Blueprint('bot', __name__)

from . import views
