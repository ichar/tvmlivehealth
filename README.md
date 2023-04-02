Install Python3 (3.8 or later) first of all.

Setup Heroku on your local host:

```bash
$ sudo snap install --classic heroku
$ heroku --version
```

Clone the project from GitHub:
```bash
$ git clone https://github.com/ichar/tvmlivehealthbot
```
Clone from Heroku:
```
heroku git:clone -a tvmlivehealth
```

Create a project inside a new virtual environment (venv):
```bash
$ cd tvmlivehealthbot
$ sudo virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Get changes from Heroku:
```
$ cd ../tvmlivehealth
$ git push heroku master
```

Then open Telegram and chat `@BotFather` to create a new bot. Get a new bot keys:
[TelegramBotName]
[telegram-id] (check the `_bot` postfix)
[telegram-token]

and add its to the same items in 'config.py' file.

Create a new Heroku application (App) and deploy it to there:
```
$ heroku login
$ git init
$ git add .
$ git commit -m "init"
$ git push heroku master
```

Rename Heroku App:
```
$ git remote rm heroku
$ heroku git:remote -a <newname>
```

Open App in Dashboard or link:
------------------------------------------
https://[heroku-app].heroku.com/setwebhook
------------------------------------------

Check there from Telegram (should be answer 'started'):
--------------------------------------------
https://api.telegram.org/bot[telegram-token]
--------------------------------------------

Run your Bot in Telegram (press /start).

To update repository:
```
$ get pull heroku master
```
Make file changes.
```
$ git status
$ git add .
$ git commit -am "make it better"
$ git push heroku master
```
