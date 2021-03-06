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

    dataset = {}
    desiderata = {}

    with open( "../data/"+ fileDataset, encoding='utf-8') as fh:
        data = json.load(fh)

    for des in data["desideratas"]:
        code = des["AAID"]["code"]
        if code not in desiderata:
            desiderata[code] = {}
        if "WeekStartStop" not in desiderata[code]:
            desiderata[code]["WeekStartStop"] = {"Theorie":[1, 12], "Exercice":[1, 12], "Travaux pratiques":[1, 12], "Projet":[1, 12]}

        desiderata[code]["WeekStartStop"][des["desiderataTypeID"]["type"]][0] = des["semaine_debut"]
        # uncomment by code below when backend start to bouger ses couilles
        #desiderata[des["AAID"]["code"]]["WeekStartStop"][des["desiderataTypeID"]["type"]][1] = des["semaine_fin"]

        if "listTeacher" not in desiderata[code]:
            desiderata[code]["listTeacher"] = des["enseignantsouhaitee"]

        if "Notes" not in desiderata[code]:
            desiderata[code]["Notes"] = {"Order":"","Rythm":""}

        if "exoAfterTheo" not in desiderata[code]:
            desiderata[code]["exoAfterTheo"] = int(des["exoAfterTheo"])




    #TFE Sheet
    if sheet == "TFE":
        dataset = {"cursus":[],"id":[],"name":[],"quadri":[],"lectureHours":[],"lectureTeachers":[],"lectureRooms":[],"lectureWeekStart":[],"lectureWeekEnd":[],"exerciseHours":[],"exerciseDivisions":[],"exerciseTeachers":[],"exerciseRooms":[],"exerciseSplit":[],"exerciseWeekStart":[],"exerciseWeekEnd":[],"tpHours":[],"tpDuration":[],"tpDivisions":[],"tpTeachers":[],"tpRooms":[],"tpWeekStart":[],"tpWeekEnd":[],"projectHours":[],"projectDuration":[],"projectTeachers":[],"projectWeekStart":[],"projectWeekEnd":[],"TP_special":[],"Remediations":[],"Visits":[],"Order":[],"Rythm":[],"Lec > Ex":[],"Altern?? / Bloc":[]}

        for AA in data["aas"]:
            # Cursus
            cursus = ""
            for cohorte in AA["cohortes"]:
                if cohorte["cohorteName"] == "BA IC (B3 - TC)":
                    cursus += "BA IC (B3 - CHIMIE/SDM),BA IC (B3 - ELEC),BA IC (B3 - IG),BA IC (B3 - MECA),BA IC (B3 - MINES),"
                else:
                    cursus += cohorte["cohorteName"] + ","

            dataset["cursus"].append(cursus[:-1])

            # Id/name/quadri/lectureHours/lectureTeachers:
            dataset["id"].append(AA["code"])
            dataset["name"].append(AA["name"])
            dataset["quadri"].append(AA["quadri"])
            dataset["lectureHours"].append(AA["ht"])
            dataset["lectureTeachers"].append(",".join([x.split("@")[0].replace("."," ") for x in AA["titulaires"]]))

            #lectureRooms (to see later)
            dataset["lectureRooms"].append("")

            #lectureWeekStart/lectureWeekEnd
            if AA["code"] in desiderata:
                dataset["lectureWeekStart"].append(desiderata[AA["code"]]["WeekStartStop"]["Theorie"][0])
                dataset["lectureWeekEnd"].append(desiderata[AA["code"]]["WeekStartStop"]["Theorie"][1])
            else:
                dataset["lectureWeekStart"].append(1)
                dataset["lectureWeekEnd"].append(12)
                print(AA["code"],": No desiderata available")




            #exerciseHours
            dataset["exerciseHours"].append(AA["htpe"])

            #exerciseDivisions/exerciseSplit
            exodiv = {"V-LANG-151":8,"V-LANG-153":4,"V-LANG-155":4,"V-LANG-152":8,"V-LANG-154":4,"V-LANG-156":4}
            if AA["code"] in exodiv:
                dataset["exerciseDivisions"].append(exodiv[AA["code"]])
                dataset["exerciseSplit"].append(1)
            else:
                dataset["exerciseDivisions"].append(1)
                dataset["exerciseSplit"].append(0)

            #exerciseTeachers
            if AA["code"] in desiderata:
                dataset["exerciseTeachers"].append(",".join([x.split("@")[0].replace("."," ") for x in desiderata[AA["code"]]["listTeacher"] ]))
            else:
                dataset["exerciseTeachers"].append("")

            # exerciseRooms (to see later)
            dataset["exerciseRooms"].append("")

            # exerciseWeekStart/exerciseWeekEnd
            if AA["code"] in desiderata:
                dataset["exerciseWeekStart"].append(desiderata[AA["code"]]["WeekStartStop"]["Exercice"][0])
                dataset["exerciseWeekEnd"].append(desiderata[AA["code"]]["WeekStartStop"]["Exercice"][1])
            else:
                dataset["exerciseWeekStart"].append(1)
                dataset["exerciseWeekEnd"].append(12)

            # tpHours/tpDuration/tpDivisions
            dataset["tpHours"].append(AA["htps"])
            dataset["tpDuration"].append(4)
            dataset["tpDivisions"].append(4)

            # tpTeachers
            if AA["code"] in desiderata:
                dataset["tpTeachers"].append(",".join([x.split("@")[0].replace(".", " ") for x in desiderata[AA["code"]]["listTeacher"]]))
            else:
                dataset["tpTeachers"].append("")

            # tpRooms (to see later)
            dataset["tpRooms"].append("")

            # tpWeekStart/tpWeekEnd
            if AA["code"] in desiderata:
                dataset["tpWeekStart"].append(desiderata[AA["code"]]["WeekStartStop"]["Travaux pratiques"][0])
                dataset["tpWeekEnd"].append(desiderata[AA["code"]]["WeekStartStop"]["Travaux pratiques"][1])
            else:
                dataset["tpWeekStart"].append(1)
                dataset["tpWeekEnd"].append(12)




            # projectHours/projectDuration
            dataset["projectHours"].append(0)
            dataset["projectDuration"].append(4)

            # projectTeachers/projectWeekStart/projectWeekEnd
            if AA["code"] in desiderata:
                dataset["projectTeachers"].append(",".join([x.split("@")[0].replace(".", " ") for x in desiderata[AA["code"]]["listTeacher"]]))
                dataset["projectWeekStart"].append(desiderata[AA["code"]]["WeekStartStop"]["Projet"][0])
                dataset["projectWeekEnd"].append(desiderata[AA["code"]]["WeekStartStop"]["Projet"][1])
            else:
                dataset["projectTeachers"].append("")
                dataset["projectWeekStart"].append(1)
                dataset["projectWeekEnd"].append(12)






            dataset["TP_special"].append(0)
            dataset["Remediations"].append(AA["hr"])
            dataset["Visits"].append(0)
            if AA["code"] in desiderata:
                dataset["Order"].append(desiderata[AA["code"]]["Notes"]["Order"])
                dataset["Rythm"].append(desiderata[AA["code"]]["Notes"]["Rythm"])
                dataset["Lec > Ex"].append(desiderata[AA["code"]]["exoAfterTheo"])
            else:
                dataset["Order"].append("")
                dataset["Rythm"].append("")
                dataset["Lec > Ex"].append(1)

            dataset["Altern?? / Bloc"].append("non")





    #Cursus Sheet
    elif sheet == "Cursus":
        dataset = {"cursus":[],"quadri":[],"weekStart":[],"dayStart":[],"slotStart":[],"weekEnd":[],"dayEnd":[],"slotEnd":[],"start":[],"end":[]}

        #Bac1 : wednesday
        for i in range(24):
            dataset["cursus"].append("BA IC (B1)")
            dataset["quadri"].append("Q" + str(i//12 + 1))
            dataset["weekStart"].append(i+1)
            dataset["dayStart"].append(3)
            dataset["slotStart"].append(3)
            dataset["weekEnd"].append(i+1)
            dataset["dayEnd"].append(3)
            dataset["slotEnd"].append(4)
            dataset["start"].append(10 + 20*i)
            dataset["end"].append(12 + 20*i)




    #Teachers Sheet
    elif sheet == "Teachers":
        dataset = {"teacher":[],"quadri":[],"weekStart":[],"dayStart":[],"slotStart":[],"weekEnd":[],"dayEnd":[],"slotEnd":[],"start":[],"end":[]}


    #CharleroiFixed Sheet
    elif sheet == "CharleroiFixed":
        dataset = {"teacher":[],"quadri":[],"AA":[],"room":[],"weekStart":[],"weekEnd":[],"day":[],"slot":[]}

    #Charleroi Sheet
    elif sheet == "Charleroi":
        dataset = {"teacher":[],"quadri":[],"AA":[],"room":[],"weekStart":[],"weekEnd":[]}

    #Breaks Sheet
    elif sheet == "Breaks":
        dataset = {"name":[],"quadri":[],"weekStart":[],"dayStart":[],"slotStart":[],"weekEnd":[],"dayEnd":[],"slotEnd":[],"start":[],"end":[]}



    dataset = pd.DataFrame(data=dataset)
    #print(dataset)

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
    cursusData = {}

    with open( "../data/"+ fileDataset, encoding='utf-8') as fh:
        data = json.load(fh)

    for group in data["groupes"]:
        if group["cohorteName"] not in cursusData:
            cursusData[group["cohorteName"]] = {}
        cursusData[group["cohorteName"]][group["name"]] = group["numberOfStudents"]

    return cursusData


def loadDataFromJSON(fileDataset, numSemaine):
    with open(fileDataset, encoding='utf-8') as fh:
        data = json.load(fh)

    AllData = []

    nameSemaine = "Semaine " + str(numSemaine)
    for d1 in data:
        if nameSemaine in d1:
            for d in d1[nameSemaine]:
                # ---------------conversion des donn??es en qqc de lisible pour nous et le code---------------------------#
                subject = d["subject"].split(':')
                prof = d["prof"]
                group = d["group"]

                # subject reprend l'id et le type de cours, on remettra comme il faut le cours apr??s
                ID = subject[0]
                typeCursus = subject[1]

                # Les teachers sont ressenc?? comme une liste d'id. Pour ??viter les probl??mes, on retransforme tout en string.
                # Les id devraient pas pos?? de probl??me, on s'en fout un peu de leur nom en soit, juste on peut pas appliquer de desiderata
                teachers = ""
                for p in prof:
                    teachers = teachers + "," + str(p)
                teachers = teachers[1:]

                # Cursus pose pas mal de probl??me au vue de la division en groupe. En plus ils reprennent les master et les archi.
                # Ca pose pas de probl??me en soit pour archi et master, au contraire, mais pour l'instant on mettra ??a de cot??.
                # Par contre il faut remettre les group comme ??tant des cursus, on fait nous m??me la division en groupe.
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
                    # M??me chose que ce qu'on faisait avec teacher
                    cursus = ""
                    for c in setCursus:
                        cursus = cursus + "," + str(c)
                    cursus = cursus[1:]

                    # Deux possibilit?? ici, soit on s'en blc qu'un id soit plusieurs fois dans AllData, soit on s'en fout pas xD
                    # Dans un premier temps, on peut dire qu'on s'en fout, mais sur le long terme surement qu'on devra s'en soucier.
                    # Il me semble que dans la fonciton objective de thomas, les heures d'exos doivent ??tre apr??s la th??orie dans une m??me semaine.
                    # Faire le dico avec toutes les cl??s pour ??viter des erreurs dans le code de thomas, le reste sera hard cod?? tkt
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

                    # on fill le nombre d'heure dans les endroits o?? y'a un cours, on mets des teachers et des rooms
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
