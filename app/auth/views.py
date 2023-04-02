# -*- coding: utf-8 -*-

import os

from flask import abort, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from werkzeug.urls import url_quote, url_unquote

from flask import session
#from passlib.hash import pbkdf2_sha256 as hasher

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsNoEmail, IsPageClosed, page_redirect, errorlog, print_to, print_exception,
     default_unicode, default_encoding, LOG_PATH, LOG_NAME
     )

from . import auth
from ..import db, babel

from ..decorators import user_required
from ..utils import normpath, monthdelta, unquoted_url, decode_base64, getDate, getToday
from ..models import User, send_email, load_system_config
from ..database import get_locale as get_user_locale
from ..settings import *

from .forms import LoginForm, ChangePasswordForm, ResetPasswordRequestForm, PasswordResetForm, RegistrationForm

IsResponseNoCached = 0

_EMERGENCY_EMAILS = ('ichar.xx@gmail.com',)

##  ===========================
##  User Authentication Package
##  ===========================

@babel.localeselector
def get_locale():
    return get_request_item('locale') or get_user_locale()

def is_valid_pwd(x):
    v = len(x) > 9 or (len(x) > 7 and
        len(re.sub(r'[\D]+', '', x)) > 0 and
        len(re.sub(r'[\d]+', '', x)) > 0 and
        len(re.sub(r'[\w]+', '', x)) > 0) \
        and True or False
    return v

def is_pwd_changed(user):
    pass

def send_message(user, token, **kw):
    pass

def send_password_reset_email(user, **kw):
    pass

def _init():
    setup_locale()
    g.maketext = maketext
    g.app_product_name = maketext('AppProductName')

    load_system_config(g.current_user)

    today = getDate(getToday(), format=LOCAL_EASY_DATESTAMP)
    log = normpath(os.path.join(basedir, LOG_PATH, '%s_%s.log' % (today, LOG_NAME)))

    g.users_registered_required = False

    setup_logging(log)


@auth.before_app_request
def before_request():
    g.current_user = current_user = None
    g.engine = None

    if not request.endpoint:
        return

    if IsTrace and IsDeepDebug:
        print_to(errorlog, '--> before_request endpoint:%s' % request.endpoint)

    if request.endpoint != 'static':
        _init()

    if current_user is not None:
        if IsDeepDebug:
            print('--> before_request:is_authenticated:%s is_active:%s' % (current_user.is_authenticated, current_user.is_active))
            
        if request.endpoint[:5] != 'auth.' and request.endpoint != 'static' and not current_user.is_authenticated:
            pass
    
        if current_user.is_authenticated and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            if not current_user.confirmed:
                return redirect(url_for('auth.unconfirmed'))
            if not is_pwd_changed(current_user):
                current_user.unconfirmed()
                return redirect(url_for('auth.change_password'))
            if request.blueprint in APP_MODULES and request.endpoint.endswith('start'):
                current_user.ping()
            if IsPageClosed and (request.blueprint in page_redirect['items'] or '*' in page_redirect['items']) and \
                current_user.login not in page_redirect['logins'] and 'loader' not in request.url:
                if 'onservice' in page_redirect['base_url']:
                    url = url_for('auth.onservice') + '?next=%s' % url_quote(request.full_path)
                else:
                    url = '%s%s' % (page_redirect['base_url'], request.full_path)
                return redirect(url)

def get_default_url(user=None):
    pass

def menu(force=None):
    pass

@auth.route('/login', methods=['GET', 'POST'])
def login():
    pass

@auth.route('/default', methods=['GET', 'POST'])
def default():
    pass

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    pass

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    pass

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    pass

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth.route('/forbidden')
def forbidden():
    abort(403)

@auth.route('/onservice')
def onservice():
    if not IsPageClosed:
        next = request.args.get('next')
        return redirect(next or '/')
        
    kw = make_platform(mode='auth')

    kw.update({
        'title'        : maketext('Application Login'),
        'page_title'   : maketext('Application Auth'),
        'header_class' : 'middle-header',
        'show_flash'   : True,
        'semaphore'    : {'state' : ''},
        'sidebar'      : {'state' : 0, 'title' : ''},
        'module'       : 'auth',
        'message'      : page_redirect.get('message') or maketext('Software upgrade'),
    })

    kw['vsc'] = vsc()

    return render_template('auth/onservice.html', **kw)

@auth.route('/unconfirmed')
def unconfirmed():
    pass

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    pass
