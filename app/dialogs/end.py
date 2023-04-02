# -*- coding: utf-8 -*-

import re

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
<b>Наши рекомендации:</b>
""",
), 
    'uk': (
"""
<b>Наші рекомендації:</b>
""",
),
}

_FINISH = {
    'ru': (
"""
Завершение диалога.
""",
"""
Мы благодарим Вас за Ваши ответы.
Желаем Вам крепкого здоровья, и всего Вам доброго!
""",
), 
    'uk': (
"""
Завершення діалогу.
""",
"""
Ми дякуємо Вам за Ваші відповіді.
Бажаємо Вам міцного здоров'я, і всього Вам доброго!
""",
),
}

def get_question(i, lang, no_eof=None):
    s = _QUESTIONS[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_finish(storage, name, i, lang, no_eof=None):
    nic = storage.get(name, 'nic', with_decode=True)
    s = '%s%s' % (nic and '%s!\n\n' % nic or _FINISH[lang][0], _FINISH[lang][i].strip())
    return no_eof and re.sub(r'\n', ' ', s) or s

def answer(bot, message, command, data=None, logger=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    question = get_question(0, lang, no_eof=True)
    storage = kw.get('storage')
    name = kw.get('name')

    if kw.get('no_advice'):
        pass
    else:
        question += '\n...'

    bot.send_message(message.chat.id, question, parse_mode=DEFAULT_PARSE_MODE)

    if 'query_id' in kw:
        bot.answer_callback_query(
            kw['query_id'],
            text=get_finish(storage, name, 1, lang),
            show_alert=True
            )


