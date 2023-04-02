# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsWithGroup, IsWithExtra, 
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, NO_RESULTS, NO_KEY, RCODES
from app.dialogs.start import help
from app.handlers import *

from app import dbs

# Ответ "Не знаю"
_with_extra = IsWithExtra

# --------------------------------
# Тест Реана на мотивацию к успеху
# --------------------------------

_TEST_NAME = 'T12'
_QCOUNT = 20

_QUESTIONS = {
    'ru': (
"""
1. Включаясь в работу, как правило, оптимистично надеюсь на успех
""",
"""
2. В деятельности активен
""",
"""
3. Склонен к проявлению инициативности
""",
"""
4. При выполнении ответственных задач стараюсь по возможности найти причины отказа от них
""",
"""
5. Часто выбираю крайности: либо заниженные, лёгкие задачи, либо нереалистично большие трудности
""",
"""
6. При встрече с препятствиями, как правило, не отступаю, а ищу способы их преодоления
""",
"""
7. При чередовании успехов и неудач склонен к переоценке своих успехов
""",
"""
8. Продуктивность деятельности в основном зависит от моей собственной целеустремлённости, а не от внешнего контроля
""",
"""
9. При выполнении достаточно трудных задач в условиях ограничения времени результативность деятельности ухудшается
""",
"""
10. Склонен проявлять настойчивость в достижении цели
""",
"""
11. Склонен планировать своё будущее на достаточно отдалённую перспективу
""",
"""
12. Если рискую, то скорее с умом, а не бесшабашно
""",
"""
13. Не очень настойчив в достижении цели, особенно если отсутствует внешний контроль
""",
"""
14. Предпочитаю ставить перед собой средние по трудности или слегка завышенные, но достижимые цели, чем нереально высокие
""",
"""
15. В случае неудачи при выполнении какого-либо задания его привлекательность, как правило, снижается
""",
"""
16. При чередовании успехов и неудач склонен к переоценке своих неудач
""",
"""
17. Предпочитаю планировать своё будущее лишь на ближайшее время
""",
"""
18. При работе в условиях ограничения времени результативность деятельности улучшается, даже если задание достаточно трудное
""",
"""
19. В случае неудачи при выполнении чего-либо от поставленной цели, как правило, не отказываюсь
""",
"""
20. Если задачу выбрал себе сам, то в случае неудачи её притягательность ещё более возрастает
""",
), 
    'uk': (
"""
1. Приступаючи до роботи, як правило, оптимістично сподіваюсь на успіх
""",
"""
2. У діяльності активний
""",
"""
3. Схильний до прояву ініціативи
""",
"""
4. При виконанні відповідальних задач намагаюся по можливості знайти причини відмовитися від них
""",
"""
5. Часто обираю крайнощі: або занижені, легкі задачі, або нереалістично великі труднощі
""",
"""
6. При зустрічі з перешкодами, як правило, не відступаю, а шукаю способи для їх подолання
""",
"""
7. При почерговій зміні успіхів та невдач схильний до переоцінки своїх успіхів
""",
"""
8. Продуктивність діяльності в основному залежить від моєї власної цілеспрямованості, а не від зовнішнього контролю
""",
"""
9. При виконанні досить важких задач в умовах обмеженого часу результативність діяльності погіршується
""",
"""
10. Схильний проявляти наполегливість у досягненні мети
""",
"""
11. Схильний планувати своє майбутнє на досить віддалену перспективу
""",
"""
12. Якщо ризикую, то швидше з розумом, а не бездумно
""",
"""
13. Не дуже наполегливий у досягненні мети, особливо якщо відсутній зовнішній контроль
""",
"""
14. Віддаю перевагу ставити перед собою середні за важкістю або трохи завищені, але досяжні цілі, аніж нереально високі
""",
"""
15. У випадку невдачі при виконанні будь-якого завдання його привабливість, як правило, знижується
""",
"""
16. При чергуванні успіхів і невдач схильний до переоцінки своїх невдач
""",
"""
17. Віддаю перевагу плануванню свого майбутнього лише на найближчий час
""",
"""
18. При роботі в умовах обмеженого часу результативність діяльності покращується, навіть якщо завдання досить важке
""",
"""
19. У випадку невдачі при виконанні будь-чого від поставленої мети, як правило, не відмовляюсь
""",
"""
20. Якщо задачу вибрав собі сам, то у випадку невдачі її привабливість ще більш зростає
""",
),
}

_ANSWERS = {
    'ru': [['Да', '%s.%s:1'], ['Нет', '%s.%s:-1']],
    'uk': [['Так', '%s.%s:1'], ['Ні', '%s.%s:-1']],
}

_no_ext_questions = ()

_EXT_ANSWERS = {
    'ru': [['Не знаю', '%s.%s:0']],
    'uk': [['Не знаю', '%s.%s:0']],
}

_PARAMS = {
    'ru' : {'1' :'Мотивация на успех'},
    'uk' : {'1' :'Мотивацію на успіх'},
}

_RESULTS = {
    'ru': {
        '1' : ([1, 2, 3, 6, 8, 10, 11, 12, 14, 16, 18, 19, 20], [4, 5, 7, 9, 13, 15, 17]),
    },
    'uk': {
        '1' : ([1, 2, 3, 6, 8, 10, 11, 12, 14, 16, 18, 19, 20], [4, 5, 7, 9, 13, 15, 17]),
    },
}

_CONCLUSIONS = {
    'ru' : (
        ( 7, 'Диагностирована мотивация на неудачу (боязнь неудачи)'), 
        (10, 'Мотивационный полюс ярко не выражен, есть тенденция к мотивации на неудачу'), 
        (13, 'Мотивационный полюс ярко не выражен, есть тенденция к мотивации на успех'), 
        (20, 'Диагностирована мотивация на успех (надежда на успех)'), 
    ),
    'uk' : (
        ( 7, 'Діагностовано мотивацію на невдачу (страх невдачі)'), 
        (10, 'Мотиваційний полюс яскраво не виражений, є тенденція до мотивації на невдачу'), 
        (13, 'Мотиваційний полюс яскраво невиражений, є тенденція до мотивації на успіх'), 
        (20, 'Діагностовано мотивацію на успіх (надія на успіх)'), 
    ),
}

_HEADERS = {
    'ru': 
"""
Отвечая на следующие вопросы, необходимо выбрать ответ «да» или «нет». Если вы затрудняетесь с ответом, то вспомните, что «да» объединяет как явное «да», так и «скорее да, чем нет». То же самое относится и к ответу «нет»: он объединяет и явное «нет», и «скорее нет, чем да».
""",
    'uk': 
"""
Відповідаючи на наступні запитання, необхідно обрати відповідь «так» чи «ні». Якщо вам важко відповісти, то згадайте, що «так» поєднує і явне «так», і «швидше так, ніж ні». Те саме стосується відповіді «ні»: вона поєднує і явне «ні», і «швидше ні, ніж так».
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

def get_result(storage, name, lang, mode=None):
    global _results

    res = ''
    data = storage.getall(name)
    results = _RESULTS[lang]
    conclusions = _CONCLUSIONS[lang]

    keys = sorted([x for x in results.keys() if x[0].isdigit()])

    cs, px = {}, {}

    for p in keys:
        # p: ключ параметра: LF или 1...8
        x = 0
        for i in range(0, 2):
            # i=0: группа "Да"
            # i=1: группа "Нет"
            # score: баллы за ответ на вопрос
            score = 1
            for n in results[p][i]:
                # n: номер вопроса
                key = ('%s.%s' % (_TEST_NAME, n)).encode()
                v = int(data.get(key, 0))
                x += i == 0 and v > 0 and score or i == 1 and v < 0 and score or 0

        if mode == 1:
            _results[p] = [x, NO_KEY]

            px[p] = x
            c = ''
            for i, item in enumerate(conclusions):
                # item: граничное значение параметра
                if x <= item[0]:
                    # c: итоговая оценка по параметру
                    c = item[1]
                    _results[p][1] = c
                    break
            # res: текст результата
            res += '%s: [%s] <b>%s</b>\n' % (p, x, c)
        else:
            if x > 5:
                return True

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

    if is_run:
        answers = deepcopy(_ANSWERS[lang])
        if _with_extra:
            if question not in _no_ext_questions:
                answers += deepcopy(_EXT_ANSWERS[lang])
        for i, a in enumerate(answers):
            answers[i][1] = answers[i][1] % (_TEST_NAME, question+1)
        send_inline_keyboard(bot, message, answers, get_question(question, lang))

    elif 'query_id' in kw:
        _test_name = test_name()

        dbs.drop_before(_test_name, **kw)
        dbs.save_params(_test_name, _PARAMS, _results, default_param=_PARAMS[lang]['1'], **kw)
        """
        for p in sorted([x for x in _RESULTS[lang].keys()]):
            if p in _results:
                value, param = _results[p]
                storage.set(name, '%s.R%s' % (_TEST_NAME, p), value)
                storage.set(name, '%s.T%s' % (_TEST_NAME, p), '%s:%s' % (param, value), with_encode=True)
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

def lines(text):
    for line in text.split('\n'):
        if not line:
            continue
        x = line.split('.')
        n, s = int(x[0].strip()), x[1].strip()
        print('"""\n%s. %s\n""",' % (n, s))

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
                s += i == 0 and v > 0 and 1 or i == 1 and v < 0 and 1 or 0
    return s

def selftest(data, lang, with_print=None):
    key = _TEST_NAME
    results = _RESULTS[lang]

    out = []
    r = 0
    for k in sorted(results.keys()):
        x = check(data, key, results[k])
        if with_print:
            print(x)
        r += x

        rp = '%s.R%s' % (key, k)
        if rp in data[key]:
            x = int(data[key].get(rp, '0'))
            if r == x:
                out.append('OK')
            else:
                out.append('Error %s [%s:%s]' % (rp, r, x))
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
