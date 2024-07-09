from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, db, TestGame, TestGameInventory, TestGameInventoryUser, TestGameInventoryItems, TestGameInventoryType
from app.models import TestGameQuest, TestGameQuestProgress, TestGameQuestType, TestGameQuestRewards, RewardItemAssociation
from app.models import TestGameBuildingProgress, TestGameBuildings
from app.testgame.forms import NewGameForm, LoadGameForm, AddXPForm, AddCashForm
from app.testgame.game_logic import GameService, GameCreation, GameQuery
import sqlalchemy as sa

from app.testgame import bp

@bp.route('/tg_startmenu', methods=['GET', 'POST'])
@login_required
def tg_startmenu():

    newgameform = NewGameForm()
    loadgameform = LoadGameForm()

    numberofgames = TestGame.query.filter_by(user_id=current_user.id).count()
       
    if request.method == 'POST' and newgameform.newgame_button.data:
        
        game_name = newgameform.game_name.data
        
        service = GameCreation(user_id=current_user.id, game_name=game_name)
        game = service.create_game()
        db.session.commit()
        
        service.set_active_game(game.id)
        service.assign_all_quests(game.id)
        db.session.commit()
        
        game_id = game.id
        
        

        return redirect(url_for('testgame.tg_play', game_id=game_id))
    
    if request.method == 'POST' and loadgameform.loadgame_button.data:
        game_id = loadgameform.game_id.data
        current_user.activetestgame = game_id
        db.session.commit()
        return redirect(url_for('testgame.tg_play', game_id=game_id))


    return render_template("testgame/tg_startmenu.html", 
                           title='Test Game - Start Menu', 
                           newgameform=newgameform,
                           loadgameform=loadgameform,
                           numberofgames=numberofgames)


##Game Instance
@bp.route('/tgplay/<game_id>', methods=['GET', 'POST'])
@login_required
def tg_play(game_id): 

    # Check if current user is admin or the current user viewing their own profile
    if not current_user.is_admin() and current_user.activetestgame != int(game_id):
        return redirect(url_for('admin.not_admin'))

    # Forms
    addxpform = AddXPForm()
    addcashform = AddCashForm()

    

    # Database Queries
    game = TestGame.query.filter_by(id=game_id).first()
    

    if request.method == 'POST' and addxpform.addxp_button.data:
        xp = addxpform.xp.data
        service = GameService(test_game_id=game_id)
        service.add_xp(xp)
        db.session.commit()
        flash(f'{xp} xp added to {game.game_name}')

    if request.method == 'POST' and addcashform.addcash_button.data:
        cash = addcashform.cash.data
        service = GameService(test_game_id=game_id)
        service.add_cash(cash)
        db.session.commit()
        flash(f'{cash} cash added to {game.game_name}')



    return render_template("testgame/tg_play.html", 
                           title='Test Game - Play',
                           game=game,
                           addxpform=addxpform,
                           addcashform=addcashform,
                           )
    


# Route to display quests
@bp.route('/tg_building_quests/<game_id>', methods=['GET', 'POST'])
@login_required
def tg_building_quests(game_id):
    
    # Query for testgame quest progress
    game = TestGame.query.filter_by(id=game_id).first()
    quests = TestGameQuestProgress.query.filter_by(game_id=game_id).all()
    
    return render_template("testgame/buildings/tg_building_quests.html", 
                           title='Test Game - Quests',
                           game=game,
                           quests=quests)

# Route to display inventory
@bp.route('/tg_building_inventory/<game_id>', methods=['GET', 'POST'])
@login_required
def tg_building_inventory(game_id):
    # Query for testgame inventory items
    game = TestGame.query.filter_by(id=game_id).first()
    userinventories = TestGameInventoryUser.query.filter_by(game_id=game_id).all()
    
    return render_template("testgame/buildings/tg_building_inventory.html",
                           title='Test Game - Inventory',
                            game=game,
                            userinventories=userinventories)


# Route to display farm
@bp.route('/tg_building_farm/<game_id>', methods=['GET', 'POST'])
@login_required
def tg_building_farm(game_id):
    # Query for testgame inventory items
    game = TestGame.query.filter_by(id=game_id).first()

    
    return render_template("testgame/buildings/tg_building_farm.html",
                           title='Test Game - Farm',
                            game=game)