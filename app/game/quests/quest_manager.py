from app.models import QuestProgress, QuestPrerequisites, QuestPreRequisitesProgress, QuestRequirementProgress
from app.models import BuildingProgress
from app import db
from app.game.context_processor import FlashNotifier

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
            if not quest.quest_active and self._check_prerequisites_met(quest.id):
                quest.quest_active = True
                quests_to_activate.append(quest)
                new_quest_available = True

        if quests_to_activate:
            db.session.commit()

        if new_quest_available:
            if len(quests_to_activate) == 1: 
                self.notifier.notify(f"{len(quests_to_activate)} new quest Available!")
            else:
                self.notifier.notify(f"{len(quests_to_activate)} new quests Available!")


    def _check_prerequisites_met(self, quest_progress_id):

        # Get all quests prerequisites progress
        prerequisites_progress = QuestPreRequisitesProgress.query.filter_by(quest_progress_id=quest_progress_id).all()
        print("Prerequisites Progress", prerequisites_progress)

        #Get all quests progress
        for progress in prerequisites_progress:
            # Query the prerequisite quests
            prerequisite = QuestPrerequisites.query.filter_by(id=progress.quest_prerequisite_id).first()
            
            # Check if the prerequisite quest is completed
            prerequisite_quest = QuestProgress.query.filter_by(game_id=self.game_id, quest_id=prerequisite.prerequisite_id).first()
            if prerequisite_quest is None or not prerequisite_quest.quest_completed:
                return False
            
            # Check if the game level is met
            if prerequisite_quest.game.level < prerequisite.game_level:
                return False
            
            # Check if the prerequisite is already completed
            if progress.prerequisite_completed:
                return False
            
            # Set the prerequisite as completed
            progress.prerequisite_completed = True

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
            return False

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

    def update_quests(self):
        self.update_quest_prerequisite_progress()
        self.update_quest_requirement_progress()
