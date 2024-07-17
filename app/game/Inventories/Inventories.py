from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User
from app.models import Game
from app.models import Quest, QuestType, QuestRewards,RewardItemAssociation, QuestProgress
from app.models import Item, Inventory, InventoryItems, InventoryType, InventoryUser
from app.models import ResourceLog
from app.models import Buildings, BuildingProgress, BuildingType
from app.game.game_logic import GameCreation, GameService, PrintNotifier, GameBuildingService

app = create_app()
app_context = app.app_context()
app_context.push()



## INVENTORY
# Create Inventory Types       
def create_inventory_types():
    try:
        inventory_type1 = InventoryType(inventory_type_name="Main Inventory", inventory_type_description="Main Inventory Description")
        inventory_type2 = InventoryType(inventory_type_name="Secondary Inventory", inventory_type_description="Secondary Inventory Description")
        inventory_type3 = InventoryType(inventory_type_name="Tertiary Inventory", inventory_type_description="Tertiary Inventory Description")
        db.session.add(inventory_type1)
        db.session.add(inventory_type2)
        db.session.add(inventory_type3)
        db.session.commit()
        print("Inventory Types Created")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to create inventory types: {e}")
    
# Inventory Creator Class
class InventoryCreator:
    def __init__(self, inventory_name, inventory_description, inventory_type_id):
        self.inventory_name = inventory_name
        self.inventory_description = inventory_description
        self.inventory_type_id = inventory_type_id
        self.inventory = None  # Placeholder for the created inventory object

    def create_inventory(self):
        try:
            self.inventory = Inventory(inventory_name=self.inventory_name, inventory_description=self.inventory_description, inventory_type_id=self.inventory_type_id)
            db.session.add(self.inventory)
            db.session.commit()
            print("Inventory Created")
            return self.inventory
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create inventory: {e}")
            
# Example usage
main_inventory = InventoryCreator(inventory_name="Main Inventory", inventory_description="Main Inventory Description", inventory_type_id=1)


def delete_inventory_data():
    # Delete Inventory Data
    db.session.query(InventoryItems).delete()
    db.session.query(InventoryUser).delete()
    db.session.query(Inventory).delete()
    db.session.query(InventoryType).delete()
    


# Create Inventory Types, Inventories
create_inventory_types()
main_inventory.create_inventory()