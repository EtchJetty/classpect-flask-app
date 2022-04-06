import json
import random
from flask import Flask, redirect, render_template, g, request, url_for
from datetime import datetime, date
from flask_babel import Babel, format_datetime
from pagefuncs import *
from consthandler import *

# TODO : rework COTD generation

app = Flask(__name__)

babel = Babel(app)

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept header the browser transmits.  We support de/fr/en in this example.  The best match wins.
    return request.accept_languages.best_match(['de', 'fr', 'en'])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone
 
@app.route("/")
def home():
    return homepage()

@app.route("/classpects/search/<custom>", methods=['GET'])
def searchfix(custom = None):
    if custom:
        request.method = "POST"
        custom = custom.split("of")
        request.form = {"class":custom[0],"aspect":custom[1]}
        return redirect(url_for('lookupclspect', json=json.dumps(request.form), code=307))

@app.route("/classpects/search", methods=['GET', 'POST'])
def lookupclspect():
    return searchpage()

@app.route("/classpects/random")
def rclspect():
    normals = []
    for i in range(12):
        roll = getRandomClasspect()
        roll = (ClasspectComponent(roll[0],"class"),ClasspectComponent(roll[1],"class"))
        normals.append("<a href='" + url_for("lookupclspect") + "/" + roll[0].name + "of" + roll[1].name + "'>" + roll[0].name + " of " + roll[1].name + "</a>\n")
    
    duals = []

    for i in range(12):
        roll = getRandomClasspect(duals=True)
        roll = (ClasspectComponent(roll[0],"class"),ClasspectComponent(roll[1],"class"))
        duals.append("<a href='" + url_for("lookupclspect") + "/" + roll[0].name + "of" + roll[1].name + "'>" + roll[0].name + " of " + roll[1].name + "</a>\n")
    
    
    return render_template(
        "checkit.html",
        normals=normals, duals=duals,sitetitle="Randoms",icon=random.randint(1,6)
        )

@app.route("/src/<name>")
def arbitraryHtml(name = None):
    return render_template(
        name)
    
@app.route("/games/homesturdle")
def homesturdle():
    return render_template(
        "homesturdle.html")

# flask_profiler.init_app(app)
