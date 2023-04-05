# -*- coding: utf-8 -*-

__all__ = [
    'make_start', 'make_description', 'make_help', 'make_commands', 'make_tests', 
    'make_begin', 'make_answer', 'make_stop', 'make_langs', 'make_version', 
    'make_message', 
    #'make_debug', 'make_log', 
    ]

import os
import sys
import re
import time
"""
from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, 
     errorlog, print_to, print_exception,
     is_webhook,
    )
"""
from config import IsDeleteChatInOpen, IsMakeDump
from app.settings import *
from app.dialogs.start import *

from app.utils import getToday, getDate, isIterable

from ..database import activate_storage, deactivate_storage

basedir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

def setup():
    if basedir not in sys.path:
        sys.path.append(basedir)

        if IsDeepDebug:
            print('... basedir: %s' % basedir)

##  =====================
##  Bot Scenario Handlers
##  =====================

class Chat:
    
    def __init__(self, message):
        self._id = message and message.chat.id or 0
        self._name = 'chat:%s' % self._id
        self._person = message and message.chat.first_name or '...'

        self.message = message

    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @property
    def person(self):
        return self._person


def activate(command, query_id, message):
    chat = Chat(message)

    storage = activate_storage(command=command, query_id=query_id, person=chat.person)

    if IsMakeDump:
        storage.dump(chat.name)

    return chat, storage

def deactivate(chat, storage):
    deactivate_storage(storage)
    del chat

def get_lang(message):
    chat, storage = activate('lang', 0, message)
    try:
        return storage.get_lang(chat.name)
    finally:
        deactivate(chat, storage)

## ========================================== ##

def make_start(bot, message, logger=None, **kw):
    start(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_description(bot, message, logger=None, **kw):
    description(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_help(bot, message, logger=None, **kw):
    help(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_commands(bot, message, logger=None, **kw):
    commands(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_tests(bot, message, logger=None, **kw):
    tests(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_langs(bot, message, logger=None, **kw):
    langs(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_version(bot, message, logger=None, **kw):
    bot.send_message(message.chat.id, product_version)
"""
def make_debug():
    chat, storage = activate('', 0, '')
    try:
        return storage.debug()
    finally:
        deactivate(chat, storage)

def make_log():
    chat, storage = activate('', 0, '')
    try:
        return storage.log()
    finally:
        deactivate(chat, storage)
"""

def make_message(bot, info, logger=None, **kw):
    chat, storage = activate('message', 0, '')
    try:
        x = info[1:].split(':')
        person = x[1]
        text = x[2]
        chat_id = storage.get_person_chat_id(person)
        if chat_id:
            bot.send_message(chat_id, text)
    except:
        pass
    deactivate(chat, storage)

## -------------------------- ##

def make_answer(bot, message, command, data=None, logger=None, **kw):
    """
        Reply an answer for the dialog's question
            message     - message from the chat (last text message sent to the chat)
            query_id    - telegram query ID
            name        - name of the chat
            lang        - language of the chat
            command     - parsed command: button
            data        - answer for the last question: T4.1:3
            logger      - logger func
            module      - module of scenario or tests
            keyboard    - text of keybord command button
            index       - number of test or step of scenario: 4
            question    - question number: 1
            with_usage  - ???
            code        - module results code
            tests       - list of tests keys: ['T1','T2' ... 'T17']
    """
    setup()

    query_id = kw.get('query_id') or -1

    if logger is not None:
        logger('%s:%s%s' % (command, query_id, data and '[%s]' % data or ''), data=message.json)

    chat, storage = activate(command, query_id, message)

    module, keyboard, index, question, with_usage, code = '', None, -1, 0, False, 1

    tests = ['T%s' % str(n) for n in range(1, tests_count())]
    scenario = SCENARIO
    words = []

    name = chat.name
    lang = storage.get_lang(name)
    startmenu = STARTMENU[lang][1]

    is_test = False
    is_scenario = False

    # -------------------------------
    # Схема интерпретации команд бота
    # -------------------------------

    if command == 'button' and data == 'begin:0':
        module = BEGIN[0]
    elif command == 'button' and data == 'tests:0':
        make_tests(bot, message, logger=logger, **kw)
        return 1
    elif command == 'begin-dialog':
        module = BEGIN[0]
    elif command == 'end':
        module = END[0]
    elif command == 'clear':
        storage.delete(name)
    elif command in startmenu.values():
        keyboard = command
    elif command.startswith('D'):
        #
        #   Ручная команда: /D /diagnosis
        #
        #print('... %s' % command)
        keyboard = 'diagnosis'
    elif command in ('ru', 'uk', 'en'):
        storage.set_lang(name, command)
    elif command in tests or command.startswith('T'):
        #
        #   Ручная команда: /T, /Q
        #       data, command:
        #       /T2
        #       /T2.Q10
        words = command.split('.')
        index = len(words) > 1 and words[0].isdigit() and int(words[0]) or 0

        is_test = True

    elif command in ('button', 'q', '...'):
        #
        #   Ответ на вопрос (кнопка)
        #       data, command:
        #       /T2
        #       /Q10
        #       words : <part1>.<part2> - команда или ответ на вопрос
        #
        if kw.get('index'):
            index = kw['index']
        else:
            words = message.text.upper().split('.')
            index = len(words) > 1 and words[0].isdigit() and int(words[0]) or 0

            if command.startswith('T') or words[0].startswith('T'):
                is_test = True
            #
            #   Беседа: ответ на вопрос
            #   -----------------------
            #    <question> - номер вопроса
            #    <spec>, <index> - пункт сценария
            #
            spec = len(scenario) > index and scenario[index][1] or None
            if spec is not None and len(words) > 2:
                question = words[1].isdigit() and int(words[1]) or 0
                if question >= spec:
                    question = -1
                    index += 1
            elif index == 0:
                if not is_test:
                    nic = storage.get(name, 'nic')
                    index = nic and 1 or 0
            else:
                index += 1

        if not is_test:
            if index > len(scenario) - 1:
                module = END[0]
            else:
                module = scenario[index][0]
                is_scenario = True
    else:
        #
        #   Пункт меню 
        #       message.text - текст
        #
        info = message.text

        if IsDeepDebug:
            print('... user info message:', info)

        if not module and not keyboard:
            if info in startmenu.keys():
                keyboard = startmenu[info]
            else:
                module = THANKS[0]

    if index == 0 and is_test:
        #
        #   Тест или ответ на вопрос теста:   
        #   ------------------------------
        #    <command> - [/]tX[.qN]
        #    <index> - номер теста
        #    <question> - номер вопроса теста
        #
        question = len(words) > 1 and words[1].isdigit() and int(words[1]) or 0
        x = 0
        if words[0].startswith('T') or words[0].startswith('/T'):
            x = re.sub(r'[/\D ]', '', words[0])
        index = x and int(x) or 0
        module = TESTS[index][0]

        if len(words) > 1 and words[1].startswith('Q'):
            x = re.sub(r'[/\D ]', '', words[1])
            if x and x.isdigit():
                question = int(x) - 1
            else:
                question = int(storage.get(name, 'T%s.LAST' % index) or 0)

    if question == 0 and IsDeleteChatInOpen:
        if IsDebug:
            print('... delete chat:%s for user:%s, command:%s', (name, chat.person, command))
        storage.delete(name, command='%s.' % command)
        storage.delete(name, command='warning')

    if question > 0 and is_test:
        storage.set(name, 'T%s.LAST' % index, question)

    if IsTrace:
        print('... action(lang, module, keyboard):[%s|%s|%s]' % (lang, module, keyboard))

    if not (is_test or is_scenario or keyboard):
        make_start(bot, message, logger=logger, **kw)

    if not (module or keyboard):
        return 0

    if keyboard:
        with_usage = True

        if IsTrace:
            print('... make_answer:%s keyboard:%s' % (chat.person, keyboard))

        module = KEYBOARD[0]

    elif index == 0 and question == 0 or question == 1:
        with_usage = True

    if is_test:
        if IsTrace:
            print('... make_answer:%s module:%s, index:%s, question:%s, answer:%s' % (
                chat.person, module, index, question, storage.answer))

    storage.register(name, data, with_usage=with_usage)

    # ----------------------
    # Старт модуля обработки
    # ----------------------

    try:
        _module = __import__(module, fromlist=['test_name', 'total_questions', 'answer',])

        if not (_module is not None and hasattr(_module, 'answer')):
            return True

        if is_test:
            test_name = _module.test_name() 
            total_questions = _module.total_questions()

            if question == 0:
                text = '<b>%s %s%s. %s (%s %s)\n* * *</b>' % (gettrans('Test', lang), gettrans('#', lang), 
                    index, 
                    TESTNAMES[lang][test_name][0], 
                    gettrans('total questions', lang), total_questions)
                bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)

        code = _module.answer(bot, message, command, data=data, logger=logger, question=question, keyboard=keyboard,
            chat=chat, storage=storage, name=name, lang=lang, 
            **kw)

    except ModuleNotFoundError:
        code = 0

    except:
        if IsPrintExceptions:
            print_exception()

    if command == 'end':
        if kw.get('with_clear'):
            storage.clear(name)

    deactivate(chat, storage)

    return code is None and 1 or code

def make_begin(bot, message, logger=None, **kw):
    begin(bot, message, logger=logger, lang=get_lang(message), **kw)
    time.sleep(1)
    make_answer(bot, message, 'begin-dialog', logger=logger)

def make_stop(bot, message, logger=None, **kw):
    stop(bot, message, logger=logger, lang=get_lang(message), **kw)

## -------------------------- ##

def selftest(chat_name, lang=None, with_print=None):
    """
        Self Test of Storage Results
    """
    setup()

    tests = {}

    storage = activate_storage()

    for module, key in TESTS:
        if not key:
            continue

        tests[key] = '...'

        try:
            _module = __import__(module, fromlist=['selftest'])
    
            if not (_module is not None and hasattr(_module, 'selftest')):
                continue

            data = storage.get_data(chat_name, '%s.*' % key, with_decode=True)

            if IsDeepDebug:
                print(chat_name, data, key)

            if not data:
                tests[key] = NO_DATA
                continue
            
            tests[key] = _module.selftest(data, lang=lang or DEFAULT_LANGUAGE, with_print=with_print)
        except:
            tests[key] = 'Exception in %s' % module

            if IsPrintExceptions:
                print_exception()

    deactivate_storage(storage)

    return tests
