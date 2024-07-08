

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
from app.models import TestGameCashLog, TestGameXPLog
from app.models import TestGameBuildings, TestGameBuildingProgress, TestGameBuildingRequirements, TestGameBuildingType
from app.testgame.game_logic import GameCreation, GameService

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
    
def create_level_requirements():
    level_requirement1 = TestGameLevelRequirements(level = 1, xp_required = 100)
    level_requirement2 = TestGameLevelRequirements(level = 2, xp_required = 200)
    level_requirement3 = TestGameLevelRequirements(level = 3, xp_required = 400)
    db.session.add(level_requirement1)
    db.session.add(level_requirement2)
    db.session.add(level_requirement3)
    db.session.commit()
    print("Level Requirements Created")

def create_test_game_for_admin():
    service = GameCreation(user_id=1, game_name="Test Game 1")
    test_game = service.create_game()
    
    db.session.commit()
    print("Test Game Created")
    
    game_id = test_game.id
    
    service.assign_all_quests(game_id)
    service.set_active_game(game_id)
    db.session.commit()
    

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

    def create_inventory_item(self, inventory_id, quantity):
        if self.item is None:
            print("Item must be created before adding to inventory.")
            return
        try:
            inventory_item = TestGameInventoryItems(inventory_id=inventory_id, item_id=self.item.id, quantity=quantity)
            db.session.add(inventory_item)
            db.session.commit()
            print("Inventory Item Created")
            return inventory_item
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create inventory item: {e}")

    def create_full_item(self, inventory_id, quantity):
        """
        Create an item and add it to an inventory.
        
        :param inventory_id: The id of the inventory to add the item to.
        :param quantity: The quantity of the item in the inventory.
        """
        self.create_item()
        self.create_inventory_item(inventory_id, quantity)
    
# Example usage
item1 = ItemCreator(item_name="Sword", item_description="A sharp sword")
item2 = ItemCreator(item_name="Shield", item_description="A sturdy shield")
item3 = ItemCreator(item_name="Potion", item_description="A healing potion")

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
# A class to independently create a building logic. independant method to create a building type, and individual method to create a building and then assign requirements to the building.
class BuildingCreator:
    def __init__(self,building_type_id,  building_name, building_description, building_link):
        self.building_type_id = building_type_id
        self.building_name = building_name
        self.building_description = building_description
        self.building_link = building_link
        self.building = None  # Placeholder for the created building object

    def create_building(self):
        try:
            self.building = TestGameBuildings(building_type_id=self.building_type_id,
                                              building_name=self.building_name, 
                                              building_description=self.building_description, 
                                              building_link=self.building_link
                                              )
            db.session.add(self.building)
            db.session.commit()
            print("Building Created")
            return self.building
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create building: {e}")

    def create_building_requirements(self, building_level, user_level_required, user_cash_required):
        if self.building is None:
            print("Building must be created before adding requirements.")
            return
        try:
            building_requirement = TestGameBuildingRequirements(building=self.building, 
                                                                building_level=building_level, 
                                                                user_level_required=user_level_required, 
                                                                user_cash_required=user_cash_required)

            db.session.add(building_requirement)
            db.session.commit()
            print("Building Requirement Created")
            return building_requirement
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create building requirement: {e}")

    def create_full_building(self, requirements_info):
        """
        Create a building with requirements.
        
        :param requirements_info: List of dictionaries with requirement details.
        """
        self.create_building()
        for requirement_info in requirements_info:
            self.create_building_requirements(**requirement_info)

# Example usage
building1 = BuildingCreator(building_type_id=1, 
                            building_name="Quest Building", 
                            building_description="Building to display quests", 
                            building_link="testgame.tg_building_quests")

requirements_info = [
    {"building_level": 1, "user_level_required": 1, "user_cash_required": 0},
    {"building_level": 2, "user_level_required": 2, "user_cash_required": 100},
    {"building_level": 3, "user_level_required": 3, "user_cash_required": 200},
]

building2 = BuildingCreator(building_type_id=2, 
                            building_name="Inventory Building", 
                            building_description="Building to display inventory", 
                            building_link="testgame.tg_building_inventory")

requirements_info = [
    {"building_level": 1, "user_level_required": 1, "user_cash_required": 0},
    {"building_level": 2, "user_level_required": 2, "user_cash_required": 100},
    {"building_level": 3, "user_level_required": 3, "user_cash_required": 200}
]

building3 = BuildingCreator(building_type_id=3, 
                            building_name="Farm", 
                            building_description="Building to collect cash", 
                            building_link="testgame.tg_building_farm")

requirements_info = [
    {"building_level": 1, "user_level_required": 1, "user_cash_required": 0},
    {"building_level": 2, "user_level_required": 2, "user_cash_required": 100},
    {"building_level": 3, "user_level_required": 3, "user_cash_required": 200}
]


# Class to assign all buildings to admin

class BuildingAssigner:
    def __init__(self, game_id):
        self.game_id = game_id
        self.buildings = TestGameBuildings.query.all()

    def assign_all_buildings(self):
        for building in self.buildings:
            building_progress = TestGameBuildingProgress(game_id=self.game_id, building_id=building.id, building_level=1)
            db.session.add(building_progress)
        db.session.commit()
        print("All Buildings Assigned")


 ## Quest Creator Class   
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

def delete_all_data():
    db.session.query(User).delete()
    db.session.query(Role).delete()
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
    db.session.query(TestGameCashLog).delete()
    db.session.query(TestGameXPLog).delete()
    db.session.query(TestGameBuildingProgress).delete()
    db.session.query(TestGameBuildingRequirements).delete()
    db.session.query(TestGameBuildings).delete()
    db.session.query(TestGameBuildingType).delete()


    db.session.commit()
    print("All data deleted")


# Run the script
if __name__ == "__main__":
    delete_all_data()
    populate_database()
    
    create_QuestTypes()
    create_inventory()
    create_level_requirements()
    
    # Create buildings, requirements progress
    create_building_types()
    building1.create_full_building(requirements_info)
    building2.create_full_building(requirements_info)
    building3.create_full_building(requirements_info)

    # Assign all buildings to admin
    assigner = BuildingAssigner(game_id=1)
    assigner.assign_all_buildings()

    
    # Create quests, rewards, and reward item associations
    Main_quest_1.create_full_quest(rewards_info, items_info)
    Main_quest_2.create_full_quest(rewards_info, items_info)
    
    # Create items and inventory items
    item1.create_full_item(inventory_id=1, quantity=1)
    item2.create_full_item(inventory_id=1, quantity=2)
    item3.create_full_item(inventory_id=2, quantity=3)
    
    

    
    create_test_game_for_admin()
        
        

    