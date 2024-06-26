from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, TransactionForm, AccountForm, ProfileForm, TransactionCategoryForm
from app.models import User, Account, Transaction, TransactionCategory
from flask_login import login_required, current_user, login_user, logout_user # type: ignore
import sqlalchemy as sa # type: ignore
from urllib.parse import urlsplit


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


@app.route('/')
@app.route('/userprofile<username>')
@login_required
def userprofile(username): 

    user = db.first_or_404(sa.select(User).where(User.username == username))
    profileform = ProfileForm()
    
    return render_template("userprofile.html", title='User Profile', user=user, profileform=profileform)


#GUESS THE NUMBER GAME

@app.route('/guessthenumberhome', methods=['GET', 'POST'])
@login_required
def guessthenumberhome():
    
    return render_template("guessthenumberhome.html", title='Guess The Number')

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
    
    categories = []
    try:
        categories = db.session.query(TransactionCategory).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in categories", e)

    # Process Transaction Form and update the database
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