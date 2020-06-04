#!/usr/bin/python3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory
)
import urllib
#import os
from m3u.auth import login_required
from m3u.db import get_db
from . import M3Uclass

bp = Blueprint('m3u', __name__)

def get_m3u(id) : 
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
        with open(f_name) as f :
            lines = f.readlines()
        g.resm3u = M3Uclass.M3U(lines)
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


@bp.route('/', methods=('GET', 'POST'))
@login_required
def m3u():

    m3u, resm3u = get_m3u(g.user['id'])
    if request.method == 'POST':
        if request.form['btn'] == 'Load' :
            url = request.form["url"]
            with urllib.request.urlopen(url) as f:
                lines = f.readlines()
            m3u = M3Uclass.M3U(lines)
            #resm3u = M3Uclass.M3U(lines,True)
    return render_template('m3u.html', m3u=m3u, resm3u=resm3u)

@bp.route('/m3u/save', methods=['POST'])
@login_required
def m3u_save():
    data = request.get_json()
    lines = []
    lines.append("#EXTM3U\n")
    for dt in data :
        lines.append("#EXTINF:-1 ,{}\n".format(dt))
        lines.append("{}\n".format(data[dt]))
    print(''.join(lines))
    #print(os.getcwd())
    f_name = current_app.instance_path + "/u_fls/" + g.user['username'] + "_playlist.m3u8"
    with open(f_name,'w') as f :
        f.write(''.join(lines))
    db = get_db()
    db.execute(
        'UPDATE m3u SET title = ?, list = ?'
        ' WHERE id = ?',
        ("You m3u", f_name, g.user['id'])
    )
    db.commit()
    return "OK"

@bp.route('/m3u/download')
@login_required
def m3u_download():
    print("here")
    return send_from_directory(current_app.instance_path + "/u_fls/", filename=g.user['username'] + "_playlist.m3u8", as_attachment=True)

