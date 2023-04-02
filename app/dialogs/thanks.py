# -*- coding: utf-8 -*-

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, 
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE

_QUESTIONS = {
    'ru': (
"""
Благодарим Вас!
""",
), 
    'uk': (
"""
Дякуємо!
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
    chat = kw.get('chat')
    storage = kw.get('storage')
    name = kw.get('name')

    text = chat and chat.message.text or 'nothing'

    if IsDeepDebug:
        print(text)

    if storage is not None:
        storage.set(name, 'nic', text)

    bot.reply_to(message, get_question(0, lang))
