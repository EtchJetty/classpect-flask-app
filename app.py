import json
import random
from flask import Flask, render_template, g, request
from datetime import datetime
from flask_babel import Babel, format_datetime
import consthandler as cspect


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
    
def fetchAllClasspects():
    classes = cspect.getAllClasspects()
    aspects = cspect.getAllClasspects("aspect")
    random.seed()
    for i in range(len(classes)):
        classes[i] = json.dumps(classes[i].__dict__)
    for i in range(len(aspects)):
        aspects[i] = json.dumps(aspects[i].__dict__)
    return {"classes":classes,"aspects":aspects}
    
@app.route("/")
def home():
    display = {}
    
    display["date"] = format_datetime(datetime.now(), "EEE, MMM d, yyyy")
    
    random.seed(format_datetime(datetime.now(), "EEE, MMM d, yyyy"))
    
    display["classpects"] = fetchAllClasspects()
    
    return render_template(
        "cotd.html",sitetitle="ERIJAN CENTRAL",
        display=display
    )

@app.route("/classpects/search", methods=['GET', 'POST'])
def lookupclspect():
    if request.method == 'GET':
        display = []
        
        return render_template(
            "lazysearch.html",
            display=display,
            sitetitle="Lookup",
            )
    if request.method == "POST":        
        form = dict(request.form)
        results = {}
        
        for i in form:
            results[i] = cspect.ClasspectComponent(name=form[i].capitalize(),type=i.capitalize().replace("Math","")) 
        
        return render_template(
            "lazysearch.html",
            results=results,classpects=fetchAllClasspects(),
            sitetitle="Lookup",
            )

    
@app.route("/classpects/random")
def rclspect():
    normals = []

    for i in range(12):
        roll = cspect.getRandomClasspect()
        normals.append(roll[0].name + " of " + roll[1].name + "\n")
    
    duals = []

    for i in range(12):
        roll = cspect.getRandomClasspect(duals=True)
        duals.append(roll[0].name + " of " + roll[1].name + "\n")
    return render_template(
        "checkit.html",
        normals=normals, duals=duals
        )

@app.route("/src/<name>")
def arbitraryHtml(name = None):
    return render_template(
        name)
    
@app.route("/games/homesturdle")
def homesturdle():
    return render_template(
        "homesturdle.html")


    