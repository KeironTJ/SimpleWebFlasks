from flask import g
from flask_login import current_user
from app.models import Game

def load_game():
    if current_user.is_authenticated:
        game_id = current_user.activegame
        if game_id:
            g.game = Game.query.get(game_id)
        else:
            g.game = None
    else:
        g.game = None