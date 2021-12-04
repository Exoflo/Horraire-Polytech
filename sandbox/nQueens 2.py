
import docplex.cp.model as cp
NB_QUEEN = 100
mdl = cp.CpoModel()
x = cp.integer_var_list(NB_QUEEN, 0, NB_QUEEN - 1, "X")
mdl.add(cp.all_diff(x))
mdl.add(cp.all_diff([x[i] + i for i in range(NB_QUEEN)]))
mdl.add(cp.all_diff([x[i] - i for i in range(NB_QUEEN)]))

msol = mdl.solve()
msol.print_solution()

# allSolutions = mdl.start_search(SearchType="DepthFirst", Workers=1)
# for i,sol in enumerate(allSolutions):
#     for j in range(NB_QUEEN):
#         print("x_"+str(j)+" = "+str(sol[x[j]]))