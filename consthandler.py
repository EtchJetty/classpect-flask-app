import csv
import random

# turn classpects into an object

class ClasspectComponent:
    'Generic classpect component. Used for classes and aspects.'
    def __init__(self, name="base", type="class"):
        self.name = name
        self.type = type
        if type == "class":
            toBe = self.classdef()
            self.vgroup = toBe["verb group"]
            self.verb = toBe["verb"]
            self.activity = toBe["passive/active"]
            self.altverb = toBe["altverb"]
        
    def __add__(self, other):
        if self.type == other.type:
            if self.type == "class":
                return ClasspectComponent(CLASSPECTS["classes"][self.name][other.name])
            else:
                return ClasspectComponent(CLASSPECTS["aspects"][self.name][other.name])
        else: 
            raise Exception("Addition between different types not yet implimented!")
        
        
    def __sub__(self, other):
        if self.type == other.type:
            if self.type == "class":
                return ClasspectComponent(next((k for k, v in CLASSPECTS["classes"][other.name].items() if v == self.name), "base"))
            else:
                return ClasspectComponent(next((k for k, v in CLASSPECTS["aspects"][other.name].items() if v == self.name), "base"))
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
            return ClasspectComponent()
    
    def classdef(self):
        classDef = {}
        try:
            getDefs(CLASSDEFS_CSV_PATH)[0][self.name]
        except:
            return {"verb group": None, "verb": None, "passive/active": None, "altverb": None}
        else: 
            for i in getDefs(CLASSDEFS_CSV_PATH): 
                classDef[i["base"]] = i[self.name]
        return classDef
    
    def fullverbgroup(self):
        fullgroup = []
        for classpect in getAllClasspects(self.type):
            if classpect.vgroup == self.vgroup:
                fullgroup.append(classpect)
        return fullgroup
    
    def inverse(self):    
        if self.type == "class":
            for i in self.fullverbgroup():
                if (i.activity != self.activity) and (i.verb != self.verb):
                    return i
        else:
            try:
                getDefs(ASPECTDEFS_CSV_PATH)[0][self.name]
            except:
                return ClasspectComponent("base","aspect")
            else: 
                for i in getDefs(ASPECTDEFS_CSV_PATH): 
                    return ClasspectComponent(i[self.name],"aspect")
        return ClasspectComponent()
        
    def paired(self):
        if self.type != "class":
            raise Exception("Only classes have paired classes!")
        for i in self.fullverbgroup():
            if (i.activity != self.activity) and (i.verb == self.verb):
                return i
        return ClasspectComponent()


    
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

# end csv util functions

# begin general use functions
def getRandomClasspect(duals:bool = False):
    rolls = []
    if duals: # i have no clue why i did it this way but hey it works
        for i in CLASSPECTS.values(): rolls.append(ClasspectComponent(i[random.choice(list(i.keys()))][random.choice(list(i.keys()))]))
    else: 
        for i in CLASSPECTS.values(): rolls.append(ClasspectComponent(random.choice(list(i.keys()))))
    return rolls

def getAllClasspects(type = "class"):
    vgroup = []
    if type == "class":
        for k in getDefs(CLASSDEFS_CSV_PATH)[0].items():
            vgroup.append(ClasspectComponent(k[0]))
    else: 
         for k in getDefs(ASPECTDEFS_CSV_PATH)[0].items():
            vgroup.append(ClasspectComponent(k[0]))
    vgroup.pop(0)
    return vgroup

# end general use functions

# begin fun functions
def tests():
    for classpect in getAllClasspects():
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
    
    sylph = ClasspectComponent("Sylph")
    bard = ClasspectComponent("Bard")
    print(sylph.name, ": One who ", sylph.verb, "s ", sylph.activity, "ly with their aspect.", sep="")
    
    time = ClasspectComponent("Time","aspect")
    light = ClasspectComponent("Light","aspect")
    print(time.name, ": A cool aspect. Hell yeah.", sep="")
    
    print(sylph.name,"+", bard.name, "=", (sylph+bard).name)
    
    editor = ClasspectComponent("Editor")
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
CLASSES_CSV_PATH  = os.path.join(THIS_FOLDER, "classes.csv")
ASPECTS_CSV_PATH  = os.path.join(THIS_FOLDER, "aspects.csv")
CLASSDEFS_CSV_PATH  = os.path.join(THIS_FOLDER, "classdefs.csv")
ASPECTDEFS_CSV_PATH  = os.path.join(THIS_FOLDER, "aspectdefs.csv")

CLASSPECTS = {"classes": getcsv(CLASSES_CSV_PATH), "aspects": getcsv(ASPECTS_CSV_PATH)}

# main()