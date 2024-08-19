from flask_wtf import FlaskForm                                                     # type:ignore
from wtforms import StringField, SubmitField, SelectField, IntegerField             # type:ignore
from wtforms.validators import DataRequired                                         # type:ignore
from app.models import User, Role



## Admin Forms

class CreateRoleForm(FlaskForm):
    role_name = StringField('Role Name', validators=[DataRequired()])
    submit = SubmitField('Create Role')

class AssignRoleForm(FlaskForm):
    user_id = SelectField('User ID', coerce=int)
    role_id = SelectField('Role ID', coerce=int)
    submit = SubmitField('Assign Role')

    def __init__(self, *args, **kwargs):
        super(AssignRoleForm, self).__init__(*args, **kwargs)
        self.user_id.choices = [(user.id, user.username) for user in User.query.all()]  # Assuming User model has id and name fields
        self.role_id.choices = [(role.id, role.name) for role in Role.query.all()]  # Assuming Role model has id and name fields


## Game related admin forms

## Game Level Requirements Forms
class LevelRequirementsForm(FlaskForm):
    level = IntegerField('Level', validators=[DataRequired()])
    xp_required = IntegerField('XP Required', validators=[DataRequired()])
    addlevel_button = SubmitField('Submit')