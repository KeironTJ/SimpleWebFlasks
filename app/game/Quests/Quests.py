from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import db, Role, User
from app.models import Game
from app.models import Quest, QuestType, QuestRewards,RewardItemAssociation, QuestProgress
from app.models import Item, Inventory, InventoryItems, InventoryType, InventoryUser
from app.models import ResourceLog
from app.models import Buildings, BuildingProgress, BuildingType
from app.game.game_logic import GameCreation, GameService, PrintNotifier, GameBuildingService

app = create_app()
app_context = app.app_context()
app_context.push()


## QUESTS
# Create Quest Types
def create_QuestTypes():
    quest_type1 = QuestType(quest_type_name="Main Quest", quest_type_description="Main Story Progression Quests")
    quest_type2 = QuestType(quest_type_name="Building Quest", quest_type_description="Building Progression Quests")
    quest_type3 = QuestType(quest_type_name="Level Quest", quest_type_description="Levelling Progression Quests")
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
            self.quest = Quest(quest_name=self.quest_name, quest_description=self.quest_description, quest_type_id=self.quest_type_id)
            db.session.add(self.quest)
            db.session.commit()
            print("Quest Created: ", self.quest_name)
            return self.quest
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest: {self.quest_name} {e}")

    def create_quest_rewards(self, xp, cash, wood, stone, metal):
        try:
            quest_reward = QuestRewards(quest_id=self.quest.id, 
                                        quest_reward_xp=xp, 
                                        quest_reward_cash=cash, 
                                        quest_reward_wood=wood, 
                                        quest_reward_stone=stone, 
                                        quest_reward_metal=metal)
            db.session.add(quest_reward)
            db.session.commit()
            print("Quest Reward Created: ", self.quest_name)
            return quest_reward
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest reward: {self.quest_name} {e}")

    def create_reward_item_associate(self, reward, item_id, quantity):
        try:
            reward_item = RewardItemAssociation(reward=reward, 
                                                item_id=item_id, 
                                                quantity=quantity)
            db.session.add(reward_item)
            db.session.commit()
            print("Reward Item Associated: ", self.quest_name)
            return reward_item
        except Exception as e:
            db.session.rollback()
            print(f"Failed to associate reward item: {self.quest_name} {e}")

    def create_full_quest(self, rewards_info, items_info):
        try:
            self.create_quest()
            rewards = self.create_quest_rewards(rewards_info['xp'], 
                                                rewards_info['cash'], 
                                                rewards_info['wood'], 
                                                rewards_info['stone'], 
                                                rewards_info['metal'])
            for item in items_info:
                self.create_reward_item_associate(rewards, 
                                                  item['item_id'], 
                                                  item['quantity'])
            print("Full Quest Created: ", self.quest_name)
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create full quest: {self.quest_name} {e}")
            
# Create Quests
def create_quests():
    # Quest 1
    quest1 = QuestCreator(quest_name="Welcome", 
                          quest_description="Welcome to Outline!", 
                          quest_type_id=1)
    quest1.create_full_quest(
        rewards_info={'xp': 110, 
                      'cash': 1000, 
                      'wood': 0, 
                      'stone': 0, 
                      'metal': 0},
        items_info=[{'item_id': 1, 'quantity': 1},
                    {'item_id': 2, 'quantity': 1}])
   
    # Quest 2
    quest2 = QuestCreator(quest_name="First Building", 
                          quest_description="Build your first building", 
                          quest_type_id=2)
    quest2.create_full_quest(
        rewards_info={'xp': 50, 
                      'cash': 1000, 
                      'wood': 0, 
                      'stone': 0, 
                      'metal': 0},
        items_info=[])
    


def delete_quest_data():
    # Delete Game Quest Data
    db.session.query(QuestProgress).delete()
    db.session.query(QuestRewards).delete()
    db.session.query(RewardItemAssociation).delete() 
    db.session.query(QuestType).delete()
    db.session.query(Quest).delete()
    


# Create quests, rewards, and reward item associations
'''
delete_quest_data()

create_QuestTypes()

create_quests()
'''
# python -m app.game.Quests.Quests