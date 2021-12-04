from ortools.sat.python import cp_model
import time
nb_queens = 100
model = cp_model.CpModel()
q = [model.NewIntVar(0, nb_queens - 1, 'x%i' % i) for i in range(nb_queens)]
model.AddAllDifferent(q)
diag1 = []
diag2 = []
for j in range(nb_queens):
  q1 = model.NewIntVar(0, 2 * nb_queens, 'diag1_%i' % j)
  diag1.append(q1)
  model.Add(q1 == q[j] + j)
  q2 = model.NewIntVar(-nb_queens, nb_queens, 'diag2_%i' % j)
  diag2.append(q2)
  model.Add(q2 == q[j] - j)
model.AddAllDifferent(diag1)
model.AddAllDifferent(diag2)

begin = time.time()
solver = cp_model.CpSolver()
status = solver.Solve(model)
print(time.time()-begin)

# if status == cp_model.OPTIMAL:
#     for i in range(nb_queens):
#         print("q_"+str(i)+" = "+str(solver.Value(q[i])))
