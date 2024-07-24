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
    email = db.Column(String(120), index=True, unique=True)
    password_hash = db.Column(String(256))
    active = db.Column(db.Boolean(), default=True)
    activegame = db.Column(db.Integer, nullable=True)

    # Relationships
    game = so.relationship("Game", back_populates="user", cascade="all, delete-orphan")
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
    

## GAME RELATED MODELS
# Model representing a game
class Game(db.Model):
    __tablename__ = 'game'
    
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
    cash = db.Column(db.Integer, default=0)
    wood = db.Column(db.Integer, default=0)
    stone = db.Column(db.Integer, default=0)
    metal = db.Column(db.Integer, default=0)

    
    next_level_xp_required = db.Column(db.Integer, default=110)
    
    # create relationships
    user = db.relationship("User", back_populates="game")
    inventories = db.relationship("InventoryUser", back_populates="game")
    quest_progress = db.relationship("QuestProgress", back_populates="game")
    building_progress = db.relationship("BuildingProgress", back_populates="game")
    resource_logs = db.relationship("ResourceLog", back_populates="game")
    
    
class InventoryType(db.Model):
    __tablename__ = 'inventory_types'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Inventory type details
    inventory_type_name = db.Column(db.String(64))
    inventory_type_description = db.Column(db.String(256))

    # Relationships
    inventory = db.relationship("Inventory", back_populates="inventory_type")
    


class Inventory(db.Model):
    __tablename__ = 'inventory'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Inventory Details
    inventory_name = db.Column(db.String(64))
    inventory_description = db.Column(db.String(256))

    # Foreign keys
    inventory_type_id = db.Column(db.Integer, db.ForeignKey('inventory_types.id'), nullable=False)

    # Relationships
    inventory_type = db.relationship("InventoryType", back_populates="inventory")
    inventory_user = db.relationship("InventoryUser", back_populates="inventory")
    

class InventoryUser(db.Model):
    __tablename__ = 'inventory_user'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    
    # Relationships
    inventory = db.relationship("Inventory", back_populates="inventory_user")
    inventory_items = db.relationship("InventoryItems", back_populates="inventory")
    game = db.relationship("Game", back_populates="inventories")


# Model to store reward item associations
class RewardItemAssociation(db.Model):
    __tablename__ = 'reward_item_association'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    reward_id = db.Column(db.Integer, db.ForeignKey('quest_rewards.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    quantity = db.Column(db.Integer, default=1)
    
    # Relationships
    reward = db.relationship("QuestRewards", backref="reward_items")
    item = db.relationship("Item", backref="reward_items")



class Item(db.Model):
    __tablename__ = 'items'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Item details
    item_name = db.Column(db.String(64))
    item_cost = db.Column(db.Integer)
    item_xp = db.Column(db.Integer)
    item_level = db.Column(db.Integer)
    item_type = db.Column(db.String(64))
    item_description = db.Column(db.String(256))

    # Relationships
    inventory_items = db.relationship('InventoryItems', back_populates="item")
    rewards = db.relationship('QuestRewards', secondary='reward_item_association', back_populates="items", overlaps="reward,reward_items, item")
    

    
# Model association table to store inventory items
class InventoryItems(db.Model):
    __tablename__ = 'inventory_items'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    
    # Item quantity
    quantity = db.Column(db.Integer, default=0)

    # Relationships
    inventory = db.relationship("InventoryUser", back_populates="inventory_items")
    item = db.relationship("Item", back_populates="inventory_items")
    
    

## GAME QUEST RELATED MODELS
# Model to store quest types    
class QuestType(db.Model):
    __tablename__ = 'quest_types'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Quest type details
    quest_type_name = db.Column(db.String(64))
    quest_type_description = db.Column(db.String(256))
    
    # Relationships
    quests = db.relationship("Quest", back_populates="quest_type")
    

# Model to store quest details    
class Quest(db.Model):
    __tablename__ = 'quests'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
  
    # Quest details
    quest_name = db.Column(db.String(64))
    quest_description = db.Column(db.String(256))
    quest_type_id = db.Column(db.Integer, db.ForeignKey('quest_types.id', name='fk_quest_type_id'))
    
    # Relationships
    quest_rewards = db.relationship("QuestRewards", back_populates="quest")
    quest_type = db.relationship("QuestType", back_populates="quests")
    quest_progress = db.relationship("QuestProgress", back_populates="quest_quest")

    # Methods
    def __repr__(self):
        return f'<Quest {self.quest_name}>'
    

# Model to store quest rewards
class QuestRewards(db.Model):
    __tablename__ = 'quest_rewards'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'))
    
    # Reward details
    quest_reward_xp = db.Column(db.Integer, default=0)
    quest_reward_cash = db.Column(db.Integer,default=0)
    quest_reward_wood = db.Column(db.Integer, default=0)
    quest_reward_stone = db.Column(db.Integer, default=0)
    quest_reward_metal = db.Column(db.Integer, default=0)
    quest_reward_item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    # Relationships
    quest = db.relationship("Quest", back_populates="quest_rewards")
    items = db.relationship("Item", secondary='reward_item_association', back_populates="rewards", overlaps="item,reward_items,reward")
    
 
# Model to store quest progress
class QuestProgress(db.Model):
    __tablename__ = 'quest_progress'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    
    # Quest progress details
    quest_progress = db.Column(db.Integer, default=0)
    quest_active = db.Column(db.Boolean, default=False)
    quest_completed = db.Column(db.Boolean, default=False)
    quest_completed_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    quest_quest = db.relationship("Quest", back_populates="quest_progress")
    game = db.relationship("Game", back_populates="quest_progress")

    
    
    
## GAME LOGS
class ResourceLog(db.Model):
    __tablename__ = 'resource_log'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))

    # Resource details
    cash = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)
    wood = db.Column(db.Integer, default=0)
    stone = db.Column(db.Integer, default=0)
    metal = db.Column(db.Integer, default=0)
    entry_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    source = db.Column(db.String(64))

    # Relationships
    game = db.relationship("Game", back_populates="resource_logs")
    



## GAME BUILDING MODELS
# Model to store building types
class BuildingType(db.Model):
    __tablename__ = 'building_types'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Building type details
    building_type_name = db.Column(db.String(64))
    building_type_description = db.Column(db.String(256))

    # Relationships
    building = db.relationship("Buildings", back_populates="building_type")

# Model to store buildings
class Buildings(db.Model):
    __tablename__ = 'buildings'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    building_type_id = db.Column(db.Integer, db.ForeignKey('building_types.id'))

    # Building details
    building_name = db.Column(db.String(64))
    building_description = db.Column(db.String(256))
    building_link = db.Column(db.String(256))
    
    # Building Upgrade Requirements
    base_building_cash_required = db.Column(db.Integer, default=0)
    base_building_level_required = db.Column(db.Integer, default=0)
    base_building_xp_required = db.Column(db.Integer, default=0)
    base_building_wood_required = db.Column(db.Integer, default=0)
    base_building_stone_required = db.Column(db.Integer, default=0)
    base_building_metal_required = db.Column(db.Integer, default=0)
    
    # Building Level Details
    max_building_level = db.Column(db.Integer, default=25)
    
    # Building Resource Collection details
    base_xp_per_minute = db.Column(db.Integer, default=0)
    base_cash_per_minute = db.Column(db.Integer, default=0)
    base_wood_per_minute = db.Column(db.Integer, default=0)
    base_stone_per_minute = db.Column(db.Integer, default=0)
    base_metal_per_minute = db.Column(db.Integer, default=0)
    
    

    # Relationships
    building_type = db.relationship("BuildingType", back_populates="building")
    building_progress = db.relationship("BuildingProgress", back_populates="building")



    
# Model to store building progress
class BuildingProgress(db.Model):
    __tablename__ = 'building_progress'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    # Building progress details
    building_level = db.Column(db.Integer, default=0)
    building_active = db.Column(db.Boolean, default=False)
    

    # Building Resource Collection details
    xp_per_minute = db.Column(db.Integer, default=0)
    cash_per_minute = db.Column(db.Integer, default=0)
    wood_per_minute = db.Column(db.Integer, default=0)
    stone_per_minute = db.Column(db.Integer, default=0)
    metal_per_minute = db.Column(db.Integer, default=0)

    # Building Resource Time Details
    accrual_start_time = db.Column(db.DateTime, nullable=True)
    max_accrual_duration = db.Column(db.Integer, default=240) # in minutes

    # Accrued Resources
    accrued_xp = db.Column(db.Integer, default=0)
    accrued_cash = db.Column(db.Integer, default=0)
    accrued_wood = db.Column(db.Integer, default=0)
    accrued_stone = db.Column(db.Integer, default=0)
    accrued_metal = db.Column(db.Integer, default=0)
    
    # Building Completion Details
    building_completed = db.Column(db.Boolean, default=False)
    building_completed_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    building = db.relationship("Buildings", back_populates="building_progress")
    game = db.relationship("Game", back_populates="building_progress")

    
        
    



