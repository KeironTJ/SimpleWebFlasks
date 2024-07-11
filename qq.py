

# Assuming your Flask app and models are defined in app.py and app/models.py respectively
from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User
from app.models import TestGame
from app.models import TestGameQuest, TestGameQuestType, TestGameQuestRewards,RewardItemAssociation, TestGameQuestProgress
from app.models import TestGameItem, TestGameInventory, TestGameInventoryItems, TestGameInventoryType, TestGameInventoryUser
from app.models import TestGameLevelRequirements
from app.models import TestGameCashLog, TestGameXPLog, TestGameResourceLog
from app.models import TestGameBuildings, TestGameBuildingProgress, TestGameBuildingType
from app.testgame.game_logic import GameCreation, GameService, PrintNotifier, GameBuildingService

app = create_app()
app_context = app.app_context()
app_context.push()

     
# Add roles and users to the database
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
       
        

    

## INVENTORY
# Create Inventory Types       
def create_inventory_types():
    inventory_type1 = TestGameInventoryType(inventory_type_name="Main Inventory", inventory_type_description="Main Inventory Description")
    inventory_type2 = TestGameInventoryType(inventory_type_name="Secondary Inventory", inventory_type_description="Secondary Inventory Description")
    inventory_type3 = TestGameInventoryType(inventory_type_name="Tertiary Inventory", inventory_type_description="Tertiary Inventory Description")
    db.session.add(inventory_type1)
    db.session.add(inventory_type2)
    db.session.add(inventory_type3)
    db.session.commit()
    print("Inventory Types Created")
    
# Inventory Creator Class
class InventoryCreator:
    def __init__(self, inventory_name, inventory_description, inventory_type_id):
        self.inventory_name = inventory_name
        self.inventory_description = inventory_description
        self.inventory_type_id = inventory_type_id
        self.inventory = None  # Placeholder for the created inventory object

    def create_inventory(self):
        try:
            self.inventory = TestGameInventory(inventory_name=self.inventory_name, inventory_description=self.inventory_description, inventory_type_id=self.inventory_type_id)
            db.session.add(self.inventory)
            db.session.commit()
            print("Inventory Created")
            return self.inventory
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create inventory: {e}")
            
# Example usage
main_inventory = InventoryCreator(inventory_name="Main Inventory", inventory_description="Main Inventory Description", inventory_type_id=1)


    
## LEVEL REQUIREMENTS
# Create Level Requirements        
def create_level_requirements():
    level_requirement1 = TestGameLevelRequirements(level = 1, xp_required = 100)
    level_requirement2 = TestGameLevelRequirements(level = 2, xp_required = 200)
    level_requirement3 = TestGameLevelRequirements(level = 3, xp_required = 400)
    db.session.add(level_requirement1)
    db.session.add(level_requirement2)
    db.session.add(level_requirement3)
    db.session.commit()
    print("Level Requirements Created")


    
    
    
## ITEMS
## Item Creator Class
class ItemCreator:
    def __init__(self, item_name, item_description):
        self.item_name = item_name
        self.item_description = item_description
        self.item = None  # Placeholder for the created item object

    def create_item(self):
        try:
            self.item = TestGameItem(item_name=self.item_name, item_description=self.item_description)
            db.session.add(self.item)
            db.session.commit()
            print("Item Created")
            return self.item
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create item: {e}")

    
# Example usage
Sword = ItemCreator(item_name="Sword", item_description="A sharp sword")
Shield = ItemCreator(item_name="Shield", item_description="A sturdy shield")
Potion = ItemCreator(item_name="Potion", item_description="A healing potion")





## BUILDINGS
# Create Building Types
def create_building_types():
    building_type1 = TestGameBuildingType(building_type_name="Main Building", building_type_description="Main Building Description")
    building_type2 = TestGameBuildingType(building_type_name="Secondary Building", building_type_description="Secondary Building Description")
    building_type3 = TestGameBuildingType(building_type_name="Tertiary Building", building_type_description="Tertiary Building Description")
    db.session.add(building_type1)
    db.session.add(building_type2)
    db.session.add(building_type3)
    db.session.commit()
    print("Building Types Created")

## Building Creator Class
# Class to create buildings, no building requirements or progress
class BuildingCreator:
    def __init__(self, building_name, building_description, building_type_id, building_link):
        self.building_name = building_name
        self.building_description = building_description
        self.building_type_id = building_type_id
        self.building_link = building_link
        self.building = None  # Placeholder for the created building object

    def create_building(self):
        try:
            self.building = TestGameBuildings(building_name=self.building_name, building_description=self.building_description, building_type_id=self.building_type_id, building_link=self.building_link)
            db.session.add(self.building)
            db.session.commit()
            print("Building Created")
            return self.building
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create building: {e}")
            
# Example usage
quest_building = BuildingCreator(building_name="Quest Building", building_description="View All Quests", building_type_id=1, building_link="testgame.tg_building_quests") 
inventory_building = BuildingCreator(building_name="Inventory Building", building_description="View Inventory", building_type_id=2, building_link="testgame.tg_building_inventory")
farm_building = BuildingCreator(building_name="Farm", building_description="Collect Cash", building_type_id=3, building_link="testgame.tg_building_farm")    
    


## QUESTS
# Create Quest Types
def create_QuestTypes():
    quest_type1 = TestGameQuestType(quest_type_name="Main Quest", quest_type_description="Main Story Progression Quests")
    quest_type2 = TestGameQuestType(quest_type_name="Building Quest", quest_type_description="Building Progression Quests")
    quest_type3 = TestGameQuestType(quest_type_name="Level Quest", quest_type_description="Levelling Progression Quests")
    db.session.add(quest_type1)
    db.session.add(quest_type2)
    db.session.add(quest_type3)
    db.session.commit()
    print("Quest Types Created")
    
 # Quest Creator Class   
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


## TEST GAME ADMIN CREATION TEST
# Create a test game for the admin user
def create_test_game_for_admin():
    service = GameCreation(user_id=1, game_name="Test Game 1")
    test_game = service.create_game()
    
    db.session.commit()
    print("Test Game Created")
    
    game_id = test_game.id
    
    service.create_all_startup(game_id)
    db.session.commit()
    
def test_GameService():
    print("TESTING GameService")
    service = GameService(test_game_id=1, notifier=PrintNotifier())
    
    # Add XP and Cash
    try:
        service.add_xp(50)
        service.add_cash(100)
        print("TEST XP and Cash - SUCCESS")
    except Exception as e:
        print(f"TEST XP and Cash - FAILED: {e}")
    

    # Add Sword to inventory      
    try:
        service.add_inventory_item(1, 1, 1)
        print("TEST Add Sword to Inventory - SUCCESS")
    except Exception as e:
        print(f"TEST Add Sword to Inventory - FAILED: {e}")
        
        
    # Add XP to increase Level
    try:
        service.add_xp(150)
        print("TEST XP added to increase Level - SUCCESS")
    except Exception as e:
        print(f"XP added to increase Level - FAILED: {e}")
        
    # Attempt commit
    try:
        db.session.commit()
        print("TEST PASSED")
    except:
        db.session.rollback()
        print("TEST FAILED")

def test_GameBuildingService():
    print("TESTING GameBuildingService")
    service = GameBuildingService(building_progress_id=3, notifier=PrintNotifier())
    
    # Add Building Progress
    print("TEST Starting resource accrual")
    try:
        service.start_accrual()
        print("TEST Start Accrual - SUCCESS")
    except Exception as e:
        print(f"TEST Add Building Progress - FAILED: {e}")

    print("TEST Collecting resources")
    try:
        service.collect_resources()
        print("TEST Collect Resources - SUCCESS")
    except Exception as e:
        print(f"TEST Collect Resources - FAILED: {e}")
        
    # Attempt commit
    try:
        
        db.session.commit()
        print("TEST PASSED")
    except:
        db.session.rollback()
        print("TEST FAILED")


    
    
    
    

def delete_all_data():
    
    # Delete User Data
    db.session.query(User).delete()
    db.session.query(Role).delete()
    
    # Delete Game Quest Data
    db.session.query(TestGameQuestProgress).delete()
    db.session.query(TestGameQuestRewards).delete()
    db.session.query(RewardItemAssociation).delete() 
    db.session.query(TestGameQuestType).delete()
    db.session.query(TestGameQuest).delete()
    
    # Delete Building Data
    db.session.query(TestGameBuildingProgress).delete()
    db.session.query(TestGameBuildings).delete()
    db.session.query(TestGameBuildingType).delete()
    
    # Delete Item Data
    db.session.query(TestGameItem).delete()
    
    # Delete Inventory Data
    db.session.query(TestGameInventoryItems).delete()
    db.session.query(TestGameInventoryUser).delete()
    db.session.query(TestGameInventory).delete()
    db.session.query(TestGameInventoryType).delete()

    # Delete Game Data
    db.session.query(TestGameCashLog).delete()
    db.session.query(TestGameXPLog).delete()
    db.session.query(TestGameResourceLog).delete()
    db.session.query(TestGameLevelRequirements).delete()
    db.session.query(TestGame).delete()

    db.session.commit()
    print("All data deleted")


# Run the script
if __name__ == "__main__":
    delete_all_data()
    populate_database()
    
    
    
    # Create Inventory Types, Inventories
    create_inventory_types()
    main_inventory.create_inventory()
    
    
    # Create Level Requirements
    create_level_requirements()
    
    # Create buildings, requirements progress
    create_building_types()
    
    quest_building.create_building()
    inventory_building.create_building()
    farm_building.create_building()

    
    # Create quests, rewards, and reward item associations
    create_QuestTypes()
    Main_quest_1.create_full_quest(rewards_info, items_info)
    Main_quest_2.create_full_quest(rewards_info, items_info)
    
    # Create items and inventory items
    Sword.create_item()
    Shield.create_item()
    Potion.create_item()
    
    create_test_game_for_admin()
    test_GameService()
    test_GameBuildingService()
        
        

    