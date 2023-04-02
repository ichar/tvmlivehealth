# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
Просим Вас представиться. Назовите Ваше имя.
""",
), 
    'uk': (
"""
Будь-ласка, назовіть своє ім’я чи як до Вас звертатися?
""",
),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    bot.send_message(message.chat.id, get_question(0, lang))

