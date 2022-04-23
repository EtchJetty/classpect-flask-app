
from datetime import date, datetime
import json
import random

from flask import render_template, request, url_for
from consthandler import CLASSPECT_DICT, ClasspectComponent, fetchAllClasspects, fetchAllDuals, getAllClasspects, getRandomClasspect
from flask_babel import format_datetime


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
    

def dualName(unknown): #compatibility function
    if unknown.__class__ != [].__class__:
        if unknown.__class__ == ClasspectComponent("base","class").__class__:
            if unknown.isCanon():
                return "<a onclick='copycat(\""+ unknown.name +"\");' role='button'>" + unknown.name + "</a>"
        return unknown.name
    else:
        x = ""
        for i in unknown:
            try:
                x = "<span style='font-size:0.05px;'>&nbsp;</span><a onclick='copycat(\"" + i.name +"\");' role='button'>" + x + "</a><span style='font-size:0.05px;'>&nbsp;</span>" + "<span style='font-size:0.05px;'>&nbsp;</span><a onclick='copycat(\""+ i.name +"\");' role='button'>" + i.name + ""
                if len(unknown) > 1 and i != unknown[-1]:
                    x = "<span style='font-size:0.05px;'>&nbsp;</span><a onclick='copycat(\""+ i.name +"\");' role='button'>" + x + "</a><span style='font-size:0.05px;'>&nbsp;</span>"
            except:
                pass
        return x

def dualClean(unknown): # dualName without js 
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
                ClasspectComponent(results[i].name,results[i].typeInverse()).isCanon()
            or
            ClasspectComponent(results[i].name,results[i].typeInverse()).isDual()
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
            newForm = {"class":form["aspect"],"aspect":form["class"],"mathclass":form["mathclass"],"mathaspect":form["mathaspect"]}
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
                results[x] = ClasspectComponent(name=newForm[x].capitalize(),type=x.capitalize().replace("Math",""))
                
    last = list(i.name for i in results.values())
    
    if len(last) != len(set(last)):
        if last[0] == last [1]:
            if not invalidCspect(ClasspectComponent(last[0],"class")):
                validtype = "aspect"
                results[validtype] = ClasspectComponent("",validtype)
            elif not invalidCspect(ClasspectComponent(last[0],"aspect")):
                validtype = "class"
                results[validtype] = ClasspectComponent("",validtype)
        try: 
            last[2]
        except: 
            pass
        else: 
            if last[2] == last [3]:
                if not invalidCspect(ClasspectComponent(last[2],"class")):
                    validtype = "aspect"
                    results["math"+validtype] = ClasspectComponent("",validtype)
                elif not invalidCspect(ClasspectComponent(last[2],"aspect")):
                    validtype = "class"
                    results["math"+validtype] = ClasspectComponent("",validtype)
    return results
    
def sortByType(e):
    return e.type
    
def makePrintable(formState, classpect_data):
    for i in classpect_data:
        if (dualClean(i) == ""):
            formState["singular"] = dualTypeInvTest(i)
        else: 
            formState["singular"] = False
                
    printable_class = dualName(classpect_data[0])
    printable_aspect = dualName(classpect_data[1]) + emote(classpect_data[1])
    
    if formState["singular"] == "class":
        return [printable_class]
    elif formState["singular"] == "aspect":
        return [printable_aspect]
    elif not (printable_aspect == "" or printable_class == ""):
        of = " of "
        return [printable_class, of, printable_aspect]
            
def dualFlavorText(formState, classpect_data):
    dual_class_data = list(classpect_data[0].dualComponents())
    dual_aspect_data = list(classpect_data[1].dualComponents())
    dual_classpect_data = [dual_class_data, dual_aspect_data] # list of lists
    printable_dual_classpect_flavor_text = wrapMuted("".join(makePrintable(formState, dual_classpect_data))) # makes list, stringifies, puts the small tag + class around the string
    return printable_dual_classpect_flavor_text

def wrapMuted(inputlist):
    return "<small class='text-muted'>or: " + inputlist + "</small>"
            
def emote(aspect:ClasspectComponent,style="height: 24px;"):
    if aspect.__class__ == [].__class__ or aspect.name == "" or (not aspect.isCanon() and not aspect.isDual()):
        return ""
    urlFront = "<a onclick='copycat(\""
    urlFront2 = "\");' role='button'><img src='" + url_for('static', filename='images/')
    urlMid = ".png' style='position: relative; bottom: 1px; "
    urlBack = "' class='img-fluid' /></a>"
    if aspect.isDual():
        return " " + urlFront + aspect.dualComponents()[0].name + urlFront2 + aspect.dualComponents()[0].name + urlMid + style + urlBack + urlFront  + aspect.dualComponents()[1].name + urlFront2 + aspect.dualComponents()[1].name + urlMid + style + urlBack
    return " " + urlFront + aspect.name + urlFront2 + aspect.name + urlMid + style + urlBack

def mathValidator(form):
    try: 
        form["mathclass"]
    except:
        form["mathclass"] = ""
        form["mathaspect"] = ""
        # if form["class"] + form["aspect"] != "":
        #     if not (invalidCspect(ClasspectComponent(form["class"],"class"))) or not (invalidCspect(ClasspectComponent(form["aspect"],"aspect"))):
        #         return True
        # return False
    
    results = {}
    for i in form:
        results[i] = (ClasspectComponent(name=form[i].capitalize(),type=i.capitalize().replace("Math","")))
    

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
                
    
def searchpage():
    if len(request.args) > 0:
        # json.loads(request.args["json"])
        argargs = {}
        # hidden = json.loads(request.args["json"])
        for fixe in ["c","a","mc","ma"]:
            try: 
                argargs[fixe] = request.args[fixe]
            except:
                argargs[fixe] = ""
        if "".join([value for key, value in argargs.items()]) != "":
            request.method = "POST"
            hidden = {"class":argargs["c"],"aspect":argargs["a"],"mathclass":argargs["mc"],"mathaspect":argargs["ma"]}
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
        if len(form) >= 3:
            
            try: 
                form["mathaspect"]
            except:
                form["mathaspect"] = ""
            try: 
                form["mathclass"]
            except:
                form["mathclass"] = ""
            if form["mathaspect"] != "" or form["mathclass"] != "":
                formState["math"] = True 
            
        for i in form:
            results[i] = ClasspectComponent(name=form[i].capitalize(),type=i.capitalize().replace("Math","")) 
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
        elif class_data.isCanon() and aspect_data.isCanon():
            printable_dual_classpect_flavor_text = "<br><small class='text-muted'>Examples include: " + CLASSPECT_DICT[class_data.name][aspect_data.name] + "</small>"
        else: 
            printable_dual_classpect_flavor_text = ""
        
            
        # generating inverse and housetrapped 
        if not invalidCspects(classpect_data):
            hr1 = "<hr>"
            hr2 = "<hr>"
            inverse_classpect_data = class_data.inverse(), aspect_data.inverse()
            printable_inverse_classpect = wrapLi("".join(makePrintable(formState, inverse_classpect_data)),"Inverse")
            if formState["dual"]:
                printable_inverse_dual_classpect_flavor_text = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,inverse_classpect_data) + "</li></ul>"
            else: 
                printable_inverse_dual_classpect_flavor_text = ""
                
            housetrapped = """
<hr><p>Want a more detailed explanation?<br>
<small><strong>Click</strong> on any canon Classpect, and you can view information on it below!</small></p>
<div class="accordion" id="accordionExample">
  <div class="card">
    <div class="card-header" id="headingOne">
      <h2 class="mb-0">
        <button id="jstarget" class="btn collapsed" type="button" data-toggle="collapse" data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne" disabled>
          Please click on a Classpect!
        </button>
      </h2>
    </div>

    <div id="collapseOne" class="collapse open" aria-labelledby="headingOne">
      <div class="card-body" style="padding: unset;">
        <div class="embed-responsive" style="height:400px;">
          <iframe class="embed-responsive-item w-100 h-100" id="housetrapped" src=""></iframe>
          </div>
      </div>
    </div>
  </div>
</div>"""
            
            
        else:
            hr1 = ""
            hr2 = ""
            printable_inverse_classpect = ""
            printable_inverse_dual_classpect_flavor_text = ""
            housetrapped = ""
            
        # generating paired class 
        if not invalidCspect(class_data):
            printable_paired_class = wrapLi(dualName(class_data.paired()),"Paired class for " + dualName(class_data)) # future me i am so sorry
            if formState["dual"]:
                printable_paired_dual_class_flavor_text = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,(class_data.paired(),ClasspectComponent("","aspect"))) + "</li></ul>"
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
                    if (not i.isDual()) and (i.name != ""):
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
                    
                    ex3 = getRandomClasspect()[sel]
                    ex4 = ex3
                    while ex4 == ex3:
                        ex4 = getRandomClasspect()[sel]
                        
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
                        if (form[i.typeInverse()] == "") and not invalidCspect(ClasspectComponent(form["math" + i.typeInverse()], i.typeInverse())):
                            summed_data = sorted((i, ClasspectComponent(form["math" + i.typeInverse()], i.typeInverse())),key=sortByType,reverse=True)
                            printable_sum = wrapLi("".join(makePrintable(formState, summed_data)),"Output")
                            addit = "<ul style='margin-bottom: 0px'><li style='color: transparent'>" + dualFlavorText(formState,summed_data) + "</li></ul>"
                            mathdisplay.extend([printable_sum,addit])
        else:
            mathdisplay = []
        mathdisplay.extend([housetrapped])
        
        display = compileArr(display)
        mathdisplay = compileArr(mathdisplay)

        niceresults = dict(results)
        for k,v in niceresults.items():
            niceresults[k] = v.name
                
        return render_template(
                "bettersearch.html",
                results=results,niceresults=niceresults,classpects=fetchAllClasspects(),
                sitetitle="Lookup",display=display,mathdisplay=mathdisplay,validator=mathValidator(form),validmath=validmath
            )

def homepageget(): 
    display = {}
    
    display["date"] = format_datetime(datetime.now(), "EEE, MMM d, yyyy")
    
            
    listy = [[{inx["type"]:ClasspectComponent(inx["name"],inx["type"]).__dict__} for inx in types] for types in dict(fetchAllClasspects()).values()]        
    listy = [{"class":i["class"],"aspect":y["aspect"]} for i in listy[0] for y in listy[1]]
    random.Random(413).shuffle(listy)
    listy = json.dumps(dict([(str(indexy), itemy) for indexy, itemy in enumerate(listy)]))
    # random.seed(413)
    # seeder = random.getstate()
    # random.Random(413).shuffle(listy)
    dual_listy = fetchAllDuals()
    dual_listy = [{"class":i,"aspect":y} for i in sorted(dual_listy["class"]) for y in sorted(dual_listy["aspect"])]
    random.Random(413).shuffle(dual_listy)
    dual_listy = dict(sorted(enumerate(dual_listy),key=lambda item: item))
    # random.Random(413).shuffle(loust)
    daysNum = ((datetime.now().date() - date(2009,4,13)).days)%4422
    print(daysNum,"days")
    smalldual_listy = [{"class":dual_listy[i]["class"],"aspect":dual_listy[i]["aspect"],"aspectduals":[component.__dict__ for component in ClasspectComponent(dual_listy[i]["aspect"],"aspect").dualComponents()]} for i in range((abs(daysNum) - 3), (abs(daysNum) + 3))]
    display["classpects"] = fetchAllClasspects()
    dual_listy = json.dumps(dual_listy)
    smalldual_listy = json.dumps(smalldual_listy)
    return (display, listy, dual_listy, smalldual_listy)

def homepage():
    pagevars = homepageget()
    return render_template(
        "cotd.html", sitetitle="Home", display=pagevars[0], listy=pagevars[1], dual_listy=pagevars[2], smalldual_listy=pagevars[3]
    )