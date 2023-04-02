# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
3. Укажите Вашу занятость:
""",
), 
    'uk': (
"""
""",
"""
3. Вкажіть Вашу зайнятість
""",
),
}

_OCCUPATION = {
    'ru': (('работаю', 'occupation:1'), ('не работаю', 'occupation:2'), ('служу', 'occupation:3'), ('учусь', 'occupation:4')),
    'uk': (('працюю', 'occupation:1'), ('не працюю', 'occupation:2'), ('служу', 'occupation:3'), ('навчаюсь', 'occupation:4')),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_keyboard(bot, message, _OCCUPATION[lang], get_question(1, lang))
