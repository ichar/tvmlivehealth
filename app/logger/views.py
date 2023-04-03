# -*- coding: utf-8 -*-

import os
import sys
import re
from urllib.parse import urlparse

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, errorlog, print_to, print_exception,
     default_unicode, default_encoding, 
     UTC_FULL_TIMESTAMP
     )

from . import logger
from .. import db, babel

from ..settings import *
from ..utils import getId, reprSortedDict, getDate, getToday, spent_time, Capitalize
from ..dialogs.scenario import activate, deactivate

from ..models import load_system_config


_DEBUG_HTML = ''
_RES_PREFIX = '.R'
_TEXT_PREFIX = '.T'

@babel.localeselector
def get_locale():
    return get_request_item('locale') or DEFAULT_LANGUAGE


@logger.before_app_request
def before_request():
    g.storage = None
    g.chat = None


def before(f):
    def wrapper(*args, **kw):
        g.chat, g.storage = activate('', 0, '')
        try:
            return f(*args, **kw)
        finally:
            deactivate(g.chat, g.storage)
    return wrapper

## ===============================

def _sorted_keys(keys, key):
    #
    #   Sort items keys by given key
    #
    def _skey(x):
        return ('00'+str(x))[-2:]
    def _question(x):
        k = x.split('.')[1]
        return not k.isdigit() and '999%s' % k or ('000'+k)[-3:]
    subkeys = [x[1] for x in sorted([('%s.%s' % (key[0], _question(x)), x)
        for x in keys if x.startswith(key[1])])]
    return subkeys


def _sorted_iterable_keys(keys, key):
    #
    #   Sort iterable items
    #
    subkeys = [x[1] for x in sorted([(x, x) for x in keys if x.startswith(key)])]
    return subkeys


def sorted_keys(keys, key):
    if isIterable(key):
        subkeys = _sorted_keys(keys, key)
    else:
        subkeys = _sorted_iterable_keys(keys, key)
    return subkeys


def _sorted_items(items):
    items.sort(key=lambda x: int(x.split('.')[1]))


def remove_subkeys(keys, subkeys):
    for x in subkeys:
        keys.remove(x)


def check_items(value, keys):
    for key in keys:
        if value.startswith(RCODES[key]):
            return True
    return False
    

class LogProcess:
    
    def __init__(self):
        self._started = getToday()

        self.is_with_points = 0
        self.ages = {}

        self.storage = g.storage

    def _init_state(self, mode=None):
        """
            Init state the class
            
            Arguments:
                mode    -- int (self.mode), mode of data parsing
                    0 (false): chat ids data (user's profile)

                    1: conclusions data pasrsing
                
                Used for self.log method
        """
        self._tests_count = tests_count()

        self.mode = mode or 0

        self.system_config = g.system_config

        if self.system_config:
            self.is_with_points = self.system_config.IsWithPoints
        #
        #   TABLE DATA DEFINITIONS  (unused just now, it's for modules compatibility)
        #
        self.total_rows = 0
        self.total_selected = None
        self.per_page = 1
        self.pages = 1
        self.page = 1
        self.is_selected = 0
        self.selected_row = None,
        self.iter_pages = ()
        self._with_chunks = 0
        self._chunk = None
        self.per_page_options = None
        self._modes = (1,2,3)
        self._sorted_by = 1
        self._current_sort = 1
        self.line = 1
        self.is_today = 1
        self._date_from = None
        self.is_yesterday = 0
        self.today = getToday()

    def point(self, name):
        if not self.is_with_points:
            return

        self._finished = getToday()

        if IsTrace:
            print_to(None, '>>> %s: %s sec' % (name, spent_time(self._started, self._finished)))

        self._started = self._finished

    """ 
        LOGGER DEFINITIONS
    """

    def _get_chat_names(self):
        #
        #   Chat names
        #
        return self.storage.get_chat_names()

    def _get_groups(self):
        #
        #   Groups for chat data parsing
        #
        groups = (
            ['person', 'profile', ('query_id', 'chat_person', 'nic', 'date', 'command', 'lang', 'usage', 'warning')], 
            ['line', 'tests', [(int(n), 'T%s.' % str(n)) for n in range(1, self._tests_count+1)]], 
            ('dialog', 'scenario', None)
            )
        return groups

    def _get_value(self, name, key, **kw):
        #
        #   Value for given key in chat name
        #
        x = self.storage.get(name, key).decode()
        return x

    def _get_value_cls(self, key, value):
        #
        #   CSS-class for given key value
        #
        if _RES_PREFIX in key:
            return ' result'
        if _TEXT_PREFIX in key:
            return ' text'
        if value.isdigit() or value.startswith('-'):
            x = int(value)
            return x < 0 and ' negative' or x == 0 and ' zero' or ' positive'
        return ''

    def _get_values(self, name, keys, key):
        #
        #   Values for all given keys items matched with key in chat name
        #
        values = dict([(key, self._get_value(name, key)) for key in keys])
        return values

    def debug(self):
        self.point('logger.debug-start')

        groups = self._get_groups()

        html = {}

        backgrounds, bid = ('bg1', 'bg2', 'bg3'), 0

        html['server'] = '<div class="server">%s</div>' % '&nbsp;'.join([
            repr(self.storage.rserver.client()), '<strong>%s</strong>' % self.storage.redis_url,
            repr(urlparse(self.storage.redis_url)), 'is_webhook:%s' % is_webhook,
        ])

        def _add_output(output, cls, keys, cols=None):
            values = dict([(key, self._get_value(name, key)) for key in keys])

            def _add(i, key, mode=0):
                row = ''
                if mode == 0:
                    if '=' in key or 'LAST' in key:
                        row = '<tr><td class="data%s" colspan="5">%s: <div class="value">%s</div></td></tr>'
                    else:
                        if cols and i > 0 and i%cols == 0:
                            output.append('</tr><tr>')
                        row = '<td class="data%s">%s: <div class="value">%s</div></td>'
                else:
                    row = '<tr><td class="data%s">%s: <div class="value">%s</div></td></tr>'

                if row:
                    output.append(row % (
                        self._get_value_cls(key, values[key]), 
                        key, 
                        values[key]
                        ))

            if not keys:
                return

            res, text = [], []
            output.append('<table class="%s">' % cls)
            output.append('<tr>')
            for i, key in enumerate(keys):
                if _RES_PREFIX in key:
                    res.append(key)
                    continue
                if _TEXT_PREFIX in key:
                    text.append(key)
                    continue
                _add(i, key)
            output.append('</tr>')
            output.append('</table>')

            if not res:
                return

            output.append('<table class="%s">' % cls)
            output.append('<tr>')
            for i, key in enumerate(res):
                _add(i, key)
            output.append('</tr>')
            output.append('</table>')

            if not text:
                return

            output.append('<table class="%s">' % cls)
            output.append('<tr>')
            for i, key in enumerate(text):
                _add(i, key, mode=1)
            output.append('</tr>')
            output.append('</table>')

        if self.storage.rserver.client():
            names = self._get_chat_names()
            html['header'] = '<div class="server">names:[%s]</div>' % ', '.join(['<span>%s</span>' % x for x in names])

            outputs = []

            # names - chat names
            # data - chat data
            # keys - chat item keys
            # groups - groups of items (global)
            # cls - group css-class
            # caption - caption of group
            # group - group items keys
            # subkeys - group subitems keys

            for name in names:
                output = []
                output.append('<div class="chat">%s:</div>' % name)

                try:
                    data = self.storage.getall(name)
                    keys = [x.decode() for x in data.keys()]
                except:
                    output.append('error:%s' % name)
                    continue

                for cls, caption, group in groups:
                    if caption:
                        output.append('<h2>%s:</h2>' % Capitalize(caption))
                    if not group:
                        _add_output(output, cls, sorted(keys), cols=15)
                    elif isIterable(group):
                        for key in group:
                            subkeys = sorted_keys(keys, key)

                            _add_output(output, cls, subkeys, cols=25)

                            remove_subkeys(keys, subkeys)

                    self.point('logger.debug-%s' % caption)

                outputs.append('<div class="person %s">%s</div>' % (backgrounds[bid], ''.join(output)))

                bid = bid < len(backgrounds)-1 and bid+1 or 0

            content = ''.join(outputs)

            self.point('logger.debug is ready')

        # _DEBUG_HTML

        debug, kw = init_response('Application DBviewer Page', mode='database')
        kw['product_version'] = product_version
        kw['is_active_scroller'] = 0

        kw['vsc'] = vsc()

        kw.update({
            'base'       : '',
            'navigation' : get_navigation(),
            'title'      : 'debug',
            'module'     : 'database',
            'width'      : 1280,
            'message'    : 'debug'.upper(),
            'html'       : html,
            'content'    : content,
            'vsc'        : vsc(),
        })
        self.point('logger.debug-finish')

        return render_template('debug.html', **kw)

    def log(self, chat_id=None):
        self.point('logger.log-start')

        html = ''
        content = "*** it's log ***"
        #
        #   View Data init
        #
        output = {'chats': {}}
        chats = output['chats']
        tests = ()
        tp = {'high':0, 'middle':0, 'normal':0, 'low':0, 'undef':0,}
        #
        #   Semaphore init
        #
        from app.semaphore.views import initDefaultSemaphore # XXX
        debug, kw = init_response('Application LogViewer Page', mode='logger')
        #
        #   List of chats (persons)
        #
        names = [x for x in self._get_chat_names() if not self.mode or x == chat_id]
        #
        #   Groups of data parts: profile, conclusions for scenario and tests
        #
        groups = self._get_groups()

        path = request.path

        for name in names:
            chats[name] = {}
            chat = chats[name]
            profile = None

            try:
                data = self.storage.getall(name)
                keys = [x.decode() for x in data.keys()]
            except:
                chat['error'] = name
                continue

            for cls, caption, group in groups:
                if caption:
                    chat[caption] = {}
                if not group:
                    # Scenario
                    subkeys = sorted(keys)
                    if 'scenario' in chat:
                        for subkey in subkeys:
                            if subkey:
                                value = self._get_value(name, subkey)
                                chat['scenario'][subkey] = value

                elif isIterable(group):
                    # Profile, Tests
                    is_tests = is_profile = 0
                    if 'tests' in caption.lower():
                        is_tests = 1
                    else:
                        is_profile = 1
                    for key in group:
                        s = None
                        if isIterable(key) and is_tests:
                            n, s = key
                            chat[caption][s] = {}
                            test = chat[caption][s]
                        elif profile is None and is_profile:
                            chat[caption] = {}
                            profile = chat[caption]

                        subkeys = sorted_keys(keys, key)

                        #action with subkeys
                        for subkey in subkeys:
                            value = self._get_value(name, subkey)
                            if is_tests and s:
                                item = subkey.replace(s, '')
                                test[item] = value
                            elif profile is not None and subkey is not None:
                                profile[subkey] = value

                        remove_subkeys(keys, subkeys)

                self.point('logger.log-%s' % caption)

        self.point('logger.log is ready')
        mode_title = ''
        #
        #   Lang of user
        #
        request_lang = get_request_item('lang')
        lang = chat_id and output['chats'][chat_id]['profile'].get('lang') or DEFAULT_LANGUAGE
        #
        #   ages -- dict, ages of persons {[N]:<age in string>}, N -- str (age group key: 1,2,3)
        #
        from app.dialogs import age
        self.ages = age.get_values(lang)

        if not self.mode:
            data_title = maketext('LOGGER PERSONS PAGE TITLE', lang=lang)
            #
            #   User's Profile [output]
            #       Tests    -- tuple, (<done tests count>, <sun of questions answered>)
            #       Scenario -- tuple, (...<sun of questions answered>)
            #
            #       action   -- str, base link to open conslusions info
            #
            for chat in output['chats']:
                out = output['chats'][chat]
                profile = out.get('profile')
    
                tests = None
                scenario = None
    
                if profile:
                    tests = [(x, len(out['tests'][x])) for x in out['tests'].keys() if x]
                    scenario = [(x, len(out['scenario'][x])) for x in out['scenario'].keys() if x]
                else:
                    out['profile'] = {}
                    profile = out['profile']
                
                profile['Tests'] = tests and (len(tests), sum([x[1] for x in tests])) or (0, 0)
                profile['Scenarios'] = scenario and (len(scenario), sum([x[1] for x in scenario])) or (0, 0)

                out['profile_action'] = f'/log/profile/{chat}'

        elif self.mode == 1:
            #
            #   Conclusion tests diagnosis for chat name
            #
            data_title = maketext('LOGGER DATA PAGE TITLE', lang=lang)
            chat = output['chats'].get(chat_id)
            profile = chat.get('profile')
            scenario = chat.get('scenario')

            for key in chat['tests']:
                test = key[:-1]
                
                out = chat['tests'][key]
                questions = list(out.keys())
                
                for q in questions:
                    if check_items(q, ('TP', 'TC')):
                        try:
                            param, value = out[q].split(':')
                            cls = conclusion_level('%s.%s' % (test, q), value)
                            if cls:
                                out[q] = f'<div class="{cls}">{param}</div>:{value}'
                                tp[cls] += 1
                            else:
                                tp['undef'] += 1
                        except:
                            raise #continue
                    else:
                        del out[q]

            tests = [('%s.' % key, name[0]) for key, name in TESTNAMES[request_lang or lang].items()]
            mode_title = maketext('Diagnosis test conclusions', lang=lang)
            #
            #   Add aditional data items to view
            #
            if profile and scenario:
                key = 'age'
                age = scenario.get(key)
                profile[key] = self.ages.get(age) or age

        self.point('logger.actions')

        action = ''
        link = ''
        back = '/log/'

        pagination = {
            'total'             : '%s' % (self.total_rows),
            'total_selected'    : '%s | 0.00' % (self.total_selected or 0),
            'per_page'          : self.per_page,
            'pages'             : self.pages,
            'current_page'      : self.page,
            'selected'          : self.is_selected and self.selected_row or (0, 0, None),
            'iter_pages'        : tuple(self.iter_pages),
            'with_chunks'       : [self._with_chunks, self._chunk],
            'has_next'          : self.page < self.pages,
            'has_prev'          : self.page > 1,
            'per_page_options'  : self.per_page_options,
            'action'            : action or '',
            'link'              : link,
            'sort'              : {
                'modes'         : self._modes,
                'sorted_by'     : self._sorted_by,
                'current_sort'  : self._current_sort,
            },
            'position'          : '%d:%d:%d:%d' % (self.page, self.pages, self.per_page, self.line),
            'today'             : {
                'selected'      : self.is_today,
                'date_from'     : self._date_from,
                'has_prev'      : self.is_today or self.is_yesterday,
                'has_next'      : self._date_from and self._date_from < self.today and True or False,
            },
        }
        
        query_string = 'per_page=%s' % self.per_page
        base = 'log?%s' % query_string

        # _DEBUG_HTML

        kw['product_version'] = product_version
        kw['is_active_scroller'] = 0

        kw.update({
            'base'          : base,
            'action'        : action,
            'link'          : link,
            'navigation'    : get_navigation(),
            'pagination'    : pagination,
            'semaphore'     : initDefaultSemaphore(),
            'title'         : 'log page',
            'module'        : 'database',
            'width'         : 1280,
            'page_title'    : maketext('LOGGER PAGE TITLE', lang=lang),
            'data_title'    : data_title,
            'search_title'  : "Logger Search context...",
            'message'       : 'debug'.upper(),
            'lang'          : lang,
            'back'          : back,
            'mode_title'    : mode_title,
            'mode'          : self.mode,
            'RD'            : getDate(getToday(), format=LOCAL_FULL_TIMESTAMP),
            'tests'         : tests,
            'content'       : content,
            'output'        : output,
            'names'         : names,
            'tp'            : tp,
        })

        self.point('logger.log-finish')

        return render_template('logger.html', **kw)


## -------------------------------

@before
def make_debug(**kw):
    process = LogProcess()
    process._init_state(0)
    try:
        return process.debug()
    except:
        if IsPrintExceptions:
            print_exception()

@before
def make_log(mode, **kw):
    process = LogProcess()
    process._init_state(mode)
    try:
        return process.log(**kw)
    except:
        if IsPrintExceptions:
            print_exception()

@logger.route('/debug', methods=['GET', 'POST'])
#@login_required
#@admin_required
def debug():
    return make_debug()

@logger.route('/', methods=['GET', 'POST'])
@logger.route('/index', methods=['GET', 'POST'])
#@login_required
#@admin_required
def index():
    return make_log(0)

@logger.route('/profile/<chat_id>', methods=['GET', 'POST'])
def profile(chat_id):
    #return f'*** Profile. chat_id={chat_id} ***'
    print('profile chat_id', chat_id)
    return make_log(1, chat_id=chat_id)

@logger.route('/begin', methods=['GET', 'POST'])
def begin():
    return 'logger.begin'

