from flask import Blueprint
from app.game.context_processor import load_game

bp = Blueprint('game', __name__)

@bp.before_app_request
def before_request():
    load_game()

from app.game import routes