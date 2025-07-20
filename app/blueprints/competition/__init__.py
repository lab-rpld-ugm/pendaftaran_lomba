from flask import Blueprint

bp = Blueprint('competition', __name__)

from app.blueprints.competition import routes