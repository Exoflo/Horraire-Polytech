import pandas as pd
import json
import math

def loadData(fileDataset,quadri,sheet):
    """
    Function loading from an .xlsx file the data contained in the sheet specified by the parameter "sheet".
    Only the quadrimester specified by the parameter "quadri" will be loaded.

    :param fileDataset: (string) file's name of the .xlsx file to load. The file must be placed in the /data folder
    :param quadri: (string) quadrimester from which the data is loaded. Must be "Q1" or "Q2"
    :param sheet: (string) sheet name from which the data is loaded.
    :return dataset: (pandas.DataFrame) DataFrame containing data.
    """

    # (dtype=object) is mandatory in order to automatically convert integer values in .xlsx file into integer variables in Python
    dataset = pd.read_excel("../data/"+fileDataset, sheet_name=sheet, engine="openpyxl",dtype=object)
    dataset = dataset[dataset["quadri"]==quadri]
    print(type(dataset))
    return dataset

def loadCursusData(fileDataset):
    """
    Function loading from an .xlsx file the data relative to cursus in the sheet "Groups"
    and generating a dictionary with the number of students per group.
    Each line of this sheet has :
        - cursus = (string) cursus name
        - numberGroups = (integer) number of groups in the cursus
        - totalStudents = (integer) estimated total number of students in the cursus
    The number of students per group is simply computed by spreading all the students off equally between groups.
    For example, the "BA3_MECA,3,32" line will result in :
        - BA3_MECA_A,16
        - BA3_MECA_B,16
        - BA3_MECA_C,15

    :param fileDataset: (string) file name of the .xlsx file to load. The file must be placed in the /data folder and have a "Groups" sheet with characteristics cited above
    :return cursusData: (dict) dictionary with :
        - key = (string) cursus name (i.e. BA1, BA2, ...)
        - value = dictionary with :
            - key = (string) automatically generated group name (i.e. BA1_A, BA1_B, ...)
            - value = (integer) number of students in this group
    """

    # (dtype=object) is mandatory in order to automatically convert integer values in .xlsx file into integer variables in Python
    datasetCursus = pd.read_excel("../data/"+fileDataset, sheet_name="Groups",engine="openpyxl",dtype=object)
    cursusData = {}
    for rowCursus in datasetCursus.itertuples():
        cursusData[rowCursus.cursus] = {}
        baseNumberOfStudents = math.trunc(rowCursus.totalStudents/rowCursus.numberGroups)
        restNumberOfStudents = rowCursus.totalStudents%rowCursus.numberGroups

        # the cursus is split in several groups named A,B,C,...
        if rowCursus.numberGroups > 1:
            for i in range(rowCursus.numberGroups):
                # for not exact divisions, the rest is filled in first groups
                # chr(i+65) generates capital letters A,B,C,...
                cursusData[rowCursus.cursus][rowCursus.cursus+"_"+chr(i+65)] = baseNumberOfStudents + (1 if i < restNumberOfStudents else 0)

        # the cursus has only one group
        # in this case, cursusData[key] is a dict with one key-value entry where the group name is the same as the cursus name
        # i.e. the BA3_IG cursus with x students results in : cursusData["BA3_IG"] = {"BA3_IG": x}
        else:
            cursusData[rowCursus.cursus][rowCursus.cursus] = baseNumberOfStudents

    return cursusData


def loadDataFromJSON(fileDataset, numSemaine):
    with open(fileDataset, encoding='utf-8') as fh:
        data = json.load(fh)

    AllData = []

    nameSemaine = "Semaine " + str(numSemaine)
    for d1 in data:
        if nameSemaine in d1:
            for d in d1[nameSemaine]:
                # ---------------conversion des données en qqc de lisible pour nous et le code---------------------------#
                subject = d["subject"].split(':')
                prof = d["prof"]
                group = d["group"]

                # subject reprend l'id et le type de cours, on remettra comme il faut le cours après
                ID = subject[0]
                typeCursus = subject[1]

                # Les teachers sont ressencé comme une liste d'id. Pour éviter les problèmes, on retransforme tout en string.
                # Les id devraient pas posé de problème, on s'en fout un peu de leur nom en soit, juste on peut pas appliquer de desiderata
                teachers = ""
                for p in prof:
                    teachers = teachers + "," + str(p)
                teachers = teachers[1:]

                # Cursus pose pas mal de problème au vue de la division en groupe. En plus ils reprennent les master et les archi.
                # Ca pose pas de problème en soit pour archi et master, au contraire, mais pour l'instant on mettra ça de coté.
                # Par contre il faut remettre les group comme étant des cursus, on fait nous même la division en groupe.
                setCursus = set()
                for g in group:
                    g = str(g).replace('-', '_')

                    if "BAB1" in g:
                        g = "BA1"
                    elif "BAB2" in g:
                        g = "BA2"
                    elif "BAB3_CHIM" in g:
                        g = "BA3_CHIM"
                    elif "BAB3_ELEC" in g:
                        g = "BA3_ELEC"
                    elif "BAB3_IG" in g:
                        g = "BA3_IG"
                    elif "BAB3_MECA" in g:
                        g = "BA3_MECA"
                    elif "BAB3_MIN" in g:
                        g = "BA3_MIN"
                    else:
                        # print(g) #debug
                        continue
                    setCursus.add(g)

                if len(setCursus) > 0:
                    # Même chose que ce qu'on faisait avec teacher
                    cursus = ""
                    for c in setCursus:
                        cursus = cursus + "," + str(c)
                    cursus = cursus[1:]

                    # Deux possibilité ici, soit on s'en blc qu'un id soit plusieurs fois dans AllData, soit on s'en fout pas xD
                    # Dans un premier temps, on peut dire qu'on s'en fout, mais sur le long terme surement qu'on devra s'en soucier.
                    # Il me semble que dans la fonciton objective de thomas, les heures d'exos doivent être après la théorie dans une même semaine.
                    # Faire le dico avec toutes les clés pour éviter des erreurs dans le code de thomas, le reste sera hard codé tkt
                    dic = {
                        "cursus": cursus,
                        "id": ID,
                        "name": "",
                        "quadri": "",
                        "lectureHours": float('nan'),
                        "lectureTeachers": float('nan'),
                        "lectureRooms": float('nan'),
                        "lectureWeekStart": float('nan'),
                        "lectureWeekEnd": float('nan'),
                        "exerciseHours": float('nan'),
                        "exerciseDivisions": float('nan'),
                        "exerciseTeachers": float('nan'),
                        "exerciseRooms": float('nan'),
                        "exerciseSplit": float('nan'),
                        "exerciseWeekStart": float('nan'),
                        "exerciseWeekEnd": float('nan'),
                        "tpHours": float('nan'),
                        "tpDuration": float('nan'),
                        "tpDivisions": float('nan'),
                        "tpTeachers": float('nan'),
                        "tpRooms": float('nan'),
                        "tpWeekStart": float('nan'),
                        "tpWeekEnd": float('nan'),
                        "projectHours": float('nan'),
                        "projectDuration": float('nan'),
                        "projectTeachers": float('nan'),
                        "projectWeekStart": float('nan'),
                        "projectWeekEnd": float('nan'),
                        "TP_special": float('nan'),
                        "Remediations": float('nan'),
                        "Visits": float('nan'),
                        "Order": float('nan'),
                        "Rythm": float('nan')
                    }

                    # on fill le nombre d'heure dans les endroits où y'a un cours, on mets des teachers et des rooms
                    if subject == "theory" or subject == "theory_exercise" or subject == "mixed":
                        dic["lectureHours"] = 2
                        dic["lectureTeachers"] = teachers
                        # L'algo va surement buguer si on assigne pas de locaux
                        dic["lectureRooms"] = cursus

                        dic["lectureWeekStart"] = numSemaine + 1
                        dic["lectureWeekEnd"] = numSemaine + 1
                    elif subject == "exercise":
                        dic["exerciseHours"] = 2
                        dic["exerciseTeachers"] = teachers
                        # L'algo va surement buguer si on assigne pas de locaux
                        dic["exerciseRooms"] = cursus

                        dic["exerciseWeekStart"] = numSemaine + 1
                        dic["exerciseWeekEnd"] = numSemaine + 1
                    elif subject == "TP":
                        dic["tpHours"] = 4
                        dic["tpTeachers"] = teachers
                        # L'algo va surement buguer si on assigne pas de locaux
                        dic["tpRooms"] = cursus

                        dic["tpWeekStart"] = numSemaine + 1
                        dic["tpWeekEnd"] = numSemaine + 1
                    elif subject == "project":
                        dic["projectHours"] = 4
                        dic["projectTeachers"] = teachers

                        dic["projectWeekStart"] = numSemaine + 1
                        dic["projectWeekEnd"] = numSemaine + 1
                    AllData.append(dic)
    return pd.DataFrame(data=AllData)
