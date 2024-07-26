from flask import render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user
from app.models import User, db, Game, Inventory
from app.models import InventoryUser, InventoryItems, InventoryType
from app.models import Quest, QuestProgress, QuestType, QuestRewards, RewardItemAssociation
from app.models import BuildingProgress, Buildings
from app.game.forms import NewGameForm, LoadGameForm, AddXPForm, AddCashForm, AddResourcesForm, CollectResourcesForm, UpgradeBuildingForm, CompleteQuestForm
from app.game.game_logic import GameService, GameCreation, GameBuildingService, QuestService
import sqlalchemy as sa

from app.game import bp

 


@bp.route('/startmenu', methods=['GET', 'POST'])
@login_required
def startmenu():

    newgameform = NewGameForm()
    loadgameform = LoadGameForm()

    numberofgames = Game.query.filter_by(user_id=current_user.id).count()
       
    if request.method == 'POST' and newgameform.newgame_button.data:
        
        game_name = newgameform.game_name.data
        
        service = GameCreation(user_id=current_user.id, game_name=game_name)
        game = service.create_game()
        
        service.create_all_startup(game.id)
        db.session.commit()
        
        game_id = game.id
        
    
        return redirect(url_for('game.play', 
                                game_id=game_id))
    
    if request.method == 'POST' and loadgameform.loadgame_button.data:
        game_id = loadgameform.game_id.data
        current_user.activegame = game_id
        db.session.commit()
        return redirect(url_for('game.play', 
                                game_id=game_id))


    return render_template("game/startmenu.html", 
                           title='Start Menu', 
                           newgameform=newgameform,
                           loadgameform=loadgameform,
                           numberofgames=numberofgames)


## Route to display game play
@bp.route('/play/<game_id>', methods=['GET', 'POST'])
@login_required
def play(game_id):
    # validate user
    if not current_user.is_admin() and current_user.activegame != int(game_id):
        return redirect(url_for('admin.not_admin'))

    game = g.game  # Optimized query
    if not game:
        flash('Game not found.', 'error')
        return redirect(url_for('main.index'))

    resourceform = AddResourcesForm()
    service = GameService(game_id=game_id)

    if request.method == 'POST' and resourceform.add_button.data:
        service.update_resources(xp=resourceform.xp.data,
                                    cash=resourceform.cash.data,
                                    wood=resourceform.wood.data,
                                    stone=resourceform.stone.data,
                                    metal=resourceform.metal.data,
                                    source="Manual Resource Form")
        flash('Resources Added')
        
        return redirect(url_for('game.play', game_id=game_id))

    return render_template("game/play.html", game=game, resourceform=resourceform)
    


# Route to display quests
@bp.route('/building_quests/<building_progress_id>', methods=['GET', 'POST'])
@login_required
def building_quests(building_progress_id):
        
    building_progress = BuildingProgress.query.get(building_progress_id)
    if not building_progress:
        flash('Building progress not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if current user is admin or the current user viewing their own profile
    if not current_user.is_admin() and current_user.activegame != int(building_progress.game_id):
        return redirect(url_for('admin.not_admin'))
    
    game = g.game  # Optimized query
    if not game:
        flash('Game not found.', 'error')
        return redirect(url_for('main.index'))

    if not current_user.is_admin() and current_user.activegame != int(game.id):
        return redirect(url_for('admin.not_admin'))
    
    # Forms
    completequestform = CompleteQuestForm(request.form)
    
    quests = QuestProgress.query.filter_by(game_id=game.id).all()
    # Categorize quests in Python to reduce database load
    active_quests = [q for q in quests if q.quest_active and not q.quest_completed]
    completed_quests = [q for q in quests if q.quest_completed]
    inactive_quests = [q for q in quests if not q.quest_active and not q.quest_completed]

    if request.method == 'POST' and completequestform.validate_on_submit():
        quest_id = completequestform.quest_id.data
        service = QuestService(quest_progress_id=quest_id)
        service.complete_quest()
        db.session.commit()
        return redirect(url_for('game.building_quests', building_progress_id=building_progress_id))

    return render_template("game/buildings/building_quests.html", 
                           title='Quests',
                           game=game,
                           quests=quests,
                           active_quests=active_quests,
                           completed_quests=completed_quests,
                           inactive_quests=inactive_quests,
                           completequestform=completequestform)

# Route to display inventory
@bp.route('/building_inventory/<game_id>', methods=['GET', 'POST'])
@login_required
def building_inventory(game_id):
    # Query for game inventory items
    game = g.game  # Optimized query
    userinventories = InventoryUser.query.filter_by(game_id=game_id).all()
    
    return render_template("game/buildings/building_inventory.html",
                           title='Inventory',
                            game=game,
                            userinventories=userinventories)


# Route to display resource buildings
@bp.route('/building_resource/<building_progress_id>', methods=['GET', 'POST'])
@login_required
def building_resource(building_progress_id):
    
    # Query for game inventory items
    building_progress = BuildingProgress.query.filter_by(id=building_progress_id).first()
    game = g.game  # Optimized query
    
    if not current_user.is_admin() and current_user.activegame != int(game.id):
        return redirect(url_for('admin.not_admin'))
    


    # Forms
    collectresourcesform = CollectResourcesForm()
    upgradebuildingform = UpgradeBuildingForm()

    # calculate accrued resources:
    buildingservice = GameBuildingService(building_progress_id=building_progress_id)
    buildingservice.calculate_accrued_resources()


    # Calculate required resources
    required_resources = buildingservice._calculate_required_resources()

    # Handle POST requests
    if request.method == 'POST' and collectresourcesform.collect_button.data:
        buildingservice.collect_resources()
        
        return redirect(url_for('game.building_resource', building_progress_id=building_progress_id))

    if request.method == 'POST' and upgradebuildingform.upgrade_button.data:
        buildingservice.upgrade_building()

        return redirect(url_for('game.building_resource', building_progress_id=building_progress_id))


    return render_template("game/buildings/building_resource.html",
                           title=building_progress.building.building_name,
                            game=game,
                            building_progress=building_progress,
                            buildingservice=buildingservice,
                            collectresourcesform=collectresourcesform,
                            upgradebuildingform=upgradebuildingform,
                            required_resources=required_resources)

