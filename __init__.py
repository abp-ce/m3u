import os

from flask import Flask, render_template, request, send_from_directory
from flask_babel import Babel


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        EPG_DATABASE=os.path.join(app.instance_path, 'epg.sqlite'),
        LANGUAGES = {
            'en': 'English',
            'ru': 'Russian'
        }
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    babel = Babel(app)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @babel.localeselector
    def get_locale():
        #return 'en'
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
        
    # a simple page that says hello
    @app.route('/yandex_180e9fedf38f3004.html')
    def yandex_180e9fedf38f3004():
        return render_template('yandex_180e9fedf38f3004.html')
    
    @app.route("/robots.txt")
    @app.route('/sitemap.xml')
    def robots():
        return send_from_directory("static", request.path[1:])

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory("static", "favicon.ico")

    from . import m3u
    m3u.init_app(app)
    app.register_blueprint(m3u.bp)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import telebot
    app.register_blueprint(telebot.bp)

    #from . import blog
    #app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='m3u')

    return app

