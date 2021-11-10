import math
import data.io as TFEdata
import variables as TFEvariables
import docplex.cp.model as cp
import itertools

def longIntervalVariablesIntegrity(model, lessonDict, constants):
    firstOrThirdSlotOnlyFunction = cp.CpoStepFunction(steps=[(i,1 if i%2 == 0 else 0) for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            for intervalVariable in variablesOfDivision:
                model.add(cp.forbid_start(interval=intervalVariable,function=firstOrThirdSlotOnlyFunction))

def morningSlotConstraint(model, lessonDict, constants, cursusWhitelist=None):
    morningOnlyFunction = cp.CpoStepFunction(steps=[(i,1 if i%4 < 2 else 0) for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
    for AA in lessonDict.values():
        if cursusWhitelist is not None and not any(cursus in AA["cursus"] for cursus in cursusWhitelist):
            continue
        for variablesOfDivision in AA["divisions"]:
            for intervalVariable in variablesOfDivision:
                model.add(cp.forbid_start(interval=intervalVariable,function=morningOnlyFunction))

def notOverlappingConstraint(model, entityIntervalVariables):
    for intervalVariables in entityIntervalVariables.values():
        model.add(cp.no_overlap(intervalVariables))

def multipliedVariablesInSameSegmentConstraint(model, lessonDict, constants):
    for AA in lessonDict.values():
        numberOfDivisions = len(AA["divisions"])
        numberOfLessons = len(AA["divisions"][0])
        if numberOfDivisions != 1:
            for j in range(numberOfLessons):
                multipliedVariables = [AA["divisions"][i][j] for i in range(numberOfDivisions)]
                for intervalVariable1,intervalVariable2 in itertools.combinations(multipliedVariables,2):
                    model.add(cp.trunc(cp.start_of(intervalVariable1) / (constants["days"] * constants["slots"])) ==
                              cp.trunc(cp.start_of(intervalVariable2) / (constants["days"] * constants["slots"])))

def maxGapBetweenMultipliedVariables(model, lessonDict, constants):
    for AA in lessonDict.values():
        numberOfDivisions = len(AA["divisions"])
        numberOfLessons = len(AA["divisions"][0])
        if numberOfDivisions != 1:
            for j in range(numberOfLessons):
                multipliedVariables = [AA["divisions"][i][j] for i in range(numberOfDivisions)]
                for intervalVariable1,intervalVariable2 in itertools.combinations(multipliedVariables,2):
                    model.add(constants["gap"] >= cp.max(cp.start_of(intervalVariable1) - cp.end_of(intervalVariable2),
                                                         cp.start_of(intervalVariable2) - cp.end_of(intervalVariable1)))

def cursusUnavailabilityConstraint(model, cursusGroups, groupsIntervalVariables, constants):
    datasetCursusUnavailabilities = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Cursus")
    unavailabilityFunctions = {}

    for rowCursusUnavailabilities in datasetCursusUnavailabilities.itertuples():
        listOfGroups = cursusGroups.getGroups([rowCursusUnavailabilities.cursus])
        startValue = math.trunc((rowCursusUnavailabilities.weekStart - 1)
                                / constants["segmentSize"]) * constants["days"] * constants["slots"] \
                     + (rowCursusUnavailabilities.dayStart - 1) * constants["slots"] \
                     + rowCursusUnavailabilities.slotStart - 1
        endValue = math.trunc((rowCursusUnavailabilities.weekEnd - 1)
                              / constants["segmentSize"]) * constants["days"] * constants["slots"] \
                   + (rowCursusUnavailabilities.dayEnd - 1) * constants["slots"] \
                   + rowCursusUnavailabilities.slotEnd
        for group in listOfGroups:
            if group not in unavailabilityFunctions:
                unavailabilityFunctions[group] = cp.CpoStepFunction()
                unavailabilityFunctions[group].set_value(0, int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]), 100)
            unavailabilityFunctions[group].set_value(startValue,endValue,0)

    for group,unavailabilityFunction in unavailabilityFunctions.items():
        if group in groupsIntervalVariables:
            for intervalVariable in groupsIntervalVariables[group]:
                model.add(cp.forbid_extent(intervalVariable,unavailabilityFunction))

def teachersUnavailabilityConstraint(model, teachersIntervalVariables, constants):
    datasetTeachersUnavailabilities = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Teachers")
    unavailabilityFunctions = {}

    for rowTeacherUnavailabilities in datasetTeachersUnavailabilities.itertuples():
        startValue = math.trunc((rowTeacherUnavailabilities.weekStart - 1)
                                / constants["segmentSize"]) * constants["days"] * constants["slots"] \
                     + (rowTeacherUnavailabilities.dayStart - 1) * constants["slots"] \
                     + rowTeacherUnavailabilities.slotStart - 1
        endValue = math.trunc((rowTeacherUnavailabilities.weekEnd - 1)
                              / constants["segmentSize"]) * constants["days"] * constants["slots"] \
                   + (rowTeacherUnavailabilities.dayEnd - 1) * constants["slots"] \
                   + rowTeacherUnavailabilities.slotEnd
        if rowTeacherUnavailabilities.teacher not in unavailabilityFunctions:
            unavailabilityFunctions[rowTeacherUnavailabilities.teacher] = cp.CpoStepFunction()
            unavailabilityFunctions[rowTeacherUnavailabilities.teacher].set_value(0, int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]), 100)
        unavailabilityFunctions[rowTeacherUnavailabilities.teacher].set_value(startValue, endValue, 0)

    for teacher, unavailabilityFunction in unavailabilityFunctions.items():
        if teacher in teachersIntervalVariables:
            for intervalVariable in teachersIntervalVariables[teacher]:
                model.add(cp.forbid_extent(intervalVariable, unavailabilityFunction))

def daysOffUnavailabilityConstraint(model, lessonDict, constants):
    datasetDaysOff = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Breaks")
    unavailabilityFunction = cp.CpoStepFunction()
    unavailabilityFunction.set_value(0, int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]), 100)

    for rowDayOff in datasetDaysOff.itertuples():
        startValue = math.trunc((rowDayOff.weekStart - 1) / constants["segmentSize"]) * constants["days"] * constants["slots"] \
                     + (rowDayOff.dayStart - 1) * constants["slots"] \
                     + rowDayOff.slotStart - 1
        endValue = math.trunc((rowDayOff.weekEnd - 1) / constants["segmentSize"]) * constants["days"] * constants["slots"] \
                   + (rowDayOff.dayEnd - 1) * constants["slots"] \
                   + rowDayOff.slotEnd
        unavailabilityFunction.set_value(startValue, endValue, 0)

    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            for intervalVariable in variablesOfDivision:
                model.add(cp.forbid_extent(intervalVariable,unavailabilityFunction))

def orderingIntervalVariablesConstraint(model, lessonDict):
    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            for i in range(len(variablesOfDivision)-1):
                model.add(cp.end_before_start(variablesOfDivision[i],variablesOfDivision[i+1]))

def segmentBoundsConstraint(model, lessonDict, constants):
    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            modelSegmentBounds = (math.floor((AA["weekBounds"][0]-1) / constants["segmentSize"]),
                               math.ceil(AA["weekBounds"][1] / constants["segmentSize"]))
            if modelSegmentBounds[0] != 0:
                for intervalVariable in variablesOfDivision:
                    model.add(cp.start_of(intervalVariable) >= modelSegmentBounds[0] * constants["days"] * constants["slots"])
            if modelSegmentBounds[1] != constants["weeks"]/constants["segmentSize"]:
                for intervalVariable in variablesOfDivision:
                    model.add(cp.end_of(intervalVariable) <= modelSegmentBounds[1] * constants["days"] * constants["slots"])


def spreadIntervalVariablesOverSegments(model, lessonDict, constants):
    totalNumberOfSegments = int(constants["weeks"] / constants["segmentSize"])
    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            modelSegmentBounds = (math.floor((AA["weekBounds"][0] - 1) / constants["segmentSize"]),
                                  math.ceil(AA["weekBounds"][1] / constants["segmentSize"]))
            sizeOfFullSequence = modelSegmentBounds[1]-modelSegmentBounds[0]
            numberOfFullSequences = math.trunc(len(variablesOfDivision)/sizeOfFullSequence)
            sizeOfFloatingSequence = int(len(variablesOfDivision)%sizeOfFullSequence)
            for i in range(numberOfFullSequences):
                for j in range(sizeOfFullSequence):
                    model.add(cp.start_of(variablesOfDivision[i * sizeOfFullSequence + j])
                              >= (modelSegmentBounds[0] + j) * constants["days"] * constants["slots"])
                    model.add(cp.end_of(variablesOfDivision[i * sizeOfFullSequence + j])
                              <= (modelSegmentBounds[0] + j + 1) * constants["days"] * constants["slots"])
                    if i != numberOfFullSequences - 1:
                        model.add(cp.end_before_start(variablesOfDivision[i * sizeOfFullSequence + j],
                                                      variablesOfDivision[(i + 1) * sizeOfFullSequence + j]))

            for i in range(sizeOfFloatingSequence):
                if i != sizeOfFloatingSequence-1:
                    model.add(cp.trunc(cp.start_of(variablesOfDivision[numberOfFullSequences*sizeOfFullSequence+i])
                                       / (constants["days"] * constants["slots"]))
                              == cp.trunc(cp.start_of(variablesOfDivision[numberOfFullSequences * sizeOfFullSequence + i + 1])
                                          / (constants["days"] * constants["slots"])) - 1)
                if modelSegmentBounds[0] != 0:
                    model.add(cp.start_of(variablesOfDivision[numberOfFullSequences*sizeOfFullSequence+i])
                              >= modelSegmentBounds[0] * constants["days"] * constants["slots"])
                if modelSegmentBounds[1] != totalNumberOfSegments:
                    model.add(cp.end_of(variablesOfDivision[numberOfFullSequences*sizeOfFullSequence+i])
                              <= modelSegmentBounds[1] * constants["days"] * constants["slots"])
            if sizeOfFloatingSequence != 0 and numberOfFullSequences != 0:
                numberOfScenarios = sizeOfFullSequence - sizeOfFloatingSequence + 1
                scenarios = []
                for i in range(numberOfScenarios):
                    constraintsOfScenario = []
                    for j in range(sizeOfFloatingSequence):
                        constraintsOfScenario.append((cp.end_of(variablesOfDivision[(numberOfFullSequences-1)*sizeOfFullSequence+i+j])
                                                      <= cp.start_of(variablesOfDivision[numberOfFullSequences*sizeOfFullSequence+j])))
                        constraintsOfScenario.append((cp.start_of(variablesOfDivision[numberOfFullSequences*sizeOfFullSequence+j])
                                                      >= (modelSegmentBounds[0]+i+j) * constants["days"] * constants["slots"]))
                        constraintsOfScenario.append((cp.end_of(variablesOfDivision[numberOfFullSequences*sizeOfFullSequence+j])
                                                      <= (modelSegmentBounds[0]+i+j+1) * constants["days"] * constants["slots"]))
                    scenarios.append(cp.logical_and(constraintsOfScenario))
                model.add(cp.logical_or(scenarios))

def strictRegularityConstraint(model, lessonDict, constants):
    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            sequences = TFEvariables.splitVariablesInSequences(variablesOfDivision, constants["fullSequenceSize"])
            for variablesOfSequence in sequences:
                for i in range(len(variablesOfSequence)-1):
                    model.add(cp.start_at_start(variablesOfSequence[i], variablesOfSequence[i + 1], delay=20))

def breakSymmetryBetweenFullSequences(model, lessonDict, constants):
    for AA in lessonDict.values():
        for variablesOfDivision in AA["divisions"]:
            sequences = TFEvariables.splitVariablesInSequences(variablesOfDivision, constants["fullSequenceSize"])
            fullSequences = [spread for spread in sequences if len(spread) == constants["fullSequenceSize"]]
            for i in range(len(fullSequences)-1):
                for j in range(len(fullSequences[0])):
                    model.add(cp.end_before_start(fullSequences[i][j],fullSequences[i+1][j]))

def lecturesBeforeConstraint(model, lecturesDict, listOfAfterLessonsDict, AAset, constants):
    for idAA in AAset:
        if idAA in lecturesDict:
            modelWeekBoundsLecture = (math.floor((lecturesDict[idAA]["weekBounds"][0] - 1) / constants["segmentSize"]),
                                      math.ceil(lecturesDict[idAA]["weekBounds"][1] / constants["segmentSize"]))
            sizeOfFullSequenceLecture = modelWeekBoundsLecture[1] - modelWeekBoundsLecture[0]
            for variablesOfDivisionLecture in lecturesDict[idAA]["divisions"]:
                numberOfFullSequencesLecture = math.trunc(len(variablesOfDivisionLecture) / sizeOfFullSequenceLecture)
                sizeOfFloatingSequenceLecture = int(len(variablesOfDivisionLecture) % sizeOfFullSequenceLecture)
                for afterLessonDict in listOfAfterLessonsDict:
                    if idAA in afterLessonDict:
                        modelWeekBoundsAfterLesson = (math.floor((afterLessonDict[idAA]["weekBounds"][0] - 1) / constants["segmentSize"]),
                                                      math.ceil(afterLessonDict[idAA]["weekBounds"][1] / constants["segmentSize"]))
                        sizeOfFullSequenceAfterLesson = modelWeekBoundsAfterLesson[1] - modelWeekBoundsAfterLesson[0]
                        if (modelWeekBoundsLecture[0] >= modelWeekBoundsAfterLesson[1]
                                or modelWeekBoundsAfterLesson[0] >= modelWeekBoundsLecture[1]):
                            continue
                        else:
                            segmentsIntersection = (max(modelWeekBoundsLecture[0],modelWeekBoundsAfterLesson[0]),
                                                    min(modelWeekBoundsLecture[1],modelWeekBoundsAfterLesson[1]))
                            for variablesOfDivisionAfterLesson in afterLessonDict[idAA]["divisions"]:
                                numberOfFullSequencesAfterLesson = math.trunc(len(variablesOfDivisionAfterLesson) / sizeOfFullSequenceAfterLesson)
                                sizeOfFloatingSequenceAfterLesson = int(len(variablesOfDivisionAfterLesson) % sizeOfFullSequenceAfterLesson)

                                if sizeOfFloatingSequenceLecture == 0:
                                    if sizeOfFloatingSequenceAfterLesson == 0 or numberOfFullSequencesAfterLesson != 0:
                                        for i in range(segmentsIntersection[0],segmentsIntersection[1]):
                                            model.add(cp.end_before_start(variablesOfDivisionLecture[(numberOfFullSequencesLecture-1)*sizeOfFullSequenceLecture+i-modelWeekBoundsLecture[0]],
                                                                          variablesOfDivisionAfterLesson[i-modelWeekBoundsAfterLesson[0]]))
                                    else:
                                        numberOfScenariosAfterLesson = sizeOfFullSequenceAfterLesson - sizeOfFloatingSequenceAfterLesson + 1
                                        overlapPossibilities = []
                                        for i in range(numberOfScenariosAfterLesson):
                                            overlapPossibilities.append([(lectureIndex,afterLessonIndex) for lectureIndex in range(sizeOfFullSequenceLecture) for afterLessonIndex in range(sizeOfFloatingSequenceAfterLesson)
                                                                         if lectureIndex + modelWeekBoundsLecture[0] == afterLessonIndex + modelWeekBoundsAfterLesson[0] + i])
                                        scenarios = []
                                        for overlap in overlapPossibilities:
                                            constraintsOfScenario = []
                                            if len(overlap) != 0:
                                                for lectureIndex,afterLessonIndex in overlap:
                                                    constraintsOfScenario.append((cp.end_of(variablesOfDivisionLecture[(numberOfFullSequencesLecture-1)*sizeOfFullSequenceLecture+lectureIndex])
                                                                                  <= cp.start_of(variablesOfDivisionAfterLesson[afterLessonIndex])))
                                                    constraintsOfScenario.append((cp.end_of(variablesOfDivisionAfterLesson[afterLessonIndex])
                                                                                  <= (lectureIndex + 1 + modelWeekBoundsLecture[0]) * constants["days"] * constants["slots"]))
                                                    constraintsOfScenario.append((cp.start_of(variablesOfDivisionAfterLesson[afterLessonIndex])
                                                                                  >= (lectureIndex + modelWeekBoundsLecture[0]) * constants["days"] * constants["slots"]))
                                                scenarios.append(cp.logical_and(constraintsOfScenario))
                                        model.add(cp.logical_or(scenarios))

                                else:
                                    if sizeOfFloatingSequenceAfterLesson == 0 or numberOfFullSequencesAfterLesson != 0:
                                        numberOfScenariosLecture = sizeOfFullSequenceLecture - sizeOfFloatingSequenceLecture + 1
                                        overlapPossibilities = []
                                        for i in range(numberOfScenariosLecture):
                                            overlapPossibilities.append([(lectureIndex, afterLessonIndex) for lectureIndex in range(sizeOfFloatingSequenceLecture) for afterLessonIndex in range(sizeOfFullSequenceAfterLesson)
                                                                         if lectureIndex + modelWeekBoundsLecture[0] + i == afterLessonIndex + modelWeekBoundsAfterLesson[0]])
                                        scenarios = []
                                        for overlap in overlapPossibilities:
                                            constraintsOfScenario = []
                                            if len(overlap) != 0:
                                                for lectureIndex, afterLessonIndex in overlap:
                                                    constraintsOfScenario.append((cp.end_of(variablesOfDivisionLecture[numberOfFullSequencesLecture * sizeOfFullSequenceLecture + lectureIndex])
                                                                                  <= cp.start_of(variablesOfDivisionAfterLesson[afterLessonIndex])))
                                                    constraintsOfScenario.append((cp.end_of(variablesOfDivisionLecture[numberOfFullSequencesLecture * sizeOfFullSequenceLecture + lectureIndex])
                                                                                  <= (afterLessonIndex+1+modelWeekBoundsAfterLesson[0]) * constants["days"] * constants["slots"]))
                                                    constraintsOfScenario.append((cp.start_of(variablesOfDivisionLecture[numberOfFullSequencesLecture * sizeOfFullSequenceLecture + lectureIndex])
                                                                                  >= (afterLessonIndex+modelWeekBoundsAfterLesson[0]) * constants["days"] * constants["slots"]))
                                                scenarios.append(cp.logical_and(constraintsOfScenario))
                                        model.add(cp.logical_or(scenarios))
                                        if numberOfFullSequencesLecture != 0:
                                            for i in range(segmentsIntersection[0], segmentsIntersection[1]):
                                                model.add(cp.end_before_start(variablesOfDivisionLecture[(numberOfFullSequencesLecture - 1) * sizeOfFullSequenceLecture + i - modelWeekBoundsLecture[0]],
                                                                              variablesOfDivisionAfterLesson[i - modelWeekBoundsAfterLesson[0]]))
                                    else:
                                        numberOfScenariosLecture = sizeOfFullSequenceLecture - sizeOfFloatingSequenceLecture + 1
                                        numberOfScenariosAfterLesson = sizeOfFullSequenceAfterLesson - sizeOfFloatingSequenceAfterLesson + 1
                                        overlapPossibilities = {}
                                        for i in range(numberOfScenariosLecture):
                                            for j in range(numberOfScenariosAfterLesson):
                                                possibilities = [(lectureIndex,afterLessonIndex) for lectureIndex in range(sizeOfFloatingSequenceLecture) for afterLessonIndex in range(sizeOfFloatingSequenceAfterLesson)
                                                                 if lectureIndex + modelWeekBoundsLecture[0] + i == afterLessonIndex + modelWeekBoundsAfterLesson[0] + j]
                                                overlapPossibilities[(i+modelWeekBoundsLecture[0],j+modelWeekBoundsAfterLesson[0])] = possibilities
                                        scenarios = []
                                        for segmentsKey,overlap in overlapPossibilities.items():
                                            constraintsOfScenario = []
                                            for lectureIndex,afterLessonIndex in overlap:
                                                constraintsOfScenario.append((cp.end_of(variablesOfDivisionLecture[numberOfFullSequencesLecture * sizeOfFullSequenceLecture + lectureIndex])
                                                                              <= cp.start_of(variablesOfDivisionAfterLesson[afterLessonIndex])))
                                            for i in range(sizeOfFloatingSequenceLecture):
                                                constraintsOfScenario.append((cp.end_of(variablesOfDivisionLecture[numberOfFullSequencesLecture * sizeOfFullSequenceLecture + i])
                                                                              <= (segmentsKey[0] + i + 1) * constants["days"] * constants["slots"]))
                                                constraintsOfScenario.append((cp.start_of(variablesOfDivisionLecture[numberOfFullSequencesLecture * sizeOfFullSequenceLecture + i])
                                                                              >= (segmentsKey[0] + i) * constants["days"] * constants["slots"]))
                                            for i in range(sizeOfFloatingSequenceAfterLesson):
                                                constraintsOfScenario.append((cp.end_of(variablesOfDivisionAfterLesson[i])
                                                                              <= (segmentsKey[1] + i + 1) * constants["days"] * constants["slots"]))
                                                constraintsOfScenario.append((cp.start_of(variablesOfDivisionAfterLesson[i])
                                                                              >= (segmentsKey[1] + i) * constants["days"] * constants["slots"]))
                                                if numberOfFullSequencesLecture != 0 and i + segmentsKey[1] in range(segmentsIntersection[0],segmentsIntersection[1]):
                                                    constraintsOfScenario.append((cp.end_of(variablesOfDivisionLecture[(numberOfFullSequencesLecture - 1) * sizeOfFullSequenceLecture + i + segmentsKey[1] - modelWeekBoundsLecture[0]])
                                                                                  <= cp.start_of(variablesOfDivisionAfterLesson[i])))
                                            scenarios.append(cp.logical_and(constraintsOfScenario))
                                        model.add(cp.logical_or(scenarios))