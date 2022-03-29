from flask import Flask, render_template, g, request
from datetime import datetime
from flask_babel import Babel, format_datetime
from consthandler import *

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
    
@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/classpect")
def fresh():
    normals = []
    # printit.append("Normals:\n")
    for i in range(12):
        roll = getRandomClasspect()
        normals.append(roll[0].name + " of " + roll[1].name + "\n")
    
    duals = []
    # printit.append("\nDuals:\n")
    for i in range(12):
        roll = getRandomClasspect(duals=True)
        duals.append(roll[0].name + " of " + roll[1].name + "\n")
    return render_template(
        "checkit.html",
        normals=normals, duals=duals
        )

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=format_datetime(datetime.now(), "EEEE, MMMM dd, yyyy 'at' h:m.")
    )

