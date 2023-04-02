# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
Мы просим Вас быть максимально искренним. Это нужно не из праздного любопытства,
а чтобы максимально точно выяснить проблему и, соответственно, максимально помочь Вам в её решении.
""",
"""
Просим Вас ответить на наши вопросы.
""",
"""
Вы даете разрешение на обработку Ваших персональных данных?
""",
), 
    'uk': (
"""
Ми просимо Вас бути максимально щирим у відповідях. Це потрібно не з пустої цікавості,
а задля того, аби максимально точно з’ясувати проблему і, відповідно, надати максимально
ефективну допомогу у її розв’язанні.
""",
"""
Просимо Вас відповісти на наші запитання.
""",
"""
Чи даєте Ви дозвіл на обробку Ваших персональних даних?
""",
),
}

_ACCEPT = {
    'ru': (('Да', 'accept:1'), ('Нет', 'accept:0'),),
    'uk': (('Так', 'accept:1'), ('Ні', 'accept:0'),),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    bot.reply_to(message, '%s\n\n%s' % (get_question(0, lang, no_eof=True), get_question(1, lang)))
    send_inline_keyboard(bot, message, _ACCEPT[lang], get_question(2, lang))
