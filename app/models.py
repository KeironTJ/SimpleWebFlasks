from datetime import datetime, timezone, timedelta
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

    # Relationships
    test_game = so.relationship("TestGame", back_populates="user", cascade="all, delete-orphan")
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


## TEST GAME RELATED MODELS
# Model representing a game test case
class TestGame(db.Model):
    __tablename__ = 'test_game'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic game information
    game_name = db.Column(db.String(64))
    game_exists = db.Column(db.Boolean, default=True)
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=0)
    cash = db.Column(db.Float, default=0)
    wood = db.Column(db.Integer, default=0)
    stone = db.Column(db.Integer, default=0)
    metal = db.Column(db.Integer, default=0)

    
    next_level_xp_required = db.Column(db.Integer, default=110)
    
    # create relationships
    user = db.relationship("User", back_populates="test_game")
    inventories = db.relationship("TestGameInventoryUser", back_populates="game")
    quest_progress = db.relationship("TestGameQuestProgress", back_populates="quest_game")
    building_progress = db.relationship("TestGameBuildingProgress", back_populates="game")
    test_game_resource_logs = db.relationship("TestGameResourceLog", back_populates="testgame")
    
    
class TestGameInventoryType(db.Model):
    __tablename__ = 'test_game_inventory_types'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Inventory type details
    inventory_type_name = db.Column(db.String(64))
    inventory_type_description = db.Column(db.String(256))

    # Relationships
    inventory = db.relationship("TestGameInventory", back_populates="inventory_type")
    


class TestGameInventory(db.Model):
    __tablename__ = 'test_game_inventory'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Inventory Details
    inventory_name = db.Column(db.String(64))
    inventory_description = db.Column(db.String(256))

    # Foreign keys
    inventory_type_id = db.Column(db.Integer, db.ForeignKey('test_game_inventory_types.id'), nullable=False)

    # Relationships
    inventory_type = db.relationship("TestGameInventoryType", back_populates="inventory")
    inventory_user = db.relationship("TestGameInventoryUser", back_populates="inventory")
    

class TestGameInventoryUser(db.Model):
    __tablename__ = 'test_game_inventory_user'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    game_id = db.Column(db.Integer, db.ForeignKey('test_game.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('test_game_inventory.id'))
    
    # Relationships
    inventory = db.relationship("TestGameInventory", back_populates="inventory_user")
    inventory_items = db.relationship("TestGameInventoryItems", back_populates="inventory")
    game = db.relationship("TestGame", back_populates="inventories")


# Model to store reward item associations
class RewardItemAssociation(db.Model):
    __tablename__ = 'reward_item_association'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    reward_id = db.Column(db.Integer, db.ForeignKey('test_game_rewards.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('test_game_items.id'))
    quantity = db.Column(db.Integer, default=1)
    
    # Relationships
    reward = db.relationship("TestGameQuestRewards", backref="reward_items")
    item = db.relationship("TestGameItem", backref="reward_items")



class TestGameItem(db.Model):
    __tablename__ = 'test_game_items'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Item details
    item_name = db.Column(db.String(64))
    item_cost = db.Column(db.Float)
    item_xp = db.Column(db.Integer)
    item_level = db.Column(db.Integer)
    item_type = db.Column(db.String(64))
    item_description = db.Column(db.String(256))

    # Relationships
    inventory_items = db.relationship('TestGameInventoryItems', back_populates="item")
    rewards = db.relationship('TestGameQuestRewards', secondary='reward_item_association', back_populates="items", overlaps="reward,reward_items, item")
    

    
# Model association table to store inventory items
class TestGameInventoryItems(db.Model):
    __tablename__ = 'test_game_inventory_items'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    inventory_id = db.Column(db.Integer, db.ForeignKey('test_game_inventory_user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('test_game_items.id'), nullable=False)
    
    # Item quantity
    quantity = db.Column(db.Integer, default=0)

    # Relationships
    inventory = db.relationship("TestGameInventoryUser", back_populates="inventory_items")
    item = db.relationship("TestGameItem", back_populates="inventory_items")
    
    

## TEST GAME QUEST RELATED MODELS
# Model to store quest types    
class TestGameQuestType(db.Model):
    __tablename__ = 'test_game_quest_types'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Quest type details
    quest_type_name = db.Column(db.String(64))
    quest_type_description = db.Column(db.String(256))
    
    # Relationships
    quests = db.relationship("TestGameQuest", back_populates="quest_type")
    

# Model to store quest details    
class TestGameQuest(db.Model):
    __tablename__ = 'test_game_quests'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
  
    # Quest details
    quest_name = db.Column(db.String(64))
    quest_description = db.Column(db.String(256))
    quest_type_id = db.Column(db.Integer, db.ForeignKey('test_game_quest_types.id', name='fk_quest_type_id'))
    
    # Relationships
    quest_rewards = db.relationship("TestGameQuestRewards", back_populates="quest")
    quest_type = db.relationship("TestGameQuestType", back_populates="quests")
    quest_progress = db.relationship("TestGameQuestProgress", back_populates="quest_quest")
    




# Model to store quest rewards
class TestGameQuestRewards(db.Model):
    __tablename__ = 'test_game_rewards'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    quest_id = db.Column(db.Integer, db.ForeignKey('test_game_quests.id'))
    
    # Reward details
    quest_reward_name = db.Column(db.String(64))
    quest_reward_description = db.Column(db.String(256))
    quest_reward_xp = db.Column(db.Integer, default=0)
    quest_reward_cash = db.Column(db.Float,default=0)
    quest_reward_item_id = db.Column(db.Integer, db.ForeignKey('test_game_items.id'))
    
    # Relationships
    quest = db.relationship("TestGameQuest", back_populates="quest_rewards")
    items = db.relationship("TestGameItem", secondary='reward_item_association', back_populates="rewards", overlaps="item,reward_items,reward")
    
 
# Model to store quest progress
class TestGameQuestProgress(db.Model):
    __tablename__ = 'test_game_quest_progress'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    quest_id = db.Column(db.Integer, db.ForeignKey('test_game_quests.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('test_game.id'))
    
    # Quest progress details
    quest_progress = db.Column(db.Integer, default=0)
    quest_active = db.Column(db.Boolean, default=False)
    quest_completed = db.Column(db.Boolean, default=False)
    quest_completed_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    quest_quest = db.relationship("TestGameQuest", back_populates="quest_progress")
    quest_game = db.relationship("TestGame", back_populates="quest_progress")
    
    
    
## TESTGAME LOGS
class TestGameResourceLog(db.Model):
    __tablename__ = 'test_game_resource_log'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    test_game_id = db.Column(db.Integer, db.ForeignKey("test_game.id"))

    # Resource details
    cash = db.Column(db.Float, default=0)
    xp = db.Column(db.Integer, default=0)
    wood = db.Column(db.Integer, default=0)
    stone = db.Column(db.Integer, default=0)
    metal = db.Column(db.Integer, default=0)
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    source = db.Column(db.String(64))

    # Relationships
    testgame = db.relationship("TestGame", back_populates="test_game_resource_logs")
    

## TEST GAME BUILDING MODELS
# Model to store building types
class TestGameBuildingType(db.Model):
    __tablename__ = 'test_game_building_types'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Building type details
    building_type_name = db.Column(db.String(64))
    building_type_description = db.Column(db.String(256))

    # Relationships
    building = db.relationship("TestGameBuildings", back_populates="building_type")

# Model to store buildings
class TestGameBuildings(db.Model):
    __tablename__ = 'test_game_buildings'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    building_type_id = db.Column(db.Integer, db.ForeignKey('test_game_building_types.id'))

    # Building details
    building_name = db.Column(db.String(64))
    building_description = db.Column(db.String(256))
    building_link = db.Column(db.String(256))

    # Relationships
    building_type = db.relationship("TestGameBuildingType", back_populates="building")
    building_progress = db.relationship("TestGameBuildingProgress", back_populates="building")



    
# Model to store building progress
class TestGameBuildingProgress(db.Model):
    __tablename__ = 'test_game_building_progress'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    building_id = db.Column(db.Integer, db.ForeignKey('test_game_buildings.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('test_game.id'))

    # Building progress details
    building_level = db.Column(db.Integer, default=1)
    building_active = db.Column(db.Boolean, default=False)
    
    # Building Upgrade Requirements
    base_building_cash_required = db.Column(db.Float, default=0)
    base_building_level_required = db.Column(db.Integer, default=0)
    
    # Building Resource Collection details
    xp_per_minute = db.Column(db.Integer, default=0)
    cash_per_minute = db.Column(db.Float, default=0)
    wood_per_minute = db.Column(db.Integer, default=0)
    stone_per_minute = db.Column(db.Integer, default=0)
    metal_per_minute = db.Column(db.Integer, default=0)

    # Building Resource Time Details
    accrual_start_time = db.Column(db.DateTime, nullable=True)
    max_accrual_duration = db.Column(db.Integer, default=8)

    # Accrued Resources
    accrued_xp = db.Column(db.Integer, default=0)
    accrued_cash = db.Column(db.Float, default=0)
    accrued_wood = db.Column(db.Integer, default=0)
    accrued_stone = db.Column(db.Integer, default=0)
    accrued_metai = db.Column(db.Integer, default=0)
    
    # Building Completion Details
    building_completed = db.Column(db.Boolean, default=False)
    building_completed_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    building = db.relationship("TestGameBuildings", back_populates="building_progress")
    game = db.relationship("TestGame", back_populates="building_progress")

    
        
    



