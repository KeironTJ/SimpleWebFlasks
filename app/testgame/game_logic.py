from app.models import User, TestGame
from app.models import TestGameQuest, TestGameQuestProgress, TestGameQuestRewards, TestGameQuestType
from app.models import TestGame, TestGameResourceLog
from app.models import TestGameBuildingType, TestGameBuildingProgress, TestGameBuildings
from app.models import TestGameInventory, TestGameInventoryItems, TestGameInventoryType, TestGameInventoryUser
from datetime import datetime, timezone, timedelta
from app import db
from flask import flash
from math import floor


## Game Setup related Service
# Class to create a new TestGame instance
class GameCreation:
    """Service for creating a new TestGame instance."""
    
    def __init__(self, user_id: int, game_name: str) -> None:
        self.user_id = user_id
        self.game_name = game_name
        self.game_id = None # game_id is set after game creation

    # function to create a new TestGame instance
    def create_game(self) -> TestGame:
        """Creates a new TestGame instance."""
        test_game = TestGame(user_id=self.user_id, game_name=self.game_name )
        db.session.add(test_game)
        db.session.commit()
        self.game_id = test_game.id
        
        return test_game

    # function to set the active game for the user
    def set_active_game(self, game_id: int) -> None:
        """Sets the active game for the user."""
        user = User.query.get(self.user_id)
        user.activetestgame = game_id
        db.session.commit()

    # function to assign all quests to the TestGame instance
    def assign_all_quests(self, game_id: int) -> None:
        """Assigns all quests to a TestGame."""
        quests = TestGameQuest.query.all()
        for quest in quests:
            quest_progress = TestGameQuestProgress(game_id=game_id, 
                                                   quest_id=quest.id)
            db.session.add(quest_progress)

    # function to assign all buildings to the TestGame instance    
    def assign_all_buildings(self, game_id: int) -> None:
        """Assigns all buildings to a TestGame."""
        buildings = TestGameBuildings.query.all()
        for building in buildings:
            building = TestGameBuildingProgress(game_id=game_id, 
                                                building_id=building.id)
            
                          
            db.session.add(building)

    # function to assign all inventories to the TestGame instance
    def assign_all_inventories(self, game_id: int) -> None:
        """Assigns all inventories to a TestGame."""
        inventories = TestGameInventory.query.all()
        for inventory in inventories:
            inventory = TestGameInventoryUser(game_id=game_id, 
                                              inventory_id=inventory.id)
            db.session.add(inventory)
        
    # function to create all startup items for the TestGame instance
    def create_all_startup(self, game_id: int) -> None:
        # Make game active
        self.set_active_game(game_id)
        """Creates all startup items for a TestGame."""
        self.assign_all_quests(game_id)
        self.assign_all_buildings(game_id)
        self.assign_all_inventories(game_id)
        db.session.commit()
            

## Context Related Service
class FlashNotifier:
    @staticmethod
    def notify(message):
        flash(message)

class PrintNotifier: 
    @staticmethod
    def notify(message):
        print(message)


## Game Related Service
# Class to action against the TestGame instance
class GameService:
    """Service for adding XP and cash to a TestGame and logging the operations."""
    
    def __init__(self, test_game_id: int, notifier=FlashNotifier()) -> None:
        self.test_game_id = test_game_id
        self.test_game = self._get_test_game()
        self.notifier = notifier
        
    
    ## Game related actions
    # functions to add XP to the TestGame instance
    def add_xp(self, xp: int, source="") -> None:
        """Adds XP to a TestGame, logs the addition, and checks for level up."""
        self.test_game.xp += xp
        resource_log= TestGameResourceLog(test_game_id=self.test_game_id, 
                                          xp=xp,
                                          source=source)
        db.session.add(resource_log)

        self._check_and_update_level()

    # method to check and update the level to support add_xp
    def _check_and_update_level(self) -> None:
        """Checks if the TestGame has leveled up and updates accordingly."""
        level_up = False
        while self.test_game.xp >= self._xp_required_for_next_level(self.test_game.level):
            self.test_game.level += 1
            level_up = True

        if level_up:
            if self.notifier:
                self.notifier.notify(f'Congratulations! You have reached level {self.test_game.level}!')
            self.test_game.next_level_xp_required = self._xp_required_for_next_level(self.test_game.level)

    # method to calculate the xp required for the next level
    def _xp_required_for_next_level(self, level: int) -> int:
        base_xp = 100
        return floor(base_xp * (1.1 ** (level + 1)))

    # function to add cash to the TestGame instance
    def add_cash(self, cash: int, source = "") -> None:
        """Adds cash to a TestGame and logs the addition."""
        test_game = self._get_test_game()
        test_game.cash += cash
        cash_log = TestGameResourceLog(test_game_id=self.test_game_id, 
                                       cash=cash,
                                       source=source)
        db.session.add(cash_log)
    
    ## Quest related actions
    def assign_quest(self, game_id: int, quest_id: int) -> None:
        """Assigns a quest to a TestGame."""
        quest_progress = TestGameQuestProgress(game_id=game_id, quest_id=quest_id)
        db.session.add(quest_progress)
        
    def remove_quest(self, game_id: int, quest_id: int) -> None:
        """Removes a quest from a TestGame."""
        quest_progress = TestGameQuestProgress.query.filter_by(game_id=game_id, quest_id=quest_id).first()
        db.session.delete(quest_progress)
    
    def add_quest_progress(self, quest_id: int, progress: int) -> None:
        """Adds progress to a quest."""
        quest_progress = TestGameQuestProgress.query.get(quest_id)
        quest_progress.progress += progress
        
        if quest_progress.progress >= 100:
            quest_progress.is_complete = True
            quest_progress.completion_date = datetime.now()
            
    def complete_quest(self, game_id: int, quest_id: int) -> None:
        """Marks a quest as complete."""
        quest_progress = TestGameQuestProgress.query.filter_by(game_id=game_id, quest_id=quest_id).first()
        quest_progress.is_complete = True
        quest_progress.completion_date = datetime.now()
        

    ## Inventory / Item related actions
    def add_game_inventory(self, game_id: int, inventory_id: int) -> None:
        """Adds an inventory to a TestGame."""
        inventory = TestGameInventoryUser(game_id=game_id, inventory_id=inventory_id)
        db.session.add(inventory)
        
    def remove_game_inventory(self, game_id: int, inventory_id: int) -> None:
        """Removes an inventory from a TestGame."""
        inventory = TestGameInventoryUser.query.filter_by(game_id=game_id, inventory_id=inventory_id).first()
        db.session.delete(inventory)
        
    def add_inventory_item(self, inventory_id: int, item_id: int, quantity: int) -> None:
        """Check if item already exists, if so, increase quantity, otherwise add item to inventory."""
        item = TestGameInventoryItems.query.filter_by(inventory_id=inventory_id, item_id=item_id).first()
        if item is not None:
            item.quantity += quantity
        else:
            item = TestGameInventoryItems(inventory_id=inventory_id, item_id=item_id, quantity=quantity)
            db.session.add(item)
        
    def remove_inventory_item(self, inventory_id: int, item_id: int, quantity: int) -> None:
        """Check if item exists, if so, decrease quantity, if quantity is 0, remove item from inventory."""
        item = TestGameInventoryItems.query.filter_by(inventory_id=inventory_id, item_id=item_id).first()
        if item is not None:
            item.quantity -= quantity
            if item.quantity <= 0:
                db.session.delete(item)


    ## Building related actions
    def add_building_level(self, building_id: int, level: int, cash_per_hour: int) -> None:
        """Adds a level to a building."""
        building = TestGameBuildingProgress.query.get(building_id)
        building.level += level
        building.cash_per_hour += cash_per_hour
        

    ## Helper functions
    def _get_test_game(self) -> TestGame:
        """Retrieves the TestGame instance or raises an error if not found."""
        test_game = TestGame.query.get(self.test_game_id)
        if test_game is None:
            raise ValueError(f"TestGame with ID {self.test_game_id} not found.")
        return test_game
    


## GameBuildingService
# Class to action against the TestGameBuilding instance
class GameBuildingService:
    ''' Service for managing game specific building actions '''
    def __init__(self, building_progress_id: int, notifier=FlashNotifier()) -> None:
        self.building_progress_id = building_progress_id
        self.building = self._get_building_progress()
        self.notifier = notifier

    def _get_building_progress(self) -> TestGameBuildingProgress:
        """Retrieves the TestGameBuildingProgress instance or raises an error if not found."""
        building = TestGameBuildingProgress.query.get(self.building_progress_id)
        if building is None:
            raise ValueError(f"TestGameBuildingProgress with ID {self.building_progress_id} not found.")
        return building  

    # Building Methods:
    def start_accrual(self):
        self.building.accrual_start_time = datetime.now(timezone.utc)
        self.building.accrued_cash = 0
        self.building.accrued_xp = 0
        self.building.accrued_wood = 0
        self.building.accrued_stone = 0
        self.building.accrued_metal = 0

    def collect_resources(self):
        self.calculate_accrued_resources()

        # Add accrued resources to the TestGame
        self.building.game.cash += self.building.accrued_cash
        self.building.game.wood += self.building.accrued_wood
        self.building.game.stone += self.building.accrued_stone
        self.building.game.metal += self.building.accrued_metal
        
        #use game service to add xp as need to check if level up
        game_service = GameService(test_game_id=self.building.game_id)
        game_service.add_xp(self.building.accrued_xp,
                            source = "Resource Collection. Building: " + str(self.building.building_id))

        

        # update log
        resource_log = TestGameResourceLog(
            test_game_id=self.building.game_id,
            cash=self.building.accrued_cash,
            wood=self.building.accrued_wood,
            stone=self.building.accrued_stone,
            metal=self.building.accrued_metal,
            source = "Resource Collection. Building: " + str(self.building.building_id)
        )

        db.session.add(resource_log)
        db.session.commit()

        # Update building progress
        self.start_accrual()
        



    def show_accrual_time(self):
        if self.building.accrual_start_time is None:
            return False
        else:
            time_difference = datetime.now(timezone.utc) - self.building.accrual_start_time
            hours = time_difference.total_seconds() / 3600
            return hours
        
    def calculate_accrued_resources(self):
        # Ensure accrual_start_time is offset-aware
        if self.building.accrual_start_time.tzinfo is None:
            accrual_start_time = self.building.accrual_start_time.replace(tzinfo=timezone.utc)
        else:
            accrual_start_time = self.building.accrual_start_time

        # Calculate with finer detail
        time_difference = datetime.now(timezone.utc) - accrual_start_time
        minutes = time_difference.total_seconds() / 60  # Calculate minutes for finer detail

        # Calculate accrued resources and round to whole numbers
        self.building.accrued_cash = round(self.building.cash_per_minute * minutes)
        self.building.accrued_xp = round(self.building.xp_per_minute * minutes)
        self.building.accrued_wood = round(self.building.wood_per_minute * minutes)
        self.building.accrued_stone = round(self.building.stone_per_minute * minutes)
        self.building.accrued_metal = round(self.building.metal_per_minute * minutes)
    
    def check_upgrade_requirements(self):
        # Check if building is already at max level
        if self.building.building_level >= self.building.building.max_building_level:
            return False
        
        # Check if user has enough cash to upgrade
        if self.building.game.cash >= self.building.building.base_building_cash_required:
            return True
        
        return False

    def upgrade_building(self):
        # Check if building is already at max level
        if self.building.building_level >= self.building.building.max_building_level:
            if self.notifier:
                self.notifier.notify("Building is already at max level.")
            return
        
        # Check if user has enough cash to upgrade
        if self.building.game.cash < self.building.building.base_building_cash_required:
            if self.notifier:
                self.notifier.notify("Insufficient cash to upgrade building.")
            return
        
        # Deduct cash from user
        game_service = GameService(test_game_id=self.building.game_id)
        game_service.add_cash(-self.building.building.base_building_cash_required, 
                              source="Building Upgrade. Building: " + str(self.building.building_id))
        
        # Collect current resources
        self.collect_resources()

        # Upgrade building
        self.building.building_level += 1
        self.building.cash_per_minute += round(self.building.cash_per_minute * 1.1)
        self.building.xp_per_minute += round(self.building.xp_per_minute * 1.1)
        self.building.wood_per_minute += round(self.building.wood_per_minute * 1.1)
        self.building.stone_per_minute += round(self.building.stone_per_minute * 1.1)
        self.building.metal_per_minute += round(self.building.metal_per_minute * 1.1)
        
        
        if self.notifier:
            self.notifier.notify(f"Building upgraded to level {self.building.building_level}.")