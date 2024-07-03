from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime # type: ignore
import sqlalchemy.orm as so # type: ignore
from app import db, login
from flask_login import UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash


## USER RELATED MODELS

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
    active = db.Column(db.Boolean(), default=True)
    activetestgame = db.Column(db.Integer, nullable=True)

    testgame = so.relationship("TestGame", back_populates="user")
    role=so.relationship("Role", secondary="user_roles")


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return 'admin' in [role.name for role in self.role]
    

## ADMIN RELATED MODELS
# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '<Role {}>'.format(self.name)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    




## FINANCE APP RELATED MODELS
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(64))
    transactions = db.relationship("Transaction", back_populates="account")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("transaction_category.id"), nullable=True)
    item_name = db.Column(db.String(64), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    account = db.relationship("Account", back_populates="transactions")
    category = db.relationship("TransactionCategory", back_populates="transactions")


class TransactionCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(64))
    parent_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    transactions = db.relationship("Transaction", back_populates="category")





## GUESS THE NUMBER RELATED MODELS
class GTNSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    startrange = db.Column(db.Integer, default=1)
    endrange = db.Column(db.Integer, default=100)
    
class GTNHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User")
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    startrange = db.Column(db.Integer)
    endrange = db.Column(db.Integer)
    number = db.Column(db.Integer)
    guesses = db.Column(db.Integer)


# Model representing a game test case
class TestGame(db.Model):
    __tablename__ = 'test_game'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    # Basic game information
    game_name = db.Column(db.String(64))
    game_exists = db.Column(db.Boolean, default=False)
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    cash = db.Column(db.Float, default=5000)
    
    # Relationships
    user = db.relationship("User", backref="test_games")
    inventory = db.relationship("TestGameInventory", back_populates="test_game")
    items = db.relationship("TestGameItem", backref="test_game")
    


    

# Model representing items within a game
class TestGameItem(db.Model):
    __tablename__ = 'test_game_items'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key to TestGame
    testgame_id = db.Column(db.Integer, db.ForeignKey("test_game.id"))
    
    # Item details
    item_name = db.Column(db.String(64))
    item_cost = db.Column(db.Float)
    item_xp = db.Column(db.Integer)
    item_level = db.Column(db.Integer)
    item_type = db.Column(db.String(64))
    item_description = db.Column(db.String(256))
    

# Model representing a user's inventory for a game
class TestGameInventory(db.Model):
    __tablename__ = 'test_game_inventory'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    test_game_id = db.Column(db.Integer, db.ForeignKey("test_game.id"))
    
    # Inventory details
    item_id = db.Column(db.Integer, db.ForeignKey("test_game_items.id"))
    quantity = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship("User", backref="inventories")
    item = db.relationship("TestGameItem", backref="inventories")
    test_game = db.relationship("TestGame", back_populates="inventory")


# Model to log xp transactions
class TestGameXPLog(db.Model):
    __tablename__ = 'test_game_xp_log'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    test_game_id = db.Column(db.Integer, db.ForeignKey("test_game.id"))

    # XP details
    xp = db.Column(db.Integer)
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
   
    # Relationships
    test_game = db.relationship("TestGame", backref="xp_logs")
    user = db.relationship("User", backref="xp_logs")

class TestGameCashLog(db.Model):
    __tablename__ = 'test_game_cash_log'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    test_game_id = db.Column(db.Integer, db.ForeignKey("test_game.id"))

    # Cash details
    cash = db.Column(db.Float)
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    test_game = db.relationship("TestGame", backref="cash_logs")
    user = db.relationship("User", backref="cash_logs")


# Create Model to store level requirements, not specfic to use or game
class TestGameLevelRequirements(db.Model):
    __tablename__ = 'test_game_level_requirements'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Level requirements
    level = db.Column(db.Integer)
    xp_required = db.Column(db.Integer)

    


## TODO: CREATE MODELS FOR QUESTS, QUEST REWARDS, AND QUEST PROGRESS not game_id specific

