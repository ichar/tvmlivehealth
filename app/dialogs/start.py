# -*- coding: utf-8 -*-

__all__ = ['start', 'description', 'help', 'langs', 'commands', 'tests', 'begin', 'stop']

import re

from app.settings import (
    DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, STARTMENU, TESTNAMES, TESTS,
    IsPrintExceptions, print_exception, print_to
)

from app.handlers import *

_design_mode = 'menu' # 'commands'

_QUESTIONS = {
    'ru': (
"""
<b>Здравствуйте!</b>
<b>Вы работаете с Telegram-Ботом "TVMLiveHealthBot". 
Спасибо, что обратились к нам!</b>
""",
"""
<b>Описание и возможности</b>

А) объяснение возможностей этого самого нашего чудо-бота
Б) сообщение, что он, бот, понимает обратившегося и может ему помочь
В) что у него, бота, есть свой метод
""",
"""
<b>Команды Бота</b>

Это команды Бота. Команду можно ввести в любое время, если ее текст набрать на клавиатуре. Команда начинается с символа "/" и записывается только латинскими буквами.

/start		Начало работы
/help		Помощь (эта информация)
/clear		Очистить результаты предыдущих тестов
/description	Краткое описание и наши возможности
/commands	Список дополнительных команд
/tests		Психологические тесты
/emergency	Экстренная помощь
/diagnosis	Информация о пройденных тестах
/profile	Личный кабинет
/menu		Главное меню
/lang		Выбор языка
/version	Версия ПО
""",
"""
<b>Клиническая беседа</b>

/begin:	Начать диалог.
/qN:	Переход к вопросу N диалога.
/end:	Завершить диалог.

<b>Тесты</b>

/tX:	Старт теста X.
/tX.q:	Продолжить тест X.
/tX.qN:	Продолжить тест X с вопроса N.
/dX:	Результаты теста X.

где N и X - число.
""",
"""
Хорошо. Давайте, продолжим...
""",
"""
Для начала диалога нажмите /begin.
""",
"""
<b>Психологические тесты</b>
""",
"""
<b>Язык диалога</b>

/ru Russian
/uk Ukranian
""",
"""
Для начала нашей беседы, пожалуйста, введите команду /begin,
для выбора теста на психологическое состояние /tests.
Помощь по работе с ботом /help.
""",
"""
Вашему вниманию предлагается наше Главное меню:
""",
"""
Вы всегда можете воспользоваться нашей Клавиатурой:
""",
), 
    'uk': (
"""
<b>Доброго дня!</b>
<b>Ви працюєте с Telegram-ботом "TVMLiveHealthBot". 
Дякуємо, що звернулися до нас!</b>
""",
"""
<b>Опис і можливості</b> 

А) пояснення можливостей цього самого нашого чудо-бота
Б) повідомлення, що він, бот, розуміє звернувся і може йому допомогти
В) що у нього, бота, є свій метод
""",
"""
<b>Команди Бота</b>

Це команди Бота. Команду можна ввести будь-коли, якщо її текст набрати на клавіатурі. Команда починається із символу "/" і записується лише латинськими літерами.

/start		Початок роботи
/help		Допомога (ця інформація)
/clear		Очистити результати попередніх тестів
/description	Короткий опис і наші можливості
/commands	Список додаткових команд
/tests		Психологічні тести
/emergency	Екстрена допомога
/diagnosis	Інформація про пройдені тести
/profile	Особистий кабінет
/menu		Головне меню
/lang		Вибір мови
/version	Версія ПО
""",
"""
<b>Клінічна бесіда</b>

/begin:	Почати діалог.
/qN:	Перехід до питання N діалогу. 
/end:	Завершити діалог.

<b>Тести</b>

/tX:	Старт тесту X.
/tX.q:	Продовжити тест X.
/tX.qN:	Продовжити тест X з питання N.
/dX:	Результати тесту X.

де N та X - число.
""",
"""
Чудово. Давайте продовжимо...
""",
"""
Для початку бесіди натисніть, будь-ласка кнопку /begin.
""",
"""
<b>Психологічні тести</b>
""",
"""
<b>Мова діалогу</b>

/ru Russian
/uk Ukranian
""",
"""
Для початку нашої бесіди, будь ласка, натисніть команду /begin, 
для вибору тесту на психологічний стан /tests.
Допомога по роботі з ботом /help.
""",
"""
Вашій увазі пропонується наше Головне меню:
""",
"""
Ви завжди можете скористатися нашою Клавіатурою:
""",
),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def mainmenu(bot, message, logger=None, lang=None):
    if _design_mode == 'menu':
        send_inline_keyboard(bot, message, STARTMENU[lang][0], get_question(9, lang))

def start(bot, message, logger=None, **kw):
    lang = kw.get('lang')
    bot.reply_to(message, get_question(0, lang, no_eof=False), parse_mode=DEFAULT_PARSE_MODE)

    mainmenu(bot, message, logger=logger, lang=lang)
    help(bot, message, logger=logger, **kw)

    reply_keyboard_markup(bot, message, STARTMENU[lang][1].keys(), get_question(10, lang), parse_mode=None)

def description(bot, message, logger=None, **kw):
    bot.reply_to(message, get_question(1, kw.get('lang'), no_eof=False), parse_mode=DEFAULT_PARSE_MODE)

def help(bot, message, logger=None, **kw):
    mode = kw.get('mode')
    text = get_question(2, kw.get('lang'))

    if mode == 1:
        bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)
    else:
        bot.reply_to(message, text, parse_mode=DEFAULT_PARSE_MODE)

def langs(bot, message, logger=None, **kw):
    bot.reply_to(message, get_question(7, kw.get('lang')), parse_mode=DEFAULT_PARSE_MODE)

def commands(bot, message, logger=None, **kw):
    bot.reply_to(message, get_question(3, kw.get('lang')), parse_mode=DEFAULT_PARSE_MODE)

def tests(bot, message, logger=None, **kw):
    lang = kw.get('lang')
    items = TESTNAMES[lang]
    tests = dict([(x, m) for m, x in TESTS if x])
    text = get_question(6, lang)+'\n'

    if _design_mode == 'menu':
        obs = []
        for i, k in sorted([(int(x[1:]), x) for x in items.keys()]):
            module = tests[k]
            qcount = 0
            try:
                _module = __import__(module, fromlist=['total_questions', 'answer'])
                qcount = _module.total_questions()
            except:
                if IsPrintExceptions:
                    print_exception()
                continue

            name = '%s. %s [%s]' % (k, items[k][1], qcount)
            obs.append((name, '/%s' % k))
        send_inline_rows_keyboard(bot, message, obs, text)
    else:
        for k in sorted(items.keys()):
            name = items[k]
            text += '\n/%s: %s.' % (k, name)
        bot.reply_to(message, text, parse_mode=DEFAULT_PARSE_MODE)

def begin(bot, message, logger=None, **kw):
    bot.reply_to(message, get_question(4, kw.get('lang'), no_eof=True))

def stop(bot, message, logger=None, **kw):
    bot.reply_to(message, get_question(5, kw.get('lang'), no_eof=True))
