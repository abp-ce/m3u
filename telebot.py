#!/usr/bin/python3
from flask import Blueprint, request, current_app
import requests
import json
from datetime import datetime, timedelta
from m3u.db import get_db

def send_message(chat_id, lst, tp):
    method = "sendMessage"
    with open(current_app.instance_path +'/teletoken') as f:
        token = f.readline()[:-1]
    url = f"https://api.telegram.org/bot{token}/{method}"
    if tp == 1 or tp == 2 or tp == 5:
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
            if tp == 2: 
                sql = 'SELECT disp_name FROM channel WHERE ch_id = ?'
                res = get_db(epg=True).execute(sql, (s,)).fetchone()
                s = res['disp_name']
            text += f"{i}. {s}.\n"
            if tp == 1: s = '$' + s  # category
            if tp == 5: s = '#' + s  # location
            if tp == 2: s = l
            l0.append({'text': str(i), 'callback_data': s})
            i += 1
        l1.append(l0)
        reply_markup['inline_keyboard'] = l1
        r_m = json.dumps(reply_markup)
        data = {"chat_id": chat_id, "text": text, "reply_markup": r_m}
    elif tp == 3:
        if type(chat_id) is int: tbl = 'telebot'
        else: tbl = 'telebot_s'
        sql = f'SELECT shift FROM {tbl} WHERE chat_id = ?'
        res = get_db(telebot=True).execute(sql, (chat_id,)).fetchone()
        if res: period = ((lst[1] + timedelta(minutes=res['shift'])).strftime("%H:%M") + ' - ' + 
                (lst[2] + timedelta(minutes=res['shift'])).strftime("%H:%M"))
        else: period = lst[1].strftime("%H:%M") + ' - ' + lst[2].strftime("%H:%M") + 'UTC'

        sql = 'SELECT disp_name FROM channel WHERE ch_id = ?'
        rs = get_db(epg=True).execute(sql, (lst[0],)).fetchone()
        text = '<b>' + rs['disp_name'] + '\n</b>' + '<i>' + period + '\n</i>' + '<b><i>' + lst[3] + '\n</i></b>' + lst[4] + '\n'
        reply_markup = ({'inline_keyboard': [[{'text': '<<', 'callback_data': f"<{lst[0]};{lst[1]}"}, 
                                              {'text': '==', 'callback_data': lst[0]}, 
                                              {'text': '>>', 'callback_data': f">{lst[0]};{lst[2]}"}]]})
        r_m = json.dumps(reply_markup)
        data = {"chat_id": chat_id, "text": text, 'parse_mode': 'HTML', "reply_markup": r_m}
    elif tp == 4:
        text = ''
        for l in lst:
            text += l + '\n'
        data = {'chat_id': chat_id, 'text': text}
    print(data)
    requests.post(url, data=data)

def get_pr_cat():
    res = get_db(epg=True).execute('SELECT DISTINCT cat FROM programme').fetchall()
    cat = []
    for r in res:
        cat.append(r['cat'])
    return cat

def get_pr_by_letters(str):
    sql = 'SELECT ch_id FROM channel WHERE disp_name_l LIKE ? '
    ptrn = f'%{str.lower()}%'
    res = get_db(epg=True).execute(sql, (ptrn,)).fetchall()
    pr = []
    for r in res:
        pr.append(r['ch_id'])
    return pr

def get_pr_by_cat(cat, tm):
    sql = 'SELECT channel FROM programme WHERE pstart < ? AND pstop > ? AND '
    if cat == 'Пусто': res = get_db(epg=True).execute((sql + 'cat IS NULL'), (tm, tm)).fetchall()
    else: res = get_db(epg=True).execute((sql + 'cat = ?'), (tm, tm, cat)).fetchall()

    if not res: print('Nothing')  

    pr = []
    for r in res:
        pr.append(r['channel'])
    return pr

def update_telebot_db(chat_id, first_name, shift):
    if type(chat_id) is int: tbl = 'telebot'
    else: tbl = 'telebot_s'
    db = get_db(telebot=True)
    sql = f'SELECT first_name, shift FROM {tbl} WHERE chat_id = ?'
    res = db.execute(sql, (chat_id,)).fetchone()
    if res:
        sql = f'UPDATE {tbl} SET first_name = ?, shift = ? WHERE chat_id = ?'
        db.execute(sql, (first_name, shift, chat_id))
    else:
        sql = f'INSERT INTO {tbl} VALUES ( ?, ?, ?)'
        db.execute(sql, (chat_id, first_name, shift))
    db.commit()

def get_programme(chat_id, prm, tm):
    sql = ('SELECT pstart, pstop, title, pdesc FROM programme '
            'WHERE channel = ? AND pstart < ? AND pstop > ? ')
    res = get_db(epg=True).execute(sql, (prm, tm, tm)).fetchone()
    pr = []
    if not res: 
        pr.append('************************************')
        pr.append('К сожалению,') 
        pr.append('************************************')
        pr.append('программа прередач отсутствует.')
        pr.append('************************************')
    else:
        pr.append(prm)
        pr.append(res['pstart'])
        pr.append(res['pstop'])
        pr.append(res['title'])
        if res['pdesc']: pr.append(res['pdesc'])
        else: pr.append('Содержание отсутствует')
    return pr


bp = Blueprint('telebot', __name__)
@bp.route('/telebot', methods=["GET", "POST"])
def telebot():
    print("***********************")
    tm_zone_list = ['МСК - 1','МСК','МСК + 1','МСК + 2','МСК + 3','МСК + 4']
    if request.method == "POST":
        print(request.json)
        if 'callback_query' in request.json:
            if 'message' in request.json['callback_query']:
                chat_id = request.json['callback_query']["message"]["chat"]["id"]
            else: return 'Message too old'
            tm = datetime.utcnow()
            if request.json['callback_query']["data"][0] == '$':
                cat = request.json['callback_query']["data"][1:]
                lst = get_pr_by_cat(cat, tm)
                tp = 2 
            elif request.json['callback_query']["data"][0] == '#':
                first_name = request.json['callback_query']["from"]["first_name"]
                lst = [f"Здравствуйте, {first_name}"]
                if 'last_name' in request.json['callback_query']['from']:
                    lst[0] += f" {request.json['callback_query']['from']['last_name']}. "
                lst[0] += f"Ваш часовой пояс {request.json['callback_query']['data'][1:]}."
                tm_zone_shift = ({ tm_zone_list[0]: 120, tm_zone_list[1]: 180, tm_zone_list[2]: 240, 
                             tm_zone_list[3]: 300, tm_zone_list[4]: 360, tm_zone_list[5]: 420})
                shift = tm_zone_shift[request.json['callback_query']["data"][1:]]
                update_telebot_db(chat_id, first_name, shift)
                tp = 4
            elif request.json['callback_query']["data"][0] == '<' or request.json['callback_query']["data"][0] == '>':
                p = request.json['callback_query']["data"].find(';')
                prm = request.json['callback_query']["data"][1:p]
                stm = request.json['callback_query']["data"][p+1:]
                tm = datetime(int(stm[:4]),int(stm[5:7]),int(stm[8:10]),int(stm[11:13]),int(stm[14:16]),int(stm[17:19]))
                if request.json['callback_query']["data"][0] == '<': tm -= timedelta(minutes=1)
                else: tm += timedelta(minutes=1)
                lst = get_programme(chat_id, prm, tm)
                if lst[0] == '************************************': tp = 4
                else: tp = 3
            else:
                prm = request.json['callback_query']["data"]
                lst = get_programme(chat_id, prm, tm)
                if lst[0] == '************************************': tp = 4
                else: tp = 3
        elif request.json["message"]["text"] == '/category':
            chat_id = request.json["message"]["chat"]["id"]
            lst = get_pr_cat()
            tp = 1
        elif request.json["message"]["text"] == '/timezone':
            chat_id = request.json["message"]["chat"]["id"]
            lst = tm_zone_list
            tp = 5
        elif request.json["message"]["text"] == '/search':
            chat_id = request.json["message"]["chat"]["id"]
            lst = ['Наберите название канала.']
            tp = 4
        elif request.json["message"]["text"] == '/start':
            chat_id = request.json["message"]["chat"]["id"]
            lst = (['Доступные команды.','/category - Выберите категорию передач',
                    '/timezone - Выберите вашу временную зону, чтобы бот правильно показывал время передач',
                    '/search - Поиск канала по буквам'])
            tp = 4
        else:
            chat_id = request.json["message"]["chat"]["id"]
            lst = get_pr_by_letters(request.json["message"]["text"])
            tp = 2
        send_message(chat_id, lst, tp)

    return "OK"