from flask import Blueprint, request, render_template
from ..repositorys.props import auth, success, error, panic
from ..models import Room
from .. import db
from ..config import Config
from ..services.tool import base_query, login, get_empty_class_room
from datetime import datetime
import requests
import json

user_view = Blueprint("user_view", __name__)


# 空教室查询
@user_view.route("/emptyroom", methods=["get"])
@panic()
def empty_room():

    is_first = False
    frequency = 0

    kaoyan_time = datetime(2020, 12, 26)
    now_time = datetime.now()
    countdown = (kaoyan_time - now_time).days + 1
    # now_time = datetime(2020, 9, 13)
    room = base_query(Room).filter_by(author="cxm").first()
    if room is not None:
        time = room.time
        frequency = room.frequency + 1
        if time.year==now_time.year and time.month==now_time.month and time.day==now_time.day:   # 代表今天的数据已经有了
            is_first = False
            room.frequency = frequency
            all = room.all
            morning = room.morning
            afternoon = room.afternoon
            evening = room.evening
        else:
            is_first = True
            frequency = 1
            login()
            all, morning, afternoon, evening = get_empty_class_room()
            room.time = now_time
            room.all = all
            room.morning = morning
            room.afternoon = afternoon
            room.evening = evening
            room.frequency = frequency
    else:
        is_first = True
        frequency = 1
        login()
        all, morning, afternoon, evening = get_empty_class_room()
        room = Room()
        room.time = now_time
        room.all = all
        room.morning = morning
        room.afternoon = afternoon
        room.evening = evening
        room.author = "cxm"
        room.frequency = 1
        db.session.add(room)
        
    weekday_ = now_time.weekday()+1
    week_dict = {1:"一", 2:"二", 3:"三", 4:"四", 5:"五", 6:"六", 7:"日"}
    weekday = week_dict[weekday_]
    db.session.commit()

    return render_template("empty_room.html", time=str(now_time)[:10], 
    weekday=weekday, all=all, morning=morning, afternoon=afternoon, evening=evening,
     is_first=is_first, frequency=frequency, countdown=countdown)