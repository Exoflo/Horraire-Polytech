import math
import docplex.cp.model as cp

def simultaneousGroups(model, AAdict1, AAdict2):
    numberOfDivisions1 = len(AAdict1["divisions"])
    numberOfDivisions2 = len(AAdict2["divisions"])
    if AAdict1["weekBounds"] == AAdict2["weekBounds"] and numberOfDivisions1 == numberOfDivisions2 and set(
            AAdict1["cursus"]) == set(AAdict2["cursus"]) and numberOfDivisions1%2 == 0:
        for d in range(numberOfDivisions1):
            for v in range(len(AAdict1["divisions"][0])):
                model.add(cp.start_at_start(AAdict1["divisions"][d][v], AAdict2["divisions"][numberOfDivisions2 - 1 - d][v]))
    else:
        print("The 2 AAs don't match (number of divisions or week bounds or cursus).")

def fixedSlots(model, AAdict, fixedDay, fixedSlot, constants):
    numberOfIntervalVariables = len(AAdict["divisions"][0])
    startWeek = math.floor((AAdict["weekBounds"][0] - 1) / constants["segmentSize"])
    endWeek = math.ceil(AAdict["weekBounds"][1] / constants["segmentSize"])
    if endWeek - startWeek == numberOfIntervalVariables and 1 <= fixedDay <= constants["days"] and 1 <= fixedSlot <= constants["slots"]:
        for index,intervalVariable in enumerate(AAdict["divisions"][0]):
            model.add(cp.start_of(intervalVariable) == index * constants["days"] * constants["slots"] + (fixedDay - 1) * constants["slots"] + fixedSlot - 1)
    else:
        print("The AA doesn't match (incorrect number of interval variables or incorrect day/slot).")