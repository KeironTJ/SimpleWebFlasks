from app import create_app
from sqlalchemy.exc import IntegrityError       # type:ignore
from app.models import db, Role, User
from app.models import Game
from app.models import QuestProgress
from app.models import InventoryItems, InventoryUser
from app.models import ResourceLog
from app.models import BuildingProgress
from app.game.GameServices import GameCreation
from app.game.Buildings.Buildings import create_building_types, create_buildings, delete_building_data
from app.game.Quests.Quests import create_QuestTypes, create_quests, delete_quest_data
from app.game.Heroes.heroes import create_heroes, delete_hero_data

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
        except IntegrityError:
            db.session.rollback()
            print(f"Failed to add user: {username}")

def create_roles_and_users():
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

    # Create a user for testing
    if User.query.filter_by(username="test").first() is None:
        add_user(username="test", email="test@test.com", password="test", role_name="user")
    else:
        print("User test already exists")


## GAME ADMIN CREATION
# Create a game for the admin user
def create_game_for_admin():
    service = GameCreation(user_id=1, game_name="Game 1")
    game = service.create_game()
    
    db.session.commit()
    print("Game Created")
    
    game_id = game.id
    
    service.create_all_startup(game_id)
    db.session.commit()

def create_game_for_user():
    service = GameCreation(user_id=2, game_name="Game 2")
    game = service.create_game()
    
    db.session.commit()
    print("Game Created")
    
    game_id = game.id
    
    service.create_all_startup(game_id)
    db.session.commit()

    


def delete_game_data():
    
    # Delete User Data
    db.session.query(User).delete()
    db.session.query(Role).delete()
    
    # Delete Game Data
    db.session.query(ResourceLog).delete()
    db.session.query(Game).delete()
    
    # Delete game progress and game related data
    db.session.query(QuestProgress).delete()
    db.session.query(BuildingProgress).delete()
    db.session.query(InventoryItems).delete()
    db.session.query(InventoryUser).delete()

    
    
    # Delete logs
    db.session.query(ResourceLog).delete()
    
    
    db.session.commit()
    print("All data deleted")


# Run the script
if __name__ == "__main__":

    # User and Role data
    delete_game_data()
    create_roles_and_users()
    

    # Building Data
    delete_building_data()
    create_building_types()
    create_buildings()

    # Quest Data
    delete_quest_data()
    create_QuestTypes()
    create_quests()

    # Hero Data
    delete_hero_data()
    create_heroes()
    


    # Create new game for admin
    create_game_for_admin()
    create_game_for_user()



        
        

    