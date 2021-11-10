context.solver.local.execfile = 'D:/IBM_ILOG_CPLEX_Studio201/cpoptimizer/bin/x64_win64/cpoptimizer.exe'
context.solver.trace_cpo = False
context.solver.trace_log = True
context.solver.add_log_to_solution = False

# context.params.TimeLimit = 10
context.params.LogVerbosity = 'Terse'
# context.params.FailureDirectedSearch = 'Off'
# context.params.SearchType = "MultiPoint"
# context.params.TemporalRelaxation = "Off"
# context.params.DefaultInferenceLevel = 'Low'
context.params.ConflictRefinerTimeLimit = 60

context.verbose = 0

context.model.add_source_location = False
context.model.length_for_alias = 10
context.model.name_all_constraints = False
context.model.dump_directory = None
context.model.sort_names = None
