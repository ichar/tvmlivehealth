# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
9. Опишите семью, в которой вы воспитывались:
""",
), 
    'uk': (
"""
""",
"""
9. Опишіть родину, в якій Ви виховувалися:
""",
),
}

_FAMILY = {
    'ru': [('полная семья','family:0'), ('был только один из родителей','family:1'), ('сирота','family:2'), ('был отчим или мачеха', 'family:3'),],
    'uk': [('повна сім’я', 'family:0'), ('був лише один з батьків', 'family:1'), ('сирота', 'family:2'), ('був відчим чи мачуха', 'family:3'),],
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _FAMILY[lang], get_question(1, lang))
