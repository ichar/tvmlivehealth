# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
4. Ваше образование
""",
), 
    'uk': (
"""
""",
"""
4. Ваша освіта
""",
),
}

_EDUCATION = {
    'ru': [('среднее', 'education:1'), ('среднее специальное', 'education:2'), ('неполное высшее', 'education:3'), ('высшее', 'education:4'),],
    'uk': [('середня', 'education:1'), ('середня спеціальна', 'education:2'), ('неповна вища', 'education:3'), ('вища', 'education:4'),],
}

def get_question(i, lang, no_eof=None):
    s = '%s:' % _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _EDUCATION[lang], get_question(1, lang))
