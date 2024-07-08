from app.models import User, TestGame, TestGameQuest, TestGameQuestProgress, TestGameQuestRewards, TestGameQuestType
from app.models import TestGame, TestGameXPLog, TestGameCashLog
from app.models import TestGameBuildingType, TestGameBuildingProgress, TestGameBuildings
from app.models import TestGameInventory, TestGameInventoryItems
from datetime import datetime
from app import db

class GameCreation:
    """Service for creating a new TestGame instance."""
    
    def __init__(self, user_id: int, game_name: int) -> None:
        self.user_id = user_id
        self.game_name = game_name
        self.game_id = None # game_id is set after game creation

    def create_game(self) -> TestGame:
        """Creates a new TestGame instance."""
        test_game = TestGame(user_id=self.user_id, game_name=self.game_name )
        db.session.add(test_game)
        db.session.commit()
        self.game_id = test_game.id
        
        return test_game

    def set_active_game(self, game_id: int) -> None:
        """Sets the active game for the user."""
        user = User.query.get(self.user_id)
        user.activetestgame = game_id

    def assign_all_quests(self, game_id: int) -> None:
        """Assigns all quests to a TestGame."""
        quests = TestGameQuest.query.all()
        for quest in quests:
            quest_progress = TestGameQuestProgress(game_id=game_id, 
                                                   quest_id=quest.id)
            db.session.add(quest_progress)
            
    def assign_all_buildings(self, game_id: int) -> None:
        """Assigns all buildings to a TestGame."""
        buildings = TestGameBuildings.query.all()
        for building in buildings:
            building = TestGameBuildingProgress(game_id=game_id, 
                                                building_id=building.id)
            db.session.add(building)
            
    def assign_all_inventories(self, game_id: int) -> None:
        """Assigns all inventories to a TestGame."""
        inventories = TestGameInventory.query.all()
        for inventory in inventories:
            inventory = TestGameInventory(game_id=game_id)
            db.session.add(inventory)
           
    def create_all_startup(self, game_id: int) -> None:
        """Creates all startup items for a TestGame."""
        self.assign_all_quests(game_id)
        self.assign_all_buildings(game_id)
        self.assign_all_inventories(game_id)
        
        
    
            
            

            

# Class to to query the TestGame instance
class GameQuery:
    """Service for querying the TestGame instance."""
    
    def __init__(self, game_id: int) -> None:
        self.game_id = game_id
        
    def get_active_game(self) -> TestGame:
        """Retrieves the active TestGame instance or raises an error if not found."""
        user = User.query.get(self.user_id)
        if user.activetestgame is None:
            raise ValueError(f"Active TestGame not found for user {self.user_id}.")
        test_game = TestGame.query.get(user.activetestgame)
        if test_game is None:
            raise ValueError(f"TestGame with ID {user.activetestgame} not found.")
        return test_game
    
    def get_all_games(self) -> TestGame:
        """Retrieves all TestGame instances for a user."""
        test_games = TestGame.query.filter_by(user_id=self.user_id).all()
        return test_games
    
    def get_game_by_id(self, game_id: int) -> TestGame:
        """Retrieves a TestGame instance by ID."""
        test_game = TestGame.query.get(game_id)
        if test_game is None:
            raise ValueError(f"TestGame with ID {game_id} not found.")
        return test_game
    
    def get_quest_by_id(self, quest_id: int) -> TestGameQuest:
        """Retrieves a TestGameQuest instance by ID."""
        quest = TestGameQuest.query.get(quest_id)
        if quest is None:
            raise ValueError(f"TestGameQuest with ID {quest_id} not found.")
        return quest
    
    def get_quest_rewards_by_id(self, quest_id: int) -> TestGameQuestRewards:
        """Retrieves a TestGameQuestRewards instance by ID."""
        quest_rewards = TestGameQuestRewards.query.get(quest_id)
        if quest_rewards is None:
            raise ValueError(f"TestGameQuestRewards with ID {quest_id} not found.")
        return quest_rewards
    
    def get_quest_type_by_id(self, quest_type_id: int) -> TestGameQuestType:
        """Retrieves a TestGameQuestType instance by ID."""
        quest_type = TestGameQuestType.query.get(quest_type_id)
        if quest_type is None:
            raise ValueError(f"TestGameQuestType with ID {quest_type_id} not found.")
        return quest_type
    
    def get_building_type_by_id(self, building_type_id: int) -> TestGameBuildingType:
        """Retrieves a TestGameBuildingType instance by ID."""
        building_type = TestGameBuildingType.query.get(building_type_id)
        if building_type is None:
            raise ValueError(f"TestGameBuildingType with ID {building_type_id} not found.")
        return building_type

    def get_building_progress_by_id(self, building_progress_id: int) -> TestGameBuildingProgress:
        """Retrieves a TestGameBuildingProgress instance by ID."""
        building_progress = TestGameBuildingProgress.query.get(building_progress_id)
        if building_progress is None:
            raise ValueError(f"TestGameBuildingProgress with ID {building_progress_id} not found.")
        return building_progress
    
    def get_building_by_id(self, building_id: int) -> TestGameBuildings:
        """Retrieves a TestGameBuildings instance by ID."""
        building = TestGameBuildings.query.get(building_id)
        if building is None:
            raise ValueError(f"TestGameBuildings with ID {building_id} not found.")
        return building
    
    def get_inventory_by_id(self, inventory_id: int) -> TestGameInventory:
        """Retrieves a TestGameInventory instance by ID."""
        inventory = TestGameInventory.query.get(inventory_id)
        if inventory is None:
            raise ValueError(f"TestGameInventory with ID {inventory_id} not found.")
        return inventory
    
    def get_inventory_item_by_id(self, inventory_item_id: int) -> TestGameInventoryItems:
        """Retrieves a TestGameInventoryItem instance by ID."""
        inventory_item = TestGameInventoryItems.query.get(inventory_item_id)
        if inventory_item is None:
            raise ValueError(f"TestGameInventoryItem with ID {inventory_item_id} not found.")
        return inventory_item
    
    def get_quest_progress_by_id(self, quest_progress_id: int) -> TestGameQuestProgress:
        """Retrieves a TestGameQuestProgress instance by ID."""
        quest_progress = TestGameQuestProgress.query.get(quest_progress_id)
        if quest_progress is None:
            raise ValueError(f"TestGameQuestProgress with ID {quest_progress_id} not found.")
        return quest_progress
    
    def get_quest_progress_by_game_id(self, game_id: int) -> TestGameQuestProgress:
        """Retrieves a TestGameQuestProgress instance by game ID."""
        quest_progress = TestGameQuestProgress.query.filter_by(game_id=game_id).all()
        return quest_progress
    
    def get_quest_progress_by_quest_id(self, quest_id: int) -> TestGameQuestProgress:
        """Retrieves a TestGameQuestProgress instance by quest ID."""
        quest_progress = TestGameQuestProgress.query.filter_by(quest_id=quest_id).all()
        return quest_progress
    
    def get_quest_progress_by_game_and_quest_id(self, game_id: int, quest_id: int) -> TestGameQuestProgress:
        """Retrieves a TestGameQuestProgress instance by game and quest ID."""
        quest_progress = TestGameQuestProgress.query.filter_by(game_id=game_id, quest_id=quest_id).first()
        return quest_progress
    
    
    
    

            
    # function to reutn TestGame instance
    def get_test_game(self) -> TestGame:
        """Retrieves the TestGame instance or raises an error if not found."""
        test_game = TestGame.query.get(self.user_id)
        if test_game is None:
            raise ValueError(f"TestGame with ID {self.user_id} not found.")
        return test_game        
    

    
        

class GameService:
    """Service for adding XP and cash to a TestGame and logging the operations."""
    
    def __init__(self, test_game_id: int) -> None:
        self.test_game_id = test_game_id

    def add_xp(self, xp: int) -> None:
        """Adds XP to a TestGame and logs the addition."""
        test_game = self._get_test_game()
        test_game.xp += xp
        xp_log = TestGameXPLog(xp=xp, test_game_id=self.test_game_id)
        db.session.add(xp_log)

    def add_cash(self, cash: int) -> None:
        """Adds cash to a TestGame and logs the addition."""
        test_game = self._get_test_game()
        test_game.cash += cash
        cash_log = TestGameCashLog(cash=cash, test_game_id=self.test_game_id)
        db.session.add(cash_log)
    
    def assign_quest(self, game_id: int, quest_id: int) -> None:
        """Assigns a quest to a TestGame."""
        quest_progress = TestGameQuestProgress(game_id=game_id, quest_id=quest_id)
        db.session.add(quest_progress)
        
    def remove_quest(self, game_id: int, quest_id: int) -> None:
        """Removes a quest from a TestGame."""
        quest_progress = TestGameQuestProgress.query.filter_by(game_id=game_id, quest_id=quest_id).first()
        db.session.delete(quest_progress)
        
    def complete_quest(self, game_id: int, quest_id: int) -> None:
        """Marks a quest as complete."""
        quest_progress = TestGameQuestProgress.query.filter_by(game_id=game_id, quest_id=quest_id).first()
        quest_progress.is_complete = True
        quest_progress.completion_date = datetime.now()
        
    def add_inventory(self, game_id: int, inventory_id: int) -> None:
        """Adds an inventory to a TestGame."""
        inventory = TestGameInventory(game_id=game_id, inventory_id=inventory_id)
        db.session.add(inventory)
        
    def remove_inventory(self, game_id: int, inventory_id: int) -> None:
        """Removes an inventory from a TestGame."""
        inventory = TestGameInventory.query.filter_by(game_id=game_id, inventory_id=inventory_id).first()
        db.session.delete(inventory)
        
    def add_inventory_item(self, inventory_id: int, item_id: int) -> None:
        """Adds an item to an inventory."""
        item = TestGameInventoryItems(inventory_id=inventory_id, item_id=item_id)
        db.session.add(item)
        
    def remove_inventory_item(self, inventory_id: int, item_id: int) -> None:
        """Removes an item from an inventory."""
        item = TestGameInventoryItems.query.filter_by(inventory_id=inventory_id, item_id=item_id).first()
        db.session.delete(item)
        
            
    def add_quest_progress(self, quest_id: int, progress: int) -> None:
        """Adds progress to a quest."""
        quest_progress = TestGameQuestProgress.query.get(quest_id)
        quest_progress.progress += progress
        
        if quest_progress.progress >= 100:
            quest_progress.is_complete = True
            quest_progress.completion_date = datetime.now()
            
    def add_game_level(self, game_id: int, level: int) -> None:
        """Adds a level to a TestGame."""
        test_game = TestGame.query.get(game_id)
        test_game.level += level
        
    def add_building_level(self, building_id: int, level: int, cash_per_hour: int) -> None:
        """Adds a level to a building."""
        building = TestGameBuildingProgress.query.get(building_id)
        building.level += level
        building.cash_per_hour += cash_per_hour
        
        
    def _get_test_game(self) -> TestGame:
        """Retrieves the TestGame instance or raises an error if not found."""
        test_game = TestGame.query.get(self.test_game_id)
        if test_game is None:
            raise ValueError(f"TestGame with ID {self.test_game_id} not found.")
        return test_game
       

                              
        


