from flask_wtf import FlaskForm                                                             # type:ignore
from wtforms import StringField, SubmitField, SelectField, IntegerField, HiddenField        # type:ignore
from wtforms.validators import DataRequired                                                 # type:ignore 
from flask_login import current_user                                                        # type:ignore                                             # type:ignore
from app.models import Game 


## Game Setup related Forms
class NewGameForm(FlaskForm):
    game_name = StringField('Game Name', validators=[DataRequired()])
    newgame_button = SubmitField('Create Game')

class LoadGameForm(FlaskForm):
    game_id = SelectField('Select Game', coerce=int)
    loadgame_button = SubmitField('Load Game')

    def __init__(self, *args, **kwargs):
        super(LoadGameForm, self).__init__(*args, **kwargs)
        self.game_id.choices = [(game.id, game.game_name) for game in Game.query.filter_by(user_id=current_user.id).all()][::-1]


## Game Play related Forms
class AddXPForm(FlaskForm):
    xp = IntegerField('XP', validators=[DataRequired()])
    addxp_button = SubmitField('Add XP')

class AddCashForm(FlaskForm):
    cash = IntegerField('Cash', validators=[DataRequired()])
    addcash_button = SubmitField('Add Cash')

class AddResourcesForm(FlaskForm):
    xp = IntegerField('XP')
    cash = IntegerField('Cash')
    wood = IntegerField('Wood')
    stone = IntegerField('Stone')
    metal = IntegerField('Iron')
    add_button = SubmitField('Add Resources')

class CollectResourcesForm(FlaskForm):
    collect_button = SubmitField('Collect Resources')
    

class UpgradeBuildingForm(FlaskForm):
    upgrade_button = SubmitField('Upgrade')

class CompleteQuestForm(FlaskForm):
    quest_id = HiddenField('Quest ID')
    complete_button = SubmitField('Complete Quest')




