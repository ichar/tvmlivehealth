# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
#from flask_mail import Mail
#from flask_moment import Moment
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask_log_request_id import RequestID, current_request_id
#from flask.ext.pagedown import PageDown
from config import IsDeepDebug, app_release, config

bootstrap = Bootstrap()
babel = Babel()
#mail = Mail()
#moment = Moment()
db = SQLAlchemy()
#pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'basic' # 'strong'
login_manager.login_view = 'auth.login'

#from .patches import *


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    #app.register_error_handler(403, forbidden)

    bootstrap.init_app(app)
    babel.init_app(app)
    #mail.init_app(app)
    #moment.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    #pagedown.init_app(app)

    #if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
    #    from flask.ext.sslify import SSLify
    #    sslify = SSLify(app)

    RequestID(app)

    from .bot import appbot as bot_blueprint
    app.register_blueprint(bot_blueprint)

    from .scenario import scenario as scenario_blueprint
    app.register_blueprint(scenario_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .semaphore import semaphore as semaphore_blueprint
    app.register_blueprint(semaphore_blueprint, url_prefix='/semaphore')

    from .logger import logger as logger_blueprint
    app.register_blueprint(logger_blueprint, url_prefix='/log')

    if IsDeepDebug:
        print('>>> app created')

    return app
