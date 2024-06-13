from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    transactions: so.WriteOnlyMapped["Transaction"] = so.relationship()


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Account(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    account_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    transactions: so.WriteOnlyMapped["Transaction"] = so.relationship()

    
class Transaction(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    transaction_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    account_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Account.id))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))



