#!venv/bin/python

import sys
import os
import datetime
import time
import pytz
import logging
import threading
import telebot

from flask import Flask, request

from config import *
from app import create_app, db, babel
from app.settings import DEFAULT_LANGUAGE, get_request_item
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time
from app.dialogs.scenario import *

P_TIMEZONE = pytz.timezone(TIMEZONE)
TIMEZONE_COMMON_NAME = TIMEZONE_COMMON_NAME

basedir = ''

def setup():
    if IsDebug:
        print(basedir)
    sys.path.append(basedir)

# --------------
# Enable logging
# --------------

today = getDate(getToday())

log = normpath(os.path.join(LOG_PATH, '%s_%s.log' % (today, LOG_NAME)))

def setup_logging():
    if not IsLogTrace:
        return
    logging.basicConfig(
        #filename=not is_webhook and log or None,
        format='%(asctime)s: %(name)s-%(levelname)s\t%(message)s', 
        level=logging.DEBUG, 
        datefmt=UTC_FULL_TIMESTAMP,
    )

logger = logging.getLogger(__name__)

# ------------
# Create a bot
# ------------

bot = telebot.TeleBot(TOKEN)

#app = Flask(__name__)
app = create_app(os.getenv('APP_CONFIG') or 'default')

# ======== #
# HANDLERS #
# ======== #

@babel.localeselector
def get_locale():
    return DEFAULT_LANGUAGE

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

@bot.message_handler(commands=['lang', 'locale'])
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
    make_answer(bot, message, command, logger=info)

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

@bot.message_handler(func=lambda message: message and message.text.startswith('/q') and True)
def question(message):
    s = message.text[1:]
    x = s[1:]
    command, index = 'q', x.isdigit() and int(x) or 1
    make_answer(bot, message, command, logger=info, index=index)

@bot.message_handler(func=lambda message: message and message.text.lower().startswith('/send') and True)
def send(message):
    make_message(bot, message.text)

@bot.message_handler(func=lambda message: True)
def text(message):
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

@app.route('/{}'.format(TOKEN), methods=['POST'])
def getMessage():
    if is_webhook:
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/getwebhookinfo', methods=['GET', 'POST'])
def get_webhook_info():
    #return is_webhook and bot.get_webhook_info().url
    return is_webhook and str(bot.get_webhook_info()) or 'none'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = is_webhook and bot.set_webhook(url='{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok: [%s]" % str(s)
    else:
        return "webhook setup failed"

@app.route('/removewebhook', methods=['GET', 'POST'])
def remove_webhook():
    bot.remove_webhook()
    return 'removed'

@app.route('/')
def index():
    return 'started'
"""
@app.route('/debug')
def debug():
    return make_debug()

@app.route('/log')
def log():
    return make_log()
"""
@app.route('/message/<info>', methods=['GET', 'POST'])
def message(info):
    make_message(bot, info or '/send:mkaro:Hi! How are you?')
    return '*** Message sent ***'

## ------ ##

def main():
    """
        Start the bot (getUpdates)
    """
    while True:
        try:
            bot.polling(none_stop=True) #, interval=0, timeout=0
        except KeyboardInterrupt:
            break
        except:
            logger.error('Impossible to start...')
            print_exception()

        time.sleep(10)


if __name__ == '__main__':
    setup_logging()

    if is_webhook:
        app.run(threaded=True) #host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), debug=True
    else:
        main()
