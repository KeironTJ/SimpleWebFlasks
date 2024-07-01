from flask import Blueprint

bp = Blueprint('financeapp', __name__)

from app.financeapp import routes