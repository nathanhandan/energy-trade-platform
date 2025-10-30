from flask import Blueprint

bp = Blueprint('activities', __name__)

@bp.route('/activities')
def activities():
    return "Activities Page"