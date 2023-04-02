# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
5. Ваше семейное положение:
""",
), 
    'uk': (
"""
""",
"""
5. Ваш сімейний стан:
""",
),
}

_MARITAL_STATUS = {
    'ru': (('женат/замужем', 'marital_status:married'), ('неженат/незамужем', 'marital_status:single'), ('совместное проживание', 'marital_status:jointly')),
    'uk': (('одружений/заміжня', 'marital_status:married'), ('не одружений/не заміжня', 'marital_status:single'), ('спільне проживання', 'marital_status:jointly')),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _MARITAL_STATUS[lang], get_question(1, lang))
