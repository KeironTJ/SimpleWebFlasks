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
    mainbuildingtype = TestGameBuildingType(building_type_name="Main Building", building_type_description="Main Game Buildings")
    inventorybuildingtype = TestGameBuildingType(building_type_name="Inventory Building", building_type_description="Inventory Buildings")
    resourcebuildingtype = TestGameBuildingType(building_type_name="Resource Building", building_type_description="Resource Buildings")
    db.session.add(mainbuildingtype)
    db.session.add(inventorybuildingtype)
    db.session.add(resourcebuildingtype)
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
    
    def set_building_requirements(self, cash=0, level=0, xp=0, wood=0, stone=0, metal=0):
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
            
    def set_base_collection_rates(self, cash=0, xp=0, wood=0, stone=0, metal=0):
        if not self.building:
            print("Building must be created before setting collection parameters.")
            return
        try:
            self.building.base_cash_per_minute = cash
            self.building.base_xp_per_minute = xp
            self.building.base_wood_per_minute = wood
            self.building.base_stone_per_minute = stone
            self.building.base_metal_per_minute = metal

            db.session.commit()
            print("Building collection parameters set")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to set building collection parameters: {e}")
            

def delete_building_data():
    # Delete Building Data
    db.session.query(TestGameBuildings).delete()
    db.session.query(TestGameBuildingType).delete()
    db.session.query(TestGameBuildingProgress).delete()
    print("Building Data Deleted")
    


# Create buildings, requirements progress
if __name__ == "__main__": 
    delete_building_data()
    
    create_building_types()
    
    # Create Quest Building
    quest_building = BuildingCreator(building_name="Quest Building", 
                                 building_description="View All Quests", 
                                 building_type_id=1, 
                                 building_link="testgame.tg_building_quests") 
    
    quest_building.create_building()
    

    # Create Inventory Building
    inventory_building = BuildingCreator(building_name="Inventory Building", 
                                     building_description="View Inventory", 
                                     building_type_id=2, 
                                     building_link="testgame.tg_building_inventory")
    inventory_building.create_building()
    

    # Create Farm Building
    farm_building = BuildingCreator(building_name="Farm", 
                                building_description="Collect Cash", 
                                building_type_id=3, 
                                building_link="testgame.tg_building_resource")
    farm_building.create_building()
    farm_building.set_building_requirements(cash=1000, level=1)
    farm_building.set_base_collection_rates(cash=10)
                                            
    
    # Create Lumber Mill Building
    lumber_mill_building = BuildingCreator(building_name="Lumber Mill", 
                                       building_description="Collect Wood", 
                                       building_type_id=3, 
                                       building_link="testgame.tg_building_resource")
    lumber_mill_building.create_building()
    lumber_mill_building.set_building_requirements(cash=1500, level=5)
    lumber_mill_building.set_base_collection_rates(wood=5)
    
    # Create Mine Quilding
    mine_building = BuildingCreator(building_name="Mine", 
                                building_description="Collect Stone", 
                                building_type_id=3, 
                                building_link="testgame.tg_building_resource")
    mine_building.create_building()
    mine_building.set_building_requirements(cash=2500, level=10, wood=500)
    mine_building.set_base_collection_rates(stone=2)
    
    # Create Forge Building
    forge_building = BuildingCreator(building_name="Forge", 
                                 building_description="Collect Metal", 
                                 building_type_id=3, 
                                 building_link="testgame.tg_building_resource")
    forge_building.create_building()
    forge_building.set_building_requirements(cash=5000, level=20, wood=1000, stone=500, metal=0)
    forge_building.set_base_collection_rates(metal=1)
    
    # python -m app.testgame.Buildings.Buildings