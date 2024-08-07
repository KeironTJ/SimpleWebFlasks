from hmac import new
from re import I
from app.models import User, Game
from app.models import Quest, QuestProgress, QuestRewards, QuestType, QuestPrerequisites, QuestPreRequisitesProgress, QuestRequirementProgress, QuestRequirements
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
        
        # Loop through all quests and assign them to the game
        for quest in quests:
            quest_progress = QuestProgress(game_id=game_id,
                                           quest_id=quest.id) 
            
            # Set quest progress parameters for quests
            if quest.id == 1001:
                quest_progress.quest_active = True
                quest_progress.quest_progress = 100

            db.session.add(quest_progress)
            db.session.commit()
            
            # Assign quest pre-requisites
            self.assign_quest_pre_requisites(quest_progress.id)

            # Assign quest requirements
            self.assign_quest_requirements(quest_progress.id)
            
    def assign_quest_pre_requisites(self, quest_progress_id: int) -> None:
        """Assigns all quest pre-requisites to a QuestProgress."""
        quest_progress = QuestProgress.query.get(quest_progress_id)
        prerequisites = QuestPrerequisites.query.filter_by(quest_id=quest_progress.quest_id).all()
        for prerequisite in prerequisites:
            prerequisite_progress = QuestPreRequisitesProgress(quest_progress_id=quest_progress_id,
                                                               quest_prerequisite_id=prerequisite.prerequisite_id)
            db.session.add(prerequisite_progress)
            db.session.commit()
            
    def assign_quest_requirements(self, quest_progress_id: int) -> None:
        """Assigns all quest requirements to a QuestProgress."""
        quest_progress = QuestProgress.query.get(quest_progress_id)
        requirements = QuestRequirements.query.filter_by(quest_id=quest_progress.quest_id).all()
        for requirement in requirements:
            requirement_progress = QuestRequirementProgress(quest_progress_id=quest_progress_id,
                                                            quest_requirement_id=requirement.id
                                                            )
            db.session.add(requirement_progress)
            db.session.commit()
            

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
    # Method to updated game resources
    def update_resources(self,xp: int=0, cash: int=0, wood: int=0, stone: int=0, metal: int=0, source = "") -> None:
        """Updates resources in a Game and logs the changes."""
        game = self._get_game()
        if xp:
            game.xp += xp
            self._check_and_update_level()
        if cash:
            game.cash += cash
        if wood:
            game.wood += wood
        if stone:
            game.stone += stone
        if metal: 
            game.metal += metal
            
        resource_log = ResourceLog(game_id=self.game_id, 
                                xp=xp,
                                cash=cash,
                                wood=wood,
                                stone=stone,
                                metal=metal,
                                source=source)
        db.session.add(resource_log)
        db.session.commit()

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
        level_factor = 1.1
        return floor(base_xp * (level_factor ** (level + 1)))

    
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
    
    
## Quest Manager
## Quest Manager
class QuestManager:
    def __init__(self, game_id, notifier=FlashNotifier()) -> None:
        self.game_id = game_id
        self.notifier = notifier


    def update_quest_prerequisite_progress(self):
        # Get all quests for the game
        quests = QuestProgress.query.filter_by(game_id=self.game_id).all()
        new_quest_available = False
        quests_to_activate = []

        for quest in quests:
            if not quest.quest_active and self._check_prerequisites_met(quest.quest_id):
                quest.quest_active = True
                quests_to_activate.append(quest)
                new_quest_available = True

        if quests_to_activate:
            db.session.bulk_save_objects(quests_to_activate)
            db.session.commit()

        if new_quest_available:
            if len(quests_to_activate) == 1: 
                self.notifier.notify(f"{len(quests_to_activate)} new quest Available!")
            else:
                self.notifier.notify(f"{len(quests_to_activate)} new quests Available!")

    def _check_prerequisites_met(self, quest_id):
        # Get all prerequisites for the quest
        prerequisites = QuestPrerequisites.query.filter_by(quest_id=quest_id).all()
        
        for prerequisite in prerequisites:
            quest = QuestProgress.query.filter_by(game_id=self.game_id, quest_id=prerequisite.prerequisite_id).first()

            # Check if quest is completed
            if quest is None or not quest.quest_completed:
                return False

            if quest.game.level < prerequisite.game_level:
                return False

            # update quest prerequisite progress
            print(quest.id)
            ## TODO: This is not working as intended - NEEDS TO ONLY UPDATE THE RELEVANT PREREQUISITE FOR THE USER/GAME - Currently updating all
            prerequisite_progress = QuestPreRequisitesProgress.query.filter_by(quest_prerequisite_id=prerequisite.prerequisite_id
                                                                               ).all()
            
            
            print(prerequisite_progress)
            for progress in prerequisite_progress:
                if progress:
                    progress.prerequisite_completed = True
        
        db.session.commit()

        return True

    def update_quest_requirement_progress(self):
        quests = QuestProgress.query.filter_by(game_id=self.game_id, quest_completed=False, quest_active=True).all()
        requirement_met = False
        quests_to_update = []
        requirements_to_update = []

        # Loop through all quests and check if requirements are met
        for quest in quests:
            requirements = QuestRequirementProgress.query.filter_by(quest_progress_id=quest.id).all()
            quest_req_met = True

            for requirement in requirements:
                if quest.game.level < requirement.quest_requirement.game_level_required:
                    quest_req_met = False
                elif quest.game.cash < requirement.quest_requirement.cash_required:
                    quest_req_met = False
                elif quest.game.wood < requirement.quest_requirement.wood_required:
                    quest_req_met = False
                elif quest.game.stone < requirement.quest_requirement.stone_required:
                    quest_req_met = False
                elif quest.game.metal < requirement.quest_requirement.metal_required:
                    quest_req_met = False
                elif requirement.quest_requirement.building_required is not None:
                    building = BuildingProgress.query.filter_by(game_id=self.game_id, building_id=requirement.quest_requirement.building_required).first()
                    if building is None or building.building_level < requirement.quest_requirement.building_level_required:
                        quest_req_met = False

                if not quest_req_met:
                    break

            if quest_req_met:
                for requirement in requirements:
                    requirement.requirement_completed = True
                    requirements_to_update.append(requirement)
                quest.quest_progress = 100
                quests_to_update.append(quest)
                requirement_met = True

        if requirements_to_update:
            db.session.bulk_save_objects(requirements_to_update)
        if quests_to_update:
            db.session.bulk_save_objects(quests_to_update)
        if requirements_to_update or quests_to_update:
            db.session.commit()

        if requirement_met:
            if len(quests_to_update) == 1:
                self.notifier.notify(f"{len(quests_to_update)} quest has been completed")
            else:
                self.notifier.notify(f"{len(quests_to_update)} quests have been completed")

               


                   

## Game Quest Service
# Class to action against the QuestProgress instance
class QuestService:
    ''' Service for managing quest specific actions '''
    def __init__(self, quest_progress_id: int, notifier=FlashNotifier()) -> None:
        self.quest_progress_id = quest_progress_id
        self.quest = self._get_quest_progress()
        self.quest_manager = QuestManager(self.quest.game_id)
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
        
        # activate all available quests where this quest is a pre-requisite and not already active, also check if they are ready to be activated
        self.quest_manager.update_quest_prerequisite_progress()
        self.quest_manager.update_quest_requirement_progress()
        
        
        self.notifier.notify(f"Rewards collected")

    def add_progress(self, progress: int):
        if progress < 0:
            raise ValueError("Progress must be a positive number.")
        self.quest.quest_progress += progress
        if self.quest.quest_progress >= 100:
            self.complete_quest()
        else:
            self.notifier.notify(f"Quest Progress: {self.quest.quest_progress}%")
                
    def collect_rewards(self):
        rewards = QuestRewards.query.filter_by(quest_id=self.quest.quest_id).first()
        if rewards is None:
            return
        
        game_service = GameService(self.quest.game_id)
        game_service.update_resources(xp=rewards.quest_reward_xp,
                                      cash=rewards.quest_reward_cash,
                                      wood=rewards.quest_reward_wood,
                                      stone=rewards.quest_reward_stone,
                                      metal=rewards.quest_reward_metal,
                                      source="Quest Rewards. Quest: " + str(self.quest.quest_id))
 
        
## GameBuildingService
# Class to action against the GameBuilding instance
class GameBuildingService:
    ''' Service for managing game specific building actions '''
    def __init__(self, building_progress_id: int, notifier=FlashNotifier()) -> None:
        self.building_progress_id = building_progress_id
        self.building = self._get_building_progress()
        self.quest_manager = QuestManager(self.building.game_id)
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
        game_service = GameService(self.building.game_id)
        game_service.update_resources(xp=self.building.accrued_xp,
                                        cash=self.building.accrued_cash,
                                        wood=self.building.accrued_wood,
                                        stone=self.building.accrued_stone,
                                        metal=self.building.accrued_metal,
                                        source="Building Collection. Building: " + str(self.building.building_id))
        
        # Update building progress
        self.start_accrual()
        
        self.quest_manager.update_quest_prerequisite_progress()
        self.quest_manager.update_quest_requirement_progress()
        
        db.session.commit()


    def show_accrual_time(self):
        if self.building.accrual_start_time is None:
            return False
        else:
            time_difference = datetime.now(timezone.utc) - self.building.accrual_start_time
            hours = time_difference.total_seconds() / 3600
            return hours
        
    def calculate_accrued_resources(self):
        minutes = self.calculate_time_to_collect()

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
            self.notifier.notify("Building is already at max level.")
            return
        
        # Check if user has enough resources to upgrade
        if not self.check_upgrade_requirements():
            self.notifier.notify("Insufficient resources to upgrade building.")
            return
        
        # Calculate required resources
        required_resources = self._calculate_required_resources()

        # Update Resources
        game_service = GameService(self.building.game_id)
        game_service.update_resources(xp=10,
                                      cash= -required_resources['cash'],
                                      wood= -required_resources['wood'],
                                      stone= -required_resources['stone'],
                                      metal= -required_resources['metal'],
                                      source="Building Upgrade. Building: " + str(self.building.building_id))
            
        # Check if building level is 0 and set rate
        self.initialize_building_production()

        # Collect current resources
        self.collect_resources()
        
        # Upgrade building
        self._update_resource_per_minute()

        # Increment building level
        self.building.building_level += 1
        
        # Check quest prerequisites
        self.quest_manager.update_quest_prerequisite_progress()
        self.quest_manager.update_quest_requirement_progress()

        # Commit cahnges
        db.session.commit()
        self.notifier.notify(f"Building upgraded to level {self.building.building_level}.")

        
    def initialize_building_production(self):
        if self.building.building_level == 0:
            self._set_base_production_rates()
            self.building.building_active = True
        
    def _set_base_production_rates(self):
        self.building.cash_per_minute = self.building.building.base_cash_per_minute
        self.building.xp_per_minute = self.building.building.base_xp_per_minute
        self.building.wood_per_minute = self.building.building.base_wood_per_minute
        self.building.stone_per_minute = self.building.building.base_stone_per_minute
        self.building.metal_per_minute = self.building.building.base_metal_per_minute
    

    def _update_resource_per_minute(self):
        upgrade_factor = 1.1
        self.building.cash_per_minute = round(self.building.cash_per_minute * upgrade_factor)
        self.building.xp_per_minute = round(self.building.xp_per_minute * upgrade_factor)
        self.building.wood_per_minute = round(self.building.wood_per_minute * upgrade_factor)
        self.building.stone_per_minute = round(self.building.stone_per_minute * upgrade_factor)
        self.building.metal_per_minute = round(self.building.metal_per_minute * upgrade_factor)
            
    def check_resources_to_collect(self):
        return self.building.accrual_start_time is not None
    
    # Get accrual start time
    def get_accrual_start_time(self):
        return self.building.accrual_start_time
    
    def calculate_time_to_collect(self):

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
        minutes = round(time_difference.total_seconds() / 60)  # Calculate minutes for finer detail

        # check if max accrual duration is reached
        if minutes > self.building.max_accrual_duration:
            minutes = round(self.building.max_accrual_duration)

        return minutes