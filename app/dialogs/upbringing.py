# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
7. Тип семейного воспитания:
""",
), 
    'uk': (
"""
""",
"""
7. Тип Вашого виховання можна визначити як:
""",
),
}

_UPBRINGING = {
    'ru': (('авторитарно', 'upbringing:1'), ('либерально', 'upbringing:2'), ('гиперопека', 'upbringing:3'), ('демократично', 'upbringing:4')),
    'uk': (('авторитарне', 'upbringing:1'), ('ліберальне', 'upbringing:2'), ('гіперопіка', 'upbringing:3'), ('демократичне', 'upbringing:4')),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _UPBRINGING[lang], get_question(1, lang))
