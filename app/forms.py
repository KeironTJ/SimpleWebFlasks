from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField, FloatField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo # type: ignore
import sqlalchemy as sa # type: ignore
from app import db
from app.models import User, TransactionCategory, Role
from flask_login import current_user


## User Forms 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
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


## Finance Forms
class TransactionForm(FlaskForm):
    transaction_date = DateField('Transaction Date', validators=[DataRequired()])
    account_id = IntegerField('Account', validators=[DataRequired()])
    category_id = IntegerField('Category', validators=[DataRequired()])
    item_name = StringField('Item', validators=[DataRequired()] )
    amount = FloatField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

class TransactionCategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class AccountForm(FlaskForm):
    account_name = StringField('Name of Account', validators=[DataRequired()])
    submit = SubmitField('Add Account')


class ProfileForm(FlaskForm):
    first_name = StringField('First Name')
    surname = StringField('Surname')
    dob = DateField('Transaction Date')
    firstlineaddress = StringField('First Line Address')
    city = StringField('Town/City')
    postcode = StringField('Post Code')
    submit = SubmitField()

                  
