from datetime import datetime

from app.models import QuestProgress, QuestRewards
from app import db
from app.game.context_processor import FlashNotifier
from app.game.game_services import GameService
from app.game.quests.quest_manager import QuestManager


## Quest Service
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
        self.quest_manager.update_quests()
        
        
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
 
        
