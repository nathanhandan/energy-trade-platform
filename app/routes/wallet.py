from flask import Blueprint

bp = Blueprint('wallet', __name__)

@bp.route('/wallet')
def wallet():
    return "Wallet Page"