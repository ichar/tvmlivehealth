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

# -----------------------------------
# Тест ГСР (Острая реакция на стресс)
# -----------------------------------

_TEST_NAME = 'T5'
_QCOUNT = 17

_QUESTIONS = {
    'ru': (
"""
1. Печальные мысли или картины происшедшего травматического события – они возникают невольно
""",
"""
2. Плохие сны или ночные кошмары про событие, причинившее травму
""",
"""
3. Повторное переживание события, причинившего травму, чувство или действие, будто оно вновь происходит
""",
"""
4. Чувство паники, злости, печали, вины
""",
"""
5. Физиологические реакции организма, которые происходят в ответ на напоминание о событии, причинившем травму (повышенная потливость,  ускоренный пульс, дыхание)
""",
"""
6. Попытки не думать о событии, причинившем травму
""",
"""
7. Нежелание говорить про событие или избегание чувств, напоминающих об этом событии
""",
"""
8. Попытки избегать людей или мест, напоминающих о травме
""",
"""
9. Попытки избегать действий, напоминающих о событии, причинившем травму
""",
"""
10. Неспособность вспомнить важные детали события, причинившего травму
""",
"""
11. Значительное снижение заинтересованности или значительное снижение активности
""",
"""
12. Значительное снижение заинтересованности в важных моментах жизнедеятельности
""",
"""
13. Ощущение отдалённости и изоляции от других людей
""",
"""
14. Ощущение притупления чувств (например, неспособность плакать или искренне смеяться)
""",
"""
15. Ощущение неспособности испытывать любовь
""",
"""
16. Ощущение, что собственные планы и надежды не реализуются
""",
"""
17. Переживание, что в будущем не сложится карьера, брак, не будет детей или жизнь будет короткой
""",
), 
    'uk': (
"""
1. Сумні думки або картини травматичної події, яка вже відбулася, - вони виникають поза волею
""",
"""
2. Погані сни або нічні жахи про подію, що заподіяла травму
""",
"""
3. Повторне переживання події, яка завдала травму, почуття або дії, як ніби вона відбувається знову
""",
"""
4. Почуття паніки, злості, смутку, провини
""",
"""
5. Фізіологічні реакції організму, які відбуваються у відповідь на нагадування про подію, що заподіяла травму (підвищена пітливість, прискорений пульс, дихання)
""",
"""
6. Спроби не думати про подію, що заподіяла травму
""",
"""
7. Небажання говорити про подію або уникання почуттів, що нагадують про цю подію
""",
"""
8. Спроби уникати людей або місць, які нагадують про травму
""",
"""
9. Спроби уникати дій, які нагадують про подію, що заподіяла травму
""",
"""
10. Нездатність згадати важливі деталі про подію, що заподіяла травму
""",
"""
11. Значне зниження зацікавленості або значне зниження активності
""",
"""
12. Значне зниження зацікавленості у важливих моментах життєдіяльності
""",
"""
13. Відчуття віддалення і ізоляції від інших людей
""",
"""
14. Відчуття притуплення почуттів (наприклад, нездатність плакати або щиро сміятися)
""",
"""
15. Відчуття нездатності відчувати любов
""",
"""
16. Почуття, що власні плани і надії на майбутнє не реалізуються
""",
"""
17. Переживання, що в майбутньому не складеться кар’єра, шлюб, не буде дітей, або життя буде коротким
""",
),
}

_scores_numbers = 'ABCD'

_SCORES = {
    'ru': [
        ('A', 'совсем неверно или случалось однократно',),
        ('B', 'один раз в неделю',),
        ('C', '2-4 раза в неделю или половину времени',),
        ('D', 'почти постоянно'), 
    ],
    'uk': [
        ('A', 'зовсім не вірно або траплялося одноразово',),
        ('B', 'один раз на тиждень',),
        ('C', '2-4 рази на тиждень або половину від усього часу',),
        ('D', 'майже постійно',),
    ],
}

_PARAMS = {
    'ru' : {'1' :'Cимптомы психотравмы'},
    'uk' : {'1' :'Cимптоми психотравми'},
}

_RESULTS = {
    'ru' : (
        ( 3, 'Состояние целиком нормальное'), 
        (17, 'Симптомы психотравмы, требующие психологического сопровождения специалистов травмофокусирующей направленности'), 
        (34, 'Субклинически проявленные симптомы психотравмы (II звено)'), 
        (51, 'Клиническое проявление симптомов психотравмы (III звено)'), 
    ),
    'uk' : (
        ( 3, 'Стан цілком нормальний'), 
        (17, 'Симптоми психотравми, які потребують психологічного супроводження фахівців травмофокусуючого напрямку'), 
        (34, 'Субклінічно проявлені симптоми психотравми (ІІ ланка)'), 
        (51, 'Клінічну проявленість симптомів психотравми (ІІІ ланка)'), 
    ),
}

_HEADERS = {
    'ru': 
"""
Перед Вами список проблем, возникающих у людей, которые пережили психотравму. Внимательно прочитайте его и укажите вариант ответа, наиболее точно описывающего частоту проблемы, беспокоившей вас на протяжении последнего месяца.
""",
    'uk': 
"""
Перед Вами список проблем, що виникають у людей, які пережили психотравму. Уважно прочитайте його і зазначте варіант відповіді, який найбільш точно описує частоту проблеми, що турбувала вас протягом останнього місяця.
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
    
    def _get_score(s):
        if s == 'A':
            return 0
        if s == 'B':
            return 1
        if s == 'C':
            return 2
        if s == 'D':
            return 3
        return 0

    if _is_random_scores:
        random.shuffle(scores)

    answers = []
    buttons = []
    qs = question + 1

    for i, x in enumerate(scores):
        b, s = x
        bs = _get_score(b)
        n = _scores_numbers[i]
        q = '%s.%s:%s' % (_TEST_NAME, qs, bs)
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
