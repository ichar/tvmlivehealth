#!venv/bin/python

import os
from app import create_app, db
from flask import url_for
from flask_script import Server, Manager, Shell
from config import setup_console, isIterable #, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO

from sqlalchemy import func, asc, desc, and_, or_

from app.models import (
     Pagination, Dialog, Question, Answer,
     drop_table, show_tables, print_tables, show_all, 
     answers, get_answers
     )

app = create_app(os.getenv('APP_CONFIG') or 'default')

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def routes(link=None):
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    sorted(links)
    if link:
        links = [x for x in links if link in x[1]]
    return links

def print_routes(link=None):
    for url in routes(link=link):
        print(url)

def print_metadata():
    for n, x in enumerate(db.metadata.tables.keys()):
        print('>>> %s. %s' % (n+1, x))

manager = Manager(app)

def make_shell_context():
    return dict(
            app=app, db=db, 
            Pagination=Pagination, func=func, asc=asc, desc=desc, and_=and_, or_=or_, 
            Dialog=Dialog, Question=Question, Answer=Answer, 
            drop_table=drop_table, show_tables=show_tables, print_tables=print_tables, show_all=show_all, 
            answers=answers, get_answers=get_answers, 
            isIterable=isIterable, routes=routes, print_routes=print_routes, url_for=url_for, 
            print_metadata=print_metadata, #print_mapper=print_mapper, print_table_columns=print_table_columns,
        )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("start", Server(host='0.0.0.0', port=5000))

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    pass

@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    #from werkzeug.contrib.profiler import ProfilerMiddleware
    #app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    #app.run()
    pass

@manager.command
def deploy():
    """Run deployment tasks."""
    #from flask.ext.migrate import upgrade
    # migrate database to latest revision
    #upgrade()
    pass

@manager.command
def start():
    """Run server."""
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    #from app.bot.views import run as bot_activate
    #bot_activate()
    manager.run()
