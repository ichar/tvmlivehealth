# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
8. Мое детство было достаточно счастливым
""",
), 
    'uk': (
"""
""",
"""
8. Моє дитинство було досить щасливим
""",
),
}

_CHILDHOOD = {
    'ru': (('Да', 'childhood:1'), ('Нет', 'childhood:2')),
    'uk': (('Так', 'childhood:1'), ('Ні', 'childhood:2')),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_keyboard(bot, message, _CHILDHOOD[lang], get_question(1, lang))
