from flask import Flask, render_template, g, request
from datetime import datetime
from flask_babel import Babel, format_datetime
from consthandler import *
import misc.pa4 as pa4

app = Flask(__name__)
babel = Babel(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['de', 'fr', 'en'])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone
    
@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=format_datetime(datetime.now(), "EEEE, MMMM dd, yyyy 'at' h:m.")
    )

@app.route("/pa4", methods=['GET', 'POST'])
def funky():
    if request.method == 'GET':
        display = []
        
        with pa4.capture_stdout() as capture:
            pa4.main(pa4.GETTY,30)
        
        for i in capture.result.split("\n\n"):
            para = []
            for x in i.split("\n"):
                para.append(x)
            display.append(para)
        
        return render_template(
            "yo.html",
            display=display,
            sitetitle="Yo",
            )
    if request.method == "POST":        
        display = []
        
        with pa4.capture_stdout() as capture:
            pa4.main(request.form["textmisc"].replace("\r","\n"),30)
        
        for i in capture.result.split("\n\n"):
            para = []
            for x in i.split("\n"):
                para.append(x)
            display.append(para)
        
        return render_template(
            "yo.html",
            display=display,
            sitetitle="Yo",
            )

