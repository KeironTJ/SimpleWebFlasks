from app.models import BuildingProgress
from app.game.Quests.QuestServices import QuestManager
from app.game.context_processor import FlashNotifier
from app.game.GameServices import GameService

from app.models import BuildingProgress
from datetime import datetime, timezone
from app import db

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
    


