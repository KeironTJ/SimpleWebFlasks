from flask import render_template, flash, redirect, request, url_for, jsonify, session, current_app
from app import app, db
from app.forms import LoginForm, RegistrationForm, TransactionForm, AccountForm, ProfileForm, TransactionCategoryForm, GuessTheNumberResetForm, GuessTheNumberForm, GuessTheNumberRangeForm
from app.models import User, Account, Transaction, TransactionCategory, GTNHistory, GTNSettings
from flask_login import login_required, current_user, login_user, logout_user # type: ignore
import sqlalchemy as sa # type: ignore
from urllib.parse import urlsplit

import random


@app.route('/')
@app.route('/index')
@login_required
def index():
    
    return render_template("index.html", title='Home Page')

#USER ROUTES

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/userprofile<username>')
@login_required
def userprofile(username): 

    user = db.first_or_404(sa.select(User).where(User.username == username))
    profileform = ProfileForm()
    
    return render_template("userprofile.html", title='User Profile', user=user, profileform=profileform)


#GUESS THE NUMBER GAME

def reset_game_session():
    session['ainumber'] = 0
    session['userguesses'] = []
    session['startrange'] = 1
    session['endrange'] = 100

@app.route('/guessthenumberhome', methods=['GET', 'POST'])
@login_required
def guessthenumberhome():
    gtnform = GuessTheNumberForm(request.form)
    gtnrangeform = GuessTheNumberRangeForm(request.form)
    gtnresetform = GuessTheNumberResetForm(request.form)

    if 'startrange' not in session:
        session['startrange'] = 1  
    if 'endrange' not in session:
        session['endrange'] = 100  
    if 'ainumber' not in session:
        session['ainumber'] = 0  
    if 'userguesses' not in session:
        session['userguesses'] = []  


    # Process the range form
    if request.method == 'POST' and gtnrangeform.validate():
        session['startrange'] = gtnrangeform.startrange.data
        session['endrange'] = gtnrangeform.endrange.data
        session['ainumber'] = 0  # Reset AI number
        session['userguesses'] = []  # Clear user guesses
        return redirect(url_for('guessthenumberhome'))
    
    # Check and create random number if not already created
    if 'ainumber' not in session or session['ainumber'] == 0:
        session['ainumber'] = random.randint(session['startrange'], session['endrange'])
        session['userguesses'] = []


    startrange = session['startrange']
    endrange = session['endrange']
    ainumber = session['ainumber']
    userguesses = session['userguesses']
    gamereply = ""

    if request.method == 'POST' and gtnform.validate():
        userguess = gtnform.guess.data
        userguesses.append(userguess)  # Update the guesses list
        session['userguesses'] = userguesses  # Save updated list back to session

        if userguess == ainumber:
            gamereply = "Congratulations! You guessed the number!"
            flash(gamereply, "success")
            flash("The number was: " + str(ainumber) + " it took you this many guesses: " + str(len(userguesses)))
            gtnhistory = GTNHistory(user_id=current_user.id,
                                    startrange=startrange,
                                      endrange=endrange,
                                      number=ainumber,
                                      guesses=len(userguesses))
            db.session.add(gtnhistory)
            db.session.commit()
            reset_game_session()
            
        elif userguess < ainumber:
            gamereply = "Your guess is too low. Try again!"
            flash(gamereply, "warning")
        elif userguess > ainumber:
            gamereply = "Your guess is too high. Try again!"
            flash(gamereply, "warning")

        return redirect(url_for('guessthenumberhome'))
    
    if request.method == 'POST' and gtnresetform.validate():
        reset_game_session()
        return redirect(url_for('guessthenumberhome'))
    

    return render_template("guessthenumberhome.html", 
                           gtnform=gtnform, 
                           ainumber=ainumber, 
                           userguesses=userguesses, 
                           gamereply=gamereply, 
                           startrange=startrange, 
                           endrange=endrange,
                           gtnrangeform=gtnrangeform,
                           gtnresetform=gtnresetform)

@app.route('/gtnhistory', methods=['GET', 'POST'])
@login_required
def gtnhistory():
    gamehistory = db.session.query(GTNHistory).all()
    return render_template("gtnhistory.html", gamehistory=gamehistory)


#PERSONAL ROUTES

@app.route('/pfhome', methods=['GET', 'POST'])
@login_required
def pfhome():

    transactionform = TransactionForm(request.form)
    accountform = AccountForm(request.form)
    transactioncategoryform = TransactionCategoryForm(request.form)
    
    # Query to return user specific transactions
    transactions = []
    try:
        transactions = db.session.query(Transaction).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in view all transactions",e )

    # Process Transaction Form and update the database
    if request.method == 'POST' and transactionform.validate():
        transaction = Transaction(transaction_date=transactionform.transaction_date.data,
                                  category_id=transactionform.category_id.data, 
                                  account_id=transactionform.account_id.data, 
                                  user_id=current_user.id,
                                  item_name=transactionform.item_name.data,
                                  amount=transactionform.amount.data)
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction Added")

        return redirect(url_for('pfhome'))
    
    # Query to return user specific accounts
    accounts = []
    try:
        accounts = db.session.query(Account).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in view all accounts", e)
    
    # Process Account Form and update the database
    if request.method == 'POST' and accountform.validate():
        account = Account(account_name=accountform.account_name.data, 
                                  user_id=current_user.id)
        db.session.add(account)
        db.session.commit()
        flash("Account Added")

        return redirect(url_for('pfhome'))
    
    # Query to return user specific categories
    categories = []
    try:
        categories = db.session.query(TransactionCategory).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in categories", e)

    # Process TransactionCategory Form and update the database
    if request.method == 'POST' and transactioncategoryform.validate():
        category = TransactionCategory(category_name=transactioncategoryform.category_name.data,
                                       user_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        flash("Category Added")

        return redirect(url_for('pfhome'))

    
    
    return render_template("pfhome.html", 
                           title='Personal Finance', 
                           transactionform=transactionform, 
                           transactions=transactions,
                           accountform=accountform,
                           accounts=accounts,
                           transactioncategoryform=transactioncategoryform,
                           categories=categories)