import data.io as TFEdata
import docplex.cp.model as cp

class CursusGroups:
    """
    Class managing groups and divisions.
    Create one object to load all known information about groups and divisions :

    self.cursusData = dictionary with :
        - key = (string) cursus name (i.e. BA1, BA2, ...)
        - value = dictionary with :
            - key = (string) group name (i.e. BA1_A, BA1_B, ...)
            - value = (integer) number of students in this group
    See /data/io.py for details about the creation of this attribute.

    self.knownDivisions = dictionary with :
        - key = tuple (group_1,...,group_n,numberOfDivisions) configuration of groups and divisions
        - value = dictionary with :
            - key = (string) group name
            - value = (integer) division index for this group

    When groups must be split in divisions with the "generateBalancedDivisions" method,
    the first step is searching the configuration in self.knownDivisions.
    A configuration is defined by a tuple with all groups and a number of divisions => key of self.knownDivisions
    If it exists in self.knownDivisions, the repartition in divisions is listed as a dictionary => value of self.knownDivisions
    This dictionary contains, for each group, the division index in which the group is placed.

    For example, when BA3_ELEC (2 groups) and BA3_MECA (2 groups) must be split in 2 divisions,
    There are 4 groups (names generated automatically) : BA3_ELEC_A, BA3_ELEC_B, BA3_MECA_A, BA3_MECA_B
    The tuple defining the configuration is thus (BA3_ELEC_A, BA3_ELEC_B, BA3_MECA_A, BA3_MECA_B,2) => key of self.knownDivisions
    The repartition in divisions is a dictionary like {"BA3_ELEC_A": 0, "BA3_ELEC_B": 0, "BA3_MECA_A": 1, "BA3_MECA_B": 1} => value of self.knownDivisions
    It means that the 2 groups of BA3_ELEC belong to the first division and the 2 groups of BA3_MECA belong to the second division

    The data in self.knownDivisions can be updated with new configurations if necessary.
    An unknown configuration encountered in the "generateBalancedDivisions" method will lead to an automatic repartition based on the number of students in each group
    Such divisions may be suboptimal and need some modifications.
    """
    def __init__(self, fileDataset):
        """
        Constructor of CursusGroups class
        Instantiates all data about groups and known divisions

        :param fileDataset: (string) file name of the .xlsx file to load. More information in /data/io.py
        """
        self.cursusData = TFEdata.loadCursusData(fileDataset)
        self.knownDivisions = {
            ("BA1_A", "BA1_B", "BA1_C", "BA1_D", "BA1_E", "BA1_F", "BA1_G", "BA1_H", 8): {
                "BA1_A": 0,
                "BA1_B": 1,
                "BA1_C": 2,
                "BA1_D": 3,
                "BA1_E": 4,
                "BA1_F": 5,
                "BA1_G": 6,
                "BA1_H": 7,
            },
            ("BA1_A","BA1_B","BA1_C","BA1_D","BA1_E","BA1_F","BA1_G","BA1_H",4): {
                "BA1_A": 0,
                "BA1_B": 0,
                "BA1_C": 1,
                "BA1_D": 1,
                "BA1_E": 2,
                "BA1_F": 2,
                "BA1_G": 3,
                "BA1_H": 3,
            },
            ("BA1_A", "BA1_B", "BA1_C", "BA1_D", "BA1_E", "BA1_F", "BA1_G", "BA1_H",2): {
                "BA1_A": 0,
                "BA1_B": 0,
                "BA1_C": 0,
                "BA1_D": 0,
                "BA1_E": 1,
                "BA1_F": 1,
                "BA1_G": 1,
                "BA1_H": 1,
            },
            ("BA2_A", "BA2_B", "BA2_C", "BA2_D", 4): {
                "BA2_A": 0,
                "BA2_B": 1,
                "BA2_C": 2,
                "BA2_D": 3
            },
            ("BA2_A", "BA2_B", "BA2_C", "BA2_D", 2): {
                "BA2_A": 0,
                "BA2_B": 0,
                "BA2_C": 1,
                "BA2_D": 1
            },
            ("BA3_ELEC_A","BA3_ELEC_B",2): {
                "BA3_ELEC_A": 0,
                "BA3_ELEC_B": 1
            },
            ("BA3_MECA_A", "BA3_MECA_B", 2): {
                "BA3_MECA_A": 0,
                "BA3_MECA_B": 1
            },
            ("BA3_CHIM", "BA3_ELEC_A", "BA3_ELEC_B", "BA3_IG", "BA3_MECA_A","BA3_MECA_B","BA3_MIN", 4): {
                "BA3_CHIM": 0,
                "BA3_ELEC_A": 1,
                "BA3_ELEC_B": 1,
                "BA3_IG": 3,
                "BA3_MECA_A": 2,
                "BA3_MECA_B": 0,
                "BA3_MIN": 3
            },
            ("BA3_CHIM", "BA3_ELEC", "BA3_IG", "BA3_MECA_A", "BA3_MECA_B", "BA3_MIN", 4): {
                "BA3_CHIM": 0,
                "BA3_ELEC": 1,
                "BA3_IG": 3,
                "BA3_MECA_A": 2,
                "BA3_MECA_B": 0,
                "BA3_MIN": 3
            },
            ("BA3_CHIM", "BA3_MIN", 2): {
                "BA3_CHIM": 0,
                "BA3_MIN": 1
            },
            ("BA3_ELEC_A","BA3_ELEC_B","BA3_MECA_A", "BA3_MECA_B", 2): {
                "BA3_ELEC_A": 0,
                "BA3_ELEC_B": 0,
                "BA3_MECA_A": 1,
                "BA3_MECA_B": 1
            },
            ("BA3_ELEC","BA3_MECA_A", "BA3_MECA_B", 2): {
                "BA3_ELEC": 0,
                "BA3_MECA_A": 1,
                "BA3_MECA_B": 1
            }
        }

    def getGroups(self, listOfCursus):
        """
        Method returning all groups of all cursus in the parameter "listOfCursus" thanks to the data loaded in self.cursusData
        i.e. ["BA2","BA3_MECA"] will return ["BA2_A","BA2_B","BA2_C","BA2_D","BA3_MECA_A","BA3_MECA_B"]

        :param listOfCursus: (list) list of string of cursus names
        :return listOfGroups: (list) list of string of all groups coming from listOfCursus
        """
        listOfGroups = []
        for cursus in listOfCursus:
            # self.cursusData keys are cursus. The value is a dictionary where keys are groups of this cursus
            for group in self.cursusData[cursus].keys():
                listOfGroups.append(group)

        return listOfGroups

    def getGroupsWithCapacity(self, listOfCursus):
        """
        Method returning all groups with the number of students of all cursus in the parameter "listOfCursus" thanks to the data loaded in self.cursusData
        i.e. ["BA2","BA3_MECA"] will return {"BA2_A": x,"BA2_B": y,"BA2_C": z,"BA2_D": w,"BA3_MECA_A": v,"BA3_MECA_B": u} with x,y,z,w,v,u integers corresponding to the number of students per group

        :param listOfCursus: (list) list of string of cursus names
        :return listOfGroups: (dict) dictionary with :
            - key = (string) group name (coming from one cursus of listOfCursus)
            - value = (integer) number of students in the group
        """
        listOfGroupsWithCapacity = {}
        for cursus in listOfCursus:
            # self.cursusData keys are cursus. The value is a dictionary where keys are groups of this cursus and values are the number of students in the group
            for group,numberOfStudents in self.cursusData[cursus].items():
                listOfGroupsWithCapacity[group] = numberOfStudents

        return listOfGroupsWithCapacity

    def generateBalancedDivisions(self, listOfCursus, numberDivisions, isGroupAuto):
        """
        Method placing groups in balanced divisions regarding the number of students in each group.
        The groups concerned by the repartition in divisions are those coming from the cursus in "listOfCursus" parameter.
        The number of divisions is defined by the "numberDivisions" parameter.
        There are two ways to generate divisions :
            - manually = explicit divisions in self.knownDivisions are returned
            - automatically = solve a subproblem aiming to balance all divisions in terms of number of students.
                            Each group has an integer variable associated to the division it will be placed in : v = 0...D-1, D = number of divisions
                            The expected mean (expectedMean) represents the expected number of students in each division. It is the sum of all students in all groups divided by D.
                            The objective function minimizes :
                            sum_d{abs(sum_g{(vg==d)*nSg}-expectedMean)}
                            with d = division, g = group, vg = variable of group g, nSg = number of students of group g.
                            For a particular solution, the expression (vg==d)*nSg is equal to nSg if group g belongs to division d, 0 otherwise.

        The "isGroupAuto" boolean defines the way divisions are generated :
            - isGroupAuto == True : divisions are generated automatically
            - isGroupAuto == False : if the configuration (defined by groups and number of divisions) is present in self.knownDivisions, then the manual way is chosen.
                                    if not, divisions are generated automatically

        :param listOfCursus: (list) list of string of cursus names
        :param numberDivisions: (integer) number of divisions in which all groups must be placed
        :param isGroupAuto: (boolean) boolean defining the method used to generate divisions
        :return: (dict) dictionary with :
            - key = (string) group name
            - value = (integer) division index for this group
        """

        listOfGroupsWithCapacity = self.getGroupsWithCapacity(listOfCursus)

        # building the configuration used as a key for the dict "self.knownDivisions"
        configurationKey = self.getGroups(listOfCursus)
        configurationKey.append(numberDivisions)

        # if the configuration is in self.knownDivisions and isGroupAuto is False, then the value in self.knownDivisions is returned
        if isGroupAuto is False and tuple(configurationKey) in self.knownDivisions:
            return self.knownDivisions[tuple(configurationKey)]

        # if the number of divisions is not equal to 1 (non trivial case), the subproblem is built then solved
        if numberDivisions != 1:
            expectedMean = 0

            # the d_th item of "divisions" is equal to sum_g{(vg==d)*nSg}
            divisions = [0 for d in range(numberDivisions)]

            # building each vg variable, sum_g{(vg==d)*nSg} and expectedMean
            for group,numberOfStudents in listOfGroupsWithCapacity.items():
                expectedMean += numberOfStudents

                # creating vg variable, domain = 0...D-1 and name = group name
                groupVariable = cp.integer_var(min=0,max=numberDivisions-1,name=group)

                # building each term of sum_g{(vg==d)*nSg}, all divisions in parallel
                for d in range(numberDivisions):
                    divisions[d] += (groupVariable == d)*numberOfStudents
            expectedMean /= numberDivisions

            # the subproblem has no constraint, except the variable domains
            subModel = cp.CpoModel()
            # the objective function is simply added to the model
            subModel.add(cp.minimize(cp.sum(cp.abs(div-expectedMean) for div in divisions)))
            # the subproblem is solved with LogVerbosity='Quiet' to disable logs
            solution = subModel.solve(LogVerbosity='Quiet')
            # the solution is an object :
            # - solution.get_all_var_solutions() returns a list of all variables with their value
            # - s.get_name() returns the variable name of "s" => group name
            # - s.get_value() returns the variable value of "s" => division index of this group
            return {s.get_name(): s.get_value() for s in solution.get_all_var_solutions()}

        # if there is only one division (all groups belong to the same division),
        # the solution is trivial and all division indexes are equal to "0" for all groups
        else:
            return {k: 0 for k in listOfGroupsWithCapacity.keys()}
