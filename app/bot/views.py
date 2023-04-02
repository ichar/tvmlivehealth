# -*- coding: utf-8 -*-

import sys
import os
import datetime
import time
import pytz
import logging
import threading

from config import *
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time
from app.dialogs.scenario import *

from . import appbot
from .. import db

from ..settings import *

P_TIMEZONE = pytz.timezone(TIMEZONE)
TIMEZONE_COMMON_NAME = TIMEZONE_COMMON_NAME

basedir = ''

# --------------
# Enable logging
# --------------

today = getDate(getToday())

log = normpath(os.path.join(LOG_PATH, '%s_%s.log' % (today, LOG_NAME)))

def setup_logging():
    if not IsLogTrace:
        return
    logging.basicConfig(
        filename=not is_webhook and log or None,
        format='%(asctime)s: %(name)s-%(levelname)s\t%(message)s', 
        level=logging.DEBUG, 
        datefmt=UTC_FULL_TIMESTAMP,
    )

logger = logging.getLogger(__name__)

# ------------
# Create a bot
# ------------

import telebot

bot = telebot.TeleBot(TOKEN)

# ======== #
# HANDLERS #
# ======== #

def info(command, force=None, is_error=False, is_warning=False, is_ok=False, data=None):
    if IsDisableOutput or not IsLogTrace:
        return
    line = '>>> %s%s' % (command, data and '\n%s' % data or '')
    if IsDeepDebug:
        print(line)
    else:
        if is_error:
            logging.error(line)
        elif is_warning:
            logging.warning(line)
        elif IsTrace or force:
            logging.info(line)
    if IsFlushOutput:
        sys.stdout.flush()

## ------ ##

class BaseService(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, daemon=daemon)

    def stop(self):
        pass

    def should_be_stop(self):
        pass

    def is_finished(self):
        pass

    def run(self):
        main()

"""
@appbot.before_app_request
def before_request():
    redis_url = os.environ.get("REDIS_URL", "http://localhost:6379")
    is_local = True if 'localhost' in redis_url else False
    url = urlparse(redis_url)

    #rserver = redis.Redis(host='localhost', port='6379')
    g.rserver = redis.Redis(host=url.hostname, port=url.port, username=url.username, password=url.password, 
        ssl=not is_local and True or False, ssl_cert_reqs=None)

    if IsDeepDebug:
        print(g.rserver.client())
"""

## ------ ##

@bot.message_handler(commands=['start'])
def start(message):
    command = message.text[1:]
    info(command, data=message.json)
    make_start(bot, message, info)

@bot.message_handler(commands=['description'])
def description(message):
    command = message.text[1:]
    info(command, data=message.json)
    make_description(bot, message, info)

@bot.message_handler(commands=['help'])
def help(message):
    command = message.text[1:]
    info(command, data=message.json)
    make_help(bot, message, info)

@bot.message_handler(commands=['lang','locale'])
def langs(message):
    command = message.text[1:]
    info(command, data=message.text)
    make_langs(bot, message)

@bot.message_handler(commands=['ru','uk']) #, 'en'
def set_lang(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info)

@bot.message_handler(commands=['version'])
def version(message):
    command = message.text[1:]
    make_version(bot, message)

@bot.message_handler(commands=['commands'])
def commands(message):
    command = message.text[1:]
    info(command, data=message.json)
    make_commands(bot, message, info)

@bot.message_handler(commands=['tests'])
def tests(message):
    command = message.text[1:]
    info(command, data=message.json)
    make_tests(bot, message, info)

@bot.message_handler(func=lambda message: message and message.text.upper().startswith('/T') and True)
def test_handler(message):
    command = message.text[1:].upper()
    info(command, data=message.json)
    make_answer(bot, message, command, logger=info, query_id=0) # query.id XXX just for last question

@bot.message_handler(commands=['begin'])
def begin(message):
    command = message.text[1:]
    info(command, data=message.json)
    make_begin(bot, message, info)

@bot.message_handler(commands=['end'])
def end(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.message_handler(commands=['clear'])
def clear(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.message_handler(commands=['emergency'])
def emergency(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.message_handler(commands=['diagnosis'])
def diagnosis(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.message_handler(func=lambda message: message and message.text.upper().startswith('/D') and True)
def result_handler(message):
    #
    #   Вывод результатов теста <N>: /dN
    #
    command = message.text[1:].upper()
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.message_handler(commands=['profile'])
def profile(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.message_handler(commands=['menu'])
def menu(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)

@bot.callback_query_handler(func=lambda call: True) 
def button(query):
    #
    #    Ответ на вопрос нажатием кнопки с вариантом ответа
    #
    command = 'button'
    if IsShowAnswerResult:
        bot.send_message(query.message.chat.id, query.data)
    if query.data.startswith('/T'):
        command = query.data.upper()[1:]
        make_answer(bot, query.message, command, data=query.data, logger=info, query_id=query.id)
    elif query.data == 'accept:0':
        make_answer(bot, query.message, 'end', logger=info, query_id=query.id, with_clear=True)
    else:
        make_answer(bot, query.message, command, data=query.data, logger=info, query_id=query.id)

@bot.message_handler(func=lambda message: message and message.text.lower().startswith('/q') and True)
def question(message):
    #
    #   Переход к вопросу <N> клинической беседы: /qN, index = N
    #       index=1 - старт опроса
    #
    s = message.text[1:]
    x = s[1:]
    command, index = 'q', x.isdigit() and int(x) or 1
    make_answer(bot, message, command, logger=info, index=index)

@bot.message_handler(func=lambda message: message and message.text.lower().startswith('/send') and True)
def send(message):
    make_message(bot, message.text)

@bot.message_handler(func=lambda message: True)
def text(message):
    #
    #   Ввод произвольного текста... имя пациента
    #
    command = 'text'

    #print('... message:', message)
    #for key in message.json:
    #    print('>>>', key, message.json[key])
    #print('... text:', message.text)

    if not make_answer(bot, message, command, logger=info):
        return 

    time.sleep(3)

    make_answer(bot, message, '...', logger=info, index=1)

@bot.message_handler(commands=['stop'])
def stop(message):
    #threading.Thread(target=shutdown).start()
    #shutdown()
    make_stop(bot, message, info)

def shutdown():
    #updater.stop()
    #updater.is_idle = False
    pass

@appbot.route('/{}'.format(TOKEN), methods=['POST'])
def getMessage():
    if is_webhook:
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@appbot.route('/getwebhookinfo', methods=['GET', 'POST'])
def get_webhook_info():
    return is_webhook and bot.get_webhook_info().url or 'none'

@appbot.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = is_webhook and bot.set_webhook(url='{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok: [%s]" % str(s)
    else:
        return "webhook setup failed"

@appbot.route('/removewebhook', methods=['GET', 'POST'])
def remove_webhook():
    bot.remove_webhook()

@appbot.route('/')
def index():
    run()
    return '*** Bot has been started ***'

"""
@appbot.route('/debug')
def debug():
    return make_debug()

@appbot.route('/log')
def chat_log():
    return make_log()
"""
@appbot.route('/message/<info>', methods=['GET', 'POST'])
def message(info):
    make_message(bot, info or '/send:mkaro:Hi! How are you?')
    return '*** Message sent ***'

## ------ ##

def main():
    """
        Start the bot (getUpdates)
    """
    while True:
        if IsDeepDebug:
            print('... bot polling started')
        try:
            bot.polling(none_stop=True) #, interval=0, timeout=0
        except KeyboardInterrupt:
            break
        except:
            logger.error('Impossible to start...')
            print_exception()

        time.sleep(10)

def setup():
    if IsDeepDebug:
        print(basedir)
    sys.path.append(basedir)

def run():
    setup_logging()

    if IsDebug:
        print('... bot activate')

    try:
        if not is_webhook:
            if not getattr(bot, 'bot_started', False):
                process = BaseService()
                process.start()

                setattr(bot, 'bot_started', True)
    except:
        raise

    if IsDebug:
        print('... bot run')
