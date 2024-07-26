from flask import Blueprint

bp = Blueprint('socket_events', __name__)

from app.socket_events import game_events