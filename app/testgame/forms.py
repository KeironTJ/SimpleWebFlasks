

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.models import TestGame
from flask_login import current_user

class NewGameForm(FlaskForm):
    game_name = StringField('Game Name', validators=[DataRequired()])
    newgame_button = SubmitField('Create Game')

class LoadGameForm(FlaskForm):
    game_id = SelectField('Select Game', coerce=int)
    loadgame_button = SubmitField('Load Game')

    def __init__(self, *args, **kwargs):
        super(LoadGameForm, self).__init__(*args, **kwargs)
        self.game_id.choices = [(game.id, game.game_name) for game in TestGame.query.filter_by(user_id=current_user.id).all()][::-1]

class AddXPForm(FlaskForm):
    xp = SelectField('XP', coerce=int, choices=[(x, x) for x in range(100, 1000)])
    addxp_button = SubmitField('Add XP')

class AddCashForm(FlaskForm):
    cash = SelectField('Cash', coerce=int, choices=[(x, x) for x in range(100, 1000)])
    addcash_button = SubmitField('Add Cash')
