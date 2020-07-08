import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


def get_db(epg=False):
    if epg:
        if 'epg_db' not in g:
            g.epg_db = sqlite3.connect(
                current_app.config['EPG_DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.epg_db.row_factory = sqlite3.Row

        return g.epg_db
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_epg_db(e=None):
    db = g.pop('epg_db', None)
    if db is not None:
        db.close()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(fn):
    if 'epg' in fn: db = get_db(epg=True)
    else: db = get_db()
    if 'secret' in fn :
        with current_app.open_instance_resource(fn) as f:
           db.executescript(f.read().decode('utf8'))
    else :
        with current_app.open_resource(fn) as f:
            db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db('schema.sql')
    click.echo('Initialized the database.')

@click.command('pop-db')
@with_appcontext
def pop_db_command():
    init_db('secrets.sql')
    click.echo('Populated the database.')

@click.command('pop-epg-db')
@with_appcontext
def pop_epg_db_command():
    db = get_db(epg=True)
    f_name = current_app.instance_path + "/xmltv.xml"
    for event, elem in ET.iterparse(f_name, events=("start","end")):
        if elem.tag == "channel" and event == "end":
            ch_id = disp_name = icon = None
            ch_id = elem.attrib['id']
            ch = elem.getchildren()
            for c in ch:
                if c.tag == 'display-name':
                    disp_name = c.text
                elif c.tag == 'icon':
                    icon = c.attrib['src']
            db.execute(
                'INSERT INTO channel (ch_id, disp_name, icon) VALUES (?, ?, ?)',
                (ch_id, disp_name.lower(), icon)
            )
            #db.commit()
            elem.clear()
        if elem.tag == "programme" and event == "end":
            channel = pstart = pstop = title = pdesc = cat = None
            channel = elem.attrib['channel']
            st = elem.attrib['start']
            pstart = datetime(int(st[:4]),int(st[4:6]),int(st[6:8]),int(st[8:10]),int(st[10:12]),int(st[12:14]))
            pstart -= timedelta(hours=int(st[14:18]), minutes=int(st[18:]))
            st = elem.attrib['stop']
            pstop = datetime(int(st[:4]),int(st[4:6]),int(st[6:8]),int(st[8:10]),int(st[10:12]),int(st[12:14]))
            pstop -= timedelta(hours=int(st[14:18]), minutes=int(st[18:]))
            ch = elem.getchildren()
            for c in ch :
                if c.tag == 'title':
                    title = c.text
                elif c.tag == 'desc':
                    pdesc = c.text
                elif c.tag == 'category':
                    cat = c.text
            db.execute(
                'INSERT INTO programme (channel, pstart, pstop, title, pdesc, cat) VALUES (?, ?, ?, ?, ?, ?)',
                (channel, pstart, pstop, title, pdesc, cat)
            )
            #db.commit()
            elem.clear()
    db.commit()

@click.command('init-epg-db')
@with_appcontext
def init_epg_command():
    init_db('epg.sql')
    click.echo('Initialized the epg database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_epg_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(pop_db_command)
    app.cli.add_command(init_epg_command)
    app.cli.add_command(pop_epg_db_command)


