import numpy as np
import math
import matplotlib.pyplot as plt
import random

def generateTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict):
    hasGeneratedColors = False
    if colorsDict is None:
        colorsDict = {}

    fullNameOfLessons = {"lec": "Cours","ex": "Exercices","tp": "TP","pr": "Projet"}
    timetables = {}
    for majorName,majorIntervalVariables in majorData.items():
        timetable = np.full((constants["slots"], int(constants["days"] * constants["weeks"] / constants["segmentSize"])), "", dtype=object)
        for majorIntervalVariable in majorIntervalVariables:
            variableName = majorIntervalVariable.get_name()
            valuesOfInterval = solution[variableName]
            caracteristicsOfVariable = variableName.split("_")

            if "ch" in variableName:
                displayName = "Charleroi/" + str(int(caracteristicsOfVariable[2])+1) + "\n" \
                              + caracteristicsOfVariable[0] + "\n"
            else:
                displayName = caracteristicsOfVariable[0] + "\n" \
                              + fullNameOfLessons[caracteristicsOfVariable[1]] + "/" \
                              + str(int(caracteristicsOfVariable[2])+1) + "\n"
            breakFlag = False
            found = False
            for minorName1,minorIntervalVariables1 in minorData1.items():
                if breakFlag:
                    break
                for minorIntervalVariable1 in minorIntervalVariables1:
                    if variableName == minorIntervalVariable1.get_name():
                        if found:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += minorName1
                        found = True
                        break
            displayName += "\n"
            breakFlag = False
            found = False
            for minorName2,minorIntervalVariables2 in minorData2.items():
                if breakFlag:
                    break
                for minorIntervalVariable2 in minorIntervalVariables2:
                    if variableName == minorIntervalVariable2.get_name():
                        if found:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += minorName2
                        found = True
                        break
            if "ch2" in variableName:
                displayName += "2"
            elif "ch4" in variableName:
                displayName += "4"

            dayOfTimetable = math.trunc(valuesOfInterval[0] / constants["slots"])
            slotOfTimetable = valuesOfInterval[0] % constants["slots"]
            timetable[slotOfTimetable][dayOfTimetable] = displayName

            if "Charleroi" not in displayName and caracteristicsOfVariable[0] not in colorsDict:
                hasGeneratedColors = True
                while True:
                    newColor = (random.randint(1,254)/255,random.randint(1,254)/255,random.randint(1,254)/255,1)
                    if newColor not in colorsDict.values():
                        colorsDict[caracteristicsOfVariable[0]] = newColor
                        break

        timetables[majorName] = timetable
    if hasGeneratedColors:
        print(colorsDict)
    return timetables, colorsDict

def saveTimetables(timetables, colorsDict, constants):
    for nameItem,timetable in timetables.items():
        m,n = timetable.shape
        segmentCounter = 1
        for j in range(n):
            dayOfSegment = j % constants["days"]
            if dayOfSegment == 0:
                fig, ax = plt.subplots()
                title = nameItem + " : Segment " + str(segmentCounter)
                nameFile = nameItem + "_Segment_" + str(segmentCounter)
                ax.set_title(title)
                ax.set_xticks(np.linspace(0, 5, 6))
                ax.set_yticks([0, 1, 1.125, 2.125, 2.625, 3.625, 3.750, 4.750])
                ax.set_xticks(np.linspace(0.5, 4.5, 5), minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels(["17h45", "15h45", "15h30", "13h30", "12h30", "10h30", "10h15", "8h15"], fontsize=6)
                ax.set_xticklabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], minor=True)
                ax.set_xlim(0, constants["days"])
                ax.set_ylim(0, 4.750)
                ax.grid()
                ax.set_axisbelow(True)
                segmentCounter += 1
            for i in range(m):
                if timetable[i][j] != "":
                    if "Charleroi" in timetable[i][j]:
                        colorDisplay = (0,0,0,1)
                        colorText = 'white'
                        if timetable[i][j][-1] == "2":
                            if i == 0:
                                yCoordinate = 3.625
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 2.625, 4.625, color=colorDisplay)
                            elif i == 2:
                                yCoordinate = 1.125
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 0.125, 2.125, color=colorDisplay)
                            else:
                                continue
                        elif timetable[i][j][-1] == "4":
                            ax.fill_between([dayOfSegment, dayOfSegment + 1], 0, 4.75, color=colorDisplay)
                            yCoordinate = 2.375
                        else:
                            continue
                        ax.text(dayOfSegment + 0.5,
                                yCoordinate,
                                timetable[i][j][:-1],
                                fontsize=6,
                                horizontalalignment='center',
                                verticalalignment='center',
                                color=colorText)
                    else:
                        colorDisplay = colorsDict[timetable[i][j].split("\n")[0]]
                        colorText = 'black' if (colorDisplay[0] * 255 * 0.299
                                                + colorDisplay[1] * 255 * 0.587
                                                + colorDisplay[2] * 255 * 0.114) > 150 else 'white'
                        yCoordinate = 0
                        if "TP/" in timetable[i][j] or "Projet/" in timetable[i][j]:
                            if i == 0:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 2.625, 4.625, color=colorDisplay)
                                yCoordinate = 3.625
                            elif i == 2:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 0.125, 2.125, color=colorDisplay)
                                yCoordinate = 1.125
                            else:
                                continue
                            ax.text(dayOfSegment + 0.5,
                                    yCoordinate,
                                    timetable[i][j],
                                    fontsize=6,
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    color=colorText)
                        else:
                            if i == 0:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 3.750, 4.750, color=colorDisplay)
                                yCoordinate = 4.25
                            elif i == 1:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 2.625, 3.625, color=colorDisplay)
                                yCoordinate = 3.125
                            elif i == 2:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 1.125, 2.125, color=colorDisplay)
                                yCoordinate = 1.625
                            elif i == 3:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 0, 1, color=colorDisplay)
                                yCoordinate = 0.5
                            ax.text(dayOfSegment + 0.5,
                                    yCoordinate,
                                    timetable[i][j],
                                    fontsize=6,
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    color=colorText)
            if dayOfSegment == 4:
                fig.savefig("results/" + constants["folderResults"] + "/" + nameFile + ".jpg")
                plt.close(fig)

def displayTimetable(timetables, colorsDict, nameItem, constants):
    if nameItem in timetables:
        timetable = timetables[nameItem]
        m,n = timetable.shape
        segmentCounter = 1
        for j in range(n):
            dayOfSegment = j % constants["days"]
            if dayOfSegment == 0:
                fig, ax = plt.subplots()
                title = nameItem + " : Segment " + str(segmentCounter)
                ax.set_title(title)
                ax.set_xticks(np.linspace(0,5,6))
                ax.set_yticks([0,1,1.125,2.125,2.625,3.625,3.750,4.750])
                ax.set_xticks(np.linspace(0.5, 4.5, 5),minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels(["17h45","15h45","15h30","13h30","12h30","10h30","10h15","8h15"],fontsize=6)
                ax.set_xticklabels(["Monday","Tuesday","Wednesday","Thursday","Friday"],minor=True)
                ax.set_xlim(0, constants["days"])
                ax.set_ylim(0, 4.750)
                ax.grid()
                ax.set_axisbelow(True)
                segmentCounter += 1
            for i in range(m):
                if timetable[i][j] != "":
                    if "Charleroi" in timetable[i][j]:
                        colorDisplay = (0,0,0,1)
                        colorText = 'white'
                        if timetable[i][j][-1] == "2":
                            if i == 0:
                                yCoordinate = 3.625
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 2.625, 4.625, color=colorDisplay)
                            elif i == 2:
                                yCoordinate = 1.125
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 0.125, 2.125, color=colorDisplay)
                            else:
                                continue
                        elif timetable[i][j][-1] == "4":
                            ax.fill_between([dayOfSegment, dayOfSegment + 1], 0, 4.75, color=colorDisplay)
                            yCoordinate = 2.375
                        else:
                            continue
                        ax.text(dayOfSegment + 0.5,
                                yCoordinate,
                                timetable[i][j][:-1],
                                fontsize=6,
                                horizontalalignment='center',
                                verticalalignment='center',
                                color=colorText)
                    else:
                        colorDisplay = colorsDict[timetable[i][j].split("\n")[0]]
                        colorText = 'black' if (colorDisplay[0] * 255 * 0.299
                                                + colorDisplay[1] * 255 * 0.587
                                                + colorDisplay[2] * 255 * 0.114) > 150 else 'white'
                        yCoordinate = 0
                        if "TP/" in timetable[i][j] or "Projet/" in timetable[i][j]:
                            if i == 0:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 2.625, 4.625, color=colorDisplay)
                                yCoordinate = 3.625
                            elif i == 2:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 0.125, 2.125, color=colorDisplay)
                                yCoordinate = 1.125
                            else:
                                continue
                            ax.text(dayOfSegment + 0.5,
                                    yCoordinate,
                                    timetable[i][j],
                                    fontsize=6,
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    color=colorText)
                        else:
                            if i == 0:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 3.750, 4.750, color=colorDisplay)
                                yCoordinate = 4.25
                            elif i == 1:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 2.625, 3.625, color=colorDisplay)
                                yCoordinate = 3.125
                            elif i == 2:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 1.125, 2.125, color=colorDisplay)
                                yCoordinate = 1.625
                            elif i == 3:
                                ax.fill_between([dayOfSegment, dayOfSegment + 1], 0, 1, color=colorDisplay)
                                yCoordinate = 0.5
                            ax.text(dayOfSegment + 0.5,
                                    yCoordinate,
                                    timetable[i][j],
                                    fontsize=6,
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    color=colorText)
            if dayOfSegment == 4:
                plt.show()

def generateAndSaveTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict):
    timetables, colorsDict = generateTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict)
    saveTimetables(timetables, colorsDict, constants)

def generateAndDisplayTimetable(solution, majorData, minorData1, minorData2, nameItem, constants, colorsDict):
    timetables, colorsDict = generateTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict)
    displayTimetable(timetables, colorsDict, nameItem, constants)