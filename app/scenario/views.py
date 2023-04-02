# -*- coding: utf-8 -*-

import re

from flask import abort, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, errorlog, print_to, print_exception,
     default_unicode, default_encoding, 
     UTC_FULL_TIMESTAMP
     )

from . import scenario
from .. import db, babel

from ..settings import *
from ..utils import getId, reprSortedDict, getDate, getToday

from app.models import (
     Pagination, Dialog, Question, Answer,
     answers, get_answers
     )


@babel.localeselector
def get_locale():
    return get_request_item('locale') or DEFAULT_LANGUAGE

@scenario.route('/', methods=['GET', 'POST'])
@scenario.route('/index', methods=['GET', 'POST'])
#@login_required
#@admin_required
def index():
    return 'scenario'

@scenario.route('/begin', methods=['GET', 'POST'])
def begin():
    return 'scenario.begin'

@scenario.route('/welcome', methods=['GET', 'POST'])
def welcome():
    kw = make_platform(mode='auth')

    kw.update({
        'title'        : gettext('Application Welcome'),
        'page_title'   : gettext('Welcome!'),
        'header_class' : 'middle-header',
        'show_flash'   : True,
        'module'       : 'scenario',
    })

    kw['vsc'] = vsc()

    return render_template('index.html', **kw)
