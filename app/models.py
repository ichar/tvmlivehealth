# -*- coding: utf-8 -*-

import os
import sys
import re
from math import ceil
from datetime import datetime
from time import time
from collections import namedtuple
from operator import itemgetter
from copy import deepcopy
import requests, json, jwt
from requests.exceptions import ConnectionError, ConnectTimeout

from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin, current_user
from flask_babel import lazy_gettext
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import app_release, db, login_manager

from sqlalchemy import create_engine, MetaData, Sequence
from sqlalchemy import func, asc, desc, and_, or_, text
from sqlalchemy.orm import column_property
from sqlalchemy.event import listen

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsNoEmail, errorlog, 
     default_unicode, default_encoding, default_print_encoding, 
     print_to, print_exception, isIterable, 
     UTC_FULL_TIMESTAMP, LOCAL_EASY_DATESTAMP, UTC_EASY_TIMESTAMP
     )

from .settings import DEFAULT_PER_PAGE, DEFAULT_HTML_SPLITTER, DEFAULT_USER_AVATAR, DEFAULT_UNDEFINED, gettext, g
#from .mails import send_simple_mail
from .utils import getDate, getDateOnly, getToday, getTimedelta, out, cid, cdate, clean, image_base64, make_config

roles_ids = ['USER', 'ADMIN', 'EDITOR', 'OPERATOR', 'VISITOR', 'X1', 'X2', 'X3', 'SERVICE', 'ROOT']
roles_names = tuple([lazy_gettext(x) for x in roles_ids])
ROLES = namedtuple('ROLES', ' '.join(roles_ids))
valid_user_roles = [n for n, x in enumerate(roles_ids)]
roles = ROLES._make(zip(valid_user_roles, roles_names))

app_roles_ids = ['EMPLOYEE', 'MANAGER', 'CHIEF', 'ADMIN', 'CTO', 'CAO', 'HEADOFFICE', 'ASSISTANT', 'CEO', 'HOLDER', 'AUDITOR']
app_roles_names = tuple([lazy_gettext(x) for x in app_roles_ids])
APP_ROLES = namedtuple('ROLES', ' '.join(app_roles_ids))
valid_user_app_roles = [n for n, x in enumerate(app_roles_ids)]
app_roles = APP_ROLES._make(zip(valid_user_app_roles, app_roles_names))

answers_ids = ['TEXT', 'INLINE', 'INLINE_ROWS', 'MULTILINE', 'X1', 'X2', 'X3']
answers_names = tuple([lazy_gettext(x) for x in answers_ids])
ANSWERS = namedtuple('ANSWERS', ' '.join(answers_ids))
valid_question_answers = [n for n, x in enumerate(answers_ids)]
answers = ANSWERS._make(zip(valid_question_answers, answers_names))


USER_DEFAULT_PHOTO = '/static/img/person-default.jpg'

password_mask = '*'*10

admin_config = {
    'users' : {
        'columns' : ('id', 'login', 'name', 'post', 'email', 'role', 'confirmed', 'enabled',),
        'headers' : {
            'id'          : (lazy_gettext('ID'),               '',),
            'login'       : (lazy_gettext('Login'),            '',),
            'name'        : (lazy_gettext('Full person name'), '',),
            'post'        : (lazy_gettext('Post'),             '',),
            'email'       : (lazy_gettext('Email'),            '',),
            'role'        : (lazy_gettext('Role'),             '',),
            'confirmed'   : (lazy_gettext('Confirmed'),        '',),
            'enabled'     : (lazy_gettext('Enabled'),          '',),
        },
        'fields' : ({
            'login'       : lazy_gettext('Login'),
            'password'    : lazy_gettext('Password'),
            'family_name' : lazy_gettext('Family name'),
            'first_name'  : lazy_gettext('First name'),
            'last_name'   : lazy_gettext('Last name'),
            'nick'        : lazy_gettext('Nick'),
            'post'        : lazy_gettext('Post'),
            'email'       : lazy_gettext('Email'),
            'role'        : lazy_gettext('Role'),
            'confirmed'   : lazy_gettext('Confirmed'),
            'enabled'     : lazy_gettext('Enabled'),
        }),
    },
}

UserRecord = namedtuple('UserRecord', admin_config['users']['columns'] + ('selected',))


def _commit(check_session=True, force=None):
    is_error = 0
    errors = []

    if check_session:
        if not (db.session.new or db.session.dirty or db.session.deleted):
            if IsTrace:
                print_to(None, '>>> No data to commit: new[%s], dirty[%s], deleted[%s]' % ( \
                    len(db.session.new),
                    len(db.session.dirty),
                    len(db.session.deleted))
                )
            if not force:
                errors.append('No data to commit')
                is_error = 1

    if not is_error or force:
        try:
            db.session.commit()
            if IsTrace:
                print_to(None, '>>> Commit OK')
        except Exception as error:
            db.session.rollback()
            is_error = 2
            errors.append(error)
            if IsTrace:
                print_to(None, '>>> Commit Error: %s' % error)
            print_to(None, '!!! System Commit Error: %s' % str(error))
            if IsPrintExceptions:
                print_exception()

    return is_error, errors

def _apply_limit(offset, top):
    def wrapped(query):
        if offset:
            query = query.limit(offset)
        if top:
            query = query.offset(top)
        return query
    return wrapped

def _get_offset(query, **kw):
    offset = 0
    top = 0
    page_options = kw.get('page_options')
    if page_options:
        offset = int(page_options.get('offset') or 0)
        top = int(page_options.get('top') or 0)
    return offset, top

def _set_offset(query, **kw):
    page_options = kw.get('page_options')
    offset, top = _get_offset(query, **kw)
    if offset is not None:
        query = query.offset(offset)
    if top is not None:
        query = query.limit(top)

    #listen(query, 'before_compile', _apply_limit(offset, top), retval=True)

    return query

##  ------------
##  Help Classes
##  ------------

class Pagination(object):
    #
    # Simple Pagination
    #
    def __init__(self, page, per_page, total, value, sql):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.value = value
        self.sql = sql

    @property
    def query(self):
        return self.sql

    @property
    def items(self):
        return self.value

    @property
    def current_page(self):
        return self.page

    @property
    def pages(self):
        return int(ceil(self.total / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def get_page_params(self):
        return (self.current_page, self.pages, self.per_page, self.has_prev, self.has_next, self.total,)

    def iter_pages(self, left_edge=1, left_current=0, right_current=3, right_edge=1):
        last = 0
        out = []
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                num > self.page - left_current - 1 and num < self.page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    out.append(-1)
                out.append(num)
                last = num
        return out

##  ==========================
##  Objects Class Construction
##  ==========================

class ExtClassMethods(object):
    """
        Abstract class methods
    """
    def __init__(self):
        self._is_error = False

    @property
    def is_error(self):
        return self._is_error
    @is_error.setter
    def is_error(self, value):
        self._is_error = value or 0

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def print_all(cls):
        for x in cls.all():
            print(x)

class ClientProfile(db.Model, ExtClassMethods):
    """
        Пользовательский профайл (Клиенты-Банки, Клиентский сегмент)
    """
    __tablename__ = 'client_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ClientID = db.Column(db.Integer, index=True, nullable=False, default=0)

    user = db.relationship('User', backref=db.backref('clients', lazy='joined'), uselist=True) #, lazy='dynamic'

    def __init__(self, user, client_id):
        self.user_id = user.id
        self.ClientID = client_id

    def __repr__(self):
        return '<ClientProfile %s:[%s-%s]>' % (cid(self), str(self.user_id), str(self.ClientID))


class Photo(db.Model, ExtClassMethods):
    """
        Пользовательский профайл (Фото)
    """
    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    data = db.Column(db.Text, nullable=True, default=None)

    user = db.relationship('User', backref=db.backref('photos', lazy='joined'), uselist=True) #, lazy='dynamic'

    def __init__(self, user, data):
        self.user_id = user.id
        self.data = data

    def __repr__(self):
        return '<Photo %s:[%s-%s]>' % (cid(self), str(self.user_id), self.data and 'Y' or 'N')


class Settings(db.Model, ExtClassMethods):
    """
        Пользовательский профайл (настройки интерфейса)
    """
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    pagesize = db.Column(db.Integer, nullable=True)

    sidebar_collapse = db.Column(db.Boolean, default=True)
    use_extra_infopanel = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('settings', lazy='joined'), uselist=True) #, lazy='dynamic'

    def __init__(self, user):
        self.user_id = user.id

    def __repr__(self):
        return '<Settings %s:[%s-%s]>' % (cid(self), str(self.user_id), self.user_id and 'Y' or 'N')


class Privileges(db.Model, ExtClassMethods):
    """
        Привилегии пользователей
    """
    __tablename__ = 'privileges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    menu = db.Column(db.String(50), default='')
    base_url = db.Column(db.String(120), index=True)
    role = db.Column(db.SmallInteger, default=app_roles.EMPLOYEE[0])

    is_manager = db.Column(db.Boolean, default=False)
    is_author = db.Column(db.Boolean, default=False)
    is_consultant = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('privileges', lazy='joined'), uselist=True) #, lazy='dynamic'

    def __init__(self, user):
        self.user_id = user.id

    def __repr__(self):
        return '<Privileges %s: [%s] [%s] %s>' % (
            cid(self), 
            self.app_role_name,
            '',
            self.user[0].login
            )

    @property
    def app_role_name(self):
        return self.role in valid_user_app_roles and app_roles_names[self.role] or gettext('undefined')


class Dialog(db.Model, ExtClassMethods):
    """
        Bot Dialog instances
    """
    __tablename__ = 'dialogs'

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(20), index=True)
    name = db.Column(db.Unicode(250), default='')

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __repr__(self):
        return '<Dialog %s:[%s-%s]>' % (cid(self), str(self.code), self.name)

    @classmethod
    def get_by_code(cls, code):
        return cls.query.filter_by(code=code).first()


class Question(db.Model, ExtClassMethods):
    """
        Bot Dialog Question instances
    """
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    dialog_id = db.Column(db.Integer, db.ForeignKey('dialogs.id'))

    number = db.Column(db.Integer, nullable=True)
    code = db.Column(db.String(20), index=True)
    answer_type = db.Column(db.SmallInteger, default=answers.INLINE[0])

    text_ru = db.Column(db.Unicode(250), default='')
    text_ua = db.Column(db.Unicode(250), default='')
    text_en = db.Column(db.Unicode(250), default='')

    dialog = db.relationship('Dialog', backref=db.backref('questions', lazy='joined'), uselist=True)

    def __init__(self, dialog):
        self.dialog_id = dialog.id

    def __repr__(self):
        return '<Questions %s: %s # %s answer_type:%s code:%s>' % (
            cid(self), 
            str(self.dialog_id), 
            str(self.number), 
            str(self.answer_type), 
            str(self.code), 
            )


class Answer(db.Model, ExtClassMethods):
    """
        Bot Dialog Answer instances
    """
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    number = db.Column(db.Integer, nullable=True)
    code = db.Column(db.String(20), index=True)

    text_ru = db.Column(db.Unicode(50), default='')
    text_ua = db.Column(db.Unicode(50), default='')
    text_en = db.Column(db.Unicode(50), default='')

    question = db.relationship('Question', backref=db.backref('answers', lazy='joined'), uselist=True)

    def __init__(self, dialog):
        self.dialog_id = dialog.id

    def __repr__(self):
        return '<Answers %s: %s # %s code:%s>' % (
            cid(self), 
            str(self.question_id), 
            str(self.number), 
            str(self.code), 
            )


class User(UserMixin, db.Model, ExtClassMethods):
    """
        Пользователи
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, index=True)

    login = db.Column(db.Unicode(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nick = db.Column(db.Unicode(40), default='')
    first_name = db.Column(db.Unicode(50), default='')
    family_name = db.Column(db.Unicode(50), default='')
    last_name = db.Column(db.Unicode(50), default='')
    role = db.Column(db.SmallInteger, default=roles.USER[0])
    email = db.Column(db.String(120), index=True)

    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    last_visit = db.Column(db.DateTime)
    last_pwd_changed = db.Column(db.DateTime)

    confirmed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean(), default=True)

    post = db.Column(db.String(100), default='')

    def __init__(self, login, name=None, role=None, email=None, **kw):
        super(User, self).__init__(**kw)
        self.login = login
        self.set_name(name, **kw)
        self.role = role in valid_user_roles and role or roles.USER[0]
        self.post = kw.get('post') or ''
        self.email = not email and '' or email
        self.reg_date = datetime.now()

    def __repr__(self):
        return '<User %s:%s %s>' % (cid(self), str(self.login), self.full_name())

    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_login(login):
        return User.query.filter_by(login=login).first()

    def has_privileges(self):
        return self.privileges is not None and len(self.privileges) > 0 and True or False

    @property
    def app_menu(self):
        return self.has_privileges() and self.privileges[0].menu or 'default'
    @property
    def base_url(self):
        return self.has_privileges() and self.privileges[0].base_url or ''
    @property
    def role_name(self):
        return self.role in valid_user_roles and roles_names[self.role] or gettext('undefined')
    
    #   --------------
    #   Authentication
    #   --------------
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change_password(self, password):
        self.password = password
        self.confirmed = True
        self.last_pwd_changed = datetime.now()
        db.session.add(self)

    def unconfirmed(self):
        self.confirmed = False
        db.session.add(self)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def get_reset_password_token(self, expires_in=600):
        payload = {'reset_password': self.id, 'exp': time() + expires_in}
        key = current_app.config['SECRET_KEY']
        x = jwt.encode(payload, key, algorithm='HS256')
        return type(x) == str and x or x.decode(default_unicode)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            id = data['reset_password']
        except:
            if IsPrintExceptions:
                print_exception()
            return
        return User.query.get(id)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode(default_unicode)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        _commit(True)

    #   -------------------------
    #   Basic roles & permissions
    #   -------------------------

    def can(self, role):
        return self.role is not None and roles[self.role] == role

    def is_superuser(self, private=False):
        return self.role in (roles.ROOT[0],)

    def is_administrator(self, private=False):
        if private:
            return self.role == roles.ADMIN[0]
        return self.role in (roles.ADMIN[0], roles.ROOT[0])

    def is_manager(self, private=False):
        if private:
            return self.role == roles.EDITOR[0]
        return self.role in (roles.EDITOR[0], roles.ADMIN[0], roles.ROOT[0])

    def is_operator(self, private=False):
        if private:
            return self.role == roles.OPERATOR[0]
        return self.role in (roles.OPERATOR[0], roles.ADMIN[0], roles.ROOT[0])

    def is_owner(self):
        return self.login == 'admin'

    def is_any(self):
        return self.enabled and True or False

    def is_anybody(self):
        return self.is_any()

    def is_nobody(self):
        return False

    @property
    def is_user(self):
        return self.role in (roles.USER[0], roles.OPERATOR[0], roles.EDITOR[0], roles.ADMIN[0], roles.ROOT[0])

    @property
    def is_emailed(self):
        return self.enabled and self.email and (
            not g.system_config.EXCLUDE_EMAILS or self.email not in g.system_config.EXCLUDE_EMAILS) and True or False

    def get_profile_clients(self, by_list=None):
        items = []
        for ob in self.clients:
            items.append(str(ob.ClientID))
        if by_list:
            return items
        return DEFAULT_HTML_SPLITTER.join(items)

    def set_profile_clients(self, data):
        is_changed = False
        for ob in self.clients:
            db.session.delete(ob)
            is_changed = True
        for id in data.split(':'):
            if not id:
                continue
            try:
                item = ClientProfile(self, int(id))
                db.session.add(item)
                is_changed = True
            except ValueError:
                pass
        if is_changed:
            _commit(True)

    def get_post(self):
        return re.sub(r'"', '&quot;', self.post)

    def get_user_post(self):
        return '%s, %s' % ('', re.sub(r'"', '&quot;', self.post))

    def get_avatar(self):
        return self.photos and DEFAULT_USER_AVATAR[0] % (self.photos[0].data, self.get_user_post(), self.login) or ''

    def get_small_avatar(self, **kw):
        photo = self.photos and self.photos[0].data or None
        if not photo:
            return ''
        tag, default_image, x, image_type, size = DEFAULT_USER_AVATAR
        try:
            photo = image_base64('', image_type, kw.get('size') or size, photo)
        except:
            return ''
        if kw.get('clean'):
            return photo
        return tag % (photo, self.get_user_post(), self.login)

    def get_photo(self):
        return self.photos and self.photos[0].data or USER_DEFAULT_PHOTO

    def set_photo(self, data):
        is_changed = False
        for ob in self.photos:
            db.session.delete(ob)
            is_changed = True
        try:
            item = Photo(self, data)
            db.session.add(item)
            is_changed = True
        except ValueError:
            pass
        if is_changed:
            _commit(True)

    def delete_photo(self):
        is_changed = False
        for ob in self.photos:
            db.session.delete(ob)
            is_changed = True
        if is_changed:
            _commit(True)
        return self.get_photo()

    def get_pagesize(self, model):
        return None

    def set_pagesize(self, model, value):
        is_changed = False

    def has_settings(self):
        return self.settings and len(self.settings) > 0

    @property
    def sidebar_collapse(self):
        if self.has_settings():
            return self.settings[0].sidebar_collapse or False
        else:
            return False

    @sidebar_collapse.setter
    def sidebar_collapse(self, collapse):
        is_changed = False
        if not self.has_settings():
            settings = self.add_settings()
            is_changed = True
        else:
            settings = self.settings[0]
        if settings.sidebar_collapse != collapse:
            settings.sidebar_collapse = collapse and True or False
            is_changed = True
        if is_changed:
            _commit(True)

    @property
    def use_extra_infopanel(self):
        if self.has_settings():
            return self.has_settings() and self.settings[0].use_extra_infopanel or False
        else:
            return False

    @staticmethod
    def get_role(role):
        for x in roles:
            if x[0] == role:
                return x
        return None

    @staticmethod
    def get_roles(ids=None):
        try:
            return [getattr(roles, x) for x in vars(roles) if not ids or x in ids]
        except:
            return [getattr(roles, x) for x in roles._fields if not ids or x in ids]

    def get_settings(self):
        return []

    def add_settings(self):
        settings = Settings(self)
        db.session.add(settings)
        return settings

    def set_settings(self, values):
        if not values:
            return
        check_session = True
        is_changed = False
        is_add = False
        try:
            if not self.settings:
                settings = Settings(self)
                is_add = True
            else:
                settings = self.settings[0]
            settings.sidebar_collapse = values[5] == '1' and True or False
            settings.use_extra_infopanel = values[6] == '1' and True or False
            if is_add:
                db.session.add(settings)
            else:
                self.settings[0] = settings
                check_session = False
            is_changed = True
        except ValueError:
            pass
        if is_changed:
            _commit(check_session)

    def get_privileges(self):
        return [
                self.app_role, 
                self.app_menu, 
                self.base_url, 
                self.app_is_manager, 
                self.app_is_author,
                self.app_is_consultant,
            ]

    def set_privileges(self, values):
        if not values:
            return
        check_session = True
        is_changed = False
        is_add = False
        try:
            privileges.role = int(values[1])
            privileges.menu = values[2]
            privileges.base_url = values[3]
            privileges.is_manager = values[4] == '1' and True or False
            privileges.is_author = values[5] == '1' and True or False
            privileges.is_consultant = values[6] == '1' and True or False
            if is_add:
                db.session.add(privileges)
            else:
                self.privileges[0] = privileges
                check_session = False
            is_changed = True
        except ValueError:
            pass
        if is_changed:
            _commit(check_session)

    def full_name(self):
        return ('%s %s %s' % (self.family_name, self.first_name, self.last_name)).strip()

    def short_name(self, is_back=None):
        if self.family_name and self.first_name and self.last_name:
            f = self.family_name
            n = self.first_name and '%s.' % self.first_name[0] or ''
            o = self.last_name and '%s.' % self.last_name[0] or ''
            return (is_back and 
                '%s%s %s' % (n, o, f) or 
                '%s %s%s' % (f, n, o)
                ).strip()
        return self.full_name()

    def set_name(self, name=None, **kw):
        if name and isIterable(name):
            self.first_name = name[0] or ''
            self.last_name = len(name) > 1 and name[1] or ''
            self.family_name = len(name) > 2 and name[2] or ''
        self.nick = kw.get('nick') or ''

    def get_data(self, mode=None, **kw):
        if not mode or mode == 'view':
            data = { 
                'id'          : self.id,
                'login'       : self.login,
                'name'        : self.full_name(),
                'post'        : self.post,
                'email'       : self.email,
                'role'        : User.get_role(self.role)[1],
                'confirmed'   : self.confirmed and 'Да' or 'Нет',
                'enabled'     : self.enabled and 'Да' or 'Нет',
                'selected'    : kw.get('id') == self.id and 'selected' or '',
            }
        elif mode == 'register':
            data = { 
                'id'          : self.id,
                'login'       : self.login,
                'password'    : self.password_hash and password_mask or '',
                'family_name' : self.family_name,
                'first_name'  : self.first_name,
                'last_name'   : self.last_name,
                'post'        : self.post,
                'email'       : self.email,
                'role'        : self.role,
                'confirmed'   : self.confirmed,
                'enabled'     : self.enabled,
            }
        else:
            data = {}
        
        return data

    #   -------------------------------
    #   Application roles & permissions
    #   -------------------------------

    @property
    def app_is_manager(self):
        # Роль: Менеджер
        return self.has_privileges() and self.privileges[0].is_manager or False
    @property
    def app_is_consultant(self):
        # Роль: Консультант
        return self.has_privileges() and self.privileges[0].is_consultant or False
    @property
    def app_is_author(self):
        # Роль: Автор
        return self.has_privileges() and self.privileges[0].is_author or False
    @property
    def app_role(self):
        return self.has_privileges() and self.privileges[0].role or 0
    @property
    def app_role_name(self):
        role = self.app_role
        return role in valid_user_app_roles and app_roles_names[role] or ''


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self, private=False):
        return False

    @property
    def is_emailed(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

## ============================================================ ##

def drop_table(cls):
    cls.__table__.drop(db.engine)

def show_tables():
    return local_reflect_meta().tables.keys()

def print_tables():
    for x in db.get_tables_for_bind():
        print(x)

def show_all():
    return local_reflect_meta().sorted_tables

def get_answers():
    return [x for x in list(answers) if not x[1].startswith('X')]

## ==================================================== ##

def load_system_config(user=None):
    g.system_config = make_config('system_config.attrs')
    """
    if not user:
        user = current_user

    if user is not None:
        login = not user.is_anonymous and user.is_authenticated and user.login or ''
    """

def send_email(subject, html, user, addr_to, addr_cc=None, addr_from=None):
    pass
