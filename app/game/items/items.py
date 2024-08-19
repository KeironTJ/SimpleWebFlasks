from app import create_app
from app.models import db
from app.models import Item


app = create_app()
app_context = app.app_context()
app_context.push()



## ITEMS
## Item Creator Class
class ItemCreator:
    def __init__(self, item_name, item_description):
        self.item_name = item_name
        self.item_description = item_description
        self.item = None  # Placeholder for the created item object

    def create_item(self):
        try:
            self.item = Item(item_name=self.item_name, item_description=self.item_description)
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

# Create items and inventory items
Sword.create_item()
Shield.create_item()
Potion.create_item()


def delete_item_data():
    # Delete Item Data
    db.session.query(Item).delete()