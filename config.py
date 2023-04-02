# -*- coding: utf-8 -*-

import os
import sys
import datetime
import traceback
import re

from collections.abc import Iterable

basedir = os.path.abspath(os.path.dirname(__file__))
errorlog = os.path.join(basedir, 'traceback.log')

app_release = 1

is_webhook = True

# ----------------------------
# Global application constants
# ----------------------------

IsDebug                = 1  # Debug[errorlog]: prints general info
IsDeepDebug            = 1  # Debug[errorlog]: prints detailed info, replicate to console
IsTrace                = 1  # Trace[stdout]: output trace
IsMakeDump             = 0  # Dump[stdout]: make storage dump in activate
IsPrintExceptions      = 1  # Flag: sets printing of exceptions
IsDeleteChatInOpen     = 0  # Flag: delete person chat results when it is selected
IsShowAnswerResult     = 1  # Flag: show answer result for every question (tests)
IsWithPrintErrors      = 1  # Flag: print selftest errors
IsRandomScores         = 1  # Flag: random score results letters
IsWithGroup            = 1  # Flag: output results with groups
IsWithExtra            = 1  # Flag: with extra answers
IsWithErrorlog         = 0  # Flag: use errorlog to print exceptions
IsTmpClean             = 1  # Flag: clean temp-folder
IsForceRefresh         = 1  # Flag: sets http forced refresh for static files (css/js)
IsDisableOutput        = 0  # Flag: disabled stdout
IsShowLoader           = 0  # Flag: sets page loader show enabled
IsNoEmail              = 1  # Flag: don't send email
IsFlushOutput          = 1  # Flag: flush stdout
IsPageClosed           = 0  # Flag: page is closed or moved to another address (page_redirect)

IsSemaphoreTrace       = 0  # Trace[errorlog]: output trace for semaphore actions
IsLogTrace             = 0  # Trace[errorlog]: output detailed trace for Log-actions
IsTmpClean             = 1  # Flag: clean temp-folder

DEFAULT_ROOT = {
    'local'  : 'https://tvmlivehealth.herokuapp.com/',
    'public' : 'https://tvmlivehealth.herokuapp.com/',
}
PUBLIC_URL = 'https://tvmlivehealth.herokuapp.com/'

page_redirect = {
    'items'    : ('*',),
    'base_url' : '/auth/onservice',
    'logins'   : ('admin',),
    'message'  : 'Waiting 30 sec',
}

SEMAPHORE_TEMPLATE = ''

LocalDebug = {
    'scenario'    : 0,
}

LOCAL_FULL_TIMESTAMP   = '%d-%m-%Y %H:%M:%S'
LOCAL_EXCEL_TIMESTAMP  = '%d.%m.%Y %H:%M:%S'
LOCAL_EASY_TIMESTAMP   = '%d-%m-%Y %H:%M'
LOCAL_EASY_DATESTAMP   = '%Y-%m-%d'
LOCAL_EXPORT_TIMESTAMP = '%Y%m%d%H%M%S'
UTC_FULL_TIMESTAMP     = '%Y-%m-%d %H:%M:%S'
UTC_EASY_TIMESTAMP     = '%Y-%m-%d %H:%M'
DATE_TIMESTAMP         = '%d/%m'
DATE_STAMP             = '%Y%m%d'

default_print_encoding = 'utf-8'
default_unicode        = 'utf-8'
default_encoding       = 'utf-8'
default_iso            = 'ISO-8859-1'


default_system_locale  = 'en_US.UTF-8'
####default_system_locale  = 'ru_RU.UTF-8'
default_chunk = 1000
# ------------------------------------
# TVMLiveHealthBot (tvmlivehealth_bot)
# ------------------------------------

URL = "https://tvmlivehealth.herokuapp.com/"
LANDING_URL = "http://mentalne.pro/landing/#"

BOT_NAME = 'TVMLiveHealthBot'
BOT_USERNAME = 'tvmlivehealth_bot'
TOKEN = '1909759017:AAGGC4ea7deL1W0LgVlMnT_-gmdm_1_SCBc' # XXX
TELEGRAM_URL = 'https://api.telegram.org/bot1909759017:AAGGC4ea7deL1W0LgVlMnT_-gmdm_1_SCBc' #/getwebhookinfo
TIMEZONE = 'Europe/Kiev'
TIMEZONE_COMMON_NAME = 'Kiev'

LOG_PATH = './logs'
LOG_NAME = 'bot'

# ----------------------------

CONNECTION = {}

# ----------------------------

ansi = not sys.platform.startswith("win")

path_splitter = '/'
n_a = 'n/a'
cr = '\n'

_config = None

def isIterable(v):
    return not isinstance(v, str) and isinstance(v, Iterable)

########################################################################

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    WTF_CSRF_ENABLED = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'storage', 'app.db.debug')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'storage', 'app.db')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = { \
    'production' : ProductionConfig,
    'default'    : DevelopmentConfig,
}

##  --------------------------------------- ##

def setup_console(sys_enc=default_unicode):
    pass

def print_to(f, v, mode='ab', request=None, encoding=default_encoding):
    if IsDisableOutput:
        return
    items = not isIterable(v) and [v] or v
    if not f:
        f = getErrorlog()
    fo = open(f, mode=mode)
    def _out(s):
        if not isinstance(s, bytes):
            fo.write(s.encode(encoding, 'ignore'))
        else:
            fo.write(s)
        fo.write(cr.encode())
    for text in items:
        try:
            if IsDeepDebug:
                print(text)
            if request is not None:
                _out('%s>>> %s [%s]' % (cr, datetime.datetime.now().strftime(UTC_FULL_TIMESTAMP), request.url))
            _out(text)
        except Exception as e:
            pass
    fo.close()

def print_exception(stack=None):
    if IsWithErrorlog:
        print_to(errorlog, '%s>>> %s:%s' % (cr, datetime.datetime.now().strftime(LOCAL_FULL_TIMESTAMP), cr))
        traceback.print_exc(file=open(errorlog, 'a'))
        if stack is not None:
            print_to(errorlog, '%s>>> Traceback stack:%s' % (cr, cr))
            traceback.print_stack(file=open(errorlog, 'a'))
    else:
        print('%s>>> %s:%s' % (cr, datetime.datetime.now().strftime(LOCAL_FULL_TIMESTAMP), cr))
        traceback.print_exc()
        if stack is not None:
            print('%s>>> Traceback stack:%s' % (cr, cr))
            traceback.print_stack()

def getErrorlog():
    return errorlog

def getCurrentDate():
    return datetime.datetime.now().strftime(LOCAL_EASY_DATESTAMP)
