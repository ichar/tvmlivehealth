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

# ---------------------
# Шкала депрессии Цунга
# ---------------------

_TEST_NAME = 'T6'
_QCOUNT = 20

_QUESTIONS = {
    'ru': (
"""
1. Я чувствую подавленность.
""",
"""
2. Утром я чувствую себя лучше всего.
""",
"""
3. У меня бывают периоды плача или близости к слезам.
""",
"""
4. У меня плохой ночной сон.
""",
"""
5. Аппетит у меня не хуже обычного.
""",
"""
6. Мне приятно смотреть на привлекательных женщин, разговаривать с ними, находиться рядом.
""",
"""
7. Я замечаю, что теряю вес.
""",
"""
8. Меня беспокоят запоры.
""",
"""
9. Моё сердце бьётся быстрее, чем обычно.
""",
"""
10. Я устаю без всяких причин.
""",
"""
11. Я мыслю так же ясно, как всегда.
""",
"""
12. Мне легко делать то, что я умею.
""",
"""
13. Чувствую беспокойство и не могу усидеть на месте.
""",
"""
14. У меня есть надежды на будущее.
""",
"""
15. Я более раздражителен, чем обычно.
""",
"""
16. Мне легко принимать решения.
""",
"""
17. Я чувствую, что полезен и необходим.
""",
"""
18. Я живу достаточно полной жизнью.
""",
"""
19. Я чувствую, что другим людям станет лучше, если я умру.
""",
"""
20. Меня до сих пор радует то, что радовало всегда.
""",
), 
    'uk': (
"""
1. Я відчуваю пригніченість.
""",
"""
2. Вранці я найкраще почуваю себе.
""",
"""
3. У мене бувають періоди плачу чи близькості до сліз.
""",
"""
4. У мене поганий нічний сон.
""",
"""
5. Апетит у мене не гірший, ніж зазвичай.
""",
"""
6. Мені приємно дивитися на привабливих жінок, розмовляти з ними, знаходитися поруч.
""",
"""
7. Я помічаю, що втрачаю вагу.
""",
"""
8. Мене непокоять закрепи.
""",
"""
9. Моє серце б’ється швидше, ніж зазвичай.
""",
"""
10. Я втомлююся без жодних причин.
""",
"""
11. Я мислю так само ясно, як і зазвичай.
""",
"""
12. Мені легко робити те, що я вмію.
""",
"""
13. Я відчуваю занепокоєння і не можу всидіти на місці.
""",
"""
14. У мене є надії на майбутнє.
""",
"""
15. Я більш дратівливий, ніж зазвичай.
""",
"""
16. Мені легко ухвалювати рішення.
""",
"""
17. Я відчуваю себе корисним і необхідним.
""",
"""
18. Я живу досить повним життям.
""",
"""
19. Я відчуваю, що іншим людям стане краще, якщо я помру.
""",
"""
20. Мене досі радує те, що радувало завжди.
""",
),
}

_scores_numbers = 'ABCD'

_SCORES = {
    'ru': [
        ['A', 'Никогда или изредка',],
        ['B', 'Иногда',],
        ['C', 'Часто',],
        ['D', 'Почти всегда или постоянно'], 
    ],
    'uk': [
        ['A', 'Ніколи чи зрідка',],
        ['B', 'Іноді',],
        ['C', 'Часто',],
        ['D', 'Майже завжди чи постійно',],
    ],
}

_PARAMS = {
    'ru' : {'1' :'Уровень депрессии Цунга'},
    'uk' : {'1' :'Рівень депресії Цунга'},
}

_RESULTS = (1,2,1,1,2,2,1,1,1,1,2,2,1,2,1,2,2,2,1,2) # mode 1: 1-2-3-4, mode 2: 4-3-2-1

_CONCLUSIONS = {
    'ru' : (
        (49, 'Состояние без депрессии'), 
        (59, 'Лёгкая депрессия ситуативного или невротического генеза'), 
        (69, 'Субдепрессивное состояние или замаскированная депрессия'), 
        (80, 'Тяжёлая депрессия'), 
    ),
    'uk' : (
        (49, 'Стан без депресії'), 
        (59, 'Легка депресія ситуативного чи невротичного генезу'), 
        (69, 'Субдепресивний стан чи замасковану депресію'), 
        (80, 'Важка депресія'), 
    ),
}

_HEADERS = {
    'ru': 
"""
Прочитайте внимательно каждое из приведенных ниже предложений и выберите соответствующий ответ в зависимости от того, как вы себя чувствуете в последнее время. Над вопросами долго не задумывайтесь, поскольку «правильных» или «неправильных» ответов нет.
""",
    'uk': 
"""
Уважно прочитайте кожне з наведених нижче висловлювань і оберіть відповідний варіант відповіді в залежності від того, як ви себе почуваєте останнім часом. Над запитаннями довго не замислюйтесь, оскільки «правильних» чи «неправильних» відповідей немає.
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
            return mode == 1 and 1 or 4
        if s == 'B':
            return mode == 1 and 2 or 3
        if s == 'C':
            return mode == 1 and 3 or 2
        if s == 'D':
            return mode == 1 and 4 or 1
        return 0

    if _is_random_scores:
        random.shuffle(scores)

    answers = []
    buttons = []
    qs = question + 1
    mode = _RESULTS[question]
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

def get_result(storage, name, lang, mode=None):
    global _results

    res = ''
    data = storage.getall(name)
    conclusions = _CONCLUSIONS[lang]

    x = 0

    for n in range(0, _QCOUNT):
        key = ('T6.%s'%(n+1)).encode()
        x += int(data.get(key, 0))
    c = ''
    for i, item in enumerate(conclusions):
        if x <= item[0]:
            c = conclusions[i][1]
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
