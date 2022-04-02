import json
from operator import itemgetter
import random
from flask import Flask, redirect, render_template, g, request, url_for
from datetime import datetime
from flask_babel import Babel, format_datetime
import consthandler as ectdata

# import flask_profiler

app = Flask(__name__)
# app.config["DEBUG"] = True

# # You need to declare necessary configuration to initialize
# # flask-profiler as follows:
# app.config["flask_profiler"] = {
#     "enabled": app.config["DEBUG"],
#     "storage": {
#         "engine": "sqlite"
#     },
#     "basicAuth":{
#         "enabled": True,
#         "username": "admin",
#         "password": "admin"
#     },
#     "ignore": [
# 	    "^/static/.*"
# 	]
# }



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
    
def compileArr(array):
    display = "".join(array)
    return display
    
def invalidCspect(aspect):
    return (not aspect.isCanon() and not aspect.isDual())
    
def invalidCspects(aspects):
    for i in aspects:
        if not invalidCspect(i):
            return False
    return True 
    
def fetchAllClasspects():
    classes = ectdata.getAllClasspects("class")
    aspects = ectdata.getAllClasspects("aspect")
    for i in range(len(classes)):
        classes[i] = ectdata.ClasspectComponent(classes[i],"class").__dict__
    for i in range(len(aspects)):
        aspects[i] = ectdata.ClasspectComponent(aspects[i],"aspect").__dict__
        
    aspects = sorted(aspects, key=itemgetter("name"))
    classes = sorted(classes, key=itemgetter("name"))

    string = ({"class":classes,"aspect":aspects})
    
    return string

def dualName(unknown): #compatibility function
    if unknown.__class__ != [].__class__:
        return unknown.name
    else:
        x = ""
        for i in unknown:
            try:
                x += i.name
            except:
                pass
        return x
    
def dualTypeInvTest(unknown): #ugly copy of dualName. can't figure out how to make nicer
    if unknown.__class__ != [].__class__:
        return unknown.typeInverse()
    else:
        x = ""
        for i in unknown:
            try:
                x += i.typeInverse()
            except:
                pass
        return x
    
def wrapLi(inputlist,text):
    return "<li>" + text + ": " + inputlist + "</li>"
    
def magicant(form,results,formState):
    for i in results:
        megaarr = (
            not(results[i].isCanon() or results[i].isDual())
        and
            (
                ectdata.ClasspectComponent(results[i].name,results[i].typeInverse()).isCanon()
            or
            ectdata.ClasspectComponent(results[i].name,results[i].typeInverse()).isDual()
            )
        and
            (
            (invalidCspect(results[results[i].typeInverse()]))
            or
            (
                formState["math"]
                and
                (
                (invalidCspect(results["math"+results[i].typeInverse()]))
                and
                (i == "math"+results[i].type)
                )
            )
            )
        )
        if megaarr:
            results = {}
            newForm = {"class":form["aspect"],"aspect":form["class"]}
            if formState["math"]:
                print(i)
                newForm["mathaspect"] = form["mathclass"]
                newForm["mathclass"] = form["mathaspect"]
                if i == "class" or i == "aspect":
                    newForm["class"] = form["aspect"] 
                    newForm["aspect"] = form["class"]
                else:
                    newForm["class"] = form["class"] 
                    newForm["aspect"] = form["aspect"]
            for x in newForm:
                results[x] = ectdata.ClasspectComponent(name=newForm[x].capitalize(),type=x.capitalize().replace("Math",""))
                
    last = list(i.name for i in results.values())
    
    if len(last) != len(set(last)):
        if last[0] == last [1]:
            if not invalidCspect(ectdata.ClasspectComponent(last[0],"class")):
                validtype = "aspect"
                results[validtype] = ectdata.ClasspectComponent("",validtype)
            elif not invalidCspect(ectdata.ClasspectComponent(last[0],"aspect")):
                validtype = "class"
                results[validtype] = ectdata.ClasspectComponent("",validtype)
        try: 
            last[2]
        except: 
            pass
        else: 
            if last[2] == last [3]:
                if not invalidCspect(ectdata.ClasspectComponent(last[2],"class")):
                    validtype = "aspect"
                    results["math"+validtype] = ectdata.ClasspectComponent("",validtype)
                elif not invalidCspect(ectdata.ClasspectComponent(last[2],"aspect")):
                    validtype = "class"
                    results["math"+validtype] = ectdata.ClasspectComponent("",validtype)
    return results
    
def sortByType(e):
    return e.type
    
def makePrintable(formState, classpect_data):
    for i in classpect_data:
        if (dualName(i) == ""):
            formState["singular"] = dualTypeInvTest(i)
                
    printable_class = dualName(classpect_data[0])
    printable_aspect = dualName(classpect_data[1]) + emote(classpect_data[1])
    if not (printable_aspect == "" or printable_class == ""):
        of = " of "
        return [printable_class, of, printable_aspect]
    elif formState["singular"] == "class":
        return [printable_class]
    elif formState["singular"] == "aspect":
        return [printable_aspect]
            
def dualFlavorText(formState, classpect_data):
    dual_class_data = list(classpect_data[0].dualComponents())
    dual_aspect_data = list(classpect_data[1].dualComponents())
    dual_classpect_data = [dual_class_data, dual_aspect_data] # list of lists
    printable_dual_classpect_flavor_text = wrapMuted("".join(makePrintable(formState, dual_classpect_data))) # makes list, stringifies, puts the small tag + class around the string
    return printable_dual_classpect_flavor_text

def wrapMuted(inputlist):
    return "<small class='text-muted'>or: " + inputlist + "</small>"
            
def emote(aspect:ectdata.ClasspectComponent,style="height: 24px;"):
    if aspect.__class__ == [].__class__ or aspect.name == "" or (not aspect.isCanon() and not aspect.isDual()):
        return ""
    urlFront = "<img src='" + url_for('static', filename='images/')
    urlMid = ".png' style='position: relative; bottom: 1px; "
    urlBack = "' class='img-fluid' />"
    if aspect.isDual():
        return " " + urlFront + aspect.dualComponents()[0].name + urlMid + style + urlBack + urlFront + aspect.dualComponents()[1].name + urlMid + style + urlBack
    return " " + urlFront + aspect.name + urlMid + style + urlBack

def mathValidator(form):
    try: 
        form["mathclass"]
    except:
        form["mathclass"] = ""
        form["mathaspect"] = ""
        # if form["class"] + form["aspect"] != "":
        #     if not (invalidCspect(ectdata.ClasspectComponent(form["class"],"class"))) or not (invalidCspect(ectdata.ClasspectComponent(form["aspect"],"aspect"))):
        #         return True
        # return False
    
    results = {}
    for i in form:
        results[i] = (ectdata.ClasspectComponent(name=form[i].capitalize(),type=i.capitalize().replace("Math","")))
    

    try: 
        results["mathclass"] + results["class"]
    except:
        try: 
            results["mathaspect"] + results["aspect"]
        except:
            try:
                results["mathclass"] - results["class"]
            except:
                try: 
                    results["mathclass"] - results["aspect"]
                except:
                    try:
                        results["class"] - results["mathclass"]
                    except:
                        try: 
                            results["aspect"] - results["mathaspect"]
                        except:
                            pass
                        else:
                            return True
                    else:
                        return True
                else:
                    return True
            else:
                return True
        else:
            return True
    else:
        return True
    
    return False 
                
    
@app.route("/")
def home():
    display = {}
    
    display["date"] = format_datetime(datetime.now(), "EEE, MMM d, yyyy")
    display["classpects"] = fetchAllClasspects()

    return render_template(
        "cotd.html",sitetitle="Home",
        display=display
    )

@app.route("/classpects/search/<custom>", methods=['GET'])
def searchfix(custom = None):
    if custom:
        request.method = "POST"
        custom = custom.split("of")
        request.form = {"class":custom[0],"aspect":custom[1]}
        return redirect(url_for('lookupclspect', json=json.dumps(request.form), code=307))

@app.route("/classpects/search", methods=['GET', 'POST'])
def lookupclspect():
    if len(request.args) > 0:
        json.loads(request.args["json"])
    
        request.method = "POST"
        hidden = json.loads(request.args["json"])
    if request.method == 'GET':
        display = []
        
        return render_template(
            "bettersearch.html",classpects=fetchAllClasspects(),
            display=display,
            sitetitle="Lookup",
            )
    if request.method == "POST":        

        form = dict(request.form)
        results = {}
        
        if list(form.values()).count("") == len(form):
            try:
                hidden
            except:
                return render_template(
            "bettersearch.html",
            results=results,classpects=fetchAllClasspects(),
            sitetitle="Lookup",display=""
            )
            else:
                form = hidden
        
        formState = {"dual":False,"math":False,"singular":False}
        if len(form) > 3:
            formState["math"] = True
            
            
            
        for i in form:
            results[i] = ectdata.ClasspectComponent(name=form[i].capitalize(),type=i.capitalize().replace("Math","")) 
            if results[i].isDual():
                formState["dual"] = True
        
        #fix the swapped aspect/class search
        results = magicant(form,results,formState)
        for i in results.values():
            if i.isDual():
                formState["dual"] = True
        
        class_data = results["class"]
        aspect_data = results["aspect"]
        classpect_data = class_data, aspect_data        
                
        for i in classpect_data:
            if (dualName(i) == ""):
                formState["singular"] = dualTypeInvTest(i)
        
        # generating the printable version
        printable_classpect = "".join(makePrintable(formState, classpect_data))
            
        # generating the dual flavor text
        if formState["dual"]:
            printable_dual_classpect_flavor_text = "<br>" + dualFlavorText(formState,classpect_data)
        else: 
            printable_dual_classpect_flavor_text = ""
            
        # generating inverse 
        if not invalidCspects(classpect_data):
            hr1 = "<hr>"
            hr2 = "<hr>"
            inverse_classpect_data = class_data.inverse(), aspect_data.inverse()
            printable_inverse_classpect = wrapLi("".join(makePrintable(formState, inverse_classpect_data)),"Inverse")
            if formState["dual"]:
                printable_inverse_dual_classpect_flavor_text = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,inverse_classpect_data) + "</li></ul>"
            else: 
                printable_inverse_dual_classpect_flavor_text = ""
        
        else:
            hr1 = ""
            hr2 = ""
            printable_inverse_classpect = ""
            printable_inverse_dual_classpect_flavor_text = ""
            
        # generating paired class 
        if not invalidCspect(class_data):
            printable_paired_class = wrapLi(dualName(class_data.paired()),"Paired class for " + class_data.name) # future me i am so sorry
            if formState["dual"]:
                printable_paired_dual_class_flavor_text = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,(class_data.paired(),ectdata.ClasspectComponent("","aspect"))) + "</li></ul>"
            else: 
                printable_paired_dual_class_flavor_text = ""
        
        else:
            printable_paired_class = ""
            printable_paired_dual_class_flavor_text = ""

        if (((invalidCspect(class_data) and aspect_data.name == "") or (invalidCspect(aspect_data) and class_data.name == "") and aspect_data.name != class_data.name)):
            hr2 = "<hr>"            
            
        # end basic classpect math generation!! :D
        display = [printable_classpect,printable_dual_classpect_flavor_text,hr1,printable_inverse_classpect,printable_inverse_dual_classpect_flavor_text,printable_paired_class,printable_paired_dual_class_flavor_text,hr2]
        
        validmath = {}
        if mathValidator(form):
            # math tooltip generation
            if formState["dual"]:
                for i in classpect_data:
                    if not i.isDual():
                        formState["dual"] = False
                    
            tooltip = ["Add or subtract classpects to make Dual Classes!<br><small>It looks like you've searched for a "]
            if not formState["dual"] and (class_data.isCanon() or aspect_data.isCanon()):
                tooltip.extend("standard Classpect. This means you can add any other standard classpect to it, and it'll give you a unique dual!</small>")
                validmath = fetchAllClasspects()
            elif formState["dual"]: 
                components = {"class":[],"aspect":[]}
                for i in classpect_data:
                    if i.isDual():
                        components[i.type].extend(i.dualComponents())
                        
                validmath = {"class":components["class"],"aspect":components["aspect"]} 
                if components["class"] == []:
                    pull = components["aspect"]
                    validmath["class"] = fetchAllClasspects()["class"]
                elif components["aspect"] == []:
                    pull = components["class"]
                    validmath["aspect"] = fetchAllClasspects()["aspect"]
                else: 
                    pull = components["class"] + components["aspect"]
                
                ex1 = random.choice(pull).name
                ex2 = ex1
                while ex2 == ex1:
                    ex2 = random.choice(pull).name
                
                if not (class_data.isCanon() or aspect_data.isCanon()):
                    tooltip.extend("Dual Classpect. Since the Dual Classpect is made up of regular Classpects, you can subtract any of its components <span class='text-muted'>(like " + ex1 + " or " + ex2 + ")</span> from your search term!</small>")
                elif class_data.isCanon() or aspect_data.isCanon():
                    if class_data.isCanon(): 
                        sel = 0
                    elif aspect_data.isCanon():
                        sel = 1
                    
                    ex3 = ectdata.getRandomClasspect()[sel]
                    ex4 = ex3
                    while ex4 == ex3:
                        ex4 = ectdata.getRandomClasspect()[sel]
                        
                    tooltip.extend("mix of the two. Since the Dual Classpect is made up of regular Classpects, you can subtract any of its components <span class='text-muted'>(like " + ex1 + " or " + ex2 + ")</span> from your search term, but you can also add any regular classpect <span class='text-muted'>(like " + ex3 + " or " + ex4 + ")</span> to the non-Dual part of your search!</small>")
            
            
            display.extend(tooltip)
        elif (((not invalidCspect(class_data) and aspect_data.name == "") or (not invalidCspect(aspect_data) and class_data.name == "") and aspect_data.name != class_data.name)):
            tooltip = ["Add or subtract classpects to make Dual Classes!"]
            validmath = {}
            display.extend(tooltip)
        else:
            validmath = {}
            
        # math result generation
        if formState["math"]:            
            mathdisplay = []
            if mathValidator(form):
            # math tooltip generation
                if not formState["dual"] and (class_data.isCanon() or aspect_data.isCanon()):
                    summed_data = results["class"] + results["mathclass"],results["aspect"] + results["mathaspect"]
                    if (summed_data[0].name + summed_data[1].name) != "":
                        printable_sum = wrapLi("".join(makePrintable(formState, summed_data)),"Sum")
                        addit = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,summed_data) + "</li></ul>"
                        mathdisplay.extend([printable_sum,addit])
                elif formState["dual"]:
                    if not (class_data.isCanon() or aspect_data.isCanon()):
                        summed_data = results["class"] - results["mathclass"],results["aspect"] - results["mathaspect"]
                        if (summed_data[0].name + summed_data[1].name) != "":
                            printable_sum = wrapLi("".join(makePrintable(formState, summed_data)),"Difference")
                            mathdisplay.extend([printable_sum])
                    elif class_data.isCanon() or aspect_data.isCanon():
                        summed_data = ()
                        if class_data.isCanon():
                            summed_data = results["class"] + results["mathclass"],results["aspect"] - results["mathaspect"]
                        elif aspect_data.isCanon():
                            summed_data = results["class"] - results["mathclass"],results["aspect"] + results["mathaspect"]
                        if (summed_data[0].name + summed_data[1].name) != "":
                            printable_sum = wrapLi("".join(makePrintable(formState, summed_data)),"Output")
                            addit = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,summed_data) + "</li></ul>"
                            mathdisplay.extend([printable_sum,addit])
            elif (((invalidCspect(class_data) and aspect_data.name == "") or (invalidCspect(aspect_data) and class_data.name == "") and aspect_data.name != class_data.name)):
                for i in classpect_data:
                    if invalidCspect(i):
                        if (form[i.typeInverse()] == "") and not invalidCspect(ectdata.ClasspectComponent(form["math" + i.typeInverse()], i.typeInverse())):
                            summed_data = sorted((i, ectdata.ClasspectComponent(form["math" + i.typeInverse()], i.typeInverse())),key=sortByType,reverse=True)
                            printable_sum = wrapLi("".join(makePrintable(formState, summed_data)),"Output")
                            addit = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,summed_data) + "</li></ul>"
                            mathdisplay.extend([printable_sum,addit])
        else:
            mathdisplay = ""

        display = compileArr(display)
        mathdisplay = compileArr(mathdisplay)

                
        return render_template(
                "bettersearch.html",
                results=results,classpects=fetchAllClasspects(),
                sitetitle="Lookup",display=display,mathdisplay=mathdisplay,validator=mathValidator(form),validmath=validmath
            )

@app.route("/classpects/random")
def rclspect():
    normals = []
    for i in range(12):
        roll = ectdata.getRandomClasspect()
        roll = (ectdata.ClasspectComponent(roll[0],"class"),ectdata.ClasspectComponent(roll[1],"class"))
        normals.append("<a href='" + url_for("lookupclspect") + "/" + roll[0].name + "of" + roll[1].name + "'>" + roll[0].name + " of " + roll[1].name + "</a>\n")
    
    duals = []

    for i in range(12):
        roll = ectdata.getRandomClasspect(duals=True)
        roll = (ectdata.ClasspectComponent(roll[0],"class"),ectdata.ClasspectComponent(roll[1],"class"))
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
