from app.game.context_processor import FlashNotifier
from app.game.quests.quest_services import QuestManager
from app.models import HeroProgress


## Hero Service
class HeroService:
    ''' Service for managing hero specific actions '''
    def __init__(self, hero_progress_id: int, notifier=FlashNotifier()) -> None:
        self.hero_progress_id = hero_progress_id
        self.hero = self._get_hero_progress()
        self.quest_manager = QuestManager(self.building.game_id)
        self.notifier = notifier

    def _get_hero_progress(self) -> HeroProgress:
        """Retrieves the BuildingProgress instance or raises an error if not found."""
        hero = HeroProgress.query.get(self.hero_progress_id)
        if hero is None:
            raise ValueError(f"BuildingProgress with ID {self.building_progress_id} not found.")
        return hero 
    

    





