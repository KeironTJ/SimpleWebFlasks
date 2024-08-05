from app import create_app
import os
import subprocess
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.sql import text
from app.models import QuestPrerequisites, db, Role, User
from app.models import Game
from app.models import Quest, QuestType, QuestRewards,RewardItemAssociation, QuestProgress, QuestPrerequisites, QuestPreRequisitesProgress, QuestRequirementProgress, QuestRequirements
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

    def create_quest_rewards(self, quest_id, xp=0, cash=0, wood=0, stone=0, metal=0):
        try:
            quest_reward = QuestRewards(quest_id=quest_id, 
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
            
    def _create_quest_prerequisites(self, quest_id, prerequisite_id, game_level=0):
        try:
            quest_prerequisite = QuestPrerequisites(quest_id=quest_id, prerequisite_id=prerequisite_id, game_level=game_level)
            db.session.add(quest_prerequisite)
            db.session.commit()
            print("Quest Prerequisite Created: ", self.quest_name)
            return quest_prerequisite
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest prerequisite: {self.quest_name} {e}")
            
    def _create_quest_requirements(self, quest_id, game_level=0, cash=0, wood=0, stone=0, metal=0, building_required=None, building_level_required=None):
        try:
            quest_requirement = QuestRequirements(quest_id=quest_id, 
                                                  game_level_required=game_level, 
                                                  cash_required=cash, 
                                                  wood_required=wood, 
                                                  stone_required=stone, 
                                                  metal_required=metal,
                                                  building_required=building_required,
                                                  building_level_required=building_level_required)
            db.session.add(quest_requirement)
            db.session.commit()
            print("Quest Requirement Created: ", self.quest_name)
            return quest_requirement
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create quest requirement: {self.quest_name} {e}")

    def _create_reward_item_associate(self, reward, item_id, quantity):
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

    # Method to create a full quest, including rewards, prerequisites, and requirements
    def create_full_quest(self, rewards=None, prerequisites=None, requirements=None, reward_items=None):
        self.create_quest()
        
        if rewards:
            for rewards in rewards:
                self.create_quest_rewards(self.quest.id, **rewards)
        
        if prerequisites:
            for prerequisite in prerequisites:
                self._create_quest_prerequisites(self.quest.id, **prerequisite)
        
        if requirements:
            for requirement in requirements:
                self._create_quest_requirements(self.quest.id, **requirement)
        
        if reward_items:
            for item in reward_items:
                self._create_reward_item_associate(self.quest.id, item['item_id'], item['quantity'])
            
        print("Quest Created: ", self.quest_name)
        
        return self.quest


    
 
 ### Quests
        
# Create Quests
def create_quests():
    # Opening Quest
    mainquest1 = QuestCreator(quest_name="The Beginning", quest_description="Start your journey", quest_type_id=1)
    mainquest1.create_full_quest(
        rewards=[{'xp': 110, 'cash': 1000, 'wood': 0, 'stone': 0, 'metal': 0}],
        prerequisites=[{'prerequisite_id': 0, 'game_level': 0}], 
        requirements=[{'game_level': 0, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0}], 
        reward_items=[]
    )
    
    # Building Quests
    buildquest1 = QuestCreator(quest_name="Build a Farm", quest_description="Build your first farm", quest_type_id=2)
    buildquest1.create_full_quest(
        rewards=[{'xp': 20, 'cash': 500, 'wood': 50, 'stone': 0, 'metal': 0}],
        prerequisites=[{'prerequisite_id': 1, 'game_level': 0}], 
        requirements=[{'game_level': 0, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0, 'building_required': 3, 'building_level_required': 1}], 
        reward_items=[]
    )
    
    buildquest2 = QuestCreator(quest_name="Build a Lumber Mill", quest_description="Build your first lumber mill", quest_type_id=2)
    buildquest2.create_full_quest(
        rewards=[{'xp': 20, 'cash': 500, 'wood': 50, 'stone': 0, 'metal': 0}],
        prerequisites=[{'prerequisite_id': 2, 'game_level': 0}], 
        requirements=[{'game_level': 0, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0, 'building_required': 4, 'building_level_required': 1}], 
        reward_items=[]
    )
    
    buildquest3 = QuestCreator(quest_name="Build a Mine", quest_description="Build your first mine", quest_type_id=2)
    buildquest3.create_full_quest(
        rewards=[{'xp': 20, 'cash': 500, 'wood': 50, 'stone': 25, 'metal': 0}],
        prerequisites=[{'prerequisite_id': 3, 'game_level': 0}], 
        requirements=[{'game_level': 0, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0, 'building_required': 5, 'building_level_required': 1}], 
        reward_items=[]
    )
    
    buildquest4 = QuestCreator(quest_name="Build a Forge", quest_description="Build your first forge", quest_type_id=2)
    buildquest4.create_full_quest(
        rewards=[{'xp': 20, 'cash': 500, 'wood': 50, 'stone': 25, 'metal': 10}],
        prerequisites=[{'prerequisite_id': 4, 'game_level': 0}], 
        requirements=[{'game_level': 0, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0, 'building_required': 6, 'building_level_required': 1}], 
        reward_items=[]
    )
    

    
    # Level Quests
    levelquest1 = QuestCreator(quest_name="Level Up 1", quest_description="Reach Level 5", quest_type_id=3)
    levelquest1.create_full_quest(
        rewards=[{'xp': 20, 'cash': 200, 'wood': 30, 'stone': 10, 'metal': 5}],
        prerequisites=[{'prerequisite_id': 2, 'game_level': 0}], 
        requirements=[{'game_level': 5, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0}], 
        reward_items=[]
    )
    
    levelquest2 = QuestCreator(quest_name="Level Up 2", quest_description="Reach Level 10", quest_type_id=3)
    levelquest2.create_full_quest(
        rewards=[{'xp': 25, 'cash': 250, 'wood': 50, 'stone': 25, 'metal': 10}],
        prerequisites=[{'prerequisite_id': 3, 'game_level': 0}], 
        requirements=[{'game_level': 10, 'cash': 0, 'wood': 0, 'stone': 0, 'metal': 0}], 
        reward_items=[]
    )

    

   
def delete_quest_data():
    # Delete Game Quest Data
    
    db.session.query(QuestPreRequisitesProgress).delete()
    db.session.query(QuestPrerequisites).delete()

    db.session.query(QuestRequirementProgress).delete()
    db.session.query(QuestRequirements).delete()
    
    db.session.query(QuestProgress).delete()
    db.session.query(QuestRewards).delete()
    db.session.query(RewardItemAssociation).delete() 
    db.session.query(Quest).delete()
    
    db.session.query(QuestType).delete()
    


# Create quests, rewards, and reward item associations
'''
delete_quest_data()

create_QuestTypes()

create_quests()
'''
# python -m app.game.Quests.Quests