from .. import db, app
from .room import Room


def init_model():
    db.create_all(app=app)