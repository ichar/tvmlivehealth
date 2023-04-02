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

# ------------------------------------------------------------
# Шкала реактивной и личностной тревожности Спилбергера-Ханина
# ------------------------------------------------------------

_TEST_NAME = 'T10'
_QCOUNT = 40

_QUESTIONS = {
    'ru': (
"""
1. Я спокоен.
""",
"""
2. Мне ничто не угрожает.
""",
"""
3. Я нахожусь в напряжении.
""",
"""
4. Я испытываю сожаление.
""",
"""
5. Я чувствую себя спокойно.
""",
"""
6. Я расстроен.
""",
"""
7. Меня волнуют возможные неудачи.
""",
"""
8. Я чувствую себя отдохнувшим.
""",
"""
9. Я встревожен.
""",
"""
10. Я испытываю чувство внутреннего удовлетворения.
""",
"""
11. Я уверен в себе.
""",
"""
12. Я нервничаю.
""",
"""
13. Я не нахожу себе места.
""",
"""
14. Я взвинчен.
""",
"""
15. Я не чувствую скованности.
""",
"""
16. Я доволен.
""",
"""
17. Я озабочен.
""",
"""
18. Я слишком возбуждён и мне не по себе.
""",
"""
19. Мне радостно.
""",
"""
20. Мне приятно.
""",
"""
21. Я испытываю удовольствие.
""",
"""
22. Я обычно устаю.
""",
"""
23. Я легко могу заплакать.
""",
"""
24. Я хотел бы быть таким же счастливым, как и другие.
""",
"""
25. Нередко я проигрываю из-за того, что недостаточно быстро принимаю решения.
""",
"""
26. Обычно я чувствую себя бодрым.
""",
"""
27. Я спокоен, хладнокровен и собран.
""",
"""
28. Ожидаемые трудности обычно очень тревожат меня.
""",
"""
29. Я слишком переживаю из-за пустяков.
""",
"""
30. Я вполне счастлив.
""",
"""
31. Я принимаю всё слишком близко к сердцу.
""",
"""
32. Мне не хватает уверенности в себе.
""",
"""
33. Обычно я чувствую себя в безопасности.
""",
"""
34. Я стараюсь избегать критических ситуаций и трудностей.
""",
"""
35. У меня бывает хандра.
""",
"""
36. Я доволен.
""",
"""
37. Всякие пустяки отвлекают и волнуют меня.
""",
"""
38. Я так сильно переживаю свои разочарования, что потом долго не могу о них забыть.
""",
"""
39. Я уравновешенный человек.
""",
"""
40. Меня охватывает сильное беспокойство, когда я думаю о своих делах и заботах.
""",
), 
    'uk': (
"""
1. Я спокійний.
""",
"""
2. Мені ніщо не загрожує.
""",
"""
3. Я відчуваю себе напружено.
""",
"""
4. Я відчуваю жаль.
""",
"""
5. Я почуваю себе спокійно.
""",
"""
6. Я засмучений.
""",
"""
7. Мене хвилюють можливі невдачі.
""",
"""
8. Я почуваю себе відпочилим.
""",
"""
9. Я стурбований.
""",
"""
10. Я маю відчуття внутрішнього задоволення.
""",
"""
11. Я впевнений у собі.
""",
"""
12. Я нервуюся.
""",
"""
13. Я не знаходжу собі місця.
""",
"""
14. Я напружений.
""",
"""
15. Я не відчуваю скутості.
""",
"""
16. Я задоволений.
""",
"""
17. Я заклопотаний.
""",
"""
18. Я занадто збуджений і мені не по собі.
""",
"""
19. Мені радісно.
""",
"""
20. Мені приємно.
""",
"""
21. Я відчуваю задоволення.
""",
"""
22. Я зазвичай втомлююсь.
""",
"""
23. Я легко можу заплакати.
""",
"""
24. Я хотів би бути таким же щасливим, як і інші.
""",
"""
25. Часто я програю через те, що недостатньо швидко ухвалюю рішення.
""",
"""
26. Зазвичай я почуваю себе бадьорим.
""",
"""
27. Я спокійний, холоднокровний і зібраний.
""",
"""
28. Очікувані труднощі зазвичай дуже турбують мене.
""",
"""
29. Я занадто переживаю через дрібниці.
""",
"""
30. Я цілком щасливий.
""",
"""
31. Я приймаю все занадто близько до серця.
""",
"""
32. Мені не вистачає впевненості у собі.
""",
"""
33. Зазвичай я почуваю себе у безпеці.
""",
"""
34. Я намагаюся уникати критичних ситуацій і труднощів.
""",
"""
35. У мене буває хандра.
""",
"""
36. Я задоволений.
""",
"""
37. Всілякі дрібниці відволікають і хвилюють  мене.
""",
"""
38. Я так сильно переживаю свої розчарування, що потім довго не можу про них забути.
""",
"""
39. Я врівноважена людина.
""",
"""
40. Мене охоплює сильне занепокоєння, коли я думаю про свої справи і турботи.""",
),
}

_scores_numbers = 'ABCD'

_SCORES = {
    'ru': [(
        ('A', 'Вовсе нет',),
        ('B', 'Пожалуй, так',),
        ('C', 'Верно',),
        ('D', 'Совершенно верно'), 
    ), (
        ('A', 'Почти никогда',),
        ('B', 'Иногда',),
        ('C', 'Часто',),
        ('D', 'Почти всегда'), 
    )],
    'uk': [(
        ('A', 'Зовсім ні',),
        ('B', 'Мабуть, так',),
        ('C', 'Вірно',),
        ('D', 'Цілком вірно'), 
    ), (
        ('A', 'Майже ніколи',),
        ('B', 'Іноді',),
        ('C', 'Часто',),
        ('D', 'Майже завжди'), 
    )],
}

_RESULTS = {
    'ru': {
        '1' : (([], [], [3, 4, 6, 7, 9, 12, 14, 15, 40, 18]), ([], [], [1, 2, 5, 8, 10, 11, 13, 16, 19, 20])),
        '2' : (([], [], [22, 23, 24, 25, 28, 29, 31, 32, 34, 35, 37, 38, 40]), ([], [], [21, 26, 27, 30, 33, 36, 39])),
    },
    'uk': {
        '1' : (([], [], [3, 4, 6, 7, 9, 12, 14, 15, 40, 18]), ([], [], [1, 2, 5, 8, 10, 11, 13, 16, 19, 20])),
        '2' : (([], [], [22, 23, 24, 25, 28, 29, 31, 32, 34, 35, 37, 38, 40]), ([], [], [21, 26, 27, 30, 33, 36, 39])),
    },
}

_C1 = {'1' : 50, '2' : 35}

_MODE_CONTROL = ()

_CONCLUSIONS = {
    'ru' : {
        '1' : ('Реактивная тревожность', [
            (31, 'Низкий уровень тревожности'), 
            (45, 'Умеренный уровень тревожности'), 
            (69, 'Высокий уровень тревожности')
        ]),
        '2' : ('Личностная тревожность', [
            (31, 'Низкий уровень тревожности'), 
            (45, 'Умеренный уровень тревожности'), 
            (69, 'Высокий уровень тревожности')
        ]),
    },
    'uk' : {
        '1' : ('Реактивна тривожність', [(31, 'Низький рівень тривожності'), (45, 'Помірний рівень тривожності'), (999, 'Високий рівень тривожності')]),
        '2' : ('Особистісна тривожність', [(31, 'Низький рівень тривожності'), (45, 'Помірний рівень тривожності'), (999, 'Високий рівень тривожності')]),
    },
}

_HEADERS = {
    'ru': 
"""
Прочитайте внимательно каждое из приведенных ниже утверждений и выберите ответ в зависимости от того, как вы себя чувствуете в данный момент. Над вопросами долго не задумывайтесь, поскольку «правильных» или «неправильных» ответов нет.
""",
    'uk': 
"""
Прочитайте уважно кожне з наведених нижче тверджень і оберіть відповідь залежно від того, як ви себе почуваєте на даний момент. Над запитаннями довго не замислюйтесь, оскільки «правильних» чи «неправильних» відповідей немає.
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
    scores = list(_SCORES[lang][question >= 20 and 1 or 0])
    
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
    conclusions = _CONCLUSIONS[lang]

    if mode == 1:
        keys = sorted([x for x in results.keys() if x[0].isdigit()])
    else:
        keys = sorted([x for x in results.keys() if x[0] in 'LF'])

    cs, px = {}, {}

    for p in keys:
        # p: ключ параметра: LF или 0,1...
        x = 0
        for i in range(0, 2):
            # i=0: группа "1 тип вопроса"
            # i=1: группа "2 тип вопроса"
            for k, sc in enumerate(results[p][i]):
                # k: номер группы 0,1,2
                # sc: номера вопросов (3 группы)
                # score: баллы за ответ на вопрос
                score = (k == 2 and 1 or k == 1 and 2 or 3) * (i == 1 and -1 or 1)
                for n in sc:
                    # n: номер вопроса
                    key = ('%s.%s' % (_TEST_NAME, n)).encode()
                    v = int(data.get(key, 0))
                    x += v*score

        if mode == 1:
            _results[p] = [x, NO_KEY]

            x = x + _C1[p]
            px[p] = x
            c = ''
            # param: наименование параметра
            # conclusion: характеристика (группа ответов)
            param, conclusion = conclusions[p]
            for i, item in enumerate(conclusion):
                # item: граничное значение параметра
                if x <= item[0]:
                    # c: итоговая оценка по параметру
                    c = item[1]
                    _results[p][1] = c
                    break
            # res: текст результата
            res += '%s. %s: [%s] <b>%s</b>\n' % (p, param, x, c)
        else:
            if x < 0:
                return True

    if mode == 1:
        return res.strip()

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
        result = get_result(storage, name, lang, mode=1)
        bot.send_message(message.chat.id, result, parse_mode=DEFAULT_PARSE_MODE)
        is_run = question < _QCOUNT

        if is_run:
            time.sleep(3)

    if question in _MODE_CONTROL and 'query_id' in kw:
        if get_result(storage, name, lang, mode=2) and not storage.get(name, 'warning'):
            text = _WARNINGS[lang][0]

            bot.answer_callback_query(
                kw['query_id'],
                text=text,
                show_alert=True
                )

            storage.set(name, 'warning', 1)
            time.sleep(3)

    if is_run:
        answers, buttons = get_answers(question, lang)
        text = '%s\n\n%s' % (get_question(question, lang), answers)
        send_inline_keyboard(bot, message, buttons, text)

    elif 'query_id' in kw:
        _test_name = test_name()

        dbs.drop_before(_test_name, **kw)
        dbs.save_params(_test_name, _CONCLUSIONS, _results, **kw)

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
        x0 = re.sub(r'\*', '', x[0])
        x1 = x[1].strip()
        if len(x) > 1 and x0.isdigit():
            n = int(x0)
            q = x1
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
        v = int(data[key][k])
        for i in range(0, 2):
            if int(q) in res[i]:
                s += v*(i == 0 and 1 or -1)
                break
    return s

def selftest(data, lang, with_print=None):
    key = _TEST_NAME
    results = _RESULTS[lang]

    out = []
    r = {}
    for k in sorted(results.keys()):
        if not k in r:
            r[k] = 0
        x = check(data, key, (results[k][0][2], results[k][1][2]))
        if with_print:
            print(x)
        r[k] += x

    for k in sorted(r.keys()):
        rp = '%s.RC%s' % (key, k)
        if rp in data[key]:
            x = int(data[key].get(rp, '0'))
            if r[k] == x:
                out.append('OK')
            else:
                out.append('Error %s [%s:%s]' % (rp, r[k], x))
        else:
            out.append(NO_RESULTS)

    is_ok, is_error = 1, 0
    for s in out:
        if s.startswith('OK'):
            pass
        elif s.startswith('Error'):
            is_ok = 0
            is_error = 1
            if with_print or IsWithPrintErrors:
                print(key, s)
            break
        else:
            is_ok = 0
            break

    return is_ok and 'OK' or is_error and 'Error' or NO_RESULTS
