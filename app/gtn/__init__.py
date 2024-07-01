from flask import Blueprint


bp = Blueprint('gtn', __name__)


from app.gtn import routes