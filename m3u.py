#!/usr/bin/python3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory, abort
)
from flask_babel import _
import urllib
import os
import json
import string
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from m3u.auth import login_required
from m3u.db import get_db
from . import M3Uclass

bp = Blueprint('m3u', __name__)

def get_m3u(id = None) : 
    if not id :
        g.m3u = M3Uclass.M3U(empty=True)
        g.resm3u = M3Uclass.M3U(empty=True)
        return g.m3u, g.resm3u
    if 'm3u' not in g :
        g.m3u = M3Uclass.M3U(empty=True)
    
    post = get_db().execute(
        'SELECT list '
        ' FROM m3u '
        ' WHERE author_id = ?',
        (id,)
    ).fetchone()

    if post : 
        f_name = post['list']
        if (f_name and os.path.exists(f_name)) :
            with open(f_name) as f :
                lines = f.readlines()
            g.resm3u = M3Uclass.M3U(lines)
        else : g.resm3u = M3Uclass.M3U(empty=True)
    else : 
        db = get_db()
        db.execute(
            'INSERT INTO m3u (title, list, author_id)'
            ' VALUES (?, ?, ?)',
            ("Your list", "", g.user['id'])
        )
        db.commit()
        g.resm3u = M3Uclass.M3U(empty=True)
    
    return g.m3u, g.resm3u

        

def del_m3u(e=None):
    m3u = g.pop('m3u', None)
    resm3u = g.pop('resm3u', None)

def init_app(app):
    app.teardown_appcontext(del_m3u)

@bp.route('/help')
def help():
    return render_template('help.html')


@bp.route('/', methods=('GET', 'POST'))
def m3u():
    if g.user :
        m3u, resm3u = get_m3u(g.user['id'])
    else :
        m3u, resm3u = get_m3u()
    if request.method == 'POST':
        if request.form['btn'] == (_('Load')) :
            url = request.form["url"]
            with urllib.request.urlopen(url) as f:
                lines = f.readlines()
            m3u = M3Uclass.M3U(lines)
            #resm3u = M3Uclass.M3U(lines,True)
    return render_template('m3u.html', m3u=m3u, resm3u=resm3u)

@bp.route('/m3u/save', methods=['POST'])
@login_required
def m3u_save():
    db = get_db()
    post = db.execute(
        'SELECT list '
        ' FROM m3u '
        ' WHERE author_id = ?',
        (g.user['id'],)
    ).fetchone()
    if post :
        if post['list'] == "" :
            rnd = ''.join(random.choice(string.ascii_letters) for i in range(5))
            f_n = str(g.user['id']) + rnd + "_playlist.m3u8"
            f_name = current_app.instance_path + "/u_fls/" + f_n
            db.execute(
                'UPDATE m3u SET title = ?, list = ?'
                ' WHERE id = ?',
                ("You m3u", f_name, g.user['id'])
            )
            db.commit()
        else : 
            f_name = post['list']
            f_n = f_name[f_name.rfind('/')+1:]
    else :
        return "*****"
    data = request.get_json()
    f = open(f_name,'w')
    f.write("#EXTM3U\n")
    for dt in data :
        f.write("#EXTINF:-1 ,{}\n".format(dt.rstrip('\n')))
        f.write("{}\n".format(data[dt].rstrip('\n')))
    f.close()
    return f_n

@bp.route('/m3u/select', methods=['POST'])
def m3u_select():
    data = request.get_json()
    st = data['date']
    nm = data['name'].lower().rstrip().rstrip(')')
    pos = nm.find('hd')
    if (pos > 0) :
        nm = nm[:pos].rstrip()
    shft = 0
    if '+' in nm : 
        pos = nm.find('+')
        shft = int(nm[pos:])
        nm = nm[:pos].rstrip('(').rstrip()
    elif '-' in nm : 
        pos = nm.find('-')
        shft = int(nm[pos:])
        nm = nm[:pos].rstrip('(').rstrip()
    print(nm)
    date = datetime(int(st[:4]), int(st[5:7]), int(st[8:10]), int(st[11:13]) + shft, int(st[14:16]), int(st[17:19]))
    res = get_db(epg=True).execute(
        'SELECT pstart, pstop, title, pdesc '
        ' FROM programme p JOIN channel c ON p.channel = c.ch_id '
        ' WHERE disp_name = ? AND pstart < ? AND pstop > ? ORDER BY pstart',
        (nm,date,date)
    ).fetchall()
    jsn = {}
    if res:
        for r in res:
            jsn['start'] = (r['pstart'] - timedelta(hours=shft)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            jsn['stop'] = (r['pstop'] - timedelta(hours=shft)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            jsn['title'] = r['title']
            jsn['desc'] = r['pdesc']
    else: 
        jsn['start'] = jsn['stop'] = jsn['title'] = jsn['desc'] =''
    return json.dumps(jsn)


@bp.route('/m3u/download/<filename>')
#@login_required
def m3u_download(filename):
    id = filename[:filename.find('_')]
    post = get_db().execute(
        'SELECT list '
        ' FROM m3u '
        ' WHERE author_id = ?',
        (id,)
    ).fetchone()
    if os.path.exists(post['list']) :
        pos = post['list'].rfind('/')
        fp = post['list'][:pos]
        fn = post['list'][pos+1:]
        return send_from_directory(os.path.abspath(fp), fn, as_attachment=True)
    else :
        return abort(404,_("File must be saved"))
