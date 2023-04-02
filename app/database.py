# -*- coding: utf-8 -*-

import os
import sys
import re
from urllib.parse import urlparse

import redis

from config import (
     CONNECTION, 
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, 
     errorlog, print_to, print_exception,
     is_webhook,
    )

from flask import (
    Response, render_template, url_for, redirect, request, make_response, 
    jsonify, flash, stream_with_context, g, current_app
)

from app import db, babel
from app.settings import (
    DEFAULT_LANGUAGE, NO_DATA, 
    g, current_app, product_version, tests_count, default_unicode, default_encoding,
    init_response, get_navigation, vsc
    )

from app.utils import getToday, getDate, isIterable

default_connection = CONNECTION.get('semaphore')

database_config = {}

#from flask_babel import gettext


@babel.localeselector
def get_locale(lang=None):
    try:
        print(current_app.config['BABEL_TRANSLATION_DIRECTORIES'])
    except:
        print('Babel Error!')
    return lang or DEFAULT_LANGUAGE
    

class RedisStorage:
    """
        Redis Storage Class
    """
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "http://localhost:6379")
        self.is_local = True if 'localhost' in self.redis_url else False

        self.rserver = None

    def _init_state(self, command, query_id, chat_person):
        self._command = command
        self._query_id = query_id
        self._chat_person = chat_person

        if self.is_local:
            url = urlparse(self.redis_url)
            self.rserver = redis.Redis(host=url.hostname, port=url.port, username=url.username, password=url.password, 
                ssl=False, ssl_cert_reqs=None)
        else:
            self.rserver = redis.from_url(self.redis_url)

        self._question = None
        self._answer = None

        #if is_webhook:
        #    g.rserver = self.rserver

        if IsDebug:
            print('>>> RedisStorage:%s' % self.rserver.client())

    @property
    def command(self):
        return self._command
    @property
    def query_id(self):
        return self._query_id
    @property
    def chat_person(self):
        return self._chat_person
    @property
    def question(self):
        return self._question
    @property
    def answer(self):
        return self._answer

    def is_exists(self, name):
        return self.rserver and self.rserver.exists(name) and True or False

    def getall(self, name):
        return self.rserver.hgetall(name)

    def get(self, name, key, with_decode=None):
        x = None
        try:
            x = self.rserver.hget(name, key)
        except:
            pass
        if x and with_decode:
            return x.decode()
        return x

    def get_items(self, name, keys, with_decode=None):
        items = {}
        if IsDebug:
            print('profile keys:%s' % sorted(list(keys)))
        for key in keys:
            items[key] = self.get(name, key, with_decode=with_decode)
            if IsDeepDebug:
                pass #print(key, items[key])
        return items

    def get_test_results(self, name, lang, tests=None, **kw):
        data = self.getall(name)
        keys = [x for x in data.keys()]

        if not tests:
            tests = TESTNAMES[lang].keys()

        items = {}

        for test in tests:
            for key in keys:
                k = key.decode()
                if k.startswith(test):
                    x = k.split('.')
                    if len(x) > 1 and x[0] == test and x[1].startswith('T'):
                        value = data[key].decode()
                        if not value:
                            continue
                        if test not in items:
                            items[test] = []
                        items[test].append(value)

            if IsTrace and IsDebug and test in items:
                print('chat: %s test %s results items:\n%s' % (name, test, '\n'.join(items[test])))
                print('-'*10)

        return items

    def get_chat_names(self):
        return self.rserver.client() and [x.decode() for x in self.rserver.keys('*')] or []

    def get_data(self, name, key, with_decode=None):
        data = self.getall(name)

        res = {}

        is_parse = '.' not in key
        is_all = '*' in key

        k0 = None
        k1 = re.sub(r'\*', '', key)
        k2 = re.sub(r'\.', '', k1)

        for k in [x.decode() for x in data.keys()]:
            k0, p = k2, '.' in k and '.' or ''
            if is_parse:
                x = k.split('.')[0]
                if x.startswith(k1):
                    k0, p = x, '.'
                else:
                    continue
            if k.startswith(k1) and k0 not in res:
                r = [(x.decode(), with_decode and data[x].decode() or data[x]) 
                        for x in data.keys() if is_all and (k0+p) in x.decode() or k0 == x.decode()]
                if len(r) > 1:
                    res[k0] = dict(r)
                else:
                    res[k0] = r and r[0][1] or ''

        return res

    def set(self, name, key, value, mapping=None, with_encode=None):
        self.rserver.hset(name, key, with_encode and value.encode() or value, mapping=mapping)

    def delete(self, name, command=None, clear=None):
        try:
            if self.is_exists(name):
                if clear:
                    self.rserver.delete(name)
                    return
                data = self.getall(name)
                keys = sorted([x.decode() for x in data.keys()])
                if command:
                    for key in keys:
                        if key.startswith(command):
                            self.rserver.hdel(name, key)
                else:
                    for key in keys:
                        if key not in ('query_id', 'chat_person', 'date', 'nic', 'lang', 'usage'):
                            self.rserver.hdel(name, key)
        except:
            pass

    def clear(self, name):
        #
        #   Fully delete chat with given name
        #
        self.delete(name, clear=True)

    def dump(self, name):
        if IsDeepDebug:
            sline = '\n%s\n' % ('='*10)
            print('dump redis for name %s:' % name)
            print(sline)
            data = self.getall(name)
            if data:
                for key in sorted(list(data.keys())):
                    print('%s:%s' % (key.decode(), data[key].decode()))
            else:
                print(NO_DATA)
            print(sline)

    def register(self, name, data, with_usage=None):
        if not data:
            return
    
        mapping = { 'command' : self.command, 'query_id' : self.query_id, 'chat_person' : self.chat_person, 'date' : getDate(getToday()) }

        is_error = False

        try:
            question, answer = data.split(':')
        except:
            question, answer = 0, -1
            is_error = True

        if with_usage:
            usage = self.get(name, 'usage')
            mapping['usage'] = usage and int(usage)+1 or 1

        if not is_error:
            self.set(name, question, answer, mapping=mapping)

        self._question = question
        self._answer = answer

    def get_person_chat_id(self, chat_person):
        if not self.rserver.client():
            return None

        for name in [x.decode() for x in self.rserver.keys('*')]:
            x = name.split(':')
            chat_id = x[1] and x[1].isdigit() and int(x[1])
            if chat_id:
                if self.get(name, 'chat_person').decode() == chat_person:
                    return chat_id

        return None
    
    def set_lang(self, name, value):
        self.set(name, 'lang', value)

    def get_lang(self, name):
        x = self.get(name, 'lang')
        lang = x and x.decode() or DEFAULT_LANGUAGE
        return lang #get_locale(lang)


def activate_storage(**kw):
    command = kw.get('command', '')
    query_id = kw.get('query_id', None)
    person = kw.get('person', None)

    storage = RedisStorage()
    storage._init_state(command, query_id, person)

    return storage

def deactivate_storage(storage):
    del storage


def getEngine(connection):
    engine = None
    if not (connection and isinstance(connection, dict)):
        pass
    elif 'dialect' in connection and 'driver' in connection and 'database' in connection and 'options' in connection:
        engine = create_engine('%(dialect)s+%(driver)s://%(user)s:%(password)s@%(host)s/%(database)s?%(options)s' % connection)
    elif 'dialect' in connection and 'driver' in connection and 'database' in connection:
        engine = create_engine('%(dialect)s+%(driver)s://%(host)s/%(database)s' % connection)
    elif 'driver' in connection and 'database' in connection:
        if 'user' not in connection:
            connection['user'] = 'user'
        if 'password' not in connection:
            connection['password'] = connection['user']
        engine = create_engine('postgresql+%(driver)s://%(user)s:%(password)s@%(host)s/%(database)s' % connection)
    else:
        pass
    return engine

def getEncoding(encoding):
    return encoding or sys.version_info > (3, 5) and default_encoding or default_iso

def logQuery(sql, with_log, caller):
    if IsDeepDebug:
        print('>>> %s: %s' % (caller, out(sql)))

    if with_log:
        print_to(None, '>>> %s: %s' % (caller, sql), encoding=default_encoding)


class DatabaseEngine():
    
    def __init__(self, name=None, user=None, connection=None):
        self.name = name or 'default'
        self.connection = connection or default_connection or {}

        if IsTrace:
            print_to(None, '--> DatabaseEngine.__init__:%s [%s]' % (name, self.connection))

        self.conn = None
        self.engine_error = False

        self.engine = getEngine(self.connection)
        if self.engine:
            self.conn = self.engine.connect()
        else:
            self.engine_error = True
        self.user = user

        if IsTrace:
            print_to(None, '--> DatabaseEngine.__init__:%s connected %s' % (name, self.user and self.user.login))

        self.encoding = getEncoding(self.connection.get('encoding'))

        if IsDeepDebug:
            print('>>> open connection[%s]' % self.name)

        self._count = 0

    def __repr__(self):
        return re.sub(r'[\<\>]', '', str(self.conn)).split(' ')[-1]

    @property
    def database(self):
        return self.connection.get('database')
    @property
    def driver(self):
        return self.engine.driver
    @property
    def is_error(self):
        return self.engine_error
    @property
    def count(self):
        return self._count
    @property
    def with_check_database(self):
        return int(self.connection.get('with_check', 1))

    def getReferenceID(self, name, key, value, tid='TID', **kw):
        id = None
        
        if isinstance(value, str):
            where = "%s='%s'" % (key, value)
        else:
            where = '%s=%s' % (key, value)
            
        cursor = self.runQuery(name, top=1, columns=(tid,), where=where, distinct=True, **kw)
        if cursor:
            id = cursor[0][0]
        
        return id

    def _get_params(self, config_, **kw):
        return 'exec_params' in kw and (config_['params'] % kw['exec_params']) or kw.get('params') or ''

    def runProcedure(self, name, args=None, no_cursor=False, with_log=False, **kw):
        """
            Executes database stored procedure.
            Could be returned cursor.

            Parameter `with_error` can check error message/severity from SQL Server (raiserror).
        """
        if self.engine_error:
            return

        config = kw.get('config') or database_config[name]

        if args:
            sql = 'EXEC %(sql)s %(args)s' % { 
                'sql'    : config['exec'],
                'args'   : config['args'],
            }
        else:
            sql = 'EXEC %(sql)s %(params)s' % { 
                'sql'    : config['exec'],
                'params' : config['params'] % kw,
            }

        with_error = kw.get('with_error') and True or False

        return self.run(sql, args=args, no_cursor=no_cursor, with_error=with_error, with_log=with_log, caller='runProcedure')

    def runQuery(self, name, top=None, offset=None, columns=None, where=None, order=None, distinct=False, as_dict=False, with_log=False, **kw):
        """
            Executes as database query so a stored procedure.
            Returns cursor.
        """
        if self.engine_error:
            return []

        config = kw.get('config') or database_config[name]

        query_columns = columns or config.get('columns')

        if 'clients' in config and self.user is not None:
            profile_clients = self.user.get_profile_clients(True)
            if profile_clients:
                clients = '%s in (%s)' % (
                    config['clients'],
                    ','.join([str(x) for x in profile_clients])
                )

                if where:
                    where = '%s and %s' % (where, clients)
                else:
                    where = clients

        _view = kw.get('view') or 'view'

        if _view in config and config[_view]:
            is_union = isIterable(where)
            union = is_union and where or [(offset, top, where)]

            items, params, sql = [], {}, ''

            params = { 
                'distinct' : distinct and 'DISTINCT' or '',
                'columns'  : query_columns and ','.join(query_columns) or '*',
                'view'     : config[_view],
            }

            for o, t, w in union:
                params.update({
                    'where' : (w and 'WHERE %s' % w) or '',
                    'top'   : (t and 'TOP %s' % str(t)) or '',
                })

                if o is not None:
                    params.update({
                        'order'  : (order and 'ORDER BY %s' % order) or '',
                        'offset' : o or 0,
                    })

                    sql = ('SELECT %(distinct)s %(top)s %(columns)s FROM (select *, ROW_NUMBER() over (%(order)s) as rows ' + 
                          'from %(view)s %(where)s) x where rows > %(offset)s') % params
                else:
                    sql = 'SELECT %(distinct)s %(top)s %(columns)s FROM %(view)s %(where)s' % params

                if kw.get('as_subquery') and 'sql' in kw:
                    sql = kw['sql'] % sql

                if kw.get('with_updlock'):
                    x = sql.split('WHERE')
                    sql = '%s WITH (UPDLOCK)%s' % (x[0].strip(), len(x) > 1 and (' WHERE %s' % x[1].strip()) or '')

                items.append(sql)

            if is_union:
                sql = ' UNION '.join(items)
            else:
                sql = items[0]

            sql += (order and ' ORDER BY %s' % order) or ''

        else:
            params = { 
                'sql'    : config['exec'],
                'params' : self._get_params(config, **kw),
            }
            sql = 'EXEC %(sql)s %(params)s' % params

        rows = []

        encode_columns = kw.get('encode_columns') or []
        worder_columns = kw.get('worder_columns') or []

        mapping = kw.get('mapping')

        cursor = self.execute(sql, no_traceback=kw.get('no_traceback'), with_log=with_log, caller='runQuery')

        if cursor is not None and not cursor.closed:
            if IsDeepDebug:
                print('--> in_transaction:%s' % cursor.connection.in_transaction())

            for n, line in enumerate(cursor):
                if as_dict and query_columns:
                    row = dict(zip(query_columns, line))
                else:
                    row = [x for x in line]

                line = None
                del line

                for column in encode_columns:
                    if column in row or isinstance(column, int):
                        if not row[column]:
                            row[column] = ''
                        elif self.encoding != default_encoding:
                            row[column] = row[column].encode(self.encoding).decode(default_encoding)
                for column in worder_columns:
                    row[column] = splitter(row[column], length=None, comma=':')
                if mapping:
                    row = dict([(key, row.get(name)) for key, name in mapping])

                rows.append(row)

            cursor.close()

        return rows

    def runCommand(self, sql, **kw):
        """
            Run sql-command with transaction.
            Could be returned cursor.
        """
        if self.engine_error:
            return

        if IsDeepDebug:
            print('>>> runCommand: %s' % sql)

        if kw.get('no_cursor') is None:
            no_cursor = True
        else:
            no_cursor = kw['no_cursor'] and True or False

        with_error = kw.get('with_error') and True or False
        with_log = kw.get('with_log') and True or False

        return self.run(sql, no_cursor=no_cursor, with_error=with_error, with_log=with_log, caller='runCommand')

    def run(self, sql, args=None, no_cursor=False, with_error=False, with_log=False, caller=None):
        if self.conn is None or self.conn.closed:
            if with_error:
                return [], ''
            else:
                return None

        rows = []
        error_msg = ''

        self._count += 1

        if self.with_check_database: # and self.database not in sql
            sql = re.sub(r'\s\[dbo\]', ' [%s].[dbo]' % self.database, sql)

        logQuery(sql, with_log, caller or 'run')

        with self.conn.begin() as trans:
            try:
                if args:
                    cursor = self.conn.execute(sql, args)
                else:
                    cursor = self.conn.execute(sql)

                if IsDeepDebug:
                    print('--> in_transaction:%s' % cursor.connection.in_transaction())

                if not no_cursor and cursor:
                    rows = [row for row in cursor if row]

                trans.commit()

            except Exception as err:
                try:
                    trans.rollback()
                except:
                    pass

                if not no_cursor:
                    rows = []

                if err is not None and hasattr(err, 'orig') and (
                        isinstance(err.orig, psycopg2.OperationalError) or 
                        isinstance(err.orig, psycopg2.IntegrityError) or
                        isinstance(err.orig, psycopg2.ProgrammingError)
                    ):
                    msg = len(err.orig.args) > 1 and err.orig.args[1] or ''
                    error_msg = msg and msg.decode().split('\n')[0] or 'unexpected error'
                    
                    if 'DB-Lib' in error_msg:
                        error_msg = re.sub(r'(,\s)', r':', re.sub(r'(DB-Lib)', r':\1', error_msg))
                else:
                    error_msg = 'database error'

                self.engine_error = True

                print_to(None, 'NO SQL QUERY: %s ERROR: %s, engine:%s' % (sql, error_msg, repr(self)))

                if IsPrintExceptions:
                    print_exception()

        if with_error:
            return rows, error_msg

        return rows

    def execute(self, sql, no_traceback=None, raise_error=None, with_log=False, caller=None):
        self._count += 1

        if self.with_check_database: # and self.database not in sql
            sql = re.sub(r'\s\[dbo\]', ' [%s].[dbo]' % self.database, sql)

        logQuery(sql, with_log, caller or 'execute')

        try:
            return self.engine.execute(sql)
        except:
            if not no_traceback:
                print_to(None, 'NO SQL EXEC: %s, engine:%s' % (sql, repr(self)))
                print_exception()

            self.engine_error = True

            if raise_error:
                raise

            return None

    def dispose(self, force=None):
        if not force:
            return

        self.engine.dispose()

        if IsTrace:
            print_to(None, '>>> dispose')

    def close(self):
        if self.conn is None or self.conn.closed:
            return

        self.conn.close()

        if IsTrace:
            print_to(None, '>>> close connection[%s]' % self.name)

        self.dispose(True)


class Base:

    def __init__(self, requested_object, *args, **kwargs):
        if IsTrace:
            print_to(None, 'Base.init')

        super().__init__(*args, **kwargs)

        self.requested_object = requested_object

        self._id = None

    @property
    def id(self):
        return self._id


class Connection(Base):
    
    def __init__(self, connection, *args, **kwargs):
        if IsTrace:
            print_to(None, 'Connection.init')

        super().__init__(*args, **kwargs)

        self._connection = connection

        self.conn = None
        self.cursor = None
        self.is_error = False

        self.encoding = getEncoding(self.connection.get('encoding'))

    def open(self, autocommit=None):
        if IsTrace:
            print_to(None, 'Connection.open, autocommit:%s, connection:%s' % (autocommit, self._connection))

        server = self._connection['server']
        user = self._connection['user']
        password = self._connection['password']
        database = self._connection['database']
        timeout = int(self._connection.get('timeout') or 0)
        login_timeout = int(self._connection.get('login_timeout') or 60)

        self.conn, self.is_error = psycopg2.connect(server, user, password, database, timeout, login_timeout), False

        if IsTrace:
            print_to(None, 'Connection.open, done')

        if autocommit is None:
            return

        self.conn.autocommit(autocommit and True or False)
        self.cursor = self.conn.cursor()

    def begin(self):
        pass

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.is_error is not None:
            if self.is_error:
                self.rollback()
            else:
                self.commit()

        self.conn.close()

    def connect(self, sql, params, **kw):
        """
            Parameterized query.

            Arguments:
                sql     -- String, SQL query with params scheme
                params  -- List, query parameters

            Keyword arguments:
                with_commit -- Boolean, use transaction or not
                with_result -- Boolean, should be returned recodset
                callproc    -- Boolean, run stored procedure

            Returns:
                cursor      -- List, cursor or query results recordset
        """
        if IsTrace:
            print_to(None, 'Connection.connect, sql:%s' % sql)

        if kw.get('check_error') and self.is_error:
            return None

        _with_commit = kw.get('with_commit')
        _with_result = kw.get('with_result')
        _callproc = kw.get('callproc')

        _is_error = False

        if not hasattr(self, 'conn') or self.conn is None:
            self.open()

        conn = self.conn

        # ------------------
        # Check `autocommit`
        # ------------------

        if _with_commit is not None:
            if _with_commit: # and conn.autocommit_state:
                conn.autocommit(False)
            else:
                conn.autocommit(True)

        cursor = self.cursor

        if IsDeepDebug:
            print_to(None, 'with_commit: %s' % _with_commit)
            print_to(None, 'sql: %s' % sql)

        res = None

        try:
            p = params is not None and tuple(params) or ()

            if IsTrace:
                print_to(None, 'connect:execute, sql:%s, params:%s' % (sql, len(p)))

            if _callproc:
                res = cursor.callproc(sql, p)
            else:
                cursor.execute(sql, p)

            if IsTrace:
                print_to(None, 'connect:done')
        except:
            if IsPrintExceptions:
                print_exception()

            print_to(None, 'SQL:[%s]' % sql)

            if IsDeepDebug:
                print_to(None, 'params:%s' % repr(params))
        
            _is_error = True

        # ------------------------------------------------
        # Manage transaction if `autocommit` is turned off
        # ------------------------------------------------

        if _with_commit is not None:
            if _with_commit and not conn.autocommit_state:
                if _is_error:
                    conn.rollback()
                else:
                    conn.commit()

        self.conn, self.is_error = conn, _is_error

        if _with_result:
            if _callproc:
                return res
            else:
                res = list(cursor.fetchall())
                return self.encode_columns(res, kw.get('encode_columns'))

        return cursor

    @staticmethod
    def encode_columns(cursor, columns):
        if not (cursor and columns):
            return cursor
        rows = []
        for n, line in enumerate(cursor):
            row = [x for x in line]
            if self.encoding != default_encoding:
                for column in columns:
                    if column in row or isinstance(column, int):
                        row[column] = row[column] and row[column].encode(self.encoding).decode(default_encoding) or ''
            rows.append(row)        
        return rows

    @staticmethod
    def get_value(x):
        return x and len(x) > 0 and x[0][0] or None


class DBEngine:
    
    def __init__(self, connection=None):
        self._connection = connection
        
        self.engine = getEngine(self._connection)
        self.conn = self.engine.connect()
        self.engine_error = False

        self.with_transaction = True
        self.transaction = None

        self.encoding = getEncoding(self._connection.get('encoding'))

    @property
    def driver(self):
        return self.engine.driver
    @property
    def database(self):
        return self._connection.get('database')
    @property
    def is_error(self):
        return self.engine_error
    @property
    def is_pyodbc(self):
        return self.driver == 'pyodbc'

    def begin(self):
        self.transaction = self.conn.begin()

    def commit(self):
        self.transaction.commit()

    def rollback(self):
        self.transaction.rollback()

    def open(self, with_transaction=None):
        self.with_transaction = with_transaction

        if self.with_transaction:
            self.begin()

    def close(self):
        if self.engine_error:
            self.rollback()
        else:
            self.commit()

        self.conn.close()
        del self.conn

    def run(self, sp, params, callproc=None, no_cursor=None, no_traceback=None, raise_error=None):
        cursor = None

        sql, with_params = sp, False

        if callproc:
            sql = 'EXEC %s' % (sql % params)
        else:
            if self.is_pyodbc:
                if params:
                    sql = re.sub(r'%[d|s]', '?', sql)
            elif self.database not in sp:
                sql = re.sub(r'\[dbo\]', '[%s].[dbo]' % self.database, sql)
            with_params = params and True or False

        if IsDebug:
            print_to(None, 'SQL:[%s]%s' % (sql, with_params and ', params:%s' % repr(params) or ''))

        try:
            if with_params:
                cursor = self.conn.execute(sql, params)
            else:
                cursor = self.conn.execute(sql)

        except Exception as err:
            self.engine_error = True

            if IsPrintExceptions and not no_traceback:
                print_exception()

            if raise_error:
                raise

        if no_cursor:
            return

        rows = []

        if cursor is not None:
            for n, line in enumerate(cursor):
                row = []
                for x in line:
                    if x and isinstance(x, str) and self.encoding != default_encoding:
                        row.append(x.encode(self.encoding).decode(default_encoding))
                    else:
                        row.append(x)
                rows.append(row)

        return rows

