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

_is_random_scores = IsRandomScores

# -----------------------------------------------
# Уровень социальной фрустрированности Вассермана
# -----------------------------------------------

_TEST_NAME = 'T9'
_QCOUNT = 20

_QUESTIONS = {
    'ru': (
"""
1. Своим образованием.
""",
"""
2. Взаимоотношениями с коллегами (на работе).
""",
"""
3. Взаимоотношениями с администрацией на работе.
""",
"""
4. Взаимоотношениями с субъектами своей профессиональной деятельности (пассажиры, ученики, пациенты, клиенты и т.
""",
"""
5. Содержанием своей работы в целом.
""",
"""
6. Условиями профессиональной деятельности (или учёбы).
""",
"""
7. Своим положением в обществе.
""",
"""
8. Материальным положением.
""",
"""
9. Жилищно-бытовыми условиями.
""",
"""
10. Отношениями с супругом(ой).
""",
"""
11. Отношениями с ребёнком (детьми).
""",
"""
12. Отношениями с родителями.
""",
"""
13. Обстановкой в обществе (государстве).
""",
"""
14. Отношениями с друзьями, ближайшими знакомыми.
""",
"""
15. Сферой услуг и бытового обслуживания.
""",
"""
16. Сферой медицинского обслуживания.
""",
"""
17. Проведением досуга.
""",
"""
18. Возможностью проводить отпуск.
""",
"""
19. Возможностью выбора места работы.
""",
"""
20. Своим образом жизни в целом.
""",
), 
    'uk': (
"""
1. Своєю освітою.
""",
"""
2. Стосунками із колегами (на роботі).
""",
"""
3. Стосунками з адміністрацією на роботі.
""",
"""
4. Стосунками із суб’єктами своєї професійної діяльності (пасажири, учні, пацієнти, клієнти тощо).
""",
"""
5. Змістом своєї роботи в цілому.
""",
"""
6. Умовами професійної діяльності (чи навчання).
""",
"""
7. Своїм положенням у суспільстві.
""",
"""
8. Матеріальними умовами.
""",
"""
9. Житлово-побутовими умовами.
""",
"""
10. Стосунками з чоловіком/дружиною.
""",
"""
11. Стосунками з дитиною (дітьми).
""",
"""
12. Стосунками з батьками.
""",
"""
13. Ситуацією у суспільстві (державі).
""",
"""
14. Стосунками з друзями, найближчими знайомими.
""",
"""
15. Сферою послуг і побутового обслуговування.
""",
"""
16. Сферою медичного обслуговування.
""",
"""
17. Проведенням дозвілля.
""",
"""
18. Можливістю проводити відпустку.
""",
"""
19. Можливістю вибору місця роботи.
""",
"""
20. Своїм образом життя у цілому.
""",
),
}

_scores_numbers = 'ABCDE'

_SCORES = {
    'ru': [
        ('A', 'Полностью удовлетворён',),
        ('B', 'Скорее удовлетворён',),
        ('C', 'Затрудняюсь ответить',),
        ('D', 'Скорее не удовлетворён'), 
        ('E', 'Полностью не удовлетворён'), 
    ],
    'uk': [
        ('A', 'Цілком задоволений',),
        ('B', 'Швидше задоволений',),
        ('C', 'Важко відповісти',),
        ('D', 'Швидше не задоволений'), 
        ('E', 'Цілком не задоволений'), 
    ],
}

_PARAMS = {
    'ru' : {'1' :'Уровень фрустрированности'},
    'uk' : {'1' :'Рівень фрустрованності'},
}

_RESULTS = () # mode 1: 0-1-2-3-4, mode 2: 4-3-2-1-0

_CONCLUSIONS = {
    'ru' : (
        (0.4, 'Отсутствие или почти отсутствие фрустрированности'), 
        (1.4, 'Очень низкий уровень фрустрированности'), 
        (1.9, 'Пониженный уровень фрустрированности'), 
        (2.4, 'Неопределённый уровень фрустрированности'), 
        (2.9, 'Умеренный уровень фрустрированности'), 
        (3.4, 'Повышенный уровень фрустрированности'), 
        (4.0, 'Очень высокий уровень фрустрированности'), 
    ),
    'uk' : (
        (0.4, 'Відсутність (майже відсутність) фрустрованності'), 
        (1.4, 'уже низький рівень фрустрованності'), 
        (1.9, 'Знижений рівень фрустрованності'), 
        (2.4, 'Невизначений рівень фрустрованності'), 
        (2.9, 'Помірний рівень фрустрованності'), 
        (3.4, 'Підвищений рівень фрустрованності'), 
        (4.0, 'Дуже високий рівень фрустрованності'), 
    ),
}

_HEADERS = {
    'ru': 
"""
Прочитайте каждый вопрос и выберите один наиболее подходящий ответ.

Удовлетворены ли вы...
""",
    'uk': 
"""
Прочитайте кожне запитання і оберіть одну відповідь, що найкраще підходить.

Чи задоволені ви...
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
    
    def _get_score(mode, s):
        if s == 'A':
            return mode == 2 and 4 or 0
        if s == 'B':
            return mode == 1 and 1 or 3
        if s == 'C':
            return mode == 1 and 2 or 2
        if s == 'D':
            return mode == 1 and 3 or 1
        if s == 'E':
            return mode == 1 and 4 or 0
        return 0

    if _is_random_scores:
        random.shuffle(scores)

    answers = []
    buttons = []
    qs = question + 1
    mode = _RESULTS and len(_RESULTS) > question and _RESULTS[question] or 1
    for i, x in enumerate(scores):
        b, s = x
        bs = _get_score(mode, b)
        n = _scores_numbers[i]
        q = '%s.%s:%s' % (_TEST_NAME, qs, bs)
        answers.append('%s) %s' % (n, s))
        buttons.append((n, q))

    if _is_random_scores:
        buttons = sorted(buttons)

    return '\n'.join(answers), buttons

def get_result(storage, name, lang, mode=None, question=None):
    global _results

    res = (0, NO_KEY)
    data = storage.getall(name)
    conclusions = _CONCLUSIONS[lang]

    x = 0

    for n in range(0, _QCOUNT):
        key = ('%s.%s' % (_TEST_NAME, n+1)).encode()
        x += int(data.get(key) or 0)
    x = x*1.0 / (question or _QCOUNT)
    c = ''
    for i, item in enumerate(conclusions):
        if x <= item[0]:
            c = conclusions[i][1]
            res = (x, '<b>%s</b>' % c)
            break

    if question == _QCOUNT:
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
        text = '[%s] %s.' % get_result(storage, name, lang, question=question) #XXX mode=1|2 ?
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

    r = r / 20.0

    rp = '%s.R' % key
    if rp in data[key]:
        x = float(data[key].get(rp, '0'))
        if r == x:
            out = 'OK'
        else:
            out = 'Error %s [%s:%s]' % (rp, r, x)
            if with_print or IsWithPrintErrors:
                print(key, out)

    return out or NO_RESULTS
