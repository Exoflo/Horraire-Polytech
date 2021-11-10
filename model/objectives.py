import docplex.cp.model as cp

def avoidAfternoonForShortIntervalVariables(listOfLessonsDict, AAblacklist, constants):
    afternoonPenalty = cp.CpoSegmentedFunction()
    for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])):
        slotPosition = i%4
        if slotPosition == 0:
            afternoonPenalty.set_value(i,i+1,0)
        elif slotPosition == 1:
            afternoonPenalty.set_value(i,i+1,0)
        elif slotPosition == 2:
            afternoonPenalty.set_value(i,i+1,0.5)
        elif slotPosition == 3:
            afternoonPenalty.set_value(i,i+1,1)

    objectiveFunction = cp.sum(
        [cp.start_eval(intervalVariable, afternoonPenalty) for lessonDict in listOfLessonsDict for ID, AA in lessonDict.items() for variablesOfDivision in
         AA["divisions"] for intervalVariable in variablesOfDivision if ID not in AAblacklist])
    return objectiveFunction

def avoidAfternoonForLongIntervalVariables(listOfLessonsDict, AAblacklist, constants):
    afternoonPenalty = cp.CpoSegmentedFunction()
    for i in range(int((constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]) / 2 + 1)):
        slotPosition = i % 2
        if slotPosition == 0:
            afternoonPenalty.set_value(2 * i, 2 * (i + 1), 1)
        elif slotPosition == 1:
            afternoonPenalty.set_value(2 * i, 2 * (i + 1), 0)

    objectiveFunction = cp.sum(
        [cp.end_eval(intervalVariable, afternoonPenalty) for lessonDict in listOfLessonsDict for ID, AA in lessonDict.items() for variablesOfDivision in
         AA["divisions"] for intervalVariable in variablesOfDivision if ID not in AAblacklist])
    return objectiveFunction

def avoidLastSlotForShortIntervalVariables(listOfLessonsDict, AAblacklist, constants):
    lastSlotPenalty = cp.CpoSegmentedFunction()
    for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])):
        slotPosition = i % 4
        if slotPosition == 3:
            lastSlotPenalty.set_value(i, i + 1, 1)

    objectiveFunction = cp.sum(
        [cp.start_eval(intervalVariable, lastSlotPenalty) for lessonDict in listOfLessonsDict for ID, AA in lessonDict.items() for variablesOfDivision in
         AA["divisions"] for intervalVariable in variablesOfDivision if ID not in AAblacklist])
    return objectiveFunction

def spreadIntervalVariables(lecturesDict, exercisesDict, tpsDict, projectsDict, AAset):
    objectiveFunction = 0
    for AA in AAset:
        hasLec = AA in lecturesDict
        hasEx = AA in exercisesDict
        hasTP = AA in tpsDict
        hasPr = AA in projectsDict

        spreadMode = hasLec*1 + hasEx*2 + hasTP*4 + hasPr*8
        if spreadMode == 1:
            objectiveFunction += cp.square(cp.standard_deviation(
                [cp.start_of(lecturesDict[AA][i+1]) - cp.start_of(lecturesDict[AA][i]) for i in
                 range(len(lecturesDict[AA])-1)]))
        elif spreadMode == 2:
            for exerciceIntervals in exercisesDict[AA]:
                objectiveFunction += cp.square(cp.standard_deviation(
                    [cp.start_of(exerciceIntervals[i+1]) - cp.start_of(exerciceIntervals[i]) for i in
                    range(len(exerciceIntervals)-1)]))
        elif spreadMode == 4:
            for tpIntervals in tpsDict[AA]:
                objectiveFunction += cp.square(cp.standard_deviation(
                    [cp.start_of(tpIntervals[i+1]) - cp.start_of(tpIntervals[i]) for i in
                     range(len(tpIntervals)-1)]))
        elif spreadMode == 8:
            objectiveFunction += cp.square(cp.standard_deviation(
                [cp.start_of(projectsDict[AA][i+1]) - cp.start_of(projectsDict[AA][i]) for i in
                 range(len(projectsDict[AA])-1)]))
        else:
            pass
    return objectiveFunction