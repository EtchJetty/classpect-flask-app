import random
from flask import Flask, redirect, render_template, g, request, url_for, jsonify
from flask_babel import Babel
from pagefuncs import *
from consthandler import *

# TODO : rework COTD generation

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return redirect(url_for('fourohfour'))


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


@app.route("/search/")
@app.route("/classpects/search/<custom>", methods=['GET'])
def searchfix(custom=None):
    if custom:
        request.method = "POST"
        criteria = ["class", "aspect", "mathclass", "mathaspect"]
        custom = dict([(criteria[inx], item)
                      for inx, item in enumerate(custom.split("of"))])
        if len(custom) != len(criteria):
            for item in criteria:
                try:
                    custom[item]
                except:
                    custom[item] = ""
        # return str(custom)
        # request.form = {"class":custom[0],"aspect":custom[1]}
        # return redirect(url_for('lookupclspect', json=json.dumps(request.form), code=307))
        return redirect(url_for('lookupclspect', c=custom["class"], a=custom["aspect"], mc=custom["mathclass"], ma=custom["mathaspect"]))

    return redirect(url_for('lookupclspect'))


@app.route("/classpects/search", methods=['GET', 'POST'])
def lookupclspect():
    return searchpage()


@app.route('/api/')
def api_page():
    methods = [""]
    methods.extend([method for method in dir(ClasspectComponent) if method[0] != "_"])
    return render_template(
        "apiexplain.html", sitetitle="API Docs", methods=methods, paths=["/classpect/","/calc/","/"])


@app.route('/api/v1/classpects', methods=['GET'])
@app.route('/api/v1/classpects/', methods=['GET'])
def api_cspects():
    try: 
        request.args["type"]
    except:
        request.args["type"] = ""
    
    try: 
        request.args["duals"]
    except:
        request.args["duals"] = ""
        
    if request.args["duals"] == "true":
        if request.args["type"] != "":
            cspectlist = list(getAllDuals(request.args["type"]))
        else: 
            cspectlist = dict([(kind, list(getAllDuals(kind))) for kind in ["class", "aspect"]])
    else:
        if request.args["type"] != "":
            cspectlist = getAllClasspects(request.args["type"])
        else: 
            cspectlist = dict([(kind, getAllClasspects(kind)) for kind in ["class", "aspect"]])
    return jsonify(cspectlist)

@app.route('/api/v1/classpects/classpect', methods=['GET'])
@app.route('/api/v1/classpects/classpect/', methods=['GET'])
def api_cspect():
    cspect = ClasspectComponent(
        request.args["name"], request.args["type"]).__dict__
    return jsonify(cspect)

@app.route('/api/v1/classpects/cotd', methods=['GET'])
@app.route('/api/v1/classpects/cotd/', methods=['GET'])
def api_cotd():
    
    return jsonify(list(homepageget()))


@app.route('/api/v1/classpects/classpect/<func>', methods=['GET'])
@app.route('/api/v1/classpects/classpect/<func>/', methods=['GET'])
def api_func(func=None):
    cspect = ClasspectComponent(request.args["name"], request.args["type"])
    if func == "inverse":
        cspect = cspect.inverse()
    elif func == "isCanon":
        cspect = cspect.isCanon()
    elif func == "isDual":
        cspect = cspect.isDual()
    elif func == "classdef":
        cspect = cspect.classdef()
    elif func == "paired":
        cspect = cspect.paired()
    elif func == "typeInverse":
        cspect = cspect.typeInverse() 
    elif func == "fullverbgroup":
        cspect = cspect.fullverbgroup()

    elif func == "dualComponents":
        try:
            cspect = [comp.__dict__ for comp in cspect.dualComponents()]
        except:
            cspect = {"status": 400,
                      "message": "You submitted a request for the dual components of a non-Dual classpect, and it failed."}
    if type(cspect) == ClasspectComponent:
        cspect = cspect.__dict__
        
        
    return jsonify(cspect)

@app.route('/api/v1/classpects/calc/', methods=['GET'])
@app.route('/api/v1/classpects/calc<func>', methods=['GET'])
@app.route('/api/v1/classpects/calc/<func>', methods=['GET'])
def api_cspect_calc(func=None):
    if func:
        cspect = ClasspectComponent(
                request.args["name"], request.args["type"])
        
        if func == "mul":
            try:
                resultcspect = (cspect * request.args["mval"]).__dict__
            except: 
                resultcspect = {"status": 400,
                      "message": "You submitted a multiplication request for the calculator, but didn't include a number to multiply by."}
        else: 
            
            mathcspect = ClasspectComponent(
                request.args["mname"], request.args["mtype"])
            
            if func == "add":
                try:
                    resultcspect = (cspect + mathcspect).__dict__
                except: 
                    resultcspect = {"status": 400,
                      "message": "You submitted an invalid addition request for the calculator."}
            if func == "sub":
                try: 
                    resultcspect = (cspect - mathcspect).__dict__
                except:
                    resultcspect = {"status": 400,
                      "message": "You submitted an invalid subtraction request for the calculator."}
    else:   
        resultcspect = {"status": 400,
                      "message": "You submitted a request for the calculator, but didn't include the function."}
    return jsonify(resultcspect)


@app.route("/classpects/random")
def rclspect():
    normals = []
    for i in range(12):
        roll = getRandomClasspect()
        roll = (ClasspectComponent(roll[0], "class"),
                ClasspectComponent(roll[1], "class"))
        normals.append("<a href='" + url_for("lookupclspect") + "/" +
                       roll[0].name + "of" + roll[1].name + "'>" + roll[0].name + " of " + roll[1].name + "</a>\n")

    duals = []

    for i in range(12):
        roll = getRandomClasspect(duals=True)
        roll = (ClasspectComponent(roll[0], "class"),
                ClasspectComponent(roll[1], "class"))
        duals.append("<a href='" + url_for("lookupclspect") + "/" +
                     roll[0].name + "of" + roll[1].name + "'>" + roll[0].name + " of " + roll[1].name + "</a>\n")

    return render_template(
        "checkit.html",
        normals=normals, duals=duals, sitetitle="Randoms", icon=random.randint(1, 6)
    )


@app.route("/src/")
@app.route("/src/<name>")
def arbitraryHtml(name="404"):
    try:
        return render_template(name + ".html", sitetitle=name)
    except:
        return render_template("404.html", sitetitle="404")


@app.route("/games/homesturdle")
def homesturdle():
    return render_template(
        "homesturdle.html", sitetitle="HOMESTURDLE")


@app.route("/about")
def about():
    return render_template(
        "about.html", sitetitle="About")


@app.route("/404")
def fourohfour():
    return render_template(
        "404.html", sitetitle="404")

# flask_profiler.init_app(app)
