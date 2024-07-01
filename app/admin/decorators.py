from flask import redirect, url_for
from functools import wraps
from app.models import Role, UserRoles
from app import db
from flask_login import current_user




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