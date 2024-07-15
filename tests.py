

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
from app.models import TestGameResourceLog
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
        service.add_xp(50, source="TEST ADD XP")
        service.add_cash(100, source="TEST ADD Cash")
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
        service.add_xp(150, source="TEST ADD LEVEL")
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



def delete_test_data():
    
    # Delete User Data
    db.session.query(User).delete()
    db.session.query(Role).delete()
    
    # Delete Game Data
    db.session.query(TestGameResourceLog).delete()
    db.session.query(TestGame).delete()
    
    # Delete game progress and game related data
    db.session.query(TestGameQuestProgress).delete()
    db.session.query(TestGameBuildingProgress).delete()
    db.session.query(TestGameInventoryItems).delete()
    db.session.query(TestGameInventoryUser).delete()
    
    # Delete logs
    db.session.query(TestGameResourceLog).delete()
    
    
    db.session.commit()
    print("All test data deleted")


# Run the script
if __name__ == "__main__":
    delete_test_data()
    populate_database()
    

   
    
    create_test_game_for_admin()
    test_GameService()
    test_GameBuildingService()
        
        

    