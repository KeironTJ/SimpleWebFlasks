from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
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
