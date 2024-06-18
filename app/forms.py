from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField # type: ignore
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo # type: ignore
import sqlalchemy as sa # type: ignore
from app import db
from app.models import User

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
        

class TransactionForm(FlaskForm):
    transaction_date = DateField('Transaction Date', validators=[DataRequired()])
    account_id = IntegerField('Account', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

class AccountForm(FlaskForm):
    account_name = StringField('Name of Account', validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name')
    surname = StringField('Surname')
    dob = DateField('Transaction Date')
    firstlineaddress = StringField('First Line Address')
    city = StringField('Town/City')
    postcode = StringField('Post Code')
    submit = SubmitField()

                  
