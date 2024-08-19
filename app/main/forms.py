from flask_wtf import FlaskForm                             # type:ignore
from wtforms import StringField, DateField, SubmitField     # type:ignore


class ProfileForm(FlaskForm):
    firstname = StringField('First Name')
    surname = StringField('Surname')
    dob = DateField('Transaction Date')
    firstlineaddress = StringField('First Line Address')
    city = StringField('Town/City')
    postcode = StringField('Post Code')
    submit = SubmitField()
