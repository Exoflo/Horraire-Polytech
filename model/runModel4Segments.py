import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import callbacks as TFEcallbacks
import data.colors as colors
import time
import docplex.cp.model as cp

"""
This script represents the configuration in the sections 7.2.2 and 7.2.3 (divisions/english/rooms)
It is divided in two parts : 
    - SETUP MODEL = All constraints used in the model. Do not change them to get sections 7.2.2 and 7.2.3 results. 
                    Further details are available in the constraints.py module
    - SOLVING AND RESULTS = After solving, results can be displayed or saved. (Un)comment lines to get what you need.
"""

################# SETUP MODEL #################
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Beginning : ",current_time)

print("Building model : ...")
begin = time.time()
model = cp.CpoModel()

"""
"constants" is a dict with all parameters used. Sections 7.2.2 and 7.2.3 results are obtained with parameters in parenthesis : 
    - weeks (12) = number of real weeks
    - days (5) = number of days per week
    - slots (4) = number of slots per day
    - segmentSize (3) = size of a segment (i.e. size of 3 means that each segment represents 3 identical weeks)
    - roundUp (True) = when converting weeks in segments, the number of lessons are rounded up (True) or rounded down (False)
    - cursus (True/False) = dict of cursus included in the model
    - quadri ("Q1") = quadrimester
    - fileDataset (7.2.2 / 7.2.3.divisions "datasetBase.xlsx" ; 
                   7.2.3.english : "datasetAnglais.xlsx" ; 
                   7.2.3.rooms : "datasetAnglaisLocaux.xlsx") = file name of the dataset. Must be placed in the /data folder
    - folderResults (7.2.3.rooms : "4SegmentsStrategies") = folder name where the results will be stored. Must be placed in the /results folder
    - groupAuto (7.2.2 : True ; 7.2.3 : False) = boolean indicating if the divisions are generated automatically considering number of students or not
"""
constants = {
    "weeks":12,
    "days":5,
    "slots":4,
    "segmentSize":3,
    "roundUp": True,
    "cursus": {
        "BA1": True,
        "BA2": False,
        "BA3_CHIM": False,
        "BA3_ELEC": False,
        "BA3_IG": False,
        "BA3_MECA": False,
        "BA3_MIN": False
    },
    "quadri": "Q1",
    "fileDataset": "datasetAnglais.xlsx", #dataset-Base/Anglais/AnglaisLocaux
    "folderResults": "4SegmentsStrategies",
    "groupAuto": False
}

"""
Generates variables and place them in appropriate dict for later use :
    - lecturesDict = (dict) all lecture interval variables divided by AA
    - exercisesDict = (dict) all exercise interval variables divided by AA
    - tpsDict = (dict) all TP interval variables divided by AA
    - projetsDict = (dict) all project interval variables divided by AA
    - groupsIntervalVariables = (dict) all interval variables followed by group
    - teachersIntervalVariables = (dict) all interval variables taught by teacher
    - roomsIntervalVariables = (dict) all interval variables occupied by room
    - cursusGroups = (CursusGroups) object dealing with group data
    - AAset = (set) all AA encountered during the model building
"""
lecturesDict, exercisesDict, tpsDict, projectsDict, \
groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, \
cursusGroups, AAset = TFEvariables.generateIntervalVariables(constants)

# constraint 6.3.4
TFEconstraints.cursusUnavailabilityConstraint(model, cursusGroups, groupsIntervalVariables, constants)
TFEconstraints.teachersUnavailabilityConstraint(model, teachersIntervalVariables, constants)

# constraint 6.3.1
TFEconstraints.longIntervalVariablesIntegrity(model, tpsDict, constants)
TFEconstraints.longIntervalVariablesIntegrity(model, projectsDict, constants)

# constraint 6.3.2
TFEconstraints.notOverlappingConstraint(model, groupsIntervalVariables)
TFEconstraints.notOverlappingConstraint(model, teachersIntervalVariables)
TFEconstraints.notOverlappingConstraint(model, roomsIntervalVariables)

# constraint 6.3.3
TFEconstraints.multipliedVariablesInSameSegmentConstraint(model, exercisesDict, constants)
TFEconstraints.multipliedVariablesInSameSegmentConstraint(model, tpsDict, constants)

# constraint 6.3.9 (6.3.5 included)
TFEconstraints.spreadIntervalVariablesOverSegments(model, lecturesDict, constants)
TFEconstraints.spreadIntervalVariablesOverSegments(model, exercisesDict, constants)
TFEconstraints.spreadIntervalVariablesOverSegments(model, tpsDict, constants)
TFEconstraints.spreadIntervalVariablesOverSegments(model, projectsDict, constants)

model.add_solver_callback(TFEcallbacks.PersonalCallback())

print(time.time()-begin)
model.write_information()
################# SETUP MODEL #################

################# SOLVING AND RESULTS #################
solution = model.solve(TimeLimit=60*60*8)

# "if solution" is True if there is at least one solution
if solution:
    print("Saving/displaying solutions : ...")
    begin = time.time()

    # (Un)comment this line to print the values of each interval variable
    # solution.write()

    # (Un)comment these lines to save (in the constants["folderResults"] folder) and/or display timetables
    # TFEtimetable.generateAndSaveTimetables(solution, groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, teachersIntervalVariables, groupsIntervalVariables, roomsIntervalVariables, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, roomsIntervalVariables, teachersIntervalVariables, groupsIntervalVariables, constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, "BA1_A", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, "BA1_B", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsIntervalVariables, teachersIntervalVariables, groupsIntervalVariables, "Ho.12", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersIntervalVariables, groupsIntervalVariables, roomsIntervalVariables, "Vandaele A", constants, colors.COLORS)

    print(time.time() - begin)

# the model is infeasible : CP Optimizer will try in 60 seconds (see cpo_config.py) to identify the cause of impossibility
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()
################# SOLVING AND RESULTS #################