from flask import Blueprint

bp = Blueprint('ai_forecast', __name__)

@bp.route('/ai-forecast')
def ai_forecast():
    return "AI Forecast Page"