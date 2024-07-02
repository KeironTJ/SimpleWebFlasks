from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, db, TestGame
from app.testgame.forms import NewGameForm, LoadGameForm
import sqlalchemy as sa

from app.testgame import bp

@bp.route('/tg_startmenu', methods=['GET', 'POST'])
@login_required
def tg_startmenu():

    newgameform = NewGameForm()
    loadgameform = LoadGameForm()

    available_games = TestGame.query.filter_by(user_id=current_user.id).all()
        
    if request.method == 'POST' and newgameform.newgame_button.data:
        new_game = TestGame(user_id=current_user.id, game_name=newgameform.game_name.data)
        db.session.add(new_game)
        db.session.commit()
        flash('New Game Created')
        return redirect(url_for('testgame.tg_startmenu'))
    
    if request.method == 'POST' and loadgameform.loadgame_button.data:
        game_id = loadgameform.game_id.data
        return redirect(url_for('testgame.tg_play', game_id=game_id))


    return render_template("testgame/tg_startmenu.html", 
                           title='Test Game - Start Menu', 
                           newgameform=newgameform,
                           loadgameform=loadgameform)


##Game Instance
@bp.route('/tgplay/<game_id>', methods=['GET', 'POST'])
@login_required
def tg_play(game_id): 

    game = TestGame.query.filter_by(id=game_id).first()

    
    return render_template("testgame/tg_play.html", 
                           title='Test Game - Play',
                           game=game)
    


