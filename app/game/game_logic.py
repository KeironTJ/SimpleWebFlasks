from app.models import User, Game
from app.models import Quest, QuestProgress, QuestRewards, QuestType
from app.models import Game, ResourceLog
from app.models import BuildingType, BuildingProgress, Buildings
from app.models import Inventory, InventoryItems, InventoryType, InventoryUser
from datetime import datetime, timezone, timedelta
from app import db
from flask import flash
from math import floor


## Game Setup related Service
# Class to create a new Game instance
class GameCreation:
    """Service for creating a new Game instance."""
    
    def __init__(self, user_id: int, game_name: str) -> None:
        self.user_id = user_id
        self.game_name = game_name
        self.game_id = None # game_id is set after game creation

    # function to create a new Game instance
    def create_game(self) -> Game:
        """Creates a new Game instance."""
        game = Game(user_id=self.user_id, game_name=self.game_name )
        db.session.add(game)
        db.session.commit()
        self.game_id = game.id
        
        return game

    # function to set the active game for the user
    def set_active_game(self, game_id: int) -> None:
        """Sets the active game for the user."""
        user = User.query.get(self.user_id)
        user.activegame = game_id
        db.session.commit()

    # function to assign all quests to the Game instance
    def assign_all_quests(self, game_id: int) -> None:
        """Assigns all quests to a Game."""
        quests = Quest.query.all()
        for quest in quests:
            quest_progress = QuestProgress(game_id=game_id,
                                           quest_id=quest.id)
            # Set quest progress parameters for quests
            if quest.id == 1:
                quest_progress.quest_active = True
                quest_progress.quest_progress = 100

            db.session.add(quest_progress)


    # function to assign all buildings to the Game instance    
    def assign_all_buildings(self, game_id: int) -> None:
        """Assigns all buildings to a Game."""
        buildings = Buildings.query.all()
        for building in buildings:
            building = BuildingProgress(game_id=game_id, 
                                                building_id=building.id)
            
            ## Set building progress parameters
            # Set quest building progress parameters for quests
            if building.building_id == 1:
                building.building_active = True
                building.building_level = 1
                
                
            # Set warehouse building progress parameters for inventories
            if building.building_id == 2:
                building.building_active = True  
                building.building_level = 1

                          
            db.session.add(building)

    # function to assign all inventories to the Game instance
    def assign_all_inventories(self, game_id: int) -> None:
        """Assigns all inventories to a Game."""
        inventories = Inventory.query.all()
        for inventory in inventories:
            inventory = InventoryUser(game_id=game_id, 
                                              inventory_id=inventory.id)
            db.session.add(inventory)
        
    # function to create all startup items for the Game instance
    def create_all_startup(self, game_id: int) -> None:
        # Make game active
        self.set_active_game(game_id)
        """Creates all startup items for a Game."""
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
# Class to action against the Game instance
class GameService:
    """Service for adding XP and cash to a Game and logging the operations."""
    
    def __init__(self, game_id: int, notifier=FlashNotifier()) -> None:
        self.game_id = game_id
        self.game = self._get_game()
        self.notifier = notifier
        
    
    ## Game related actions
    # functions to add XP to the Game instance
    def add_xp(self, xp: int, source="") -> None:
        """Adds XP to a Game, logs the addition, and checks for level up."""
        self.game.xp += xp
        
        self._check_and_update_level()

    # method to check and update the level to support add_xp
    def _check_and_update_level(self) -> None:
        """Checks if the Game has leveled up and updates accordingly."""
        level_up = False
        while self.game.xp >= self._xp_required_for_next_level(self.game.level):
            self.game.level += 1
            level_up = True

        if level_up:
            if self.notifier:
                self.notifier.notify(f'Congratulations! You have reached level {self.game.level}!')
            self.game.next_level_xp_required = self._xp_required_for_next_level(self.game.level)

    # method to calculate the xp required for the next level
    def _xp_required_for_next_level(self, level: int) -> int:
        base_xp = 100
        return floor(base_xp * (1.1 ** (level + 1)))

    # function to add cash to the Game instance
    def add_cash(self, cash: int, source = "") -> None:
        """Adds cash to a Game and logs the addition."""
        game = self._get_game()
        game.cash += cash
        cash_log = ResourceLog(game_id=self.game_id, 
                                       cash=cash,
                                       source=source)
        db.session.add(cash_log)

    def assign_quest(self, quest_id: int) -> None:
        """Assigns a Quest to a Game."""
        quest_progress = QuestProgress(game_id=self.game_id, 
                                       quest_id=quest_id)
        db.session.add(quest_progress)
        db.session.commit()

    def assign_building(self, building_id: int) -> None:
        """Assigns a Building to a Game."""
        building_progress = BuildingProgress(game_id=self.game_id, 
                                             building_id=building_id)
        db.session.add(building_progress)
        db.session.commit()

    def assign_inventory(self, inventory_id: int) -> None:
        """Assigns an Inventory to a Game."""
        inventory = InventoryUser(game_id=self.game_id, 
                                  inventory_id=inventory_id)
        db.session.add(inventory)
        db.session.commit()

    ## Helper functions
    def _get_game(self) -> Game:
        """Retrieves the Game instance or raises an error if not found."""
        game = Game.query.get(self.game_id)
        if game is None:
            raise ValueError(f"Game with ID {self.game_id} not found.")
        return game
    

    

## Game Quest Service
# Class to action against the QuestProgress instance
class QuestService:
    ''' Service for managing quest specific actions '''
    def __init__(self, quest_progress_id: int, notifier=FlashNotifier()) -> None:
        self.quest_progress_id = quest_progress_id
        self.quest = self._get_quest_progress()
        self.notifier = notifier

    def _get_quest_progress(self) -> QuestProgress:
        """Retrieves the QuestProgress instance or raises an error if not found."""
        quest = QuestProgress.query.get(self.quest_progress_id)
        if quest is None:
            raise ValueError(f"QuestProgress with ID {self.quest_progress_id} not found.")
        return quest

    # Quest Methods:
    def complete_quest(self):
        self.quest.quest_completed = True
        self.quest.quest_completed_date = datetime.now()
        self.collect_rewards()

        self.notifier.notify("Quest: Completed!")

    def add_progress(self, progress: int):
        self.quest.quest_progress += progress
        if self.quest.quest_progress >= 100:
            self.complete_quest()
            if self.notifier:
                self.notifier.notify("Quest Completed!")
        else:
            if self.notifier:
                self.notifier.notify(f"Quest Progress: {self.quest.progress}%")
                
    def collect_rewards(self):
        rewards = QuestRewards.query.filter_by(quest_id=self.quest.quest_id).first()
        if rewards is None:
            return

        game_service = GameService(self.quest.game_id)
        game_service.add_xp(rewards.quest_reward_xp, source="Quest Reward")
        game_service.game.cash += rewards.quest_reward_cash
        game_service.game.wood += rewards.quest_reward_wood
        game_service.game.stone += rewards.quest_reward_stone
        game_service.game.metal += rewards.quest_reward_metal
        self.update_resource_log()


        if self.notifier:
            self.notifier.notify("Quest Rewards Collected")

    def update_resource_log(self):
        rewards = QuestRewards.query.filter_by(quest_id=self.quest.quest_id).first()
        resource_log = ResourceLog(
            game_id=self.quest.game_id,
            cash=rewards.quest_reward_cash,
            wood=rewards.quest_reward_wood,
            stone=rewards.quest_reward_stone,
            metal=rewards.quest_reward_metal,
            xp = rewards.quest_reward_xp,
            source = "Quest Rewards. Quest: " + str(self.quest.quest_id)
        )

        db.session.add(resource_log)
        db.session.commit()

        


## GameBuildingService
# Class to action against the GameBuilding instance
class GameBuildingService:
    ''' Service for managing game specific building actions '''
    def __init__(self, building_progress_id: int, notifier=FlashNotifier()) -> None:
        self.building_progress_id = building_progress_id
        self.building = self._get_building_progress()
        self.notifier = notifier

    def _get_building_progress(self) -> BuildingProgress:
        """Retrieves the BuildingProgress instance or raises an error if not found."""
        building = BuildingProgress.query.get(self.building_progress_id)
        if building is None:
            raise ValueError(f"BuildingProgress with ID {self.building_progress_id} not found.")
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

        # Add accrued resources to the Game
        self.building.game.cash += self.building.accrued_cash
        self.building.game.wood += self.building.accrued_wood
        self.building.game.stone += self.building.accrued_stone
        self.building.game.metal += self.building.accrued_metal

        # update log
        self.update_resource_log()

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
        # Check if accrual_start_time is set
        if self.building.accrual_start_time is None:
            return 0
        else:
            # Ensure accrual_start_time is offset-aware
            accrual_start_time = self.building.accrual_start_time
            if accrual_start_time.tzinfo is None:
                # If accrual_start_time is offset-naive, make it offset-aware by assuming it's in UTC
                accrual_start_time = accrual_start_time.replace(tzinfo=timezone.utc)

        # Now that both datetimes are offset-aware, perform the subtraction
        time_difference = datetime.now(timezone.utc) - accrual_start_time
        minutes = time_difference.total_seconds() / 60  # Calculate minutes for finer detail

        # check if max accrual duration is reached
        if minutes > self.building.max_accrual_duration:
            minutes = round(self.building.max_accrual_duration)


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

        # Calculate required resources for the current upgrade level
        required_resources = self._calculate_required_resources()

        # Check if user has enough resources to upgrade
        for resource, required_amount in required_resources.items():
            if getattr(self.building.game, resource) < required_amount:
                return False

        return True

    def _calculate_required_resources(self):
        """Calculates the resources required for the next upgrade based on the current level."""
        
        if self.building.building_level == 0:
            level_factor = 1
        else:
            level_factor = (1.5 ** self.building.building_level)
        
        required_resources = {
            'level': round(self.building.building.base_building_level_required),
            'cash': round(self.building.building.base_building_cash_required * level_factor),
            'wood': round(self.building.building.base_building_wood_required * level_factor),
            'stone': round(self.building.building.base_building_stone_required * level_factor),
            'metal': round(self.building.building.base_building_metal_required * level_factor),
        }
        return required_resources

    def upgrade_building(self):
        # Check if building is already at max level
        if self.building.building_level >= self.building.building.max_building_level:
            if self.notifier:
                self.notifier.notify("Building is already at max level.")
            return
        
        # Check if user has enough cash to upgrade
        if not self.check_upgrade_requirements():
            if self.notifier:
                self.notifier.notify("Insufficient resources to upgrade building.")
            return
        
        # Deduct cash from user
        required_resources = self._calculate_required_resources()
        for resource, required_amount in required_resources.items():
            if resource == 'level':
                continue
            setattr(self.building.game, resource, getattr(self.building.game, resource) - required_amount)
            

        
        
        # Check if building level is 0 and set rate
        if self.building.building_level == 0:
            self.building.cash_per_minute = self.building.building.base_cash_per_minute
            self.building.xp_per_minute = self.building.building.base_xp_per_minute
            self.building.wood_per_minute = self.building.building.base_wood_per_minute
            self.building.stone_per_minute = self.building.building.base_stone_per_minute
            self.building.metal_per_minute = self.building.building.base_metal_per_minute
            self.building.building_active = True

        # Collect current resources
        self.collect_resources()
        
        # Upgrade building
        self.building.building_level += 1
        self.building.cash_per_minute = round(self.building.cash_per_minute * 1.1)
        self.building.xp_per_minute = round(self.building.xp_per_minute * 1.1)
        self.building.wood_per_minute = round(self.building.wood_per_minute * 1.1)
        self.building.stone_per_minute = round(self.building.stone_per_minute * 1.1)
        self.building.metal_per_minute = round(self.building.metal_per_minute * 1.1)

        # Increase XP
        game_service = GameService(self.building.game_id)
        game_service.add_xp(10, source="Building Upgrade")

        # Update resource log
        resource_log = ResourceLog(
            game_id=self.building.game_id,
            cash= -required_resources['cash'],
            wood= -required_resources['wood'],
            stone= -required_resources['stone'],
            metal= -required_resources['metal'],
            xp = 10,
            source = "Building Upgrade. Building: " + str(self.building.building_id)
        )

        db.session.add(resource_log)
        
        
        if self.notifier:
            self.notifier.notify(f"Building upgraded to level {self.building.building_level}.")
            
    def check_resources_to_collect(self):
        if self.building.accrual_start_time is None:
            return False
        else:
            return True
        
    def update_resource_log(self):
        resource_log = ResourceLog(
            game_id=self.building.game_id,
            cash=self.building.accrued_cash,
            wood=self.building.accrued_wood,
            stone=self.building.accrued_stone,
            metal=self.building.accrued_metal,
            source = "Resource Collection. Building: " + str(self.building.building_id)
        )

        db.session.add(resource_log)
        db.session.commit()