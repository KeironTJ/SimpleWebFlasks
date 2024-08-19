from math import floor

from app import db
from app.game.context_processor import FlashNotifier
from app.models import (
    BuildingProgress, Buildings, Game, Hero, HeroProgress, Inventory, InventoryUser,
    Quest, QuestProgress, QuestPrerequisites, QuestPreRequisitesProgress,
    QuestRequirementProgress, QuestRequirements, ResourceLog, User
)


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
            self.assign_quest_requirements(quest_progress.id)
            
    def assign_quest_pre_requisites(self, quest_progress_id: int) -> None:
        """Assigns all quest pre-requisites to a QuestProgress."""
        quest_progress = QuestProgress.query.get(quest_progress_id)
        prerequisites = QuestPrerequisites.query.filter_by(quest_id=quest_progress.quest_id).all()
        for prerequisite in prerequisites:
            prerequisite_progress = QuestPreRequisitesProgress(quest_progress_id=quest_progress_id,
                                                               quest_prerequisite_id=prerequisite.id)
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

    def assign_all_heroes(self, game_id: int) -> None:
        """Assigns all heroes to a Game."""
        heroes = Hero.query.all()
        for hero in heroes:
            new_hero = HeroProgress(game_id=self.game_id,
                                    hero_id=hero.id)
            db.session.add(new_hero)
            

            
        
    # function to create all startup items for the Game instance
    def create_all_startup(self, game_id: int) -> None:
        # Make game active
        self.set_active_game(game_id)
        """Creates all startup items for a Game."""
        self.assign_all_quests(game_id)
        self.assign_all_buildings(game_id)
        self.assign_all_inventories(game_id)
        self.assign_all_heroes(game_id)
        db.session.commit()



        
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

    def assign_hero(self, hero_id: int) -> None:
        ''' Assings a hero to the game '''
        hero = HeroProgress(game_id = self.game_id,
                            hero_id = hero_id)
        db.session.add(hero)
        db.session.commit()

    ## Helper functions
    def _get_game(self) -> Game:
        """Retrieves the Game instance or raises an error if not found."""
        game = Game.query.get(self.game_id)
        if game is None:
            raise ValueError(f"Game with ID {self.game_id} not found.")
        return game