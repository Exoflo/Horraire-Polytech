import pandas as pd
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