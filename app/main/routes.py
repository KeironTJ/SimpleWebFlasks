from flask import render_template, redirect, url_for
from flask_login import login_required, current_user # type:ignore

from app.models import User

from app.main import bp

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    print(current_user.activegame)
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
    
    
    return render_template("edit_profile.html", title='Edit Profile', user=user)    








