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

    kaoyan_time = datetime(Config.KAOYAN_TIME[0], Config.KAOYAN_TIME[1], Config.KAOYAN_TIME[2])    # 21年考研日期，婷婷
    now_time = datetime.now()
    countdown = (kaoyan_time - now_time).days + 1
    # now_time = datetime(2020, 9, 13)
    # room = base_query(Room).filter_by(author="cxm").first()
    room = base_query(Room).order_by(Room.id.desc()).first()
    
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
            one_two = room.one_two
            three_four = room.three_four
            five_six = room.five_six
            seven_eight = room.seven_eight
            nine_ten = room.nine_ten
        else:
            is_first = True
            room = Room()    # 每天的数据都保留着
            frequency = 1
            login()
            all, morning, afternoon, evening, one_two, three_four, five_six, seven_eight, nine_ten = get_empty_class_room()
            room.time = now_time
            room.all = all
            room.morning = morning
            room.afternoon = afternoon
            room.evening = evening
            room.frequency = frequency
            room.one_two = one_two
            room.three_four = three_four
            room.five_six = five_six
            room.seven_eight = seven_eight
            room.nine_ten = nine_ten
            db.session.add(room)
    else:
        is_first = True
        frequency = 1
        login()
        all, morning, afternoon, evening, one_two, three_four, five_six, seven_eight, nine_ten = get_empty_class_room()
        room = Room()
        room.time = now_time
        room.all = all
        room.morning = morning
        room.afternoon = afternoon
        room.evening = evening
        room.one_two = one_two
        room.three_four = three_four
        room.five_six = five_six
        room.seven_eight = seven_eight
        room.nine_ten = nine_ten
        room.author = "cxm"
        room.frequency = 1
        db.session.add(room)
        
    weekday_ = now_time.weekday()+1
    week_dict = {1:"一", 2:"二", 3:"三", 4:"四", 5:"五", 6:"六", 7:"日"}
    weekday = week_dict[weekday_]
    db.session.commit()

    return render_template("empty_room.html", time=str(now_time)[:10], 
    weekday=weekday, all=all, morning=morning, afternoon=afternoon, evening=evening,
     is_first=is_first, frequency=frequency, countdown=countdown,
     one_two = one_two, three_four = three_four, five_six = five_six, seven_eight = seven_eight, nine_ten = nine_ten)