from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired


## Guess the Number Forms
class GuessTheNumberForm(FlaskForm):
    guess = IntegerField('Guess')
    submit_guess = SubmitField('Submit Guess')

class GuessTheNumberSettingsForm(FlaskForm):
    startrange = IntegerField('Start Range', validators=[DataRequired()])
    endrange = IntegerField('End Range', validators=[DataRequired()])
    submit_settings = SubmitField('Save Settings')

class GuessTheNumberResetForm(FlaskForm):
    submit_reset = SubmitField('Reset Game')