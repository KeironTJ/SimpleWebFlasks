from app import create_app

from app.models import db
from app.models import Buildings, BuildingProgress, BuildingType

app = create_app()
app_context = app.app_context()
app_context.push()


## BUILDINGS
# Create Building Types
def create_building_types():
    mainbuildingtype = BuildingType(building_type_name="Main Building", building_type_description="Main Game Buildings")
    inventorybuildingtype = BuildingType(building_type_name="Inventory Building", building_type_description="Inventory Buildings")
    resourcebuildingtype = BuildingType(building_type_name="Resource Building", building_type_description="Resource Buildings")
    db.session.add(mainbuildingtype)
    db.session.add(inventorybuildingtype)
    db.session.add(resourcebuildingtype)
    db.session.commit()

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
            self.building = Buildings(building_name=self.building_name, 
                                              building_description=self.building_description, 
                                              building_type_id=self.building_type_id, 
                                              building_link=self.building_link)
            db.session.add(self.building)
            db.session.commit()
            return self.building
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create building: {self.building_name} {e}")
    
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
        except Exception as e:
            db.session.rollback()
            print(f"Failed to set building requirements: {self.building_name} {e}")
            
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
        except Exception as e:
            db.session.rollback()
            print(f"Failed to set building collection parameters: {self.building_name} {e}")
            

def delete_building_data():
    # Delete Building Data
    db.session.query(Buildings).delete()
    db.session.query(BuildingType).delete()
    db.session.query(BuildingProgress).delete()
    
def create_buildings():
     # Create Quest Building
    quest_building = BuildingCreator(building_name="Quests", 
                                 building_description="View All Quests", 
                                 building_type_id=1, 
                                 building_link="game.building_quests") 
    
    quest_building.create_building()
    

    # Create Inventory Building
    inventory_building = BuildingCreator(building_name="Inventory", 
                                     building_description="View Inventory", 
                                     building_type_id=2, 
                                     building_link="game.building_inventory")
    inventory_building.create_building()
    

    # Create Farm Building
    farm_building = BuildingCreator(building_name="Farm", 
                                building_description="Collect Cash", 
                                building_type_id=3, 
                                building_link="game.building_resource")
    farm_building.create_building()
    farm_building.set_building_requirements(cash=1000, level=1)
    farm_building.set_base_collection_rates(cash=50)
                                            
    
    # Create Lumber Mill Building
    lumber_mill_building = BuildingCreator(building_name="Lumber Mill", 
                                       building_description="Collect Wood", 
                                       building_type_id=3, 
                                       building_link="game.building_resource")
    lumber_mill_building.create_building()
    lumber_mill_building.set_building_requirements(cash=1500, level=5)
    lumber_mill_building.set_base_collection_rates(wood=20)
    
    # Create Mine Quilding
    mine_building = BuildingCreator(building_name="Mine", 
                                building_description="Collect Stone", 
                                building_type_id=3, 
                                building_link="game.building_resource")
    mine_building.create_building()
    mine_building.set_building_requirements(cash=2500, level=10, wood=500)
    mine_building.set_base_collection_rates(stone=10)
    
    # Create Forge Building
    forge_building = BuildingCreator(building_name="Forge", 
                                 building_description="Collect Metal", 
                                 building_type_id=3, 
                                 building_link="game.building_resource")
    forge_building.create_building()
    forge_building.set_building_requirements(cash=5000, level=20, wood=1000, stone=500, metal=0)
    forge_building.set_base_collection_rates(metal=5)

    # Create Barracks Building
    barracks_building = BuildingCreator(building_name="Barracks",
                                    building_description="Recruit Heroes",
                                    building_type_id=1,
                                    building_link="game.building_barracks")
    barracks_building.create_building()
    barracks_building.set_building_requirements(cash=500, level=1, wood=0, stone=0, metal=0)


# Create buildings, requirements progress
if __name__ == "__main__": 
    '''
        delete_building_data()
        create_building_types()
        create_buildings()
    '''
   
    
    # python -m app.game.Buildings.Buildings