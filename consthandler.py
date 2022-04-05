import csv, random
from operator import itemgetter
from shillelagh.backends.apsw.db import connect

# turn classpects into an object

class ClasspectComponent:
    'Generic classpect component. Used for classes and aspects.'
    def __init__(self, name, type):
        type = type.lower()
        self.name = name
        self.type = type
        if type == "class":
            toBe = self.classdef()
            self.vgroup = toBe["verb group"]
            self.verb = toBe["verb"]
            self.activity = toBe["passive/active"]
            self.altverb = toBe["altverb"]
        
    def __add__(self, other):
        if (self.name == "") or (self.isDual() and not other.isDual()) or (other.isCanon() and not self.isCanon()) or ((not self.isDual() and not self.isCanon()) and other.isDual() and other.isCanon()):
            return other
        elif (other.name == "") or (other.isDual() and not self.isDual()) or (self.isCanon() and not other.isCanon())  or ((not other.isDual() and not other.isCanon()) and self.isDual() and self.isCanon()):
            return self
        elif self.type == other.type:
            try:
                return ClasspectComponent(CLASSPECTS[self.type][self.name][other.name], self.type)
            except:
                raise Exception("Failed to add classpects!")
        else: 
            raise Exception("Addition between different types not yet implimented!")
        
        
    def __sub__(self, other):
        if (self.name == ""):
            return other
        elif (other.name == ""):
            return self
        elif self.type == other.type:
            try:
                return ClasspectComponent(next((k for k, v in CLASSPECTS[self.type][other.name].items() if v == self.name), ""),self.type)
            except:
                return ClasspectComponent("",self.type)
        else: 
            raise Exception("Subtraction between different types not yet implimented!")
        
    def __mul__(self, other):
        if other == -1:
            return self.inverse()
        elif other == 1:
            return self
        elif other == 2:
            return self+self
        else:
            return ClasspectComponent("",self.type)
    
    def classdef(self):
        classDef = {}
        try:
            CLASSDEFS[0][self.name]
        except:
            return {"verb group": None, "verb": None, "passive/active": None, "altverb": None}
        else: 
            for i in CLASSDEFS: 
                classDef[i["base"]] = i[self.name]
        return classDef
    
    def fullverbgroup(self):
        fullgroup = []
        for classpect in getAllClasspects(self.type):
            if ClasspectComponent(classpect,self.type).vgroup == self.vgroup:
                fullgroup.append(classpect)
        return fullgroup
    
    def isCanon(self):
        for classpect in getAllClasspects(self.type):
            if classpect == self.name:
                return True
        return False
    
    def isDual(self):
        if self.isCanon():
            return False
        if self.name in getAllDuals(self.type):
            return True
        return False
    
    def dualComponents(self):
        if not self.isDual():
            return self, None
        for classpect in getAllClasspects(self.type):
            for sum in getAllClasspects(self.type):
                if (ClasspectComponent(classpect,self.type)+ClasspectComponent(sum,self.type)).name == self.name:
                    return ClasspectComponent(classpect,self.type), ClasspectComponent(sum,self.type)
    
    def inverse(self):    
        if self.isDual():
            table = []
            for i in self.dualComponents():
                table.append(i.inverse())
            return (table[0] + table[1])
        if self.type == "class":
            for tester in self.fullverbgroup():
                i = ClasspectComponent(tester,self.type)
                if (i.activity != self.activity) and (i.verb != self.verb):
                    return i
        else:
            try:
                ASPECTDEFS[0][self.name]
            except:
                return ClasspectComponent("",self.type)
            else: 
                for i in ASPECTDEFS: 
                    return ClasspectComponent(i[self.name],self.type)
        return ClasspectComponent("",self.type)
    
    def typeInverse(self):    
        if self.type == "class":
            return "aspect"
        else:
            return "class"
        
    def paired(self):
        if self.type != "class":
            raise Exception("Only classes have paired classes!")
        if self.isDual():
            table = []
            for i in self.dualComponents():
                table.append(i.paired())
            return (table[0] + table[1])
        for tester in self.fullverbgroup():
            i = ClasspectComponent(tester,self.type)
            if (i.activity != self.activity) and (i.verb == self.verb):
                return i
        return ClasspectComponent("",self.type)


    
# csv util functions
def getcsv(filename:str = "aspects.csv"):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return {item['base']:item for item in list(reader)}
    
    
def getDefs(filename = "classdefs.csv"):
    defs = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        defs = list(reader) 
    return defs 

def gSheets():
    connection = connect(":memory:")
    cursor = connection.cursor()

    SQL = """
    SELECT *
    FROM "https://docs.google.com/spreadsheets/d/1Giy-e7veuPPftBssjvYguJwxBD3pTooAJOeqdsxSTAw/edit#gid=0"
    """

    column_names = ["Time","Space","Light","Void","Life","Doom","Breath","Blood","Hope","Rage","Mind","Heart"]
    row_names = ["Heir","Witch","Seer","Mage","Page","Knight","Rogue","Thief","Sylph","Maid","Bard","Prince"]
    
    
    data = {}
    for idz, row in enumerate(cursor.execute(SQL)):
        if idz < 12:
            rowdict = {}
            for idx, col in enumerate(row):
                rowdict[column_names[idx]] = col
            data[row_names[idz]] = rowdict
    return data

# end csv util functions

def getAllDuals(type):
    if type == "class":
        return set().union(*(d.values() for d in CLASSDUALS))
    else: 
        return set().union(*(d.values() for d in ASPECTDUALS))


# begin general use functions
def getRandomClasspect(duals:bool = False):
    rolls = []
    if not duals: # i have no clue why i did it this way but hey it works
        return [random.choice(getAllClasspects("class")),random.choice(getAllClasspects("aspect"))]
    else: 
        return [(ClasspectComponent(random.choice(getAllClasspects("class")),"class")+ClasspectComponent(random.choice(getAllClasspects("class")),"class")).name,(ClasspectComponent(random.choice(getAllClasspects("aspect")),"aspect")+ClasspectComponent(random.choice(getAllClasspects("aspect")),"aspect")).name]

def getAllClasspects(type):
    if type == "class":
        listy = CLASSDUALS
    else: 
        listy = ASPECTDUALS
    x = (set().union(*(d.keys() for d in listy)))
    x.remove("base")
    x = list(x)
    return x

# end general use functions
def fetchAllDuals():
    return dict([(kind,(getAllDuals(kind)) - (set(getAllClasspects(kind))) - {"base"}) for kind in fetchAllClasspects()])
     

    
def fetchAllClasspects():
    classes = getAllClasspects("class")
    aspects = getAllClasspects("aspect")
    for i in range(len(classes)):
        classes[i] = ClasspectComponent(classes[i],"class").__dict__
    for i in range(len(aspects)):
        aspects[i] = ClasspectComponent(aspects[i],"aspect").__dict__
        
    aspects = sorted(aspects, key=itemgetter("name"))
    classes = sorted(classes, key=itemgetter("name"))

    string = ({"class":classes,"aspect":aspects})
    
    return string

     
# begin fun functions
def tests():
    for classpect in getAllClasspects("class"):
        print(classpect.name)
    print()
    for classpect in getAllClasspects("aspect"):
        print(classpect.name)
    print("Normals:")
    for i in range(12):
        roll = getRandomClasspect()
        print(roll[0].name,"of",roll[1].name)
        
    print("\nDuals:")
    for i in range(12):
        roll = getRandomClasspect(duals=True)
        print(roll[0].name,"of",roll[1].name)
    print("\nDefinitions Experiment:")
    
    sylph = ClasspectComponent("Sylph","class")
    bard = ClasspectComponent("Bard","class")
    print(sylph.name, ": One who ", sylph.verb, "s ", sylph.activity, "ly with their aspect.", sep="")
    
    time = ClasspectComponent("Time","aspect")
    light = ClasspectComponent("Light","aspect")
    print(time.name, ": A cool aspect. Hell yeah.", sep="")
    
    print(sylph.name,"+", bard.name, "=", (sylph+bard).name)
    
    editor = ClasspectComponent("Editor","class")
    print(editor.name,"-", bard.name, "=", (editor-bard).name)
    print(sylph.name,"-", sylph.name, "=", (sylph-sylph).name)
    
    print(sylph.name,"* -1 =", (sylph*-1).name)
    print(sylph.name,"* 2 =",(sylph*2).name)
    print(sylph.name,"* 1 =",(sylph*1).name)
    print(sylph.name,"* 0 =",(sylph*0).name)
    
    print(time.name,"+", bard.name, "=", (sylph+bard).name)
    
    memes = ClasspectComponent("Memes","aspect")
    print(memes.name,"-", light.name, "=", (memes-light).name)
    print(time.name,"-", time.name, "=", (time-time).name)
    
    print(time.name,"* -1 =", (time*-1).name)
    print(time.name,"* 2 =",(time*2).name)
    print(time.name,"* 1 =",(time*1).name)
    print(time.name,"* 0 =",(time*0).name)
    
def main():
    tests()
    
# end function definitions

import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
CLASSES_CSV_PATH  = os.path.join(THIS_FOLDER, "static/classes.csv")
ASPECTS_CSV_PATH  = os.path.join(THIS_FOLDER, "static/aspects.csv")
CLASSDEFS_CSV_PATH  = os.path.join(THIS_FOLDER, "static/classdefs.csv")
ASPECTDEFS_CSV_PATH  = os.path.join(THIS_FOLDER, "static/aspectdefs.csv")

CLASSPECTS = {"class": getcsv(CLASSES_CSV_PATH), "aspect": getcsv(ASPECTS_CSV_PATH)}
CLASSDEFS = getDefs(CLASSDEFS_CSV_PATH)
ASPECTDEFS = getDefs(ASPECTDEFS_CSV_PATH)
CLASSDUALS = getDefs(CLASSES_CSV_PATH)
ASPECTDUALS = getDefs(ASPECTS_CSV_PATH)
CLASSPECT_DICT = gSheets()