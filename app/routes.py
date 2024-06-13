from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, TransactionForm
from app.models import User, Account, Transaction
from flask_login import login_required, current_user, login_user, logout_user
import sqlalchemy as sa
from urllib.parse import urlsplit


@app.route('/')
@app.route('/index')
@login_required
def index():
    
    return render_template("index.html", title='Home Page')


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

#GUESS THE NUMBER GAME

@app.route('/guessthenumberhome', methods=['GET', 'POST'])
@login_required
def guessthenumberhome():
    
    return render_template("guessthenumberhome.html", title='Guess The Number')


@app.route('/pfhome', methods=['GET', 'POST'])
@login_required
def pfhome():
    form = TransactionForm(request.form)
    transactions = []

    try:
        print("Executing view all transactions function")
        transactions = db.session.query(Transaction).all()
        print("complete")
    except Exception as e:
        print("Error in view all transactions, e")


    if request.method == 'POST' and form.validate():
        transaction = Transaction(transaction_date=form.transaction_date.data, 
                                  account_id=form.account_id.data, 
                                  user_id=current_user.id)
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction Added")
        return redirect(url_for('pfhome'))
    return render_template("pfhome.html", title='Personal Finance - Home', form=form, transactions=transactions)