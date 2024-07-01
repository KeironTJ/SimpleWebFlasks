from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from app.gtn.forms import GuessTheNumberForm, GuessTheNumberResetForm, GuessTheNumberSettingsForm
from app.models import User, GTNSettings, GTNHistory
import random
from app import db
from app.gtn import bp

# GUESS THE NUMBER GAME

# Helper Functions
# Reset the game session
def reset_game_session():
    session['ainumber'] = 0
    session['userguesses'] = []

# Initialize the game session
def initialise_game():
    gtnsettings = db.session.query(GTNSettings).filter_by(user_id=current_user.id).first()
    if 'ainumber' not in session or session['ainumber'] == 0:
        session['ainumber'] = random.randint(gtnsettings.startrange, gtnsettings.endrange)
    if 'userguesses' not in session:
        session['userguesses'] = []


@bp.route('/guessthenumberhome', methods=['GET', 'POST'])
@login_required
def guessthenumberhome():

    # Initialize forms
    gtnform = GuessTheNumberForm(request.form)
    gtnresetform = GuessTheNumberResetForm(request.form)
    
    # Initialize database queries
    gtnsettings = db.session.query(GTNSettings).filter_by(user_id=current_user.id).first()
    startrange = gtnsettings.startrange
    endrange = gtnsettings.endrange

    initialise_game()

    ainumber = session['ainumber']
    userguesses = session['userguesses']
    gamereply = ""

    # Process the Guess Form
    if request.method == 'POST' and 'submit_guess' in request.form and gtnform.validate():

        userguess = gtnform.guess.data
        
        # Check if the user guess is valid
        if userguess == None or userguess > endrange or userguess < startrange:
            flash("Please enter a valid guess.", "danger")
            return redirect(url_for('gtn.guessthenumberhome'))
        
        else:
            userguesses.append(userguess)  # Update the guesses list
            session['userguesses'] = userguesses  # Save updated list back to session

            # Check if the user guess is correct
            if userguess == ainumber:
                gamereply = "Congratulations! You guessed the number!"
                flash(gamereply, "success")
                flash("The number was: " + str(ainumber) + " it took you " + str(len(userguesses)) + " guesses.", "info")
                gtnhistory = GTNHistory(user_id=current_user.id,
                                        startrange=startrange,
                                        endrange=endrange,
                                        number=ainumber,
                                        guesses=len(userguesses))
                db.session.add(gtnhistory)
                db.session.commit()
                reset_game_session()
                return redirect(url_for('gtn.guessthenumberhome'))

            # Check if the user guess is too high or too low
            elif userguess < ainumber:
                gamereply = "Your guess is too low. Try again!"
                flash(gamereply, "warning")
                return redirect(url_for('gtn.guessthenumberhome'))
            elif userguess > ainumber:
                gamereply = "Your guess is too high. Try again!"
                flash(gamereply, "warning")
                return redirect(url_for('gtn.guessthenumberhome'))

    
    # Process the Reset Form
    if request.method == 'POST' and 'submit_reset' in request.form and gtnresetform.validate():
        reset_game_session()
        return redirect(url_for('gtn.guessthenumberhome'))
    

    return render_template("gtn/guessthenumberhome.html", 
                           gtnform=gtnform, 
                           ainumber=ainumber, 
                           userguesses=userguesses, 
                           gamereply=gamereply, 
                           startrange=startrange, 
                           endrange=endrange,
                           gtnresetform=gtnresetform)

@bp.route('/gtnhistory', methods=['GET', 'POST'])
@login_required
def gtnhistory():
    gamehistory = db.session.query(GTNHistory).all()
    return render_template("gtn/gtnhistory.html", gamehistory=gamehistory)

@bp.route('/gtnsettings', methods=['GET', 'POST'])
@login_required
def gtnsettings():

    # Inistialize forms
    gtnrangeform = GuessTheNumberSettingsForm(request.form)

    # Initialize Queries
    gtnsettings = db.session.query(GTNSettings).filter_by(user_id=current_user.id).first()

    # Process the range form
    if request.method == 'POST' and gtnrangeform.validate():

        if  gtnrangeform.startrange.data == None or gtnrangeform.startrange.data < 0:
            flash("Please enter a start range value above 0.", "danger")
            return redirect(url_for('gtn.gtnsettings'))
        
        if  gtnrangeform.endrange.data == None or gtnrangeform.endrange.data <= gtnrangeform.startrange.data:
            flash("Please enter a valid end range greater than the start range.", "danger")
            return redirect(url_for('gtn.gtnsettings'))

        # Update the session
        session['ainumber'] = 0  # Reset AI number
        session['userguesses'] = []  # Clear user guesses

        # Update the database
        gtnsettings.startrange = gtnrangeform.startrange.data
        gtnsettings.endrange = gtnrangeform.endrange.data
        db.session.commit()

        return redirect(url_for('gtn.guessthenumberhome'))
    
    return render_template("gtn/gtnsettings.html", 
                           gtnrangeform=gtnrangeform,
                           gtnsettings=gtnsettings)