from flask import Blueprint

bp = Blueprint('team', __name__, url_prefix='/tim')

from app.blueprints.team import routes