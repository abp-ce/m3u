#!/usr/bin/python3
from flask import Blueprint, request
import requests
import json
from datetime import datetime
from m3u.db import get_db

def send_message(chat_id, lst, tp):
    method = "sendMessage"
    token = "1371707108:AAFw6l7184tWFBh9AvldcAkfAjJPAlpnz5Q"
    url = f"https://api.telegram.org/bot{token}/{method}"
    if tp == 1 or tp == 2:
        reply_markup = {}
        l0 = []
        l1 = []
        i = 1
        text = ''
        for l in lst:
            if i % 8 == 0:
                l1.append(l0)
                reply_markup['inline_keyboard'] = l1
                r_m = json.dumps(reply_markup)
                data = {"chat_id": chat_id, "text": text, "reply_markup": r_m}
                requests.post(url, data=data)
                text = ''
                l0.clear()
                l1.clear()
            if l == None: s = 'Пусто'
            else: s = l
            text += f"{i}. {s}.\n"
            if tp == 1: s = '$' + s
            l0.append({'text': str(i), 'callback_data': s})
            i += 1
        l1.append(l0)
        reply_markup['inline_keyboard'] = l1
        r_m = json.dumps(reply_markup)
        data = {"chat_id": chat_id, "text": text, "reply_markup": r_m}
    elif tp == 3:
        text = '<b>' + lst[0] + '\n</b>' + '<i>' + lst[1] + '\n</i>' + '<b><i>' + lst[2] + '\n</i></b>' + lst[3] + '\n'
        data = {"chat_id": chat_id, "text": text, 'parse_mode': 'HTML'}
    elif tp == 4:
        text = lst[0] + '\n'
        data = {"chat_id": chat_id, "text": text}
    print(data)
    requests.post(url, data=data)

def get_pr_cat():
    res = get_db(epg=True).execute(
        'SELECT DISTINCT cat '
        ' FROM programme '
    ).fetchall()
    cat = []
    for r in res:
        cat.append(r['cat'])
    return cat

def get_pr_by_cat(cat, tm):
    sql = 'SELECT disp_name FROM channel c JOIN programme p ON p.channel = c.ch_id WHERE pstart < ? AND pstop > ? AND '
    if cat == 'Пусто': res = get_db(epg=True).execute((sql + 'cat IS NULL'), (tm, tm)).fetchall()
    else: res = get_db(epg=True).execute((sql + 'cat = ?'), (tm, tm, cat)).fetchall()

    if not res: print('Nothing')  

    pr = []
    for r in res:
        pr.append(r['disp_name'])
    return pr

def get_programme(prm, tm):
    sql = 'SELECT pstart, pstop, title, pdesc FROM programme p JOIN channel c ON p.channel = c.ch_id WHERE disp_name = ? AND pstart < ? AND pstop > ? ORDER BY pstart'
    res = get_db(epg=True).execute(sql, (prm, tm, tm)).fetchone()
    pr = []
    if not res: 
        pr.append('************************************')
        pr.append('К сожалению,') 
        pr.append('программа прередач отсутствует.')
        pr.append('************************************')
    else:
        print(res['pstart'])
        pr.append(prm)
        pr.append(res['pstart'].strftime("%H:%M") + ' - ' + res['pstop'].strftime("%H:%M") + 'UTC')
        pr.append(res['title'])
        if res['pdesc']: pr.append(res['pdesc'])
        else: pr.append('Содержание отсутствует')
    return pr


bp = Blueprint('telebot', __name__)
@bp.route('/telebot', methods=["GET", "POST"])
def telebot():
    print("***********************88")
    if request.method == "POST":
        print(request.json)
        if 'callback_query' in request.json:
            if request.json['callback_query']["data"][0] == '$':
                tm = datetime.utcnow()
                chat_id = request.json['callback_query']["message"]["chat"]["id"]
                cat = request.json['callback_query']["data"][1:]
                lst = get_pr_by_cat(cat, tm)
                tp = 2
            else:
                tm = datetime.utcnow()
                chat_id = request.json['callback_query']["message"]["chat"]["id"]
                prm = request.json['callback_query']["data"]
                lst = get_programme(prm, tm)
                tp = 3
        elif request.json["message"]["text"] == '/start':
            chat_id = request.json["message"]["chat"]["id"]
            lst = get_pr_cat()
            tp = 1
        else:
            chat_id = request.json["message"]["chat"]["id"]
            lst = []
            lst.append('Наберите /start.')
            tp = 4
        send_message(chat_id, lst, tp)

    return "OK"