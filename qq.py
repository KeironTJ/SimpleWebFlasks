

# Assuming your Flask app and models are defined in app.py and app/models.py respectively
from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User
from app.models import TestGame
from app.models import TestGameQuest, TestGameQuestType, TestGameQuestRewards,RewardItemAssociation, TestGameQuestProgress
from app.models import TestGameItem, TestGameInventory, TestGameInventoryItems
from app.models import TestGameLevelRequirements
from app.testgame.game_logic import GameCreation, GameService

app = create_app()
app_context = app.app_context()
app_context.push()

def check_and_initialize_database():
    if os.path.exists("app.db"):
        print("Database already exists")
    else:
        print("Database does not exist. Creating database")

def add_role(role_name):
    """Add a role to the database."""
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)
        try:
            db.session.commit()
            print(f"Added role: {role_name}")
        except IntegrityError:
            db.session.rollback()
            print(f"Failed to add role: {role_name}")

def add_user(username, email, password, role_name):
    """Add a user to the database."""
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, email=email)
        user.set_password(password)
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.role.append(role)
        db.session.add(user)
        db.session.commit()
        try:
            db.session.commit()
            print(f"Added user: {username}")
        except IntegrityError:
            db.session.rollback()
            print(f"Failed to add user: {username}")

def populate_database():
    """Populate the database with predefined data."""
    # Your existing functions to add roles and users
    # Check if the roles are already in the database
    if Role.query.filter_by(name="admin").first() is None:
        add_role("admin")
    else:
        print("Role admin already exists")
    if Role.query.filter_by(name="user").first() is None:
        add_role("user")
    else:
        print("Role user already exists")
    # Check if the user is already in the database
    if User.query.filter_by(username="KeironTJ").first() is None:
        add_user(username="KeironTJ", email="abc123@abc.com", password="abc123", role_name="admin")
    else:
        print("User KeironTJ already exists")
       
        
def create_QuestTypes():
    quest_type1 = TestGameQuestType(quest_type_name="Main Quest", quest_type_description="Main Story Progression Quests")
    quest_type2 = TestGameQuestType(quest_type_name="Building Quest", quest_type_description="Building Progression Quests")
    quest_type3 = TestGameQuestType(quest_type_name="Level Quest", quest_type_description="Levelling Progression Quests")
    db.session.add(quest_type1)
    db.session.add(quest_type2)
    db.session.add(quest_type3)
    db.session.commit()
    print("Quest Types Created")
    

def create_inventory():
    inventory1 = TestGameInventory(game_id=1)
    inventory2 = TestGameInventory(game_id=2)
    inventory3 = TestGameInventory(game_id=3)
    db.session.add(inventory1)
    db.session.add(inventory2)
    db.session.add(inventory3)
    db.session.commit()
    print("Inventories Created")
    
def create_items():
    item1 = TestGameItem(item_name="Item 1", item_description="Item 1 Description")
    item2 = TestGameItem(item_name="Item 2", item_description="Item 2 Description")
    item3 = TestGameItem(item_name="Item 3", item_description="Item 3 Description")
    db.session.add(item1)
    db.session.add(item2)
    db.session.add(item3)
    db.session.commit()
    print("Items Created")
    
def create_inventory_items():
    inventory_item1 = TestGameInventoryItems(inventory_id=1, item_id=1, quantity=1)
    inventory_item2 = TestGameInventoryItems(inventory_id=1, item_id=2, quantity=2)
    inventory_item3 = TestGameInventoryItems(inventory_id=2, item_id=3, quantity=3)
    db.session.add(inventory_item1)
    db.session.add(inventory_item2)
    db.session.add(inventory_item3)
    db.session.commit()
    print("Inventory Items Created")
    
def create_level_requirements():
    level_requirement1 = TestGameLevelRequirements(quest_id=1, level_requirement=1)
    level_requirement2 = TestGameLevelRequirements(quest_id=2, level_requirement=2)
    level_requirement3 = TestGameLevelRequirements(quest_id=3, level_requirement=3)
    db.session.add(level_requirement1)
    db.session.add(level_requirement2)
    db.session.add(level_requirement3)
    db.session.commit()
    print("Level Requirements Created")

def create_test_game_for_admin():
    test_game = TestGame(user_id=1, game_name="Test Game 1")
    db.session.add(test_game)
    db.session.commit()
    print("Test Game Created")
    

    
    
    
def delete_all_data():
    db.session.query(TestGameQuestProgress).delete()
    db.session.query(TestGameInventoryItems).delete()
    db.session.query(TestGameInventory).delete()
    db.session.query(TestGameItem).delete()
    db.session.query(TestGameQuestRewards).delete()
    db.session.query(TestGameQuest).delete()
    db.session.query(TestGameQuestType).delete()
    db.session.query(RewardItemAssociation).delete()    
    db.session.query(TestGameLevelRequirements).delete()
    db.session.query(TestGame).delete()


    db.session.commit()
    print("All data deleted")


if __name__ == "__main__":
    check_and_initialize_database()
    delete_all_data()
    populate_database()
    
    create_QuestTypes()
    create_items()
    create_inventory()
    create_inventory_items()
    
    create_test_game_for_admin()
    
 
class QuestCreator:
    def __init__(self, quest_name, quest_description, quest_type_id):
        self.quest_name = quest_name
        self.quest_description = quest_description
        self.quest_type_id = quest_type_id
        self.quest = None  # Placeholder for the created quest object

    def create_quest(self):
        try:
            self.quest = TestGameQuest(quest_name=self.quest_name, quest_description=self.quest_description, quest_type_id=self.quest_type_id)
            db.session.add(self.quest)
            db.session.commit()
            print("Quest Created")
            return self.quest
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest: {e}")

    def create_quest_rewards(self, quest_reward_name, quest_reward_description, quest_reward_xp, quest_reward_cash):
        if self.quest is None:
            print("Quest must be created before adding rewards.")
            return
        try:
            quest_reward = TestGameQuestRewards(quest=self.quest, 
                                                quest_reward_name=quest_reward_name, 
                                                quest_reward_description=quest_reward_description, 
                                                quest_reward_xp=quest_reward_xp, 
                                                quest_reward_cash=quest_reward_cash)
            db.session.add(quest_reward)
            db.session.commit()
            print("Quest Reward Created")
            return quest_reward
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest reward: {e}")

    def create_reward_item_associate(self, reward, item_id, quantity):
        try:
            reward_item = RewardItemAssociation(reward=reward, 
                                                item_id=item_id, 
                                                quantity=quantity)
            db.session.add(reward_item)
            db.session.commit()
            print("Reward Item Associated")
            return reward_item
        except Exception as e:
            db.session.rollback()
            print(f"Failed to associate reward item: {e}")

    def create_full_quest(self, rewards_info, items_info):
        """
        Create a quest with rewards and associate items with those rewards.
        
        :param rewards_info: List of dictionaries with reward details.
        :param items_info: Dictionary mapping reward names to lists of item associations.
        """
        self.create_quest()
        for reward_info in rewards_info:
            reward = self.create_quest_rewards(**reward_info)
            for item_info in items_info.get(reward_info['quest_reward_name'], []):
                self.create_reward_item_associate(reward, **item_info)

# Example usage
Main_quest_1 = QuestCreator(quest_name="Main Quest 1", quest_description="Main Quest 1 Description", quest_type_id=1)
rewards_info = [
    {"quest_reward_name": "XP Reward", "quest_reward_description": "XP Reward Description", "quest_reward_xp": 100, "quest_reward_cash": 0},
    {"quest_reward_name": "Cash Reward", "quest_reward_description": "Cash Reward Description", "quest_reward_xp": 0, "quest_reward_cash": 100}
]
items_info = {
    "XP Reward": [
        {"item_id": 1, "quantity": 1},
        {"item_id": 2, "quantity": 2}
    ],
    "Cash Reward": [
        {"item_id": 3, "quantity": 3}
    ]
}
Main_quest_1.create_full_quest(rewards_info, items_info)

Main_quest_2 = QuestCreator(quest_name="Main Quest 2", quest_description="Main Quest 2 Description", quest_type_id=1)
rewards_info = [
    {"quest_reward_name": "XP Reward", "quest_reward_description": "XP Reward Description", "quest_reward_xp": 200, "quest_reward_cash": 0},
    {"quest_reward_name": "Cash Reward", "quest_reward_description": "Cash Reward Description", "quest_reward_xp": 0, "quest_reward_cash": 200}
]
items_info = {
    "XP Reward": [
        {"item_id": 1, "quantity": 2},
        {"item_id": 2, "quantity": 4}
    ],
    "Cash Reward": [
        {"item_id": 3, "quantity": 6}
    ]
}

Main_quest_2.create_full_quest(rewards_info, items_info)



        
        

    