from app import create_app
from app.models import db
from app.models import Buildings, BuildingType

app = create_app()
app_context = app.app_context()
app_context.push()


## BUILDINGS
# Create Building Types
def sync_building_types():
    building_types = [
        {"building_type_name": "Main Building", "building_type_description": "Main Game Buildings"},
        {"building_type_name": "Inventory Building", "building_type_description": "Inventory Buildings"},
        {"building_type_name": "Resource Building", "building_type_description": "Resource Buildings"}
    ]
        
    existing_b_types = {t.building_type_name: t for t in BuildingType.query.all()}
    for b_type in building_types:
        if b_type["building_type_name"] in existing_b_types:
            existing_b_types[b_type["building_type_name"]].building_type_description = b_type["building_type_description"]
            del existing_b_types[b_type["building_type_name"]]
        else:
            new_b_type = BuildingType(building_type_name=b_type["building_type_name"], building_type_description=b_type["building_type_description"])
            db.session.add(new_b_type)

    for b_type in existing_b_types.values():
        db.session.delete(b_type)


    db.session.commit()
    print("Building Types Synchronized")

## Building Creator Class
# Class to create buildings, no building requirements or progress
class BuildingCreator:
    def __init__(self, building_name, building_description, building_type_id, building_link):
        self.building_name = building_name
        self.building_description = building_description
        self.building_type_id = building_type_id
        self.building_link = building_link
        self.building = None  # Placeholder for the created building object

    def create_or_update_building(self):
        existing_building = Buildings.query.filter_by(building_name=self.building_name).first()
        if existing_building:
            existing_building.building_description = self.building_description
            existing_building.building_type_id = self.building_type_id
            existing_building.building_link = self.building_link
            self.building = existing_building
            print(f"Building {self.building_name} Updated")
        else:
            self.building = Buildings(building_name=self.building_name,
                                      building_description = self.building_description,
                                      building_type_id = self.building_type_id, 
                                      building_link = self.building_link)
            db.session.add(self.building)
            print(f"Building (self.building_name) Created")
        db.session.commit()
        return self.building


    
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
            

   
def sync_buildings():
    
    buildings = [
        {"building_name":"Quests", "building_description": "View All Quests", "building_type_id":1, "building_link": "game.building_quests", "max_building_level":1,
         "requirements": {"cash":0, "wood":0, "stone":0, "metal": 0, "level":0, "xp":0},
         "collection": {"xp":0,"cash":0,"wood":0,"stone":0,"metal":0}},

        {"building_name":"Inventory", "building_description": "View Inventory", "building_type_id":2, "building_link": "game.building_inventory", "max_building_level":1,
         "requirements": {"cash":0, "wood":0, "stone":0, "metal": 0, "level":0, "xp":0},
         "collection": {"xp":0,"cash":0,"wood":0,"stone":0,"metal":0}},

        {"building_name":"Farm", "building_description": "Collect Cash", "building_type_id":3, "building_link": "game.building_resource", "max_building_level":50, 
         "requirements": {"cash":1000, "wood":0, "stone":0, "metal": 0, "level":1,"xp":0},
         "collection": {"xp":0,"cash":50,"wood":0,"stone":0,"metal":0}},

        {"building_name":"Lumber Mill", "building_description": "Collect Wood", "building_type_id":3, "building_link": "game.building_resource", "max_building_level":50, 
        "requirements": {"cash":1500, "wood":0, "stone":0, "metal": 0, "level":5,"xp":0},
        "collection": {"xp":0,"cash":0,"wood":20,"stone":0,"metal":0}},

        {"building_name":"Mine", "building_description": "Collect Stoned", "building_type_id":3, "building_link": "game.building_resource", "max_building_level":50, 
        "requirements": {"cash":2500, "wood":500, "stone":0, "metal": 0, "level":10,"xp":0},
        "collection": {"xp":0,"cash":0,"wood":0,"stone":10,"metal":0}},

        {"building_name":"Forge", "building_description": "Collect Metal", "building_type_id":3, "building_link": "game.building_resource", "max_building_level":50, 
        "requirements": {"cash":5000, "wood":1000, "stone":500, "metal": 0, "level":20,"xp":0},
        "collection": {"xp":0,"cash":0,"wood":0,"stone":0,"metal":5}},

        {"building_name":"Barracks", "building_description": "Recruit Heroes", "building_type_id":1, "building_link": "game.building_barracks", "max_building_level":1, 
        "requirements": {"cash":500, "wood":0, "stone":0, "metal": 0, "level":1,"xp":0},
        "collection": {"xp":0,"cash":0,"wood":0,"stone":0,"metal":0}},
        
        {"building_name":"Campaign", "building_description": "Complete Missions to earn XP and rewards", "building_type_id":1, "building_link": "game.building_campaign", "max_building_level":1, 
        "requirements": {"cash":0, "wood":0, "stone":0, "metal": 0, "level":1,"xp":0},
        "collection": {"xp":0,"cash":0,"wood":0,"stone":0,"metal":0}},
    ]

    existing_buildings = {b.building_name: b for b in Buildings.query.all()}

    for building_data in buildings:
        if building_data["building_name"] in existing_buildings:
            building = existing_buildings[building_data["building_name"]]
            building.building_description = building_data["building_description"]
            building.building_type_id = building_data["building_type_id"]
            building.building_link = building_data["building_link"]
            building.max_building_level = building_data["max_building_level"]

            # Requirements
            building.base_building_cash_required = building_data["requirements"]["cash"]
            building.base_building_level_required = building_data["requirements"]["level"]
            building.base_building_xp_required = building_data["requirements"]["xp"]
            building.base_building_wood_required = building_data["requirements"]["wood"]
            building.base_building_stone_required = building_data["requirements"]["stone"]
            building.base_building_metal_required = building_data["requirements"]["metal"]

            # Base Collestion
            building.base_xp_per_minute = building_data["collection"]["xp"]
            building.base_cash_per_minute = building_data["collection"]["cash"]
            building.base_wood_per_minute = building_data["collection"]["wood"]
            building.base_stone_per_minute = building_data["collection"]["stone"]
            building.base_metal_per_minute = building_data["collection"]["metal"]
            del existing_buildings[building_data["building_name"]]
            print(f"Building {building_data['building_name']} Updated")

        else:
            new_building = Buildings(building_name=building_data["building_name"],
                                     building_description=building_data["building_description"],
                                     building_type_id=building_data["building_type_id"],
                                     building_link=building_data["building_link"],
                                     max_building_level=building_data["max_building_level"],
                                     base_building_cash_required=building_data["requirements"]["cash"],
                                     base_building_level_required=building_data["requirements"]["level"],
                                     base_building_xp_required=building_data["requirements"]["xp"],
                                     base_building_wood_required=building_data["requirements"]["wood"],
                                     base_building_stone_required=building_data["requirements"]["stone"],
                                     base_building_metal_required=building_data["requirements"]["metal"],
                                     base_xp_per_minute=building_data["collection"]["xp"],
                                     base_cash_per_minute=building_data["collection"]["cash"],
                                     base_wood_per_minute=building_data["collection"]["wood"],
                                     base_stone_per_minute=building_data["collection"]["stone"],
                                     base_metal_per_minute=building_data["collection"]["metal"])
            db.session.add(new_building)
            print(f"Building {building_data['building_name']} Created")

    for building in existing_buildings.values():
        db.session.delete(building)
        print(f"Building {building_data['building_name']} Deleted")

    db.session.commit()
    print("Buildings Synchronized")


# Create buildings, requirements progress
def update_buildings():
    sync_building_types()
    sync_buildings()
   
    
    # python -m app.game.Buildings.Buildings