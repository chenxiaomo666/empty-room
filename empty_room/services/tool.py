from sqlalchemy import or_
import requests
import base64
import json
import rsa
from bs4 import BeautifulSoup as bs
from ..config import Config

try:
    import cookielib
except:
    import http.cookiejar as cookielib


session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename='cookie.txt')
url = 'http://jwxt.neuq.edu.cn/jwglxt/xtgl/login_slogin.html'
# database = db.db()

# 定义的header
header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Content-Length": "462",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "jwxt.neuq.edu.cn",
            "Origin": "http://jwxt.neuq.edu.cn",
            "Proxy-Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Mobile Safari/537.36",
        }


def base_query(model):
    """
    所有未被删除的记录
    """
    return model.query.filter(or_(model.is_delete.is_(None), model.is_delete == 0))


# 登录主体函数
def login():
    try:
        session.cookies.load(ignore_discard=True)
        url = 'http://jwxt.neuq.edu.cn/jwglxt/xtgl/index_initMenu.html'
        res = session.get(url=url, allow_redirects=False)
        statue = res.status_code
        old_cookie = session.get(url=url).request.headers['Cookie']
        if(statue == 200):
            print('登陆成功！')
            print('此时的cookie是', old_cookie)
        else:
            print('cookie过期，重新登录')
            parse()

    except:
        print('未能加载cookie')
        parse()


# 提交登录表单，并利用cookiejar保存cookie
def parse():
    username = Config.STUDENTID
    payload = {
        'csrftoken': get_csrf_token(),
        'yhm': username,
        'mm': get_passwd()
    }
    r = session.post(url, data=payload, headers=header)
    test_login_url = 'http://jwxt.neuq.edu.cn/jwglxt/xtgl/index_initMenu.html'
    response = session.get(url=test_login_url, allow_redirects=False)
    statue = response.status_code
    if (statue == 200):
        print('登陆成功！')
        cookies = session.cookies
        cookies.save(ignore_discard=True, ignore_expires=True)
        print('新的Cookie是' + r.request.headers['Cookie'])
    else:
        print('用户名密码错误！')
        print('请重新输入用户名密码')
        parse()


# 获取csrf_token，该值为表单中必须的
def get_csrf_token():
    page = session.get(url)
    soup = bs(page.text, "html.parser")
    # 获取认证口令csrftoken
    csrftoken = soup.find(id="csrftoken").get("value")
    return csrftoken


# 从公钥接口获取到构造公钥的模和指数，并在本地生成公钥对明文密码加密。
def get_passwd():
    mm = bytes(Config.PASSWORD, encoding='utf-8')
    publickey = session.get('http://jwxt.neuq.edu.cn/jwglxt/xtgl/login_getPublicKey.html').json()
    b_modulus = base64.b64decode(publickey['modulus'])  # 将base64解码转为bytes
    b_exponent = base64.b64decode(publickey['exponent'])  # 将base64解码转为bytes
    # 公钥生成,python3从bytes中获取int:int.from_bytes(bstring,'big')
    modulus = int.from_bytes(b_modulus, 'big')
    exponent = int.from_bytes(b_exponent, 'big')
    mm_key = rsa.PublicKey(modulus, exponent)
    # 利用公钥加密,bytes转为base64编码
    passwd = base64.b64encode(rsa.encrypt(mm, mm_key))
    return passwd


def get_current_week():
    from datetime import datetime
    # 开学时间，手动维护
    start_year, start_month, start_day = Config.START_TIME

    now_time = datetime.now()
    now_year, now_month, now_day = now_time.year, now_time.month, now_time.day

    if (now_year % 400 == 0) or (now_year % 4 == 0 and now_year % 100 != 0):
        month_year = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        month_year = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if start_year == now_year:
        if now_month > start_month:
            already_day = (month_year[start_month] - start_day) + sum(month_year[start_month + 1:now_month]) + now_day
        else:
            already_day = now_day - start_day
        result_week = (already_day // 7) + 1
    else:
        # 上一年总天数
        last_yearday = month_year[start_month] - start_day + sum(month_year[start_month + 1:])
        now_yearday = sum(month_year[0:now_month]) + now_day
        result_week = (last_yearday + now_yearday) // 7 + 1

    return 2**(result_week-1), now_time.weekday()+1


def jwc_post(week, weekday, period):
    url = "http://jwxt.neuq.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?doType=query&gnmkdm=N2155"
    data = {
        "fwzt": "cx",
        "xqh_id": "3D669E6DAB06A186E053AB14CECA64B4",
        "xnm": 2020,
        "xqm": 3,
        "cdlb_id": "",
        "cdejlb_id": "",
        "qszws": "",
        "jszws": "",
        "cdmc": "",
        "lh": "01",
        "jyfs": 0,
        "cdjylx": "",
        "zcd": week,
        "xqj": weekday,
        "jcd": period,  # 一上午：15   一下午：240  晚上：768   全天：1023
        "_search": False,
        "nd": "1599472100494",
        "queryModel.showCount": 100,
        "queryModel.currentPage": 1,
        "queryModel.sortName": "cdbh",
        "queryModel.sortOrder": "asc",
        "time": 5
    }

    r = session.post(url, data=data, headers=header)
    return json.loads(r.text)


def get_empty_class_room():
    week, weekday = get_current_week()
    # period 一上午：15   一下午：240  晚上：768   全天：1023
    empty_room_all = jwc_post(week, weekday, 1023)
    empty_room_morning = jwc_post(week, weekday, 15)
    empty_room_afternoon = jwc_post(week, weekday, 240)
    empty_room_evening = jwc_post(week, weekday, 768)
    empty_room_one_two = jwc_post(week, weekday, 3)  # 一二节课
    empty_room_three_four = jwc_post(week, weekday, 12)  # 三四节课
    empty_room_five_six = jwc_post(week, weekday, 48) # 五六节课
    empty_room_seven_eight = jwc_post(week, weekday, 192)  # 四八节课
    empty_room_nine_ten = jwc_post(week, weekday, 768)  # 九十节课

    all = []
    morning = []
    afternoon = []
    evening = []
    one_two = []
    three_four = []
    five_six = []
    seven_eight = []
    nine_ten = []

    for x in empty_room_all["items"]:
        all.append(x["cdbh"])
    for x in empty_room_morning["items"]:
        morning.append(x["cdbh"])
    for x in empty_room_afternoon["items"]:
        afternoon.append(x["cdbh"])
    for x in empty_room_evening["items"]:
        evening.append(x["cdbh"])
    for x in empty_room_one_two["items"]:
        one_two.append(x["cdbh"])
    for x in empty_room_three_four["items"]:
        three_four.append(x["cdbh"])
    for x in empty_room_five_six["items"]:
        five_six.append(x["cdbh"])
    for x in empty_room_seven_eight["items"]:
        seven_eight.append(x["cdbh"])
    for x in empty_room_nine_ten["items"]:
        nine_ten.append(x["cdbh"])

    all_ = ", ".join(all)
    morning_ = ", ".join(morning)
    afternoon_ = ", ".join(afternoon)
    evening_ = ", ".join(evening)
    one_two_ = ", ".join(one_two)
    three_four_ = ", ".join(three_four)
    five_six_ = ", ".join(five_six)
    seven_eight_ = ", ".join(seven_eight)
    nine_ten_ = ", ".join(nine_ten)

    return all_, morning_, afternoon_, evening_, one_two_, three_four_, five_six_, seven_eight_, nine_ten_

