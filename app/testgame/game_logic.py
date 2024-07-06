from app.models import User, TestGame, TestGameQuest, TestGameQuestProgress
from app.models import TestGame, TestGameXPLog, TestGameCashLog
from datetime import datetime
from app import db

class GameCreation:
    """Service for creating a new TestGame instance."""
    
    def __init__(self, user_id: int, game_name: str) -> None:
        self.user_id = user_id
        self.game_name = game_name

    def create_game(self) -> TestGame:
        """Creates a new TestGame instance."""
        test_game = TestGame(user_id=self.user_id, game_name=self.game_name)
        db.session.add(test_game)
        return test_game

    def set_active_game(self, game_id: int) -> None:
        """Sets the active game for the user."""
        user = User.query.get(self.user_id)
        user.activetestgame = game_id

    def assign_all_quests(self, game_id: int) -> None:
        """Assigns all quests to a TestGame."""
        quests = TestGameQuest.query.all()
        for quest in quests:
            quest_progress = TestGameQuestProgress(game_id=game_id, quest_id=quest.id)
            db.session.add(quest_progress)
    
    
        

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

    def _get_test_game(self) -> TestGame:
        """Retrieves the TestGame instance or raises an error if not found."""
        test_game = TestGame.query.get(self.test_game_id)
        if test_game is None:
            raise ValueError(f"TestGame with ID {self.test_game_id} not found.")
        return test_game
    
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


