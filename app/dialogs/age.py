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
2. Вкажіть Ваш вік:
""",
),
}

_AGE = {
    'ru': (('младше 18', 'age:0'), ('18-29', 'age:1'), ('30-49', 'age:2'), ('50-69', 'age:3'), ('старше 70', 'age:4')),
    'uk': (('до 18 років', 'age:0'), ('18-29', 'age:1'), ('30-49', 'age:2'), ('50-69', 'age:3'), ('70 і більше', 'age:4')),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _AGE[lang], get_question(1, lang))
