import random
import string
import functools
import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_babel import _
from werkzeug.security import check_password_hash, generate_password_hash

from m3u.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = _('Username is required.')
        elif not password:
            error = _('Password is required.')
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            #error = _('User {} is already registered.'.format(username))
            error = _('User is already registered.')

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = _('Incorrect username.')
        elif not check_password_hash(user['password'], password):
            error = _('Incorrect password.')

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('m3u'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('m3u'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def gen_pswd(pl = 8) :
    p_ch = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(p_ch) for i in range(pl))

def process_email(email) :
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE username = ?', (email,)).fetchone()
    if user is not None :
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('m3u'))
    else :
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (email, generate_password_hash(gen_pswd()))
        )
        db.commit()
        flash(_('Your registred. Please log in.'))
        return render_template('auth/login.html')



@bp.route('/yandex', methods=('GET', 'POST'))
def yandex():
    mdata = {
        'grant_type' : 'authorization_code',
        'client_id' : '049c68e5c66c440f8c736d006d4a5989',
        'client_secret' : 'c883e85c44284a849556cc0027882d58'
    }
    if 'code' in request.args :
        mdata['code'] = request.args['code']
        r = requests.post('https://oauth.yandex.ru/token', data = mdata)
        print(r.json())
        if 'access_token' in r.json() :
            tok = r.json()['access_token']
            r = requests.get('https://login.yandex.ru/info', params = { "oauth_token" : tok })
            print(r.json())
            return process_email(r.json()['emails'][0])
    return redirect(url_for('m3u'))

@bp.route('/google', methods=('GET', 'POST'))
def google():
    mdata = {
    'response_type' : 'code',
    'client_id' : '1059153616307-a60m0vusroenkvs0uft36ndon71su2jd.apps.googleusercontent.com',
    'client_secret' : 'cTcMehGeuTvKWLe1gDM5jZ5w',
    #'redirect_uri' : "http://a.abp-te.tk:48889/auth/google",
    'redirect_uri' : "https://abp-m3u.tk/auth/google",
    'scope' : 'https://www.googleapis.com/auth/userinfo.email',
    'grant_type': 'authorization_code'
    }
    if 'code' not in request.args:
        print(mdata['redirect_uri'])
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type={}&client_id={}&redirect_uri={}&scope={}'.
        format(mdata['response_type'], mdata['client_id'], mdata['redirect_uri'], mdata['scope']))
        return redirect(auth_uri)
    else:
        mdata['code'] = request.args.get('code')
        print(mdata['code'])
        mdata.pop('response_type', None)
        r = requests.post('https://oauth2.googleapis.com/token', data=mdata)
        tok = r.json()['access_token']
        print(tok)
        headers = {'Authorization' : 'Bearer {}'.format(tok)}
        print(headers)
        r = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers)
        return process_email(r.json()['email'])
    #return redirect(url_for('m3u'))