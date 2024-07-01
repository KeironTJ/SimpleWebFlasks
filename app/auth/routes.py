from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import urlsplit
from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User, GTNSettings, UserRoles
import sqlalchemy as sa
from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        # Check if the user is active
        if not user.active:
            return redirect(url_for('auth.reactivate_account', user_id=user.id))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/reactivate_account<user_id>', methods=['GET', 'POST'])
def reactivate_account(user_id):
    user = db.session.query(User).get(user_id)

    return render_template('auth/reactivate_account.html', title='Re-activate Account', user=user)



@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
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
        
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)