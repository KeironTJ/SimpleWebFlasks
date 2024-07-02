from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.main.forms import ProfileForm
from app.models import User, db
import sqlalchemy as sa

from app.main import bp

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@bp.route('/view_profile/<user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id): 

    user = User.query.filter_by(id=user_id).first_or_404()

    # Check if current user is admin or the current user viewing their own profile
    if not current_user.is_admin() and current_user.id != user.id:
        return redirect(url_for('admin.not_admin'))
    
    return render_template("view_profile.html" , title='View Profile', user=user)


@bp.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id): 

    user = User.query.filter_by(id=user_id).first_or_404()

    # Check if current user is admin or the current user viewing their own profile
    if not current_user.is_admin() and current_user.id != user.id:
        return redirect(url_for('admin.not_admin'))
    
    profileform = ProfileForm()

    if request.method == "GET":
        profileform.firstname.data = user.firstname
        profileform.surname.data = user.surname
        profileform.dob.data = user.dob
        profileform.firstlineaddress.data = user.firstlineaddress
        profileform.city.data = user.city
        profileform.postcode.data = user.postcode

    if request.method == "POST" and profileform.validate_on_submit():
        user.firstname = profileform.firstname.data
        user.surname = profileform.surname.data
        user.dob = profileform.dob.data
        user.firstlineaddress = profileform.firstlineaddress.data
        user.city = profileform.city.data
        user.postcode = profileform.postcode.data

        flash('Profile updated successfully')
        db.session.commit()

        return redirect(url_for('main.view_profile', user_id=user.id))
    
    return render_template("edit_profile.html", title='Edit Profile', user=user, profileform=profileform)    








