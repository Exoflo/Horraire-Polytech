import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import objectives as TFEobjectives
import callbacks as TFEcallbacks
import initialization as TFEinitialization
import data.colors as colors
import time
import docplex.cp.model as cp

"""
This script represents the configuration in the section 7.2.4
It is divided in two parts : 
    - SETUP MODEL = All constraints used in the model. Do not change them to get section 7.2.4 results. 
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
"constants" is a dict with all parameters used. Sections 7.2.4 results are obtained with parameters in parenthesis : 
    - weeks (12) = number of real weeks
    - days (5) = number of days per week
    - slots (4) = number of slots per day
    - segmentSize (3) = size of a segment (i.e. size of 3 means that each segment represents 3 identical weeks)
    - roundUp (True) = when converting weeks in segments, the number of lessons are rounded up (True) or rounded down (False)
    - cursus (True) = dict of cursus included in the model
    - quadri ("Q1") = quadrimester
    - fileDataset ("datasetFinal.xlsx") = file name of the dataset. Must be placed in the /data folder
    - folderResults ("4SegmentsFinal") = folder name where the results will be stored. Must be placed in the /results folder
    - groupAuto (False) = boolean indicating if the divisions are generated automatically considering number of students or not
"""
constants = {
    "weeks":12,
    "days":5,
    "slots":4,
    "segmentSize":3,
    "roundUp": True,
    "cursus": {
        "BA IC (B1)": True,
        "BA IC ARCHI (B1)":False,
        "BA IC (B2)": False,
        "BA IC ARCHI (B2)":False,
        "BA IC (B3 - CHIMIE/SDM)": False,
        "BA IC (B3 - ELEC)": False,
        "BA IC (B3 - IG)": True,
        "BA IC (B3 - MECA)": False,
        "BA IC (B3 - MINES)": False,
        "BA IC ARCHI (B3)":False,
        "MA IC CHIMIE-SDM (B1)":False,
        "MA IC CHIMIE-SDM P2E (B1)": False,
        "MA IC CHIMIE-SDM SGM (B1)": False,
        "MA IC ELEC (B1)":False,
        "MA IC ELEC AISC (B1)": False,
        "MA IC ELEC EE (B1)": False,
        "MA IC ELEC SigSys (B1)": False,
        "MA IC ELEC (B1 - OPTION IPIT)":False,
        "MA IC ELEC (B1 - OPTION PCRE)":False,
        "MA IC IG (B1)": True,
        "MA IC MECA (B1)":False,
        "MA IC MECA CP (B1)": False,
        "MA IC MECA GE (B1)": False,
        "MA IC MECA MECATRO (B1)": False,
        "MA IC MINES (B1)": False,
        "MA IC ARCHI (B1)":False,
        "MA IC ARCHI (B1 - IBAT)":False,
        "MA IC ARCHI (B1 - UDEBAT)":False,
        "MA IC CHIMIE-SDM P2E (B2 - MO)": False,
        "MA IC CHIMIE-SDM SGM (B2 - MO)": False,
        "MA IC ELEC AISC (B2 - MO)": False,
        "MA IC ELEC EE (B2 - MO)": False,
        "MA IC ELEC SigSys (B2 - MO)": False,
        "MA IC IG (B2 - MO)": False,
        "MA IC MECA CP (B2 - MO)": False,
        "MA IC MECA GE (B2 - MO)": False,
        "MA IC MECA MECATRO (B2 - MO)": False,
        "MA IC MINES (B2 - MO)": False,
        "MA IC ARCHI (B2 - MO)": False,
        "MA IC ARCHI (B2 - Option UDEBAT)":False,
        "MA IC ARCHI (B2 - Option IBAT)":False
    },
    "quadri": "Q1",
    "fileDataset": "input.json",
    "folderResults": "4SegmentsFinal",
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

print("Reading data : " + str(time.time() - begin))

# constraint 6.3.4 : Unavailability
TFEconstraints.cursusUnavailabilityConstraint(model, cursusGroups, groupsIntervalVariables, constants)

# constraint 6.3.1 : Long interval continuity (4h blocks)
TFEconstraints.longIntervalVariablesIntegrity(model, tpsDict, constants)
TFEconstraints.longIntervalVariablesIntegrity(model, projectsDict, constants)

# constraint 6.3.2 : No conflict
TFEconstraints.notOverlappingConstraint(model, groupsIntervalVariables)
TFEconstraints.notOverlappingConstraint(model, teachersIntervalVariables)
TFEconstraints.notOverlappingConstraint(model, roomsIntervalVariables)

# constraint 6.3.3 : Avoid big delay between same exercises or TP between groups
TFEconstraints.multipliedVariablesInSameSegmentConstraint(model, exercisesDict, constants)
TFEconstraints.multipliedVariablesInSameSegmentConstraint(model, tpsDict, constants)

# constraint 6.3.9 (6.3.5 included) : Segment repartition
TFEconstraints.spreadIntervalVariablesOverSegments(model, lecturesDict, constants)
TFEconstraints.spreadIntervalVariablesOverSegments(model, exercisesDict, constants)
TFEconstraints.spreadIntervalVariablesOverSegments(model, tpsDict, constants)
TFEconstraints.spreadIntervalVariablesOverSegments(model, projectsDict, constants)

# constraint 6.3.10 : Theory before TP and exercices
TFEconstraints.lecturesBeforeConstraint(model, lecturesDict, [exercisesDict,tpsDict], AAset, constants)

# synchronise exercises of I-PHYS-020 and I-SDMA-020
if constants["quadri"] == "Q1":
    TFEinitialization.simultaneousGroups(model,exercisesDict["I-PHYS-020"],exercisesDict["I-SDMA-020"])

# place projects I-POLY-011 and I-ILIA-024 friday afternoon
if constants["quadri"] == "Q1":
    TFEinitialization.fixedSlots(model, projectsDict["I-POLY-011"], 5, 3, constants)
    TFEinitialization.fixedSlots(model, projectsDict["I-ILIA-024"], 5, 3, constants)

objectiveFunctions = []
coefficients = []
# objective function 6.5.1 (weight of 4)
objectiveFunctions.append(TFEobjectives.avoidAfternoonForShortIntervalVariables([lecturesDict], [], constants))
coefficients.append(4)
# objective function 6.5.2 (weight of 1)
objectiveFunctions.append(TFEobjectives.avoidLastSlotForShortIntervalVariables([exercisesDict], ["V-LANG-151", "V-LANG-153", "V-LANG-155"], constants))
coefficients.append(1)

model.minimize(cp.scal_prod(objectiveFunctions,coefficients))

model.add_solver_callback(TFEcallbacks.PersonalCallback())

print(time.time()-begin)
model.write_information()
################# SETUP MODEL #################

################# SOLVING AND RESULTS #################
solution = model.solve(TimeLimit=60*4)

# "if solution" is True if there is at least one solution
if solution:
    print("Saving/displaying solutions : ...")
    begin = time.time()

    # (Un)comment this line to print the values of each interval variable
    solution.write()

    # (Un)comment these lines to save (in the constants["folderResults"] folder) and/or display timetables
    TFEtimetable.generateAndSaveTimetables(solution, groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, constants, colors.COLORS)
    TFEtimetable.generateAndSaveTimetables(solution, teachersIntervalVariables, groupsIntervalVariables, roomsIntervalVariables, constants, colors.COLORS)
    TFEtimetable.generateAndSaveTimetables(solution, roomsIntervalVariables, teachersIntervalVariables, groupsIntervalVariables, constants, colors.COLORS)
    TFEtimetable.generateAndDisplayTimetable(solution, groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, "BA1_A", constants, colors.COLORS)
    TFEtimetable.generateAndDisplayTimetable(solution, groupsIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, "BA1_B", constants, colors.COLORS)
    TFEtimetable.generateAndDisplayTimetable(solution, roomsIntervalVariables, teachersIntervalVariables, groupsIntervalVariables, "Ho.12", constants, colors.COLORS)
    TFEtimetable.generateAndDisplayTimetable(solution, teachersIntervalVariables, groupsIntervalVariables, roomsIntervalVariables, "Vandaele A", constants, colors.COLORS)
    TFEtimetable.generateAndDisplayTimetable(solution, teachersIntervalVariables, groupsIntervalVariables, roomsIntervalVariables, "MA1_IG", constants, colors.COLORS)

    print(time.time() - begin)

# the model is infeasible : CP Optimizer will try in 60 seconds (see cpo_config.py) to identify the cause of impossibility
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()
################# SOLVING AND RESULTS #################
