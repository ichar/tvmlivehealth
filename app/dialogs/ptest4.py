# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy
import random

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsRandomScores,
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, NO_RESULTS, NO_KEY, RCODES
from app.dialogs.start import help
from app.handlers import *

from app import dbs

# Случайный порядок ответов
_is_random_scores = IsRandomScores

# ------------------------
# Уровень тревожности Бека
# ------------------------

_TEST_NAME = 'T4'
_QCOUNT = 21

_QUESTIONS = {
    'ru': (
"""
1. Притупление чувств, покалывание или жжение
""",
"""
2. Ощущение жары
""",
"""
3. Дрожь в ногах, непроизвольные движения ногами
""",
"""
4. Невозможность успокоиться
""",
"""
5. Страх, что случится самое страшное
""",
"""
6. Головокружение или помутнение сознания
""",
"""
7. Учащенное сердцебиение
""",
"""
8. Неуравновешенность
""",
"""
9. Ощущение паники
""",
"""
10. Нервозность
""",
"""
11. Ощущение удушья
""",
"""
12. Дрожь в руках
""",
"""
13. Слабость в ногах ( «ватные ноги»)
""",
"""
14. Страх потерять самообладание
""",
"""
15. Тяжелое дыхание
""",
"""
16. Страх смерти
""",
"""
17. Испуг
""",
"""
18. Расстройство пищеварения, дискомфорт в животе
""",
"""
19. Ощущение обморока
""",
"""
20. Покраснение лица, жар
""",
"""
21. Холодный пот
""",
), 
    'uk': (
"""
1. Притуплення почуттів, поколювання або печія
""",
"""
2. Відчуття спеки
""",
"""
3. Тремтіння в ногах, мимовільні рухи ногами
""",
"""
4. Неможливість заспокоїтися
""",
"""
5. Страх, що трапиться найстрашніше
""",
"""
6. Запаморочення або затьмарення свідомості
""",
"""
7. Прискорене серцебиття
""",
"""
8. Неврівноваженість
""",
"""
9. Відчуття паніки
""",
"""
10. Нервозність
""",
"""
11. Відчуття задухи
""",
"""
12. Тремтіння в руках
""",
"""
13. Слабкість в ногах («ватні ноги»)
""",
"""
14. Страх втратити самовладання
""",
"""
15. Важке дихання
""",
"""
16. Страх смерті
""",
"""
17. Переляк
""",
"""
18. Розлад травлення, відчуття дискомфорту у животі
""",
"""
19. Відчуття непритомності
""",
"""
20. Почервоніння особи, жар
""",
"""
21. Холодний піт.
""",
),
}

_scores_numbers = 'ABCD'

_SCORES = {
    'ru': [
        ( 0, 'совсем не беспокоит',),
        ( 1, 'беспокоит в легкой степени (не особо беспокоит)',),
        ( 2, 'беспокоит в средней степени (это было очень неприятно, но я справлюсь с этим) ',),
        ( 3, 'беспокоит значительной степени (с трудом справился с этим)'), 
    ],
    'uk': [
        ( 0, 'зовсім не турбує',),
        ( 1, 'турбує в легкому ступені (не особливо турбує)',),
        ( 2, 'турбує в середньому ступені (це було дуже неприємно, але я впораюся з цим)',),
        ( 3, 'турбує значною мірою (насилу впорався з цим)',),
    ],
}

_PARAMS = {
    'ru' : {'1' :'Уровень тревожности'},
    'uk' : {'1' :'Рівень тривожності'},
}

_RESULTS = {
    'ru' : (
        ( 9, 'Симптомы тревожности  отсутствуют'), 
        (18, 'Низкий уровень тревожности'), 
        (29, 'Средний уровень тревожности'), 
        (63, 'Высокий уровень тревожности, клиническое проявление. Настоятельно рекомендуется обратиться к специалисту'), 
    ),
    'uk' : (
        ( 9, 'Симптоми тривожності відсутні'), 
        (18, 'Низький рівень тривожності'), 
        (29, 'Середній рівень тривожності'), 
        (63, 'Високий рівень тривожності, клінічне проявлення. Наполегливо рекомендується звернутися до фахівця'), 
    ),
}

_HEADERS = {
    'ru': 
"""
Перед Вами список симптомов тревоги. Прочитайте их и отметьте, в какой степени каждый из них беспокоит Вас в течение последней недели включительно с сегодняшним днем. 
""",
    'uk': 
"""
Перед Вами список симптомів тривоги. Прочитайте їх і позначте, якою мірою кожен з них турбує Вас протягом останнього тижня включно із сьогоднішнім днем.
""",
}

_WARNINGS = {
    'ru': (
"""
Внимание, предоставленные данные выглядят недостоверными, рекомендуется быть более искренним в ответах или обратиться к специалисту!
""",
), 
    'uk': (
"""
Увага, надані відповіді видаються не надто достовірними; рекомендується бути більш щирим у відповідях або звернутися до фахівця!
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

_results = {}


def test_name():
    return _TEST_NAME

def total_questions():
    return _QCOUNT

def get_question(i, lang, no_eof=None):
    x = _QUESTIONS[lang][i].strip()
    s = '%s.%s:' % (_TEST_NAME, x[-1] == '.' and x[:-1] or x)
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_header(lang, no_eof=None):
    s = '<b>%s</b>' % _HEADERS[lang].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_finish(storage, name, i, lang, no_eof=None):
    nic = storage.get(name, 'nic', with_decode=True)
    s = '%s%s' % (nic and '%s!\n\n' % nic or _FINISH[lang][0], _FINISH[lang][i].strip())
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_answers(question, lang, no_eof=None):
    scores = list(_SCORES[lang])

    if _is_random_scores:
        random.shuffle(scores)

    answers = []
    buttons = []
    for i, x in enumerate(scores):
        b, s = x
        n = _scores_numbers[i]
        q = '%s.%s:%s' % (_TEST_NAME, question+1, b)
        answers.append('%s) %s' % (n, s))
        buttons.append((n, q))

    if _is_random_scores:
        buttons = sorted(buttons)

    return '\n'.join(answers), buttons

def get_result(storage, name, lang, mode=None):
    global _results

    res = ''
    data = storage.getall(name)
    results = _RESULTS[lang]

    x = 0

    for n in range(0, _QCOUNT):
        key = ('%s.%s' % (_TEST_NAME, n+1)).encode()
        x += int(data.get(key, 0))
    c = ''
    for i, item in enumerate(results):
        if x <= item[0]:
            c = results[i][1]
            res = (x, '<b>%s</b>' % c)
            break

    _results['1'] = (x, c)

    return res

def answer(bot, message, command, data=None, logger=None, question=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    storage = kw.get('storage')
    name = kw.get('name')

    is_run = True

    if question == 0:
        text = get_header(lang)
        bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)

    if question == _QCOUNT or (IsDebug and question > 0 and question%10 == 0):
        text = '[%s] %s.' % get_result(storage, name, lang)
        bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)
        is_run = question < _QCOUNT

        if is_run:
            time.sleep(3)

    if is_run:
        answers, buttons = get_answers(question, lang)
        text = '%s\n\n%s' % (get_question(question, lang), answers)
        send_inline_keyboard(bot, message, buttons, text)

    elif 'query_id' in kw:
        _test_name = test_name()

        dbs.drop_before(_test_name, **kw)
        dbs.save_params(_test_name, _PARAMS, _results, default_param=_PARAMS[lang]['1'], **kw)
        """
        if 'value' in _results:
            value, param = _results['value']
            storage.set(name, '%s.R' % _TEST_NAME, value)
            storage.set(name, '%s.T' % _TEST_NAME, '%s:%s' % (param, value), with_encode=True)
        """

        if kw['query_id']:
            bot.answer_callback_query(
                kw['query_id'],
                text=get_finish(storage, name, 1, lang),
                show_alert=True
                )

            time.sleep(3)

        help(bot, message, logger=logger, mode=1, **kw)

## -------------------------- ##


def lines1(text):
    #
    # Ответы разные
    #
    numbers = _scores_numbers
    scores = {}
    qtext = "\nОберіть варіант відповіді:\n"
    n = 0
    i = 0
    for line in text.split('\n'):
        if not line:
            continue
        x = line.split('.')
        if len(x) > 1 and x[0].isdigit():
            n = int(x[0])
            q = x[1].strip()
            print('""",\n"""\n%s. %s.%s' % (n, q, qtext))
            i = 0
            scores[n] = []
            continue
        m = re.match(r'(- )(.*)(\(\d+\))', line)
        if not m:
            continue
        b = int(re.sub(r'[\(\)]', r'', m.group(3)))
        s = m.group(2).strip()
        scores[n].append(b)
        print("%s) %s%s" % (numbers[i], s, i < 3 and ',' or '.'))
        i += 1

def lines2(text):
    #
    # Ответы одинаковые
    #
    numbers = _scores_numbers
    scores = []
    qtext = "\nОберіть варіант відповіді:\n"
    n = 0
    i = 0
    for line in text.split('\n'):
        if not line:
            continue
        x = line.split('.')
        if len(x) > 1 and x[0].isdigit():
            n = int(x[0])
            q = x[1].strip()
            print('""",\n"""\n%s. %s.' % (n, q))
            i = 0
            continue
        if n == 1:
            m = re.match(r'(- )(.*)(\(\d+\))', line)
            if not m:
                continue
            b = int(re.sub(r'[\(\)]', r'', m.group(3)))
            s = m.group(2).strip()
            scores.append((s, b))
            i += 1
    for i, x in enumerate(scores):
        s, b = x
        print("%s(%s, '%s',)," % (' '*8, b, s))

def check(data, key, res):
    s = 0
    for k in data[key].keys():
        #print(k)
        q = k.split('.')[1]
        if not q.isdigit():
            continue
        #print(q)
        if not res or int(q) in res:
            s += int(data[key][k])
    return s

def selftest(data, lang, with_print=None):
    key = _TEST_NAME
    params = ('1',)

    out = ''
    r = 0
    for k in sorted(params):
        x = check(data, key, None)
        if with_print:
            print(x)
        r += x

    rp = '%s.R' % key
    if rp in data[key]:
        x = int(data[key].get(rp, '0'))
        if r == x:
            out = 'OK'
        else:
            out = 'Error %s [%s:%s]' % (rp, r, x)
            if with_print or IsWithPrintErrors:
                print(key, out)

    return out or NO_RESULTS
