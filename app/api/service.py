# -*- coding: utf-8 -*-
"""
from flask import jsonify, request, g, url_for, current_app, make_response

from config import (
     CONNECTION,
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsNoEmail, LocalDebug, 
     basedir, errorlog, print_to, print_exception,
     default_unicode, default_encoding
     )
"""
from app.settings import *

from . import api
from .decorators import service_required
from .errors import forbidden

from ..database import activate_storage, deactivate_storage
from ..dialogs.scenario import selftest as dialogs_selftest

##  ===================
##  Service API Package
##  ===================

def _activate():
    return activate_storage()

def _deactivate(storage):
    deactivate_storage(storage)

def _request_data():
    data = None
    try:
        data = request.json
    except:
        try:
            data = request.data.decode(default_unicode)
        except:
            if IsPrintExceptions:
                print_exception()
    return data


@api.route('/ping/', methods=['GET'])
def ping():
    """
        Ping for service activated. Returns 'It works!' if OK.
    """
    if IsTrace:
        print_to(errorlog, '--> service.ping')

    try:
        storage = _activate()
        response = make_response(
            'It works!',
        )
        del response.headers['WWW-Authenticate']
        return response
    finally:
        _deactivate(storage)

@api.route('/chat/names', methods=['GET','POST'])
#@service_required
def get_chat_names():
    """
    Get chat names.
    
    Returns:
        'names': list of names
    """
    storage = _activate()

    location = url_for('api.get_chat_names')

    names = storage.get_chat_names()

    kw = {
        'accepted' : 'get_chat_names',
        'names' : names,
    }

    if IsTrace:
        print_to(errorlog, '--> service.get_chat_names')

    _deactivate(storage)

    return jsonify(kw), 201, {'Location': location}

@api.route('/data/<name>/<key>', methods=['GET','POST'])
#@service_required
def get_data(name, key):
    """
    Get storage data by the given chat name and data item key.
    
    Arguments:
        name: str, chat name
        key: str, data item key

    Name is a chat ID without prefix 'chat.' like this: 
        798066483 for 'chat.798066483'

    Key can include symbols '.' and '*' than means for example:
        T1.* - all params for test T1: T1.1, T1.2, T1.3...
        T1.2* - items started with '2' for test T1: T1.21, T1.22...
        T1.11 - just given item 

    Keyword arguments:
        with_decode: bool, 1 - data with binary decoding (.decode()), 0 - raw data

    Returns:
        'data': dict of items values (json)
    """
    storage = _activate()

    chat_name = 'chat:%s' % name
    location = url_for('api.get_data', name=name, key=key)

    data = storage.get_data(chat_name, key, with_decode=True)

    kw = {
        'accepted' : 'get_data',
        'name' : name,
        'key' : key,
        'data' : data,
    }

    if IsTrace:
        print_to(errorlog, '--> service.get_data.key[%s] for %s' % (key, chat_name))

    _deactivate(storage)

    return jsonify(kw), 201, {'Location': location}

@api.route('/selftest/<name>', methods=['GET','POST'])
def selftest(name):
    """
        Self Test. Returns 'OK' or 'Error/Exception'.
    """
    chat_name = 'chat:%s' % name
    location = url_for('api.selftest', name=name)

    tests = dialogs_selftest(chat_name, with_print=0)

    kw = {
        'accepted' : 'get_data',
        'name' : name,
        'tests' : tests,
    }

    if IsTrace:
        print_to(errorlog, '--> service.selftest for %s' % chat_name)

    return jsonify(kw), 201, {'Location': location}

@api.route('/status/<int:id>', methods=['GET'])
@service_required
def get_order_status(id):
    """
    response = make_response(
        jsonify(kw),
        201,
    )
    response.headers["Location"] = location
    response.headers['WWW-Authenticate'] = None
    return response
    """
    pass
