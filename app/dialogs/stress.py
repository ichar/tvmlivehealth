# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
""",
"""
12. Где в Вашем теле находится локализация этого напряжения:
""",
), 
    'uk': (
"""
""",
"""
12. Де в Вашому тілі знаходиться локалізація цієї напруги:
""",
),
}

_STRESS = {
    'ru': [('голова', 'stress:0'), ('за грудью', 'stress:1'), ('правая рука', 'stress:2'), ('левая рука', 'stress:3'), ('шейно-воротниковая зона', 'stress:4'), ('эпигастрий', 'stress:5'), ('правая нога', 'stress:6'), ('левая нога', 'stress:7'), ('горло', 'stress:8'), ('позвоночник', 'stress:9'), ('кожа', 'stress:10'), ('глаза', 'stress:11'), ('уши', 'stress:12'), ('нос', 'stress:13'), ('сердце', 'stress:14'), ('душа', 'stress:15'), ('сложно сказать/затрудняюсь ответить', 'stress:16'),],
    'uk': [('голова', 'stress:0'), ('за грудьми', 'stress:1'), ('права рука', 'stress:2'), ('ліва рука', 'stress:3'), ('шийно-коміркова зона', 'stress:4'), ('епігастрії', 'stress:5'), ('права нога', 'stress:6'), ('ліва нога', 'stress:7'), ('горло',' stress:8'), ('хребет','stress:9'), ('шкіра',' stress:10'), ('очі','stress:11'), ('вуха',' stress:12'), ('ніс',' stress:13'), ('серце',' stress:14'), ('душа','stress:15') , ('складно сказати/важко відповісти', 'stress:16'),], 
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    send_inline_rows_keyboard(bot, message, _STRESS[lang], get_question(1, lang))
