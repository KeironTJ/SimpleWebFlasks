from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime # type: ifnore
import sqlalchemy.orm as so # type: ignore
from app import db, login
from flask_login import UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(64), index=True, unique=True)
    firstname = db.Column(String(64), nullable=True)
    surname = db.Column(String(64), nullable=True)
    dob = db.Column(DateTime, nullable=True)
    firstlineaddress = db.Column(String(64), nullable=True)
    city = db.Column(String(64), nullable=True)
    postcode = db.Column(String(64), nullable=True)
    email = db.Column(String(120), index=True, unique=True)
    password_hash = db.Column(String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(64))
    transactions = db.relationship("Transaction", back_populates="account")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    item_name = db.Column(db.String(64), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    account = db.relationship("Account", back_populates="transactions")


class TransactionCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(64))
    parent_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))






