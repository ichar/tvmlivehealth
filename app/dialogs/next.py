# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
2. Укажите Ваш возраст:
""",
), 
    'uk': (
"""
""",
"""
2. Укажите Ваш возраст:
""",
),
}

_AGES = {
    'ru': (('младше 17', 'age:0'), ('18-29', 'age:1'),),
    'uk': (('младше 17', 'age:0'), ('18-29', 'age:1'),),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    bot.send_message(message.chat.id, data)
    send_inline_keyboard(bot, message, _AGES[lang], get_question(1, lang))
