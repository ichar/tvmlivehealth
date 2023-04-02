# -*- coding: utf-8 -*-

import re
import sys
import os

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, errorlog, print_to, print_exception,
     default_unicode, default_encoding, 
     UTC_FULL_TIMESTAMP
     )

from . import admin
from .. import db

from ..settings import *
from ..utils import getId, reprSortedDict, getDate, getToday

from app.models import (
     Pagination, Dialog, Question, Answer,
     drop_table, show_tables, print_tables, show_all, 
     answers, get_answers
     )


@admin.route('/', methods = ['GET','POST'])
@admin.route('/index', methods = ['GET','POST'])
#@login_required
#@admin_required
def index():
    return 'admin'
