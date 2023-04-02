# -*- coding: utf-8 -*-

import re
import time

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, 
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, NO_RESULTS, NO_KEY, RCODES
from app.dialogs.start import help
from app.handlers import *

from app import dbs

# ---------------------------------------------
# Госпитальная шкала тревоги и депрессии (HADS)
# ---------------------------------------------

_TEST_NAME = 'T1'
_QCOUNT = 14

_QUESTIONS = {
    'ru': (
"""
1. Я испытываю напряжение, мне не по себе
""",
"""
2. Я испытываю страх, кажется, что что-то ужасное может вот-вот случиться
""",
"""
3. Беспокойные мысли крутятся у меня в голове
""",
"""
4. Я легко могу присесть и расслабиться
""",
"""
5. Я испытываю внутреннее напряжение или дрожь
""",
"""
6. Я испытываю неусидчивость, мне постоянно нужно двигаться
""",
"""
7. У меня бывает внезапное чувство паники
""",
"""
8. То, что приносило мне большое удовольствие, и сейчас вызывает у меня такое же чувство
""",
"""
9. Я способен рассмеяться и увидеть в том или ином событии смешное
""",
"""
10. Я испытываю бодрость
""",
"""
11. Мне кажется, что я стал все делать очень медленно
""",
"""
12. Я не слежу за своей внешностью
""",
"""
13. Я считаю, что мои дела (занятия, увлечения) могут принести мне чувство удовлетворения
""",
"""
14. Я могу получить удовольствие от хорошей книги, радио- или телепрограммы
""",
), 
    'uk': (
"""
1. Я відчуваю напругу, мені незатишно
""",
"""
2. Я відчуваю страх, здається, ось-ось має трапитися щось жахливе
""",
"""
3. Тривожні думки крутяться у мене в голові
""",
"""
4. Я легко можу присісти й розслабитися
""",
"""
5. Я відчуваю внутрішню напругу чи тремтіння
""",
"""
6. Я відчуваю непосидючість, мені постійно потрібно рухатися
""",
"""
7. У мене буває раптове почуття паніки
""",
"""
8. Те, що приносило мені велике задоволення, і зараз викликає у мене таке ж відчуття
""",
"""
9. Я здатен розсміятися і побачити смішне у тій чи іншій події
""",
"""
10. Я відчуваю бадьорість
""",
"""
11. Мені здається, я став робити все дуже повільно
""",
"""
12. Я не стежу за своєю зовнішністю
""",
"""
13. Я вважаю, що мої справи (заняття, захоплення) можуть принести мені почуття задоволення
""",
"""
14. Я можу отримати задоволення від гарної книги, радіо- чи телепрограми
""",
),
}

_ANSWERS = ({
    'ru': (('всё время', 'T1.1:3'), ('часто', 'T1.1:2'), ('время от времени, иногда', 'T1.1:1'), ('совсем не испытываю', 'T1.1:0')),
    'uk': (('увесь час', 'T1.1:3'), ('часто', 'T1.1:2'), ('час від часу, іноді', 'T1.1:1'), ('зовсім не відчуваю', 'T1.1:0')),
}, {
    'ru': (('определенно это так, и страх очень велик', 'T1.2:3'), ('да, это так, но страх не очень велик', 'T1.2:2'), ('иногда, но это меня не беспокоит', 'T1.2:1'), ('совсем не испытываю', 'T1.2:0')),
    'uk': (('безперечно, це так, і страх дуже великий', 'T1.2:3'), ('так, це так, але страх не дуже великий', 'T1.2:2'), ('іноді, але це мене не турбує', 'T1.2:1'), ('зовсім не відчуваю', 'T1.2:0')),
}, {
    'ru': (('постоянно', 'T1.3:3'), ('большую часть времени', 'T1.3:2'), ('время от времени и не так часто', 'T1.3:1'), ('только иногда', 'T1.3:0')),
    'uk': (('постійно', 'T1.3:3'), ('більшу частину часу', 'T1.3:2'), ('час від часу і не так часто', 'T1.3:1'), ('лише іноді', 'T1.3:0')),
}, {
    'ru': (('определенно, это так', 'T1.4:0'), ('наверно, это так', 'T1.4:1'), ('лишь изредка, это так', 'T1.4:2'), ('совсем не могу', 'T1.4:3')),
    'uk': (('безперечно, це так', 'T1.4:0'), ('мабуть, це так', 'T1.4:1'), ('лише іноді це так', 'T1.4:2'), ('зовсім не можу', 'T1.4:3')),
}, {
    'ru': (('совсем не испытываю', 'T1.5:0'), ('иногда', 'T1.5:1'), ('часто', 'T1.5:2'), ('очень часто', 'T1.5:3')),
    'uk': (('зовсім не відчуваю', 'T1.5:0'), ('іноді', 'T1.5:1'), ('часто', 'T1.5:2'), ('дуже часто', 'T1.5:3')),
}, {
    'ru': (('определенно, это так', 'T1.6:3'), ('наверно, это так', 'T1.6:2'), ('лишь в некоторой степени, это так', 'T1.6:1'), ('совсем не испытываю', 'T1.6:0')),
    'uk': (('безперечно, це так', 'T1.6:3'), ('мабуть, це так', 'T1.6:2'), ('лише певною мірою це так', 'T1.6:1'), ('зовсім не відчуваю', 'T1.6:0')),
}, {
    'ru': (('очень часто', 'T1.7:3'), ('довольно часто', 'T1.7:2'), ('не так уж часто', 'T1.7:1'), ('совсем не бывает', 'T1.7:0')),
    'uk': (('дуже часто', 'T1.7:3'), ('досить часто', 'T1.7:2'), ('не так вже й часто', 'T1.7:1'), ('зовсім не буває', 'T1.7:0')),
}, {
    'ru': (('определенно, это так', 'T1.8:0'), ('наверное, это так', 'T1.8:1'), ('лишь в очень малой степени, это так', 'T1.8:2'), ('это совсем не так', 'T1.8:3')),
    'uk': (('безперечно, це так', 'T1.8:0'), ('мабуть, це так', 'T1.8:1'), ('лише малою мірою це так', 'T1.8:2'), ('це зовсім не так', 'T1.8:3')),
}, {
    'ru': (('определенно, это так', 'T1.9:0'), ('наверное, это так', 'T1.9:1'), ('лишь в очень малой степени, это так', 'T1.9:2'), ('совсем не способен', 'T1.9:3')),
    'uk': (('безперечно, це так', 'T1.9:0'), ('мабуть, це так', 'T1.9:1'), ('лише малою мірою це так', 'T1.9:2'), ('це зовсім не так', 'T1.9:3')),
}, {
    'ru': (('совсем не испытываю', 'T1.10:3'), ('очень редко', 'T1.10:2'), ('иногда', 'T1.10:1'), ('практически все время', 'T1.10:0')),
    'uk': (('зовсім не відчуваю', 'T1.10:3'), ('дуже рідко', 'T1.10:2'), ('іноді', 'T1.10:1'), ('практично увесь час', 'T1.10:0')),
}, {
    'ru': (('практически все время', 'T1.11:3'), ('часто', 'T1.11:2'), ('иногда', 'T1.11:1'), ('совсем нет', 'T1.11:0')),
    'uk': (('практично увесь час', 'T1.11:3'), ('часто', 'T1.11:2'), ('іноді', 'T1.11:1'), ('зовсім ні', 'T1.11:0')),
}, {
    'ru': (('определенно, это так', 'T1.12:3'), ('я не уделяю этому столько времени, сколько нужно', 'T1.12:2'), ('может быть, я стал меньше уделять этому времени', 'T1.12:1'), ('я слежу за собой так же, как и раньше', 'T1.12:0')),
    'uk': (('безперечно, це так', 'T1.12:3'), ('я не приділяю цьому стільки уваги, скільки потрібно', 'T1.12:2'), ('можливо, я став приділяти цьому менше уваги', 'T1.12:1'), ('я стежу за собою, як і раніше', 'T1.12:0')),
}, {
    'ru': (('точно так же, как и обычно', 'T1.13:0'), ('да, но не в той степени, как раньше', 'T1.13:1'), ('значительно меньше, чем обычно', 'T1.13:2'), ('совсем так не считаю', 'T1.13:3')),
    'uk': (('точно так само, як і зазвичай', 'T1.13:0'), ('так, але не тією ж мірою, як раніше', 'T1.13:1'), ('значно менше, ніж зазвичай', 'T1.13:2'), ('зовсім так не вважаю', 'T1.13:3')),
}, {
    'ru': (('часто', 'T1.14:0'), ('иногда', 'T1.14:1'), ('редко', 'T1.14:2'), ('очень редко', 'T1.14:3')),
    'uk': (('часто', 'T1.14:0'), ('іноді', 'T1.14:1'), ('зрідка', 'T1.14:2'), ('дуже рідко', 'T1.14:3')),
})

_PARAMS = {
    'ru' : {
        '1' : ('Тревожность', (1, 2, 3, 4, 5, 6, 7)),
        '2' : ('Депрессия', (8, 9, 10, 11, 12, 13, 14)),
    },
    'uk' : {
        '1' : ('Тривожність', (1, 2, 3, 4, 5, 6, 7)),
        '2' : ('Депресія', (8, 9, 10, 11, 12, 13, 14)),
    },
}

_RESULTS = {
    'ru': {
        '1' : ['Тревожность', (
            (7, 'У Вас нет никаких особых проблем с тревожностью, с которой Вы бы не смогли справиться самостоятельно, психологическая помощь не требуется'), 
            (10, 'В наличии субклинически выраженная тревожность, вероятно, имеет смысл обратиться за помощью к психологу'), 
            (99, 'В наличии клинически выраженная тревожность, настоятельно рекомендуется обратиться к специалисту')
        )],
        '2' : ['Депрессия', (
            (7, 'У Вас нет никаких особых проблем с депрессией, с которой Вы бы не смогли справиться самостоятельно, психологическая помощь не требуется'), 
            (10, 'В наличии субклинически выраженная депрессия, вероятно, имеет смысл обратиться за помощью к психологу'), 
            (99, 'В наличии клинически выраженная депрессия, настоятельно рекомендуется обратиться к специалисту')
        )],
    },
    'uk': {
        '1' : ['Тривожність', ((7, 'У Вас немає жодних особливих психологічних проблем, які би Ви не могли здолати самостійно, психологічна допомога не потрібна'), (10, 'В наявності субклінічно виражена тривожність, ймовірно, має сенс звернутися за допомогою до психолога'), (99, 'В наявності клінічно виражена тривожність, наполегливо рекомендується звернутися до психолога'))],
        '2' : ['Депресія', ((7, 'У вас немає жодних особливих психологічних проблем, які би ви не могли здолати самостійно, психологічна допомога не потрібна'), (10, 'В наявності субклінічно виражена депресія, ймовірно, має сенс звернутися за допомогою до психолога'), (99, 'В наявності клінічно виражена депресія, наполегливо рекомендується звернутися до психолога'))],
    },
    'en': {
        '1' : ['Anxiety', (
             (7, 'You don\'t have any particular anxiety problems that you can\'t manage on your own, you don\'t need psychological help'),
             (10, 'In the presence of subclinical anxiety, it probably makes sense to seek help from a psychologist'),
             (99, 'Clinical anxiety present, specialist advice highly recommended')
         )],
        '2' : ['Depression', (
             (7, 'You don\'t have any particular problems with depression that you can\'t deal with on your own, you don\'t need psychological help')
             (10, 'In the presence of subclinical depression, it probably makes sense to seek help from a psychologist'),
             (99, 'Clinical depression present, specialist consultation highly recommended')
         )],
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

def get_finish(storage, name, i, lang, no_eof=None):
    nic = storage.get(name, 'nic', with_decode=True)
    s = '%s%s' % (nic and '%s!\n\n' % nic or _FINISH[lang][0], _FINISH[lang][i].strip())
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_result(storage, name, lang, mode=None):
    global _results

    res = ''
    data = storage.getall(name)
    params = _PARAMS[lang]
    results = _RESULTS[lang]

    keys = sorted([x for x in params.keys() if x.isdigit()])

    for k in keys:
        # k: ключ параметра: 1,2...
        x = 0
        for n in params[k][1]:
            key = ('%s.%s' % (_TEST_NAME, n)).encode()
            x += int(data.get(key, 0))
        param, values = results[k]
        c = ''
        for i, item in enumerate(values):
            if x <= item[0]:
                c = item[1]
                res += '%s[%s]: <b>%s</b>\n' % (param, x, c)
                break

        _results[k] = (x, c)

    return res.strip()

def answer(bot, message, command, data=None, logger=None, question=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    storage = kw.get('storage')
    name = kw.get('name')

    if question == _QCOUNT:
        text = get_result(storage, name, lang)
        bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)

    if question < _QCOUNT:
        send_inline_rows_keyboard(bot, message, _ANSWERS[question][lang], get_question(question, lang))

    elif 'query_id' in kw:
        _test_name = test_name()

        dbs.drop_before(_test_name, **kw)
        dbs.save_params(_test_name, _RESULTS, _results, **kw)
        """
        for p in sorted([x for x in _RESULTS[lang].keys()]):
            if p in _results:
                param = _PARAMS[lang][p][0]
                value, s1 = _results[p]
                storage.set(name, '%s.%s%s' % (_TEST_NAME, RCODES['RP'], p), value)
                storage.set(name, '%s.%s%s' % (_TEST_NAME, RCODES['TP'], p), '<i>%s</i>. %s:%s' % (param, s1, value), with_encode=True)
                storage.set(name, '%s.%s%s' % (_TEST_NAME, RCODES['NP'], p), param, with_encode=True)
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

    out = []
    r = {}
    for k in sorted(params.keys()):
        x = check(data, key, params[k])
        if with_print:
            print(x)
        r[k] = x

        rp = '%s.RP%s' % (key, k)
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
