# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy
import random

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsRandomScores, IsWithGroup,
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, NO_RESULTS, NO_KEY, RCODES
from app.dialogs.start import help
from app.handlers import *

from app import dbs

# Группировка результатов
_with_group = IsWithGroup
# Случайный порядок ответов
_is_random_scores = IsRandomScores

# --------------------------------------------
# Тест на диагностику враждебности Кука-Медлея
# --------------------------------------------

_TEST_NAME = 'T14'
_QCOUNT = 27

_QUESTIONS = {
    'ru': (
"""
1. Я часто встречаю людей, называющих себя экспертами, хотя они таковыми не являются.
""",
"""
2. Мне часто приходилось выполнять указания людей, которые знали меньше, чем я.
""",
"""
3. Многих людей можно обвинить в аморальном поведении.
""",
"""
4. Многие люди преувеличивают тяжесть своих неудач, чтобы получить сочувствие и помощь.
""",
"""
5. Временами мне приходилось грубить людям, которые вели себя невежливо по отношению ко мне и действовали мне на нервы.
""",
"""
6. Большинство людей заводят друзей, потому что друзья могут быть полезны.
""",
"""
7. Часто необходимо затратить много усилий, чтобы убедить других в своей правоте.
""",
"""
8. Люди часто разочаровывали меня.
""",
"""
9. Обычно люди требуют большего уважения своих прав, чем стремятся уважать права других.
""",
"""
10. Большинство людей не нарушают закон, потому что боятся быть пойманными.
""",
"""
11. Зачастую люди прибегают к нечестным способам, чтобы не потерять возможной выгоды.
""",
"""
12. Я считаю, что многие люди используют ложь, для того чтобы двигаться дальше.
""",
"""
13. Существуют люди, которые настолько мне неприятны, что я невольно радуюсь, когда их постигают неудачи.
""",
"""
14. Я часто могу отойти от своих принципов, чтобы превзойти своего противника.
""",
"""
15. Если люди поступают со мной плохо, я обязательно отвечаю им тем же, хотя бы из принципа.
""",
"""
16. Как правило, я отчаянно отстаиваю свою точку зрения.
""",
"""
17. Некоторые члены моей семьи имеют привычки, которые меня раздражают.
""",
"""
18. Я не всегда легко соглашаюсь с другими.
""",
"""
19. Никого никогда не заботит то, что с тобой происходит.
""",
"""
20. Более безопасно никому не верить.
""",
"""
21. Я могу вести себя дружелюбно с людьми, которые, по моему мнению, поступают неверно.
""",
"""
22. Многие люди избегают ситуаций, в которых они должны помогать другим.
""",
"""
23. Я не осуждаю людей за то, что они стремятся присвоить себе всё, что только можно.
""",
"""
24. Я не виню человека за то, что он в своих целях использует других людей, позволяющих ему это делать.
""",
"""
25. Меня раздражает, когда другие отрывают меня от дела.
""",
"""
26. Мне бы определённо понравилось, если бы преступника наказали его же преступлением.
""",
"""
27. Я не стремлюсь скрыть плохое мнение о других людях.
""",
), 
    'uk': (
"""
1. Я часто зустрічаю людей, які називають себе експертами, хоча такими не є.
""",
"""
2. Мені часто доводилося виконувати вказівки людей, які знали менше, ніж я.
""",
"""
3. Багатьох людей можна звинуватити у аморальній поведінці.
""",
"""
4. Багато людей перебільшують тягар своїх невдач, аби отримати співчуття і допомогу.
""",
"""
5. Часом мені доводиться казати грубощі людям, які поводилися неввічливо щодо мене і нервували мене.
""",
"""
6. Більшість людей заводить друзів, тому що друзі можуть бути корисними.
""",
"""
7. Часто необхідно витратити багато зусиль, аби переконати інших у своїй правоті.
""",
"""
8. Люди часто розчаровували мене.
""",
"""
9. Зазвичай люди вимагають більшої поваги до своїх прав, аніж намагаються поважати права інших.
""",
"""
10. Більшість людей не порушують закон, тому що бояться бути спійманими.
""",
"""
11. Часто люди вдаються до нечесних способів, щоб не втратити можливу вигоду.
""",
"""
12. Я вважаю, що багато людей використовують брехню, аби рухатися далі.
""",
"""
13. Існують люди, які настільки мені неприємні, що я мимоволі радію, коли їх спіткає невдача.
""",
"""
14. Я часто можу відійти від своїх принципів, щоб перевершити свого супротивника.
""",
"""
15. Якщо люди вчиняють зі мною погано, я обов’язково відповідаю їм тим самим, хоча б з принципу.
""",
"""
16. Як правило, я відчайдушно обстоюю свою точку зору.
""",
"""
17. Деякі член моєї родини мають звички, які мене дратують.
""",
"""
18. Я не завжди легко погоджуюся з іншими.
""",
"""
19. Нікого ніколи не турбує те, що з тобою відбувається.
""",
"""
20. Більш безпечно нікому не вірити.
""",
"""
21. Я можу дружньо поводитися з людьми, які, на мою думку, чинять неправильно.
""",
"""
22. Багато людей уникають ситуацій, в яких вони повинні допомагати іншим.
""",
"""
23. Я не засуджую людей за те, що вони намагаються привласнити собі все, що тільки можливо.
""",
"""
24. Я не звинувачую людину за те, що він у своїх цілях використовує інших людей, які дозволяють йому це робити.
""",
"""
25. Мене дратує, коли інші відривають мене від справи.
""",
"""
26. Мені б напевно сподобалося, якби злочинця карали його ж злочином.
""",
"""
27. Я не прагну приховати поганого ставлення про інших людей.
""",
),
}

_scores_numbers = 'ABCDEF'

_SCORES = {
    'ru': [
        ( 6, 'Обычно',),
        ( 5, 'Частично',),
        ( 4, 'Иногда',),
        ( 3, 'Случайно',),
        ( 2, 'Редко',),
        ( 1, 'Никогда',),
    ],
    'uk': [
        ( 6, 'Зазвичай',),
        ( 5, 'Частково',),
        ( 4, 'Іноді',),
        ( 3, 'Випадково',),
        ( 2, 'Зрідка',),
        ( 1, 'Ніколи',),
    ],
}

_PARAMS = {
    'ru': {
        '01' : ('Цинизм', (1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 19, 20, 22)),
        '02' : ('Агрессивность', (5, 14, 15, 16, 21, 23, 24, 26, 27)),
        '03' : ('Враждебность', (8, 13, 17, 18, 25)),
    },
    'uk': {
        '01' : ('Цинізм', (1, 2, 3, 4, 6, 7, 9, 10, 11, 12, 19, 20, 22)),
        '02' : ('Агресивність', (5, 14, 15, 16, 21, 23, 24, 26, 27)),
        '03' : ('Ворожість', (8, 13, 17, 18, 25)),
    },
}

_RESULTS = {
    'ru' : {
        '01' : [
            (12, ''), 
            (25, 'Низкий показатель цинизма'), 
            (40, 'Средний показатель цинизма с тенденцией к низкому'), 
            (64, 'Средний показатель цинизма с тенденцией к высокому'), 
            (78, 'Высокий показатель цинизма'),
        ],
        '02' : [
            (8, ''), 
            (15, 'Низкий показатель агрессивности'), 
            (30, 'Средний показатель агрессивности с тенденцией к низкому'), 
            (45, 'Средний показатель агрессивности с тенденцией к высокому'), 
            (54, 'Высокий показатель агрессивности'),
        ],
        '03' : [
            (4, ''), 
            (10, 'Низкий показатель враждебности'), 
            (18, 'Средний показатель враждебности с тенденцией к низкому'), 
            (25, 'Средний показатель враждебности с тенденцией к высокому'), 
            (30, 'Высокий показатель враждебности'),
        ],
    },
    'uk' : {
        '01' : [(12, ''), (25, 'Низький показник цинізму'), (40, 'Середній показник цинізму із тенденцією до низького'), (64, 'Середній показник цинізму із тенденцією до високого'), (78, 'Високий показник цинізму'),],
        '02' : [(8, ''), (15, 'Низький показник агресивності'), (30, 'Середній показник агресивності із тенденцією до низького'), (45, 'Середній показник агресивності із тенденцією до високого'), (54, 'Високий показник агресивності'),],
        '03' : [(4, ''), (10, 'Низький показник ворожості'), (18, 'Середній показник ворожості із тенденцією до низького'), (25, 'Середній показник ворожості із тенденцією до високого'), (30, 'Високий показник ворожості'),],
    },
}

_CONCLUSIONS = {
    'ru' : {
        'F1' : ([(0, ''), (0, ''), (0, '')]),
    },
    'uk' : {
        'F1' : ([(0, ''), (0, ''), (0, '')]),
    },
}

_HEADERS = {
    'ru': 
"""
Внимательно прочитайте предложенные суждения и выберите ответ, который наиболее точно соответствует вашему мнению.
""",
    'uk': 
"""
Уважно прочитайте запропоновані твердження і оберіть відповідь, яка найбільш точно відповідає вашій думці.
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
    params = _PARAMS[lang]
    scores = _SCORES[lang]
    results = _RESULTS[lang]
    conclusions = _CONCLUSIONS[lang]

    keys = sorted([x for x in params.keys() if x.isdigit()])

    cs, px = {}, {}

    for p in keys:
        # p: ключ параметра: 01,02...
        # name: наименование параметра
        x = 0
        param, sc = params[p]
        # sc: словарь ответов по каждой группе
        for n in sc:
            # n: номер вопроса
            key = ('%s.%s' % (_TEST_NAME, n)).encode()
            v = int(data.get(key, 0))
            x += v

        px[p] = x

        c = ''
        for i, item in enumerate(results[p]):
            # i: индекс результата
            # item: граничное значение параметра
            if x <= item[0]:
                # c: итоговая оценка по параметру
                c = item[1]
                if _with_group:
                    if i not in cs:
                        cs[i] = []
                    cs[i].append(p)
                break

        _results[p] = (x, c)

        # res: текст результата (параметры)
        res += '%s. %s: [%s] <b>%s</b>\n' % (p, param, x, c)

    #res += ' * '*3+'\n'

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
        text = get_result(storage, name, lang)
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
        dbs.save_params(_test_name, _PARAMS, _results, **kw)
        """
        storage.delete(name, command='%s.R' % _TEST_NAME)
        storage.delete(name, command='%s.T' % _TEST_NAME)

        for p in sorted([x for x in _RESULTS[lang].keys()]):
            if p in _results:
                param = _PARAMS[lang][p][0]
                value, s1 = _results[p]
                storage.set(name, '%s.RP%s' % (_TEST_NAME, p), value)
                storage.set(name, '%s.TP%s' % (_TEST_NAME, p), '<i>%s</i>. %s:%s' % (param, s1, value), with_encode=True)
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
        m = re.match(r'([%s])\.(.*)(\(\d+\))' % numbers, line)
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
            m = re.match(r'([%s])\.(.*)(\(\d+\))' % numbers, line)
            if not m:
                continue
            b = int(re.sub(r'[\(\)]', r'', m.group(3)))
            s = m.group(2).strip()
            scores.append((s, b))
            i += 1
    for i, x in enumerate(scores):
        s, b = x
        print("%s( %s, '%s',)," % (' '*8, b, s))

def check(data, key, res):
    s = 0
    for k in data[key].keys():
        #print(k)
        q = k.split('.')[1]
        if not q.isdigit():
            continue
        #print(q)
        if int(q) in res:
            s += int(data[key][k])
    return s

def selftest(data, lang, with_print=None):
    key = _TEST_NAME
    params = _PARAMS[lang]
    conclusions = _CONCLUSIONS[lang]

    out = []
    r = {}
    for i, p in enumerate(sorted(params.keys())):
        x = check(data, key, params[p][1])
        if with_print:
            print(x)

        rp = '%s.RP%s' % (key, p)
        if rp in data[key]:
            r[rp] = int(data[key].get(rp, '0'))
            out.append(r[rp] == x and 'OK.%s [%s]' % (p, x) or 'Error %s [%s:%s]' % (rp, x, r[rp]))
            if with_print:
                print(out[i])
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
