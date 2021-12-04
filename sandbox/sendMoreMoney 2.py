import docplex.cp.model as cp

mdl = cp.CpoModel()

s = cp.integer_var(0,9,name="S")
e = cp.integer_var(0,9,name="E")
n = cp.integer_var(0,9,name="N")
d = cp.integer_var(0,9,name="D")
m = cp.integer_var(0,9,name="M")
o = cp.integer_var(0,9,name="O")
r = cp.integer_var(0,9,name="R")
y = cp.integer_var(0,9,name="Y")

mdl.add(cp.all_diff([s,e,n,d,m,o,r,y]))
mdl.add((d + e + 10*(n + r) + 100*(e + o) + 1000*(s + m)) == (y + 10*e + 100*n + 1000*o + 10000*m))

allSolutions = mdl.start_search(SearchType="DepthFirst", Workers=1)
for i,sol in enumerate(allSolutions):
    print("S = " + str(sol[s]))
    print("E = " + str(sol[e]))
    print("N = " + str(sol[n]))
    print("D = " + str(sol[d]))
    print("M = " + str(sol[m]))
    print("O = " + str(sol[o]))
    print("R = " + str(sol[r]))
    print("Y = " + str(sol[y]))