from flask import Blueprint

bp = Blueprint('buy_sell', __name__)

@bp.route('/buy-sell')
def buy_sell():
    return "Buy/Sell Power Page"