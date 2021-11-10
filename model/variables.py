import CursusGroups as TFEcursusGroups
import data.io as TFEdata
import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

def generateIntervalVariables(constants):
    """
    Function creating and placing interval variables in appropriate dictionaries

    An interval variable has 2 unknowns (startTime and endTime) and many parameters (length, intensity function, etc.).
    CP Optimizer supports interesting scheduling constraints with this type of variable
    (more information : https://fr.slideshare.net/PhilippeLaborie/introduction-to-cp-optimizer-for-scheduling)

    Lecture and exercise lessons are short (2h) and thus have a length of 1 (1 unit of time = 2 hours)
    TP and projects lessons are long (4h) and thus have a length of 2

    lecturesDict, exercisesDict, tpsDict and projectsDict (all called "lessonDict" below) contain interval variables and information about the AA :
    A lessonDict is a dictionary with :
        - key = (string) AA code (i.e. "I-MARO-020")
        - value = a dictionary with 3 key-values:
            - 1 = "weekBounds" : (tuple) (weekStart,weekEnd) week number of start and end of the AA (from 1 to constants["weeks"])
            - 2 = "divisions" : (list) list of interval variables per division
            - 3 = "cursus" : (list) list of cursus following the AA

    groupsIntervalVariables, teachersIntervalVariables and roomsIntervalVariables are defaultdict(list)
    The structure is :
        - key = resource name
        - value = all interval variables where the resource is needed
    A defaultdict(list) means that a new entry will be initialised with a list

    cursusGroups is an object of the CursusGroups class with useful information about groups and divisions
    AAset is a set with all AA encountered during the creation of interval variables

    :param constants: (dict) dictionary with information about the model to build. Mandatory keys are :
        - fileDataset
        - weeks
        - days
        - slots
        - segmentSize
        - quadri
        - cursus
        - roundUp
        - groupAuto
    :return: lecturesDict,exercisesDict,tpsDict,projectsDict,
                groupsIntervalVariables,teachersIntervalVariables,roomsIntervalVariables,
                cursusGroups,AAset
    """
    lecturesDict = {}
    exercisesDict = {}
    tpsDict = {}
    projectsDict = {}

    groupsIntervalVariables = defaultdict(list)
    teachersIntervalVariables = defaultdict(list)
    roomsIntervalVariables = defaultdict(list)

    cursusGroups = TFEcursusGroups.CursusGroups(constants["fileDataset"])
    AAset = set()

    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])

    # count the number of added/deleted lessons in order to fit weeks in segments
    delta = 0

    datasetAA = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "TFE")
    # datasetAA.itertuples() creates a iterable where each item is a row of the datasetAA DataFrame
    # each attribute of a row can be accessed as a property (rowAA.x returns the "x" column of rowAA)
    # more details about each attribute are available in README.md
    for rowAA in datasetAA.itertuples():

        # the "cursus" field in dataset contains all cursus following the AA, separated with ","
        listOfCursus = rowAA.cursus.split(",")
        # the AA is skipped if there is no cursus (following the AA) matching "constants["cursus"]"
        if not any(constants["cursus"][cursus] is True for cursus in listOfCursus):
            continue

        # the AA is skipped if it has been already processed
        if rowAA.id in AAset:
            continue
        AAset.add(rowAA.id)

        # creating interval variables for lectures
        # an AA has lectures iff its "lectureHours" field in the dataset has a value
        if not pd.isna(rowAA.lectureHours):
            # cursusGroups.getGroups() generates all the groups' names from multiple cursus in "listOfCursus"
            listOfGroups = cursusGroups.getGroups(listOfCursus)
            lecturesDict[rowAA.id] = {
                "weekBounds": (rowAA.lectureWeekStart,rowAA.lectureWeekEnd),
                "divisions": [
                    [] # since a lecture is given once, all the groups belong to the same and unique division
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment
            # assumption : a lecture lasts for 2 hours
            trueNumberOfLessons = math.ceil(rowAA.lectureHours / 2)
            # the true number of lessons is rounded up or down (depending on the boolean "constants["roundUp"]") in order to fit in segments
            # i.e. 7 lessons in segments of size 3 will be rounded to 9 lessons (rounded up) or 6 lessons (rounded down)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]

            # cp.interval_var_list creates a list of "asize" interval variables
            lectureIntervalVariables = cp.interval_var_list(asize=modelNumberOfLessons, # "modelNumberOfLessons" interval variables are created in one list
                                                    start=(0, totalSlots - 1), # the last start time for all lecture interval variables is "totalSlots-1"
                                                    end=(1, totalSlots), # the first end time for all lecture interval variables is "1"
                                                    size=1, # the size of all lecture interval variables is 1
                                                    length=1, # the length of all lecture interval variables is 1
                                                    name=rowAA.id + "_lec") # the 3_rd element of the list of the I-XXX-000 lecture will have the name "I-XXX-000_lec_2"

            # all the interval variables are added to the first and only division for the AA
            lecturesDict[rowAA.id]["divisions"][0].extend(lectureIntervalVariables)

            # all the interval variables are added to corresponding groups, teachers and rooms dictionaries

            for group in listOfGroups:
                groupsIntervalVariables[group].extend(lectureIntervalVariables)
            # the "lectureTeachers" field in dataset contains all teachers for AA' lectures, separated with ","
            for teacher in rowAA.lectureTeachers.split(","):
                teachersIntervalVariables[teacher].extend(lectureIntervalVariables)
            # the "lectureRooms" field in dataset contains all rooms for AA' lectures, separated with ","
            for room in rowAA.lectureRooms.split(","):
                roomsIntervalVariables[room].extend(lectureIntervalVariables)

        # creating interval variables for exercises
        # an AA has exercises iff its "exerciseHours" field in the dataset has a value
        if not pd.isna(rowAA.exerciseHours):
            # the following function generates balanced divisions (automatically or not depending on the boolean "constants["groupAuto"]")
            # it first gets all groups in all cursus contained in "listOfCursus" and returns a dict with key = group ; value = index of division
            # i.e. two divisions with the cursus "BA1" containing "BA1_A" and "BA1_B" groups, one in each division will result in :
            # listOfDivisions = {"BA1_A": 0, "BA1_B": 1}
            listOfDivisions = cursusGroups.generateBalancedDivisions(listOfCursus, rowAA.exerciseDivisions, constants["groupAuto"])
            exercisesDict[rowAA.id] = {
                "weekBounds": (rowAA.exerciseWeekStart,rowAA.exerciseWeekEnd),
                "divisions": [
                    [] for d in range(rowAA.exerciseDivisions) # an exercise can be multiplied and thus creates "rowAA.exerciseDivisions" divisions
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment (a doubled lesson is counted twice)
            # assumption : an exercise lasts for 2 hours
            trueNumberOfLessons = math.ceil(rowAA.exerciseHours / 2)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += (modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons) * rowAA.exerciseDivisions
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= (trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]) * rowAA.exerciseDivisions

            # the "exerciseTeachers" field in dataset contains all teachers for AA' exercises, separated with ","
            listOfTeachers = rowAA.exerciseTeachers.split(",")
            # the "exerciseRooms" field in dataset contains all rooms for AA' exercises, separated with ","
            listOfRooms = rowAA.exerciseRooms.split(",")
            # each multiplied exercise is an interval variable
            # i.e. for 6 exercises and 2 divisions, 12 interval variables must be created, 6 for each division
            # each interval variable will be added in corresponding lists and dictionaries
            for currentDivisionIndex in range(rowAA.exerciseDivisions):
                for l in range(modelNumberOfLessons):
                    # cp.interval_var creates one interval variable
                    exerciseIntervalVariable = cp.interval_var(start=(0, totalSlots - 1), # the last start time for an exercise interval variable is "totalSlots-1"
                                                       end=(1, totalSlots), # the first end time for an exercise interval variable is "1"
                                                       size=1, # the size of an exercise interval variable is 1
                                                       length=1, # the length of an exercise interval variable is 1
                                                       name=rowAA.id + "_ex_" + str(l) + "_d_" + str(currentDivisionIndex)) # the 3_rd exercise interval variable of I-XXX-000 in the 1_st division will have the name "I-XXX-000_ex_2_d_0"

                    # the interval variable is added to the current division
                    exercisesDict[rowAA.id]["divisions"][currentDivisionIndex].append(exerciseIntervalVariable)

                    # the currentDivisionIndex refers to the division currently built in the loop
                    # listOfDivisions contains index of division with all groups within this division
                    # the interval variable is thus placed in the right list of intervals when currentDivisionIndex == divisionIndex

                    # i.e. when listOfDivisions = {"BA1_A": 0, "BA1_B": 1} and currentDivisionIndex = 0,
                    # that means we are building variables for the first division, thus these must only be placed in the "BA1_A" entry of grouIntervalVariables dict
                    for group,divisionIndex in listOfDivisions.items():
                        if divisionIndex == currentDivisionIndex:
                            groupsIntervalVariables[group].append(exerciseIntervalVariable)

                    # when an exercise must be "split", it means that only a subset of teachers and rooms are planned for this lesson
                    # rowAA.exerciseSplit = n : n teachers and n rooms per multiplied lesson
                    # the teachers and rooms planned in lessons are determined in a cyclic way
                    # i.e. for 5 multiplied lessons, 4 rooms (R1, R2, R3, R4) and exerciseSplit = 2 :
                    #   - the subset R1,R2 will be planned for the first, third and fifth division
                    #   - the subset R3,R4 will be planned for the second and fourth division
                    if rowAA.exerciseSplit != 0:
                        # for teachers
                        # numberSubsets = number of subsets of teachers
                        numberSubsets = math.ceil(len(listOfTeachers) / rowAA.exerciseSplit)
                        # sizeLastSubset = number of teachers in the last subset
                        sizeLastSubset = len(listOfTeachers) % rowAA.exerciseSplit if rowAA.exerciseSplit != 1 else 1
                        # currentSubsetIndex = index of the current subset of teachers
                        currentSubsetIndex = currentDivisionIndex % numberSubsets
                        # sizeCurrentSubset = number of teachers in the current subset (= exerciseSplit or sizeLastSubset for the last subset)
                        sizeCurrentSubset = rowAA.exerciseSplit if currentSubsetIndex != numberSubsets - 1 else sizeLastSubset
                        for c in range(sizeCurrentSubset):
                            # listOfTeachers contains all the teachers
                            # currentSubsetIndex * rowAA.exerciseSplit = shift to the current subset of teachers
                            # currentSubsetIndex * rowAA.exerciseSplit + c = goes through the subset
                            teachersIntervalVariables[listOfTeachers[currentSubsetIndex * rowAA.exerciseSplit + c]].append(
                                exerciseIntervalVariable)
                        # for rooms
                        numberSubsets = math.ceil(len(listOfRooms) / rowAA.exerciseSplit)
                        sizeLastSubset = len(listOfRooms) % rowAA.exerciseSplit if rowAA.exerciseSplit != 1 else 1
                        currentSubsetIndex = currentDivisionIndex % numberSubsets
                        sizeCurrentSubset = rowAA.exerciseSplit if currentSubsetIndex != numberSubsets - 1 else sizeLastSubset
                        for c in range(sizeCurrentSubset):
                            roomsIntervalVariables[listOfRooms[currentSubsetIndex * rowAA.exerciseSplit + c]].append(
                                exerciseIntervalVariable)

                    # rowAA.exerciseSplit = 0 : no split (all teachers and rooms are planned for all interval variables)
                    else:
                        for teacher in listOfTeachers:
                            teachersIntervalVariables[teacher].append(exerciseIntervalVariable)
                        for room in listOfRooms:
                            roomsIntervalVariables[room].append(exerciseIntervalVariable)

        # creating interval variables for tp
        # an AA has tp iff its "tpHours" field in the dataset has a value
        if not pd.isna(rowAA.tpHours):
            # same as exercise divisions
            listOfDivisions = cursusGroups.generateBalancedDivisions(listOfCursus, rowAA.tpDivisions, constants["groupAuto"])
            tpsDict[rowAA.id] = {
                "weekBounds": (rowAA.tpWeekStart,rowAA.tpWeekEnd),
                "divisions": [
                    [] for d in range(rowAA.tpDivisions) # a tp can be multiplied and thus creates "rowAA.tpDivisions" divisions
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment (a doubled lesson is counted twice)
            # a tp lasts for 3 or 4 hours (rowAA.tpDuration)
            trueNumberOfLessons = int(rowAA.tpHours / rowAA.tpDuration)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += (modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons) * rowAA.tpDivisions
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= (trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]) * rowAA.tpDivisions

            # each multiplied exercise is an interval variable
            # i.e. for 6 tps and 2 divisions, 12 interval variables must be created, 6 for each division
            # each interval variable will be added in corresponding lists and dictionaries
            for currentDivisionIndex in range(rowAA.tpDivisions):
                for l in range(modelNumberOfLessons):
                    # cp.interval_var creates one interval variable
                    tpIntervalVariable = cp.interval_var(start=(0, totalSlots - 2), # the last start time for a tp interval variable is "totalSlots-2"
                                                 end=(2, totalSlots), # the first end time for a tp interval variable is "2"
                                                 size=2, # the size of a tp interval variable is 2
                                                 length=2, # the length of a tp interval variable is 2
                                                 name=rowAA.id + "_tp_" + str(l) + "_d_" + str(currentDivisionIndex)) # the 2_nd tp interval variable of I-XXX-000 in the 3_rd division will have the name "I-XXX-000_tp_1_d_2"

                    # the interval variable is added to the current division
                    tpsDict[rowAA.id]["divisions"][currentDivisionIndex].append(tpIntervalVariable)

                    # same as exercises
                    for group, divisionIndex in listOfDivisions.items():
                        if divisionIndex == currentDivisionIndex:
                            groupsIntervalVariables[group].append(tpIntervalVariable)

                    # all interval variables are added to corresponding teachers and rooms dictionaries

                    # the "tpTeachers" field in dataset contains all teachers for AA' tps, separated with ","
                    for teacher in rowAA.tpTeachers.split(","):
                        teachersIntervalVariables[teacher].append(tpIntervalVariable)
                    # the "tpRooms" field in dataset contains all rooms for AA' tps, separated with ","
                    for room in rowAA.tpRooms.split(","):
                        roomsIntervalVariables[room].append(tpIntervalVariable)

        # creating interval variables for projects
        # an AA has projects iff its "projectHours" field in the dataset has a value
        if not pd.isna(rowAA.projectHours):
            # cursusGroups.getGroups() generates all the groups' names from multiple cursus in "listOfCursus"
            listOfGroups = cursusGroups.getGroups(listOfCursus)
            projectsDict[rowAA.id] = {
                "weekBounds": (rowAA.projectWeekStart,rowAA.projectWeekEnd),
                "divisions": [
                    [] # since a project is given once, all the groups belong to the same and unique division
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment
            # a project lasts for 3 or 4 hours (rowAA.projectDuration)
            trueNumberOfLessons = int(rowAA.projectHours / rowAA.projectDuration)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]

            # cp.interval_var_list creates a list of "asize" interval variables
            projectIntervalVariables = cp.interval_var_list(asize=modelNumberOfLessons, # "modelNumberOfLessons" interval variables are created in one list
                                                    start=(0,totalSlots-2), # the last start time for a project interval variable is "totalSlots-2"
                                                    end=(2,totalSlots), # the first end time for a project interval variable is "2"
                                                    size=2, # the size of a project interval variable is 2
                                                    length=2, # the length of a project interval variable is 2
                                                    name=rowAA.id + "_pr") # the 3_rd element of the list of the I-XXX-000 project will have the name "I-XXX-000_pr_2"

            # all the interval variables are added to the first and only division for the AA
            projectsDict[rowAA.id]["divisions"][0].extend(projectIntervalVariables)

            # all the interval variables are added to corresponding groups and teachers dictionaries (no room for projects)
            for group in listOfGroups:
                groupsIntervalVariables[group].extend(projectIntervalVariables)
            # the "projectTeachers" field in dataset contains all teachers for AA' projects, separated with ","
            for teacher in rowAA.projectTeachers.split(","):
                teachersIntervalVariables[teacher].extend(projectIntervalVariables)

    print("delta", delta)
    return lecturesDict,exercisesDict,tpsDict,projectsDict,\
           groupsIntervalVariables,teachersIntervalVariables,roomsIntervalVariables,\
           cursusGroups,AAset

def generateCharleroiIntervalVariables(model, teachersIntervalVariables, roomsIntervalVariables, constants):
    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    numberOfSegments = int(constants["weeks"] / constants["segmentSize"])
    longVariableFunction = cp.CpoStepFunction(steps=[(i, 1 if i % 4 == 0 else 0) for i in range(
        int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
    shortVariableFunction = cp.CpoStepFunction(steps=[(i, 1 if i % 2 == 0 else 0) for i in range(
        int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])

    datasetCharleroiTeachers = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Charleroi")
    for rowTeacher in datasetCharleroiTeachers.itertuples():
        listOfAA = rowTeacher.AA.split(",")
        variableName = listOfAA[0]
        if len(listOfAA) != 1:
            variableName += ",..."

        numberLongVariablesPerWeek = math.trunc(len(listOfAA) / 2)
        hasShortVariablePerWeek = len(listOfAA)%2
        charleroiVariables = []
        for v in range(numberLongVariablesPerWeek):
            for s in range(numberOfSegments):
                longCharleroiIntervalVariable = cp.interval_var(start=(0,totalSlots-4),
                                                        end=(4,totalSlots),
                                                        size=4,
                                                        length=4,
                                                        name=variableName+"_ch4_"+str((v*4)+s))
                model.add(cp.forbid_start(interval=longCharleroiIntervalVariable, function=longVariableFunction))
                charleroiVariables.append(longCharleroiIntervalVariable)

                teachersIntervalVariables[rowTeacher.teacher].append(longCharleroiIntervalVariable)
                roomsIntervalVariables[rowTeacher.room].append(longCharleroiIntervalVariable)

        if hasShortVariablePerWeek == 1:
            for s in range(numberOfSegments):
                shortCharleroiIntervalVariable = cp.interval_var(start=(0, totalSlots - 2),
                                                    end=(2, totalSlots),
                                                    size=2,
                                                    length=2,
                                                    name=variableName + "_ch2_" + str((numberLongVariablesPerWeek * 4) + s))
                model.add(cp.forbid_start(interval=shortCharleroiIntervalVariable, function=shortVariableFunction))
                charleroiVariables.append(shortCharleroiIntervalVariable)

                teachersIntervalVariables[rowTeacher.teacher].append(shortCharleroiIntervalVariable)
                roomsIntervalVariables[rowTeacher.room].append(shortCharleroiIntervalVariable)

        for v in range(numberLongVariablesPerWeek):
            for s in range(numberOfSegments):
                model.add(cp.start_of(charleroiVariables[(v * numberOfSegments) + s]) >= s * constants["days"] * constants["slots"])
                model.add(cp.end_of(charleroiVariables[v * numberOfSegments + s]) <= (s + 1) * constants["days"] * constants["slots"])
                if v != numberLongVariablesPerWeek - 1:
                    model.add(cp.end_before_start(charleroiVariables[v * numberOfSegments + s], charleroiVariables[(v + 1) * numberOfSegments + s]))

        if hasShortVariablePerWeek != 0:
            for s in range(numberOfSegments):
                model.add(cp.start_of(charleroiVariables[numberLongVariablesPerWeek * numberOfSegments + s]) >= s * constants["days"] * constants["slots"])
                model.add(cp.end_of(charleroiVariables[numberLongVariablesPerWeek * numberOfSegments + s]) <= (s + 1) * constants["days"] * constants["slots"])

def generateCharleroiFixedIntervalVariables(model, teachersIntervalVariables, roomsIntervalVariables, constants):
    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    datasetCharleroiTeachers = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "CharleroiFixed")

    for rowTeacher in datasetCharleroiTeachers.itertuples():
        variableName = rowTeacher.AA
        realWeekBounds = (rowTeacher.weekStart,rowTeacher.weekEnd)
        modelSegmentBounds = (math.floor((realWeekBounds[0] - 1) / constants["segmentSize"]), math.ceil(realWeekBounds[1] / constants["segmentSize"]))

        for w in range(modelSegmentBounds[0],modelSegmentBounds[1]):
            charleroiIntervalVariable = cp.interval_var(start=(0,totalSlots-2),
                                                end=(2,totalSlots),
                                                size=2,
                                                length=2,
                                                name=variableName+"_ch2_"+str(w))

            teachersIntervalVariables[rowTeacher.teacher].append(charleroiIntervalVariable)
            roomsIntervalVariables[rowTeacher.room].append(charleroiIntervalVariable)

            model.add(cp.start_of(charleroiIntervalVariable) == w * constants["days"] * constants["slots"] + constants["slots"] * (rowTeacher.day - 1) + rowTeacher.slot - 1)

def splitVariablesInSequences(intervalVariables, fullSequenceSize):
    numberOfSequences = math.ceil(len(intervalVariables) / fullSequenceSize)
    sequences = [[] for s in range(numberOfSequences)]
    for v in range(len(intervalVariables)):
        sequences[math.trunc(v / fullSequenceSize)].append(intervalVariables[v])
    return sequences