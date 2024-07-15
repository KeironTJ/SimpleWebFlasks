from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User
from app.models import TestGame
from app.models import TestGameQuest, TestGameQuestType, TestGameQuestRewards,RewardItemAssociation, TestGameQuestProgress
from app.models import TestGameItem, TestGameInventory, TestGameInventoryItems, TestGameInventoryType, TestGameInventoryUser
from app.models import TestGameResourceLog
from app.models import TestGameBuildings, TestGameBuildingProgress, TestGameBuildingType
from app.testgame.game_logic import GameCreation, GameService, PrintNotifier, GameBuildingService

app = create_app()
app_context = app.app_context()
app_context.push()


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
            self.building = TestGameBuildings(building_name=self.building_name, 
                                              building_description=self.building_description, 
                                              building_type_id=self.building_type_id, 
                                              building_link=self.building_link)
            db.session.add(self.building)
            db.session.commit()
            print("Building Created")
            return self.building
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create building: {e}")
    
    def set_building_requirements(self, cash, level, xp, wood, stone, metal):
        if not self.building:
            print("Building must be created before setting requirements.")
            return
        try:
            self.building.base_building_cash_required = cash
            self.building.base_building_level_required = level
            self.building.base_building_xp_required = xp
            self.building.base_building_wood_required = wood
            self.building.base_building_stone_required = stone
            self.building.base_building_metal_required = metal

            db.session.commit()
            print("Building requirements set")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to set building requirements: {e}")
            
# Example usage
quest_building = BuildingCreator(building_name="Quest Building", 
                                 building_description="View All Quests", 
                                 building_type_id=1, 
                                 building_link="testgame.tg_building_quests") 


inventory_building = BuildingCreator(building_name="Inventory Building", 
                                     building_description="View Inventory", 
                                     building_type_id=2, 
                                     building_link="testgame.tg_building_inventory")

farm_building = BuildingCreator(building_name="Farm", 
                                building_description="Collect Cash", 
                                building_type_id=3, 
                                building_link="testgame.tg_building_farm")   



def delete_building_data():
    # Delete Building Data
    db.session.query(TestGameBuildingProgress).delete()
    db.session.query(TestGameBuildings).delete()
    db.session.query(TestGameBuildingType).delete()
    


    # Create buildings, requirements progress
    create_building_types()
    
    quest_building.create_building()
    
    inventory_building.create_building()
    
    farm_building.create_building()
    farm_building.set_building_requirements(cash=1000, level=1, xp=0, wood=0, stone=0, metal=0)