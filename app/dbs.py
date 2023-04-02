# -*- coding: utf-8 -*-

__all__ = [
    'drop_before', 'save_params', 'save_conclusions', 'save'
    ]

from app.settings import DEFAULT_LANGUAGE, RCODES, isIterable

lang = ''
storage = None
name =''

def before(f):
    def wrapper(*args, **kw):
        global lang, storage, name
        lang = kw.get('lang') or DEFAULT_LANGUAGE
        storage = kw.get('storage')
        name = kw.get('name')
        return f(*args, **kw)
    return wrapper


@before
def drop_before(test_name, **kw):
    """
        Удалить ранее сформированные результаты теста
    """
    for x in '=NRT':
        storage.delete(name, command='%s.%s' % (test_name, x))

    for x in ('T13', 'test'):
        storage.clear(x)

@before
def save_params(test_name, params, results, **kw):
    """
        Сохранить результаты параметров теста

            test_name   - str, name of test: T1,T2...

            params      - dict, declaration of params: _PARAMS or _CONCLUSIONS or _RESULTS

            results     - dict, lists of params results: (value, diagnosis)

            split_param - flag, we have not params list as _PARAMS, so need to split just param key _RESULTS
                          i.e. name of param is inside _RESULTS instance:
                          T2
            is_not_tuple- flag, name of param is not in a tuple
                          T11
            default_param - str, name of default param for tests with one param defined:
                          T3 T4 T12
    """
    split_param = kw.get('split_param') or 0
    default_param = kw.get('default_param') or None
    is_not_tuple = kw.get('is_not_tuple') or 0

    for p in sorted([x for x in params[lang].keys()]):
        if p in results:
            value, s1 = results[p]
            if default_param:
                param = default_param
            elif split_param:
                n, param = p.split('.')
                p = n
            elif is_not_tuple:
                param = params[lang][p]
            else:
                param = params[lang][p][0]
            storage.set(name, '%s.%s%s' % (test_name, RCODES['RP'], p), value)
            storage.set(name, '%s.%s%s' % (test_name, RCODES['TP'], p), '<i>%s</i>. %s:%s' % (param, s1, value), with_encode=True)
            storage.set(name, '%s.%s%s' % (test_name, RCODES['NP'], p), param, with_encode=True)

@before
def save_conclusions(test_name, conclusions, results, **kw):
    """
        Сохранить диагноз теста

            conclusions - dict, declaration of params with conclusions: _CONCLUSIONS

            results     - dict, lists of params results: (value, diagnosis)
    """
    for p in sorted(list(conclusions[lang].keys())):
        if p in results:
            param = conclusions[lang][p][0]
            value, s1 = results[p]
            storage.set(name, '%s.%s%s' % (test_name, RCODES['RC'], p), value)
            storage.set(name, '%s.%s%s' % (test_name, RCODES['TC'], p), '<i>%s</i>. %s:%s' % (param, s1, value), with_encode=True)

@before
def save(test_name, param, values, **kw):
    if isIterable(values):
        value, s1 = values
        storage.set(name, '%s.%s' % (test_name, param), '%s:%s' % (s1, value), with_encode=True)
    else:
        storage.set(name, '%s.%s' % (test_name, param), values, with_encode=True)

