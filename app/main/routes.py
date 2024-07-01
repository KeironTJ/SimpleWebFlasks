
from app.main import bp
from flask import render_template
from flask_login import login_required
from app import db
from app.models import User
from app.main.forms import ProfileForm
import sqlalchemy as sa


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@bp.route('/userprofile<username>', methods=['GET', 'POST'])
@login_required
def userprofile(username): 

    user = db.first_or_404(sa.select(User).where(User.username == username))
    profileform = ProfileForm()
    
    return render_template("userprofile.html", title='User Profile', user=user, profileform=profileform)







