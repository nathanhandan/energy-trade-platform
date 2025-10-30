from flask import Blueprint

bp = Blueprint('community', __name__)

@bp.route('/community')
def community():
    return "Community Page"