from flask import Blueprint

bp = Blueprint('history', __name__)

@bp.route('/history')
def history():
    return "History Page"