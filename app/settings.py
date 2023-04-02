# -*- coding: utf-8 -*-

import re
import random
import json
from datetime import datetime
import pytz
import logging

#https://pypi.org/project/user-agents/
from user_agents import parse as user_agent_parse

from flask import (
    Response, render_template, url_for, redirect, request, make_response, 
    jsonify, url_for, flash, stream_with_context, g, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext, lazy_gettext

from config import (
    CONNECTION, PUBLIC_URL, URL, LANDING_URL, 
    IsDebug, IsDeepDebug, IsTrace, IsLogTrace, IsShowLoader, IsForceRefresh, IsPrintExceptions, IsNoEmail, isIterable,
    basedir, errorlog, print_to, print_exception, default_system_locale,
    default_unicode, default_encoding,
    LOCAL_FULL_TIMESTAMP, LOCAL_EASY_DATESTAMP, UTC_FULL_TIMESTAMP, LOCAL_EASY_TIMESTAMP, LOCAL_EASY_DATESTAMP, PUBLIC_URL, getCurrentDate, 
    TIMEZONE, TIMEZONE_COMMON_NAME,
    is_webhook
)

from .patches import is_limited, is_forbidden
from .utils import getToday, getDate
from .messages import MESSAGES


def setup_locale():
    import os
    import locale
    import platform

    if locale.getlocale()[0] is None:
        locale.setlocale(locale.LC_ALL, default_system_locale)
    info = {'loc': locale.getlocale(), 'lod_def': locale.getdefaultlocale()}

    if IsDeepDebug and IsLogTrace:
        pass #print_to(None, '>>> locale: %s os:%s platform:%s' % (info,  os.name, platform.system()))


#
#   DON'T IMPORT utils HERE !!!
#

product_version = ['1.02.1', '2023-04-01', '(Python3, Redis)']

#########################################################################################

#   -------------
#   Default types
#   -------------

DEFAULT_LANGUAGE = 'ru'
DEFAULT_PARSE_MODE = 'HTML'
DEFAULT_PER_PAGE = 10
DEFAULT_PAGE = 1
DEFAULT_UNDEFINED = '---'
DEFAULT_DATE_FORMAT = ('%d/%m/%Y', '%Y-%m-%d',)
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d< %H:%M:%S'
DEFAULT_DATETIME_INLINE_FORMAT = '<nobr>%Y-%m-%d</nobr> <nobr>%H:%M:%S</nobr>'
DEFAULT_DATETIME_INLINE_SHORT_FORMAT = '<nobr>%Y-%m-%d</nobr><br><nobr>%H:%M</nobr>'
DEFAULT_DATETIME_TODAY_FORMAT = '%d.%m.%Y'
DEFAULT_HTML_SPLITTER = ':'
DEFAULT_USER_AVATAR = ('<img class="avatar" src="%s" title="%s" alt="%s">', '/static/img/person-default.jpg', '', 'jpg', (40, None))

default_locale = 'rus'

SEMAPHORE = {
    'count'    : 7,
    'timeout'  : 5000,
    'action'   : '901',
    'speed'    : '100:1000',
    'seen_at'  : (5,10,),
    'inc'      : (1,1,1,1,1,1,1,),
    'duration' : (9999, 5000, 0, 0, 0, 3000, -1,),
}

BEGIN = (
    'dialogs.begin',
)
"""
    Модули клинической беседы
"""
SCENARIO = (
    ('dialogs.person', None),
    ('dialogs.gender', None),
    ('dialogs.age', None),
    ('dialogs.occupation', None),
    ('dialogs.education', None),
    ('dialogs.marital_status', None),
    ('dialogs.children', None),
    ('dialogs.upbringing', None),
    ('dialogs.childhood', None),
    ('dialogs.family', None),
    ('dialogs.relationships', None),
    ('dialogs.discomfort', None),
    ('dialogs.stress', None),
    ('dialogs.grievance', 23),
)
#
#   Модули обработки тестов
#
TESTS = (
    ('', None),
    ('dialogs.ptest1', 'T1',),
    ('dialogs.ptest2', 'T2',),
    ('dialogs.ptest3', 'T3',),
    ('dialogs.ptest4', 'T4',),
    ('dialogs.ptest5', 'T5',),
    ('dialogs.ptest6', 'T6',),
    ('dialogs.ptest7', 'T7',),
    ('dialogs.ptest8', 'T8',),
    ('dialogs.ptest9', 'T9',),
    ('dialogs.ptest10', 'T10',),
    ('dialogs.ptest11', 'T11',),
    ('dialogs.ptest12', 'T12',),
    ('dialogs.ptest13', 'T13',),
    ('dialogs.ptest14', 'T14',),
    ('dialogs.ptest15', 'T15',),
    ('dialogs.ptest16', 'T16',),
    ('dialogs.ptest17', 'T17',),
)
#
#    Коды результатов
#
RCODES = {
    'NP' : '=P',    # параметр (наименование, текст)
    'RP' : 'RP',    # результат по параметру (число)
    'TP' : 'TP',    # диагноз по параметру (текст)
    'RC' : 'RC',    # итоговый результат (число)
    'TC' : 'TC',    # итоговый диагноз (текст)
}
#
#    Наименования и коды тестов
#
TESTNAMES = {
    'ru': {
        'T1'  : ('Госпитальная шкала тревоги и депрессии (HADS)',                   'Шкала депрессии HADS'),
        'T2'  : ('Индивидуально-типологический опросник Собчик (ИТО)',              'Опросник Собчик ИТО'),
        'T3'  : ('Измерение уровня депрессии (BDI)',                                'Уровень депрессии BDI'),
        'T4'  : ('Уровень тревожности Бека',                                        'Тревожность Бека'),
        'T5'  : ('Острая реакция на стресс',                                        'Острая реакция на стресс'),
        'T6'  : ('Шкала депрессии Цунга',                                           'Шкала депрессии Цунга'),
        'T7'  : ('Определение характеристик темперамента',                          'Характеристики Темперамента'),
        'T8'  : ('Тревожность Тейлора',                                             'Тревожность Тейлора'),
        'T9'  : ('Уровень социальной фрустрированности Вассермана',                 'Уровень Вассермана'),
        'T10' : ('Шкала реактивной и личностной тревожности Спилбергера-Ханина',    'Шкала Спилбергера-Ханина'),
        'T11' : ('Эмоциональное выгорание Бойко',                                   'Выгорание Бойко'),
        'T12' : ('Мотивация к успеху Реана',                                        'Мотивация Реана'),
        'T13' : ('Эмоциональное выгорание Маслач',                                  'Выгорание Маслач'),
        'T14' : ('Диагностика враждебности Кука-Медлея',                            'Враждебность Кука-Медлея'),
        'T15' : ('Акцентуация характера Шмишека',                                   'Характер Шмишека'),
        'T16' : ('Исследование самоотношения Пантелеева',                           'Исследование Пантелеева'),
        'T17' : ('Агрессивность Почебут',                                           'Агрессивность Почебут'),
    },
    'uk': {
        'T1'  : ('Госпітальна шкала тривоги та депресії (HADS)',                    'Шкала тривоги та депресії (HADS)'),
        'T2'  : ('Індивідуально-типологічний опитувальник Собчик (ІТО)',            'Опитувальник Собчик (ІТО)'),
        'T3'  : ('Вимірювання рівня депресії (BDI)',                                'Рівень депресії (BDI)'),
        'T4'  : ('Рівень тривожності Бека',                                         'Рівень тривожності Бека'),
        'T5'  : ('Гостра реакція на стрес',                                         'Гостра реакція на стрес'),
        'T6'  : ('Шкала депресії Цунга',                                            'Шкала депресії Цунга'),
        'T7'  : ('Визначення характеристик темпераменту',                           'Характеристики темпераменту'),
        'T8'  : ('Тривожність Тейлора',                                             'Тривожність Тейлора'),
        'T9'  : ('Рівень соціальної фрустрованність Васермана',                     'Рівень Васермана'),
        'T10' : ('Шкала реактивної і особистісної тривожності Спілбергера-Ханіна',  'Шкала Спілбергера-Ханіна'),
        'T11' : ('Емоційне вигорання Бойко',                                        'Емоційне вигорання Бойко'),
        'T12' : ('Мотивацію до успіху Реана',                                       'Мотивація Реана'),
        'T13' : ('Психологічне вигорання Маслач',                                   'Вигорання Маслач'),
        'T14' : ('Діагностика ворожості Кука-Медлея',                               'Ворожость Кука-Медлея'),
        'T15' : ('Акцентуація характеру Шмішека',                                   'Характер Шмішека'),
        'T16' : ('Дослідження самоставлення Пантєєлєва',                            'Дослідження Пантєєлєва'),
        'T17' : ('Агресивність Почебут',                                            'Агресивність Почебут'),
    },
    'en': {
         'T1' : ('Hospital Anxiety and Depression Scale (HADS)', 'HADS Anxiety and Depression Scale'),
         'T2' : ('Individual-typological questionnaire Sobchik (ITO)', 'Questionnaire Sobchik ITO'),
         'T3' : ('BDI Depression Measurement', 'BDI Depression Level'),
         'T4' : ('Beck\'s Anxiety Level', 'Beck\'s Anxiety'),
         'T5' : ('Acute stress reaction', 'Acute stress reaction'),
         'T6' : ('Zung Depression Scale', 'Zung Depression Scale'),
         'T7' : ('Determining Temperament Characteristics', 'Temperament Characteristics'),
         'T8' : ('Taylor anxiety', 'Taylor anxiety'),
         'T9' : ('Wasserman\'s social frustration level', 'Wasserman\'s level'),
         'T10': ('Spielberger-Khanin Reactive and Personal Anxiety Scale', 'Spielberger-Khanin Scale'),
         'T11': ('Boiko\'s burnout', 'Boiko\'s burnout'),
         'T12': ('Rean\'s motivation for success', 'Rean\'s motivation'),
         'T13': ('Burnout Maslach', 'Burnout Maslach'),
         'T14': ('Cook-Medley Hostility Diagnostic', 'Cook-Medley Hostility'),
         'T15': ('Schmishek character accent', 'Schmishek character'),
         'T16': ('Panteleev\'s study of self-attitude', 'Panteleev\'s study'),
         'T17': ('Pochebut Aggressiveness', 'Pochebut Aggressiveness'),    
    },
}
#
#   Уровень диагноза
#z`
_LEVELS = {
    'T1' : ((0, 'normal'), (9, 'middle'), (90, 'high'),),
    'T2' : ((2, 'low'), (4, 'normal'), (6, 'middle'), (9, 'high'),),
    'T3' : ((9, 'low'), (18, 'normal'), (29, 'middle'), (63, 'high'),),
    'T4' : ((9, 'low'), (18, 'normal'), (29, 'middle'), (63, 'high'),),
    'T5' : ((3, 'normal'), (17, 'middle'), (34, 'high'),),
    'T6' : ((49, 'normal'), (59, 'middle'), (69, 'high'),),
    'T7.TP2' : ((6, 'low'), (11, 'normal'), (15, 'middle'), (28, 'high'),),
    'T7.TP4' : ((8, 'low'), (13, 'normal'), (19, 'middle'), (29, 'high'),),
    'T8' : ((5, 'low'), (25, 'normal'), (40, 'middle'), (50, 'high'),),
    'T9' : ((0.4, ''), (1.9, 'low'), (2.4, 'normal'), (3.4, 'middle'), (4.0, 'high'),),
    'T10' : ((31, 'low'), (45, 'middle'), (69, 'high'),),
    'T11' : ((9, 'low'), (15, 'middle'), (30, 'high'),),
    'T12' : ((7, 'low'), (10, 'middle'), (13, 'normal'), (20, 'high'),),
    'T13.TP01' : ((10, 'low'), (20, 'middle'), (30, 'normal'), (40, 'high'),),
    'T13.TP02' : ((5, 'low'), (11, 'middle'), (17, 'normal'), (23, 'high'),),
    'T13.TP02' : ((18, 'high'), (28, 'middle'), (38, 'normal'), (48, 'low'),),
    'T13.TCF1' : ((23, 'low'), (49, 'middle'), (75, 'normal'), (101, 'high'),),
    'T14.TP01' : ((25, 'low'), (40, 'normal'), (64, 'middle'), (78, 'high'),),
    'T14.TP02' : ((15, 'low'), (30, 'normal'), (45, 'middle'), (54, 'high'),),
    'T14.TP03' : ((10, 'low'), (18, 'normal'), (25, 'middle'), (30, 'high'),),
    'T15' : ((12, 'normal'), (18, 'middle'), (24, 'high'),),
    'T16.TP01' : ((1, 'normal'), (8, 'middle'), (11, 'high'),),
    'T16.TP02' : ((4, 'normal'), (11, 'middle'), (14, 'high'),),
    'T16.TP03' : ((3, 'normal'), (8, 'middle'), (12, 'high'),),
    'T16.TP04' : ((2, 'normal'), (8, 'middle'), (11, 'high'),),
    'T16.TP05' : ((3, 'normal'), (10, 'middle'), (14, 'high'),),
    'T16.TP06' : ((4, 'normal'), (9, 'middle'), (12, 'high'),),
    'T16.TP07' : ((2, 'normal'), (8, 'middle'), (11, 'high'),),
    'T16.TP08' : ((2, 'normal'), (12, 'middle'), (15, 'high'),),
    'T16.TP09' : ((2, 'normal'), (8, 'middle'), (10, 'high'),),
    'T17' : ((2, 'normal'), (4, 'middle'), (8, 'high'),),
}

def conclusion_level(tp, value):
    if '.' in value:
        v = float(value)
    else:
        v = int(value)
    if value:
        if tp not in _LEVELS:
            test, _ = tp.split('.')
        else:
            test = tp
        for x, level in _LEVELS.get(test, ((0, ''),)):
            if x >= v:
                return level
    return ''
#
#   Главное меню
#
STARTMENU = {
    'ru': [
        (('Беседа', 'begin:0'), ('Тесты', 'tests:0')), 
        { 
            'Экстренная помощь'              : 'emergency', 
            'Информация о пройденных тестах' : 'diagnosis', 
            'Личный кабинет'                 : 'profile',
            'Главное меню'                   : 'menu',
        }, 
        (('', '')),
    ],
    'uk': [
        (('Бесіда', 'begin:0'), ('Тести', 'tests:0')), 
        { 
            'Екстрена допомога'              : 'emergency', 
            'Інформація про пройдені тести'  : 'diagnosis', 
            'Особистий кабінет'              : 'profile',
            'Головне меню'                   : 'menu',
        }, 
        (('', '')),
    ],
}
#
#   Словарь ключевых слов (переводы)
#
_TRANS = {
    'ru': {
        "#"                : "№",
        "Landing"          : "Портал психологического здоровья",
        "Application site" : "Сайт приложения",
        "Debug"            : "Журнал бота",
        "Test"             : "Тест",
        "total questions"  : "всего вопросов",
    },
    'uk': {
        "#"                : "№",
        "Landing"          : "Портал психологічного здоров'я",
        "Application site" : "Сайт програми",
        "Debug"            : "Журнал бота",
        "Test"             : "Тест",
        "total questions"  : "всього питань",
    },
}

KEYBOARD = (
    'dialogs.keyboard',
)

THANKS = (
    'dialogs.thanks',
)

END = (
    'dialogs.end',
)

NO_RESULTS = 'not enough results'
NO_DATA = 'no data'
NO_KEY = '...'

default_locale = 'rus'


def tests_count():
    return len(TESTS)

def gettrans(key, lang):
    return _TRANS[lang or DEFAULT_LANGUAGE].get(key) or key

## ================================================== ##



class DataEncoder(json.JSONEncoder):
    def default(self, ob):
        if isinstance(ob, decimal.Decimal):
            return str(ob)
        return json.JSONEncoder.default(self, ob)


def app_logger(mode, message, force=None, is_error=False, is_warning=False, is_info=False, data=None, **kw):
    #
    #   g.app_logger
    #
    if IsDisableOutput or not IsLogTrace:
        return
    line = ': mode[{mode:<12}] : {ip} : {host} : login=[{login:<10}] : {message} {data}'.format(
        mode= mode,
        ip= request.remote_addr,
        host= kw.get('host') or request.form.get('host') or request.host_url,
        login= g.current_user.is_authenticated and g.current_user.login or 'AnonymousUser',
        message= message,
        data= data and '\n%s' % data or '',
    )
    if IsDeepDebug:
        print_to(None, line)
    if IsLogTrace:
        if is_error:
            g.app_logging.error(line)
        elif is_warning:
            g.app_logging.warning(line)
        elif IsTrace and (force or is_info):
            g.app_logging.info(line)
    if IsFlushOutput:
        sys.stdout.flush()


def setup_logging(log):
    if not IsLogTrace:
        return
    try:
        if g.app_logger is not None:
            return
    except:
        pass

    P_TIMEZONE = pytz.timezone(TIMEZONE)

    logging.basicConfig(
        filename=log,
        format='%(asctime)s : %(name)s-%(levelname)s >>> %(message)s', 
        level=logging.DEBUG, 
        datefmt=UTC_FULL_TIMESTAMP,
    )

    g.app_logging = logging.getLogger(__name__)
    g.app_logger = app_logger


def clearFlash(msg, is_save_one=None):
    key = '_flashes'
    if key not in session:
        return
    is_exist = 0
    for i, (m, x) in enumerate(session[key]):
        if msg == x:
            is_exist = 1
        if not x:
            pass
    if is_exist:
        session['_flashes'].clear()
    if is_save_one:
        flash(msg)


_agent = None
_user_agent = None

def IsAndroid():
    return _agent.platform == 'android'
def IsiOS():
    return _agent.platform == 'ios' or 'iOS' in _user_agent.os.family
def IsiPad():
    return _agent.platform == 'ipad' or 'iPad' in _user_agent.os.family
def IsLinux():
    return _agent.platform == 'linux'

def IsChrome():
    return _agent.browser == 'chrome'
def IsFirefox():
    return _agent.browser == 'firefox'
def IsSafari():
    return _agent.browser == 'safari' or 'Safari' in _user_agent.browser.family
def IsOpera():
    return _agent.browser == 'opera' or 'Opera' in _user_agent.browser.family

def IsIE(version=None):
    ie = _agent.browser.lower() in ('explorer', 'msie',)
    if not ie:
        return False
    elif version:
        return float(_agent.version) == version
    return float(_agent.version) < 10
def IsSeaMonkey():
    return _agent.browser.lower() == 'seamonkey'
def IsEdge():
    return 'Edge' in _agent.string
def IsMSIE():
    return _agent.browser.lower() in ('explorer', 'ie', 'msie', 'seamonkey',) or IsEdge()

def IsMobile():
    return IsAndroid() or IsiOS() or IsiPad() or _user_agent.is_mobile or _user_agent.is_tablet
def IsNotBootStrap():
    return IsIE(10) or IsAndroid()
def IsWebKit():
    return IsChrome() or IsFirefox() or IsOpera() or IsSafari()

def IsMobile():
    return IsAndroid() or IsiOS() or IsiPad() or _user_agent.is_mobile or _user_agent.is_tablet
def IsNotBootStrap():
    return IsIE(10) or IsAndroid()
def IsWebKit():
    return IsChrome() or IsFirefox() or IsOpera() or IsSafari()

def BrowserVersion():
    return _agent.version

def BrowserInfo(force=None):
    mobile = 'IsMobile:[%s]' % (IsMobile() and '1' or '0')
    info = 'Browser:[%s] %s Agent:[%s]' % (_agent.browser, mobile, _agent.string)
    browser = IsMSIE() and 'IE' or IsOpera() and 'Opera' or IsChrome() and 'Chrome' or IsFirefox() and 'FireFox' or IsSafari() and 'Safari' or None
    if force:
        return info
    return browser and '%s:%s' % (browser, mobile) or info

## -------------------------------------------------- ##

def get_request_item(name, check_int=None, args=None, is_iterable=None):
    if args:
        x = args.get(name)
    elif request.method.upper() == 'POST':
        if is_iterable:
            return request.form.getlist(name)
        else:
            x = request.form.get(name)
    else:
        x = None
    if not x and (not check_int or (check_int and x in (None, ''))):
        x = request.args.get(name)
    if check_int:
        if x in (None, ''):
            return None
        elif x.isdigit():
            return int(x)
        elif x in 'yY':
            return 1
        elif x in 'nN':
            return 0
        else:
            return None
    if x:
        if x == DEFAULT_UNDEFINED or x.upper() == 'NONE':
            x = None
        elif x.startswith('{') and x.endswith('}'):
            return eval(re.sub('null', '""', x))
    return x or ''

def get_request_items():
    return request.method.upper() == 'POST' and request.form or request.args

def has_request_item(name):
    return name in request.form or name in request.args

def get_request_search():
    return get_request_item('reset_search') != '1' and get_request_item('search') or ''

def get_page_params(view=None):
    pass

def default_user_avatar(user=None):
    pass

# ===========================


def maketext(key, lang=None, force=None):
    request_lang = get_request_item('lang')
    text = key
    try:
        text = gettext(key)
    except:
        pass
    if request_lang == 'en':
        return key
    if text == key or force:
        if key in MESSAGES:
            text = MESSAGES[key][request_lang or lang or DEFAULT_LANGUAGE]
    return text or key


def make_platform(mode=None, debug=None):
    global _agent, _user_agent

    agent = request.user_agent
    browser = agent.browser

    if browser is None:
        return { 'error' : 'Access is not allowed!' }

    os = agent.platform
    root = '%s/' % request.script_root

    _agent = agent
    _user_agent = user_agent_parse(agent.string)

    if IsTrace:
        print_to(errorlog, '\n==> agent:%s[%s], browser:%s' % (repr(agent), _user_agent, browser), request=request)

    is_owner = False
    is_admin = False
    is_manager = True
    is_operator = False
    is_superuser = False

    avatar = None
    sidebar_collapse = not (int(get_request_item('sidebar') or 0) and True or False)

    try:
        if g.current_user is not None:
            is_superuser = g.current_user.is_superuser(private=True)
            is_owner = g.current_user.is_owner()
            is_admin = g.current_user.is_administrator(private=False)
            is_manager = g.current_user.is_manager(private=True)
            is_operator = g.current_user.is_operator(private=True)
            avatar = g.current_user.get_avatar()

            if has_request_item('sidebar'):
                sidebar_collapse = get_request_item('sidebar', check_int=True) == 0 and True or False
                if sidebar_collapse != g.current_user.sidebar_collapse:
                    g.current_user.sidebar_collapse = sidebar_collapse
            else:
                # By default Sidebar is expanded (state:0)
                sidebar_collapse = g.current_user.sidebar_collapse or False
            
            g.current_user.sidebar_collapse = sidebar_collapse
        else:
            pass
    except:
        pass

    sidebar_state = not sidebar_collapse and 1 or 0

    referer = ''
    links = {}

    is_mobile = IsMobile()
    is_default = 1 or os in ('ipad', 'android',) and browser in ('safari', 'chrome',) and 1 or 0 
    is_frame = not is_mobile and 1 or 0

    version = agent.version
    css = IsMSIE() and 'ie' or is_mobile and 'mobile' or 'web'

    platform = '[os:%s, browser:%s (%s), css:%s, %s %s%s%s]' % (
        os, 
        browser, 
        version, 
        css, 
        default_locale, 
        is_default and ' default' or ' flex',
        is_frame and ' frame' or '', 
        debug and ' debug' or '',
    )

    kw = {
        'os'             : os, 
        'platform'       : platform,
        'root'           : root, 
        'back'           : '',
        'agent'          : agent.string,
        'version'        : version, 
        'browser'        : browser, 
        'browser_info'   : BrowserInfo(0),
        'is_linux'       : IsLinux() and 1 or 0,
        'is_demo'        : 0, 
        'is_frame'       : is_frame, 
        'is_mobile'      : is_mobile and 1 or 0,
        'is_superuser'   : is_superuser and 1 or 0,
        'is_admin'       : is_admin and 1 or 0,
        'is_operator'    : (is_operator or is_manager or is_admin) and not is_owner and 1 or 0,
        'is_show_loader' : IsShowLoader,
        'is_explorer'    : IsMSIE() and 1 or 0,
        'css'            : css, 
        'referer'        : referer, 
        'bootstrap'      : '',
        'model'          : 0,
    }

    if mode:
        kw[mode] = True

    if mode in ('auth', 'database',):
        kw['bootstrap'] = '-new'

    kw.update({
        'links'          : links, 
        'style'          : {'default' : is_default, 'header' : datetime.today().day%2==1 and 'dark' or 'light', 'show_scroller' : 0},
        'screen'         : request.form.get('screen') or '',
        'scale'          : request.form.get('scale') or '',
        'usertype'       : is_manager and 'manager' or is_operator and 'operator' or 'default',
        'sidebar'        : {'state' : sidebar_state, 'title' : maketext('Click to close top menu')},
        'avatar'         : avatar,
        'with_avatar'    : 1,
        'with_post'      : 1,
        'logo'           : '', 
        'image_loader'   : '%s%s' % (root, 'static/img/loader.gif'), 
        'is_main'        : 1,
    })

    kw['is_active_scroller'] = 0 if IsMSIE() or IsFirefox() or is_mobile else 1
    kw['product_version'] = product_version
    kw['vsc'] = vsc(force=g.system_config.IsForceRefresh)

    if IsTrace and IsDeepDebug:
        print_to(errorlog, '--> make_platform:%s' % mode)

    return kw

def make_keywords():
    return (
        # --------------
        # Error Messages
        # --------------
        "'Execution error':'%s'" % maketext('Execution error'),
        # -------
        # Buttons
        # -------
        "'Add':'%s'" % maketext('Add'),
        "'Back':'%s'" % maketext('Back'),
        "'Calculate':'%s'" % maketext('Calculate'),
        "'Cancel':'%s'" % maketext('Cancel'),
        "'Confirm':'%s'" % maketext('Confirm'),
        "'Close':'%s'" % maketext('Close'),
        "'Execute':'%s'" % maketext('Execute'),
        "'Finished':'%s'" % maketext('Done'),
        "'Frozen link':'%s'" % maketext('Frozen link'),
        "'Link':'%s'" % maketext('Link'),
        "'OK':'%s'" % maketext('OK'),
        "'Open':'%s'" % maketext('Open'),
        "'Reject':'%s'" % maketext('Decline'),
        "'Rejected':'%s'" % maketext('Rejected'),
        "'Remove':'%s'" % maketext('Remove'),
        "'Run':'%s'" % maketext('Run'),
        "'Save':'%s'" % maketext('Save'),
        "'Search':'%s'" % maketext('Search'),
        "'Select':'%s'" % maketext('Select'),
        "'Update':'%s'" % maketext('Update'),
        # ----
        # Help
        # ----
        "'Attention':'%s'" % maketext('Attention'),
        "'All':'%s'" % maketext('All'),
        "'Commands':'%s'" % maketext('Commands'),
        "'Help':'%s'" % maketext('Help'),
        "'Help information':'%s'" % maketext('Help information'),
        "'Helper keypress guide':'%s'" % maketext('Helper keypress guide'),
        "'System information':'%s'" % maketext('System information'),
        "'Total':'%s'" % maketext('Total'),
        # --------------------
        # Flags & Simple Items
        # --------------------
        "'error':'%s'" % maketext('error'),
        "'yes':'%s'" % maketext('Yes'),
        "'no':'%s'" % maketext('No'),
        "'none':'%s'" % maketext('None'),
        "'true':'%s'" % 'true',
        "'false':'%s'" % 'false',
        # ------------------------
        # Miscellaneous Dictionary
        # ------------------------
        "'batch':'%s'" % maketext('batch'),
        # -------------
        # Notifications
        # -------------
        "'Admin Find':'%s'" % maketext('Find (name, login, email)'),
    )

def init_response(title, mode):
    host = request.form.get('host') or request.host_url

    if 'debug' in request.args:
        debug = request.args['debug'] == '1' and True or False
    else:
        debug = None

    kw = make_platform(debug=debug)
    keywords = make_keywords()
    forms = ('index', 'admin',)

    now = datetime.today().strftime(DEFAULT_DATE_FORMAT[1])

    kw.update({
        'title'        : '%s. %s' % (maketext('ADVANCEMENTALHEALTHGROUP'), maketext(title)),
        'host'         : host,
        'locale'       : default_locale, 
        'language'     : DEFAULT_LANGUAGE == 'uk' and 'uk' or 'ru',
        'keywords'     : keywords, 
        'forms'        : forms,
        'now'          : now,
    })

    kw['selected_data_menu_id'] = get_request_item('selected_data_menu_id')
    kw['window_scroll'] = get_request_item('window_scroll')
    kw['avatar_width'] = '80'

    return debug, kw

def vsc(force=False):
    return (IsIE() or IsForceRefresh or force) and ('?%s' % str(int(random.random()*10**12))) or ''

def is_app_public():
    return IsPublic and request.host_url == PUBLIC_URL

def get_navigation():
    return None
