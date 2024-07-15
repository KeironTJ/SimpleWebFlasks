from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User
from app.models import TestGame
from app.models import TestGameQuest, TestGameQuestType, TestGameQuestRewards,RewardItemAssociation, TestGameQuestProgress
from app.models import TestGameItem, TestGameInventory, TestGameInventoryItems, TestGameInventoryType, TestGameInventoryUser
from app.models import TestGameResourceLog
from app.models import TestGameBuildings, TestGameBuildingProgress, TestGameBuildingType
from app.testgame.game_logic import GameCreation, GameService, PrintNotifier, GameBuildingService

app = create_app()
app_context = app.app_context()
app_context.push()


## QUESTS
# Create Quest Types
def create_QuestTypes():
    quest_type1 = TestGameQuestType(quest_type_name="Main Quest", quest_type_description="Main Story Progression Quests")
    quest_type2 = TestGameQuestType(quest_type_name="Building Quest", quest_type_description="Building Progression Quests")
    quest_type3 = TestGameQuestType(quest_type_name="Level Quest", quest_type_description="Levelling Progression Quests")
    db.session.add(quest_type1)
    db.session.add(quest_type2)
    db.session.add(quest_type3)
    db.session.commit()
    print("Quest Types Created")
    
 # Quest Creator Class   
class QuestCreator:
    def __init__(self, quest_name, quest_description, quest_type_id):
        self.quest_name = quest_name
        self.quest_description = quest_description
        self.quest_type_id = quest_type_id
        self.quest = None  # Placeholder for the created quest object

    def create_quest(self):
        try:
            self.quest = TestGameQuest(quest_name=self.quest_name, quest_description=self.quest_description, quest_type_id=self.quest_type_id)
            db.session.add(self.quest)
            db.session.commit()
            print("Quest Created")
            return self.quest
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest: {e}")

    def create_quest_rewards(self, quest_reward_name, quest_reward_description, quest_reward_xp, quest_reward_cash):
        if self.quest is None:
            print("Quest must be created before adding rewards.")
            return
        try:
            quest_reward = TestGameQuestRewards(quest=self.quest, 
                                                quest_reward_name=quest_reward_name, 
                                                quest_reward_description=quest_reward_description, 
                                                quest_reward_xp=quest_reward_xp, 
                                                quest_reward_cash=quest_reward_cash)
            db.session.add(quest_reward)
            db.session.commit()
            print("Quest Reward Created")
            return quest_reward
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest reward: {e}")

    def create_reward_item_associate(self, reward, item_id, quantity):
        try:
            reward_item = RewardItemAssociation(reward=reward, 
                                                item_id=item_id, 
                                                quantity=quantity)
            db.session.add(reward_item)
            db.session.commit()
            print("Reward Item Associated")
            return reward_item
        except Exception as e:
            db.session.rollback()
            print(f"Failed to associate reward item: {e}")

    def create_full_quest(self, rewards_info, items_info):
        """
        Create a quest with rewards and associate items with those rewards.
        
        :param rewards_info: List of dictionaries with reward details.
        :param items_info: Dictionary mapping reward names to lists of item associations.
        """
        self.create_quest()
        for reward_info in rewards_info:
            reward = self.create_quest_rewards(**reward_info)
            for item_info in items_info.get(reward_info['quest_reward_name'], []):
                self.create_reward_item_associate(reward, **item_info)

# Example usage
Main_quest_1 = QuestCreator(quest_name="Main Quest 1", quest_description="Main Quest 1 Description", quest_type_id=1)
rewards_info = [
    {"quest_reward_name": "XP Reward", "quest_reward_description": "XP Reward Description", "quest_reward_xp": 100, "quest_reward_cash": 0},
    {"quest_reward_name": "Cash Reward", "quest_reward_description": "Cash Reward Description", "quest_reward_xp": 0, "quest_reward_cash": 100}
]
items_info = {
    "XP Reward": [
        {"item_id": 1, "quantity": 1},
        {"item_id": 2, "quantity": 2}
    ],
    "Cash Reward": [
        {"item_id": 3, "quantity": 3}
    ]
}


Main_quest_2 = QuestCreator(quest_name="Main Quest 2", quest_description="Main Quest 2 Description", quest_type_id=1)
rewards_info = [
    {"quest_reward_name": "XP Reward", "quest_reward_description": "XP Reward Description", "quest_reward_xp": 200, "quest_reward_cash": 0},
    {"quest_reward_name": "Cash Reward", "quest_reward_description": "Cash Reward Description", "quest_reward_xp": 0, "quest_reward_cash": 200}
]
items_info = {
    "XP Reward": [
        {"item_id": 1, "quantity": 2},
        {"item_id": 2, "quantity": 4}
    ],
    "Cash Reward": [
        {"item_id": 3, "quantity": 6}
    ]
}

def delete_quest_data():
    # Delete Game Quest Data
    db.session.query(TestGameQuestProgress).delete()
    db.session.query(TestGameQuestRewards).delete()
    db.session.query(RewardItemAssociation).delete() 
    db.session.query(TestGameQuestType).delete()
    db.session.query(TestGameQuest).delete()
    


# Create quests, rewards, and reward item associations
create_QuestTypes()
Main_quest_1.create_full_quest(rewards_info, items_info)
Main_quest_2.create_full_quest(rewards_info, items_info)