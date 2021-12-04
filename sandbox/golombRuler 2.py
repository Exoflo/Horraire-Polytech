import docplex.cp.model as cp

ORDER = 5
MAX_LENGTH = 10

mdl = cp.CpoModel()
marks = cp.integer_var_list(ORDER, 0, MAX_LENGTH, "M")

dist = [marks[i] - marks[j] for i in range(1, ORDER) for j in range(0, i)]
mdl.add(cp.all_diff(dist))

mdl.add(marks[0] == 0)
for i in range(1, ORDER):
    mdl.add(marks[i] > marks[i - 1])

mdl.add((marks[1] - marks[0]) < (marks[ORDER - 1] - marks[ORDER - 2]))

mdl.add(mdl.minimize(marks[ORDER - 1]))

msol = mdl.solve()
msol.print_solution()
rsol = mdl.refine_conflict()
rsol.print_conflict()