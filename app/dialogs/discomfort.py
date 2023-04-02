# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
11. Определите величину Вашего внутреннего психологического дискомфорта, напряжения, 
тревоги, которые Вы ощущаете сейчас и, возможно, за последние две недели, по шкале от
0 до 9, где: 0 – минимальное значение (отсутствие) такового, 9 – максимальное значение.
""",
), 
    'uk': (
"""
""",
"""
11. Визначте величину Вашого внутрішнього психологічного дискомфорту, напруги, тривожності,
які Ви відчуваєте зараз та, можливо, останні два тижні, за шкалою від 0 до 9,
де 0 – мінімальне значення (відсутність), 9 – максимальне значення.
""",
),
}

_DISCOMFORT = {
    'ru': (
        (('0', 'discomfort:0'), ('1', 'discomfort:1'), ('2', 'discomfort:2'), ('3', 'discomfort:3'), ('4', 'discomfort:4')), 
        (('5', 'discomfort:5'), ('6', 'discomfort:6'), ('7', 'discomfort:7'), ('8', 'discomfort:8'), ('9', 'discomfort:9')),
    ),
    'uk': (
        (('0', 'discomfort:0'), ('1', 'discomfort:1'), ('2', 'discomfort:2'), ('3', 'discomfort:3'), ('4', 'discomfort:4')), 
        (('5', 'discomfort:5'), ('6', 'discomfort:6'), ('7', 'discomfort:7'), ('8', 'discomfort:8'), ('9', 'discomfort:9')),
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
    send_multiline_keyboard(bot, message, _DISCOMFORT[lang], get_question(1, lang, no_eof=True))
