# coding:utf-8

from .. import db


class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column("id", db.Integer, primary_key=True)
    time = db.Column("time", db.DateTime)
    all = db.Column("all", db.Text)
    morning = db.Column("morning", db.Text)
    afternoon = db.Column("afternoon", db.Text)
    evening = db.Column("evening", db.Text)
    author = db.Column("author", db.Text)
    frequency = db.Column("frequency", db.Integer)
    is_delete = db.Column("is_delete", db.Integer)