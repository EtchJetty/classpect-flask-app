import csv
import random
# turn classpects into an object

def getcsv(filename:str = "aspects.csv"):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return {item['base']:item for item in list(reader)}
    
def getClasspect(classpects: list, duals:bool = False):
    rolls = []
    if duals:
        for i in classpects.values(): rolls.append(i[random.choice(list(i.keys()))][random.choice(list(i.keys()))])
    else: 
        for i in classpects.values(): rolls.append(random.choice(list(i.keys())))
    return rolls
    
def getClassDef(classname):
    defs = []
    with open("classdefs.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        defs = list(reader) 

    for i in defs:
        print(classname," ",i["base"],": ",i[classname], sep="")
    return 
    
def main():
    classpects = {"classes": getcsv("classes.csv"), "aspects": getcsv("aspects.csv")}

    print("Normals:")
    for i in range(12):
        roll = getClasspect(classpects)
        print(roll[0],"of",roll[1])
        
    print("\nDuals:")
    for i in range(12):
        roll = getClasspect(classpects, duals=True)
        print(roll[0],"of",roll[1])
    print("\nDefinitions Experiment:")
    getClassDef("Sylph")
main()