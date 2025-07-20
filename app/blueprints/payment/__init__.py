from flask import Blueprint

bp = Blueprint('payment', __name__, url_prefix='/pembayaran')

from app.blueprints.payment import routes