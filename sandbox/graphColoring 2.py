import docplex.cp.model as cp
import numpy as np
import networkx as nx
import time

numberNodes = 50
density = 0.5
graph = nx.erdos_renyi_graph(numberNodes,density,seed=1)
cliques = list(nx.algorithms.enumerate_all_cliques(graph))
graph = nx.convert_matrix.to_numpy_array(graph)

mdl = cp.CpoModel()
nodes = cp.integer_var_list(numberNodes,min=0,max=numberNodes,name="N")

for i in range(numberNodes):
    for j in range(i):
        if graph[i][j] == 1:
            mdl.add(nodes[i] != nodes[j])

# mdl.add(nodes[0] == 0)

for i,c in enumerate(cliques[-1]):
    mdl.add(nodes[c] == i)

mdl.add(mdl.minimize(cp.max(nodes)))

begin = time.time()
msol = mdl.solve()
msol.print_solution()
print(time.time() - begin)
