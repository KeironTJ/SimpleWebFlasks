from flask import render_template, flash, redirect, request, url_for, jsonify, session, current_app
from app import app, db
from app.forms import LoginForm, RegistrationForm, AssignRoleForm, CreateRoleForm, TransactionForm, AccountForm, ProfileForm, TransactionCategoryForm, GuessTheNumberResetForm, GuessTheNumberForm, GuessTheNumberSettingsForm
from app.models import User, Account, Transaction, TransactionCategory, GTNHistory, GTNSettings, Role, UserRoles
from flask_login import login_required, current_user, login_user, logout_user # type: ignore
import sqlalchemy as sa # type: ignore
from urllib.parse import urlsplit
from functools import wraps

import random

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not user_has_admin(current_user.id):
            return redirect(url_for('not_admin'))
        return f(*args, **kwargs)
    return decorated_function

def user_has_admin(user_id):
    admin_role = db.session.query(Role).join(UserRoles, UserRoles.role_id == Role.id).filter(Role.name == 'admin', UserRoles.user_id == user_id).first()
    return admin_role is not None

# USER ROUTES

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
        
        # Check if the user is active
        if not user.active:
            return redirect(url_for('reactivate_account', user_id=user.id))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)

@app.route('/reactivate_account<user_id>', methods=['GET', 'POST'])
def reactivate_account(user_id):
    user = db.session.query(User).get(user_id)

    return render_template('reactivate_account.html', title='Re-activate Account', user=user)



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
        
        # Create default GTNSettings for the user
        gtnsettings = GTNSettings(user_id=user.id, startrange=1, endrange=100)
        assign_user_role = UserRoles(user_id=user.id, role_id=2)
        print(assign_user_role.role_id)
        db.session.add(gtnsettings)
        db.session.add(assign_user_role)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/userprofile<username>', methods=['GET', 'POST'])
@login_required
def userprofile(username): 

    user = db.first_or_404(sa.select(User).where(User.username == username))
    profileform = ProfileForm()
    
    return render_template("userprofile.html", title='User Profile', user=user, profileform=profileform)


## Admin Routes

@app.route('/admin_home', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home():


    return render_template("admin_home.html", title='Admin Home')

@app.route('/admin_users', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():

    user_roles = db.session.query(UserRoles).all()
    users = db.session.query(User).all()
    roles= db.session.query(Role).all()

    assign_role_form = AssignRoleForm()

    if request.method == 'POST' and assign_role_form.validate():

        assign_role = UserRoles(user_id=assign_role_form.user_id.data, 
                                role_id=assign_role_form.role_id.data)
        db.session.add(assign_role)
        db.session.commit()
        flash("Role Assigned")
        return redirect(url_for('admin_users'))

    return render_template("admin_users.html", 
                           title='Admin Users', 
                           users=users, 
                           assign_role_form=assign_role_form, 
                           roles=roles,
                           user_roles=user_roles)

@app.route('/admin_roles', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_roles():
    roles = db.session.query(Role).all()
    roleform = CreateRoleForm()

    if request.method == 'POST' and roleform.validate():
        role = Role(name=roleform.role_name.data)
        db.session.add(role)
        db.session.commit()
        flash("Role Added")
        return redirect(url_for('admin_roles'))

    return render_template("admin_roles.html", title='Admin Roles', roles=roles, roleform=roleform)

@app.route('/deactivate_user<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def deactivate_user(user_id):
    user = db.session.query(User).get(user_id)
    user.active = False # Deactivate the user
    db.session.commit()
    flash("User Deactivated")

    return redirect(url_for('admin_users'))

# This route is used to reactivate a user account
@app.route('/activate_user/<user_id>', methods=['GET', 'POST'])
def activate_user(user_id):

    user = db.session.query(User).get(user_id)

    # Check if the user exists and is inactive
    if user:
        user.active = True

        # Create default GTNSettings for the user
        gtnsettings = GTNSettings(user_id=user_id, startrange=1, endrange=100)

        # Assign the user the default role
        assign_user_role = UserRoles(user_id=user_id, role_id=2)

        db.session.add(gtnsettings)
        db.session.add(assign_user_role)
        db.session.commit()
        flash("Account Reactivated")

        # Redirect to the login page (or admin users if admin)
        try:
            for role in current_user.role:
                if role.name == 'admin':
                    return redirect(url_for('admin_users'))
            return redirect(url_for('login'))
        except Exception as e:
            # Log the error if logging is set up
            print(f"Error: {e}")  # Replace with logging if applicable
            return redirect(url_for('login'))
        
    # If the user does not exist or is already active
    else:
        return redirect(url_for('index'))

# This route is used to render a page that denies access to an admin page
@app.route('/not_admin', methods=['GET', 'POST'])
@login_required
def not_admin():
    return render_template("not_admin.html", title='Not Admin')



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


@app.route('/guessthenumberhome', methods=['GET', 'POST'])
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
            return redirect(url_for('guessthenumberhome'))
        
        else:
            userguesses.append(userguess)  # Update the guesses list
            session['userguesses'] = userguesses  # Save updated list back to session

            # Check if the user guess is correct
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
                return redirect(url_for('guessthenumberhome'))

            # Check if the user guess is too high or too low
            elif userguess < ainumber:
                gamereply = "Your guess is too low. Try again!"
                flash(gamereply, "warning")
                return redirect(url_for('guessthenumberhome'))
            elif userguess > ainumber:
                gamereply = "Your guess is too high. Try again!"
                flash(gamereply, "warning")
                return redirect(url_for('guessthenumberhome'))

    
    # Process the Reset Form
    if request.method == 'POST' and 'submit_reset' in request.form and gtnresetform.validate():
        reset_game_session()
        return redirect(url_for('guessthenumberhome'))
    

    return render_template("guessthenumberhome.html", 
                           gtnform=gtnform, 
                           ainumber=ainumber, 
                           userguesses=userguesses, 
                           gamereply=gamereply, 
                           startrange=startrange, 
                           endrange=endrange,
                           gtnresetform=gtnresetform)

@app.route('/gtnhistory', methods=['GET', 'POST'])
@login_required
def gtnhistory():
    gamehistory = db.session.query(GTNHistory).all()
    return render_template("gtnhistory.html", gamehistory=gamehistory)

@app.route('/gtnsettings', methods=['GET', 'POST'])
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
            return redirect(url_for('gtnsettings'))
        
        if  gtnrangeform.endrange.data == None or gtnrangeform.endrange.data <= gtnrangeform.startrange.data:
            flash("Please enter a valid end range greater than the start range.", "danger")
            return redirect(url_for('gtnsettings'))

        # Update the session
        session['ainumber'] = 0  # Reset AI number
        session['userguesses'] = []  # Clear user guesses

        # Update the database
        gtnsettings.startrange = gtnrangeform.startrange.data
        gtnsettings.endrange = gtnrangeform.endrange.data
        db.session.commit()

        return redirect(url_for('guessthenumberhome'))
    
    return render_template("gtnsettings.html", 
                           gtnrangeform=gtnrangeform,
                           gtnsettings=gtnsettings)

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