# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
6. Есть ли у вас дети?
""",
), 
    'uk': (
"""
""",
"""
6. Чи є у Вас діти?
""",
),
}

_CHILDREN = {
    'ru': (('нет', 'children:0'), ('1 ребенок', 'children:1'), ('2 ребенка', 'children:2'), ('3 ребенка', 'children:3'), ('4 и больше', 'children:4')),
    'uk': (('немає', 'children:0'), ('1 дитина', 'children:1'), ('2 дитини', 'children:2'), ('3 дитини', 'children:3'), ('4 і більше дітей', 'children:4')),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _CHILDREN[lang], get_question(1, lang))
