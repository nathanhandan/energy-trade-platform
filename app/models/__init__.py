from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.users import User  # This needs to be after db initialization