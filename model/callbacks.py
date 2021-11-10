import docplex.cp.model as cp

class PersonalCallback(cp.CpoCallback):
    """
    Class inheriting cp.CpoCallback
    The "invoke" method must be overwritten

    When an object of this class is added to the model with :
        model.add_solver_callback(PersonalCallback())
    several events will be invoked during solve.
    """
    def invoke(self, solver, event, jsol):
        objValue = jsol.get_objective_values()
        objBounds = jsol.get_objective_bounds()
        objGaps = jsol.get_objective_gaps()
        solveStatus = jsol.get_solve_status()
        solveTime = jsol.get_info('SolveTime')
        memory = jsol.get_info('MemoryUsage')
        if event != "Periodic":
            print("{}: {}, objective: {} bounds: {}, gaps: {}, time: {}, memory: {}".
                  format(event, solveStatus, objValue, objBounds, objGaps, solveTime, memory))
