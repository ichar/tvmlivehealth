# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
1. Укажите Ваш пол:
""",
), 
    'uk': (
"""
""",
"""
1.  Вкажіть Вашу стать
""",
),
}

_GENDER = {
    'ru': [('Мужской', 'gender:man'), ('Женский', 'gender:woman')],
    'uk': [('Чоловічий', 'gender:man'), ('Жіночий', 'gender:woman')],
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_keyboard(bot, message, _GENDER[lang], get_question(1, lang))
