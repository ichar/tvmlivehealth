# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy
import random

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsWithGroup, IsWithExtra,
     errorlog, print_to, print_exception
    )

from app.settings import (
     PUBLIC_URL, URL, LANDING_URL,
     DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, TESTNAMES, NO_RESULTS, NO_KEY, gettrans
    )
from app.dialogs.start import help, mainmenu
from app.handlers import *


_MAX_LEN = 3000
_INFO = {
    'ru': (
"""
<b>Экстренная помощь</b>

Связь с дежурным психологом: +7 999 111-22-33
Переход на сайт компании: 
%(landing)s
%(application)s
%(debug)s
""",
"""
<b>Информация о пройденных тестах</b>
""",
"""
<b>Личный кабинет</b>
""",
"""
<b>Главное меню</b>
""",
"""
Вами пройдено всего тестов <b>%s</b> со следующими результатами.
""",
"""
Вами еще не пройдено ни одного теста.
""",
), 
    'uk': (
"""
<b>Екстрена допомога</b>

Зв'язок із черговим психологом: +7 999 111-22-33
Перехід до сайту компанії:  
%(landing)s
%(application)s
%(debug)s
""",
"""
<b>Інформація про пройдені тести</b>
""",
"""
<b>Особистий кабінет</b>
""",
"""
<b>Головне меню</b>
""",
"""
Пройдено всього тестів %s з наступними результатами.
""",
"""
Вами ще не пройдено жодного тесту.
""",
),
}

_KEYS = {
    'ru' : {
        'query_id'    : 'ID', 
        'chat_person' : 'Телеграм-чат', 
        'nic'         : 'Имя пользователя', 
        'date'        : 'Дата последнего посещения', 
        'lang'        : 'Язык', 
        'usage'       : 'Активность', 
        'age'         : 'Возраст', 
        'gender'      : 'Пол', 
        'accept'      : 'Акцепт',
    },
    'uk' : {
        'query_id'    : 'ID', 
        'chat_person' : 'Телеграм-чат', 
        'nic'         : "Ім'я користувача", 
        'date'        : 'Дата останнього відвідування', 
        'lang'        : 'Мова', 
        'usage'       : 'Активність', 
        'age'         : 'Вік', 
        'gender'      : 'Пол', 
        'accept'      : 'Акцепт',
    },
}



def total_questions():
    return 0

def get_info(i, lang, no_eof=None):
    s = _INFO[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_link(href, title, text):
    return '<a href="%s" title="%s">%s</a>' % (href, title, text)

def send(bot, message, info):
    bot.send_message(message.chat.id, info.strip(), parse_mode=DEFAULT_PARSE_MODE)
    return ''

def answer(bot, message, command, data=None, logger=None, keyboard=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    storage = kw.get('storage')
    name = kw.get('name')

    def sortbykeys(values):
        return int(x[1:])

    is_run, is_help = True, False
    url = (URL in PUBLIC_URL or ':5000' not in PUBLIC_URL) and URL or PUBLIC_URL

    params = {
        'url' : url,
    }

    if IsTrace and IsDeepDebug:
        print_to(errorlog, '--> application url:[%s]' % url)

    info = ''

    if not keyboard:
        return
    elif keyboard == 'emergency':
        params['landing'] = get_link(LANDING_URL, keyboard, gettrans('Landing', lang))
        params['application'] = get_link('%s%s' % (url, 'welcome'), keyboard, gettrans('Application site', lang))
        params['debug'] = get_link('%s%s' % (url, 'log'), keyboard, gettrans('Debug', lang))
        info = get_info(0, lang) % params
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        is_help = True

    elif keyboard == 'diagnosis' or command.startswith('D'):
        key = None
        tests = sorted(list(TESTNAMES[lang].keys()), key=lambda x: int(x[1:]))
        if command:
            key = command[1:]
            if key and key.isdigit():
                tests = [x for x in tests if x == 'T%s' % key]
            else:
                info = send(bot, message, get_info(1, lang))
                key = None

        items = storage.get_test_results(name, lang, tests=tests, with_decode=True)
        count = len(items.keys())
        rows = []
        if count > 0:
            if not key:
                info = send(bot, message, get_info(4, lang) % count)
            for test in tests:
                if test in items:
                    info += '\n%s<b>%s %s: "%s"</b>' % ('', gettrans('Test', lang), test, TESTNAMES[lang][test][0])
                    values = sorted(items[test])
                    for i, item in enumerate(values):
                        x = values[i].split(':')

                        if x[0] in ('', NO_KEY) or NO_KEY in x[0]:
                            if IsTrace and IsDeepDebug:
                                print('!!! %s.%s  x:%s' % (test, i, x))
                            continue
                        else:
                            s1 = '. '.join(x[0:-1])
                            s2 = len(x) > 1 and ' [%s]' % x[-1] or ''
                            s = '%s%s' % (s1, s2)
                            if s not in rows:
                                info += '\n%s%s' % (' '*4, s)
                                rows.append(s)
                    info = send(bot, message, info)
        else:
            info = send(bot, message, get_info(5, lang))

    elif keyboard == 'profile':
        info = get_info(2, lang)
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        keys = _KEYS[lang].keys()
        items = storage.get_items(name, keys, with_decode=True)
        info = ''
        for key in keys:
            info += '<b>%s</b>: %s\n' % (_KEYS[lang][key], items[key])
        bot.send_message(message.chat.id, info.strip(), parse_mode=DEFAULT_PARSE_MODE)

    elif keyboard == 'menu':
        info = get_info(3, lang)
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        mainmenu(bot, message, logger=logger, lang=lang)

    else:
        is_run = False

    if not is_run or is_help:
        time.sleep(3)

        help(bot, message, logger=logger, mode=1, **kw)

    return 0
