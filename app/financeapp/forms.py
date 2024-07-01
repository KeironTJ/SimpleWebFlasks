from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, StringField, FloatField, SubmitField
from wtforms.validators import DataRequired




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