#!/usr/bin/python3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory, abort
)
import urllib
import os
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


@bp.route('/', methods=('GET', 'POST'))
def m3u():
    if g.user :
        m3u, resm3u = get_m3u(g.user['id'])
    else :
        m3u, resm3u = get_m3u()
    if request.method == 'POST':
        if request.form['btn'] == 'Load' :
            url = request.form["url"]
            with urllib.request.urlopen(url) as f:
                lines = f.readlines()
            m3u = M3Uclass.M3U(lines)
            #resm3u = M3Uclass.M3U(lines,True)
    return render_template('m3u.html', m3u=m3u, resm3u=resm3u)

@bp.route('/m3u/save', methods=['POST'])
#@login_required
def m3u_save():
    if not g.user :
        return "Log in required"
    data = request.get_json()
    print(data)
    f_name = current_app.instance_path + "/u_fls/" + g.user['username'] + "_playlist.m3u8"
    f = open(f_name,'w')
    f.write("#EXTM3U\n")
    for dt in data :
        f.write("#EXTINF:-1 ,{}\n".format(dt.rstrip('\n')))
        f.write("{}\n".format(data[dt].rstrip('\n')))
    f.close()
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
    #print("here")
    #print(current_app.instance_path)
    #print(g.user['username'])
    #return send_from_directory(current_app.instance_path + "/u_fls/", filename=g.user['username'] + "_playlist.m3u8", as_attachment=True)
    fp = os.path.join(current_app.instance_path, 'u_fls')
    fn = g.user['username'] + "_playlist.m3u8"
    if os.path.exists(fp + '/' + fn) :
        return send_from_directory(os.path.abspath(fp), fn, as_attachment=True)
    else :
        return abort(404,"File must be saved")
