from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField


class ProfileForm(FlaskForm):
    firstname = StringField('First Name')
    surname = StringField('Surname')
    dob = DateField('Transaction Date')
    firstlineaddress = StringField('First Line Address')
    city = StringField('Town/City')
    postcode = StringField('Post Code')
    submit = SubmitField()
