from flask import Blueprint

bp = Blueprint('testgame', __name__)

from app.testgame import routes