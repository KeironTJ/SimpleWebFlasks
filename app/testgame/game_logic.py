from app.models import TestGame, TestGameXPLog, TestGameCashLog
from app import db



class GameService:
    """Service for adding XP and cash to a TestGame and logging the operations."""
    
    def __init__(self, user_id: int, test_game_id: int) -> None:
        self.user_id = user_id
        self.test_game_id = test_game_id

    def add_xp(self, xp: int) -> None:
        """Adds XP to a TestGame and logs the addition."""
        test_game = self._get_test_game()
        test_game.xp += xp
        xp_log = TestGameXPLog(xp=xp, user_id=self.user_id, test_game_id=self.test_game_id)
        db.session.add(xp_log)

    def add_cash(self, cash: int) -> None:
        """Adds cash to a TestGame and logs the addition."""
        test_game = self._get_test_game()
        test_game.cash += cash
        cash_log = TestGameCashLog(cash=cash, user_id=self.user_id, test_game_id=self.test_game_id)
        db.session.add(cash_log)

    def _get_test_game(self) -> TestGame:
        """Retrieves the TestGame instance or raises an error if not found."""
        test_game = TestGame.query.get(self.test_game_id)
        if test_game is None:
            raise ValueError(f"TestGame with ID {self.test_game_id} not found.")
        return test_game


