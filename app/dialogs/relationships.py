# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
10. Тип отношений в семье:
""",
), 
    'uk': (
"""
""",
"""
10. Тип стосунків у Вашій родині:
""",
),
}

_RELATIONSHIPS = {
    'ru': (('в процессе разработки', 'relationships:0'),),
    'uk': (('в процесі розробки', 'relationships:0'),),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_keyboard(bot, message, _RELATIONSHIPS[lang], get_question(1, lang))
