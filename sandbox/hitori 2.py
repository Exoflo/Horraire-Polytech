import docplex.cp.model as cp

HITORI_PROBLEM_0 = ( (2, 2, 1),
                     (2, 3, 1),
                     (1, 1, 1) )
HITORI_PROBLEM_1 = ( (2, 2, 1, 5, 3),
                     (2, 3, 1, 4, 5),
                     (1, 1, 1, 3, 5),
                     (1, 3, 5, 4, 2),
                     (5, 4, 3, 2, 1) )
HITORI_PROBLEM_2 = ( (4, 8, 1, 6, 3, 2, 5, 7),
                     (3, 6, 7, 2, 1, 6, 5, 4),
                     (2, 3, 4, 8, 2, 8, 6, 1),
                     (4, 1, 6, 5, 7, 7, 3, 5),
                     (7, 2, 3, 1, 8, 5, 1, 2),
                     (3, 5, 6, 7, 3, 1, 8, 4),
                     (6, 4, 2, 3, 5, 4, 7, 8),
                     (8, 7, 1, 4, 2, 3, 5, 6) )
HITORI_PROBLEM_3 = ( ( 2,  5,  6,  3,  8, 10,  7,  4, 13,  6, 14, 15,  9,  4,  1),
                     ( 3,  1,  7, 12,  8,  4, 10,  4,  4, 11,  5, 13,  4,  9,  2),
                     ( 4, 14, 10, 10, 14,  5, 11,  1,  6,  2,  7, 11, 13, 15, 12),
                     ( 5, 10,  2,  5, 13,  3,  8,  5,  9,  7,  4, 10,  6, 10,  2),
                     ( 1,  6,  8, 15, 10,  7,  4,  2, 15, 14,  9,  3,  3, 11,  4),
                     ( 6, 14,  3, 11,  2,  4,  9,  5,  7, 13, 12,  8, 10, 14,  1),
                     (12,  8, 14, 11,  3,  7, 15, 13, 10,  7, 12, 13,  5,  2, 13),
                     (11,  4, 12, 15,  5,  6,  5,  3, 15, 10,  7,  9,  5, 13, 14),
                     ( 8, 15,  4,  6, 15,  3, 13, 14,  6, 12, 10,  1, 11,  3,  5),
                     (15, 15,  9, 12,  1,  8, 11, 10,  2,  2, 11,  9,  4, 12,  2),
                     ( 7,  1,  9,  9, 10,  5,  3, 11, 13,  6,  7,  4, 12,  5,  8),
                     (14, 10, 13,  4, 12, 15, 11, 10,  5,  7,  8, 12,  5,  3,  6),
                     ( 5, 10, 11,  5, 11, 14, 14, 15,  8, 13, 13,  2,  7,  9,  9),
                     ( 9,  7, 15, 10, 12, 11,  8,  6,  1,  5,  7, 14, 13,  1,  3),
                     ( 6,  9,  1, 13,  6,  4, 12,  7, 14,  4,  2,  1,  3,  8, 12) )

def neighbors(i,j,n):
    res = []
    if j != 0:
        res.append((i, j - 1))
    if j != n - 1:
        res.append((i, j + 1))
    if i != 0:
        res.append((i - 1, j))
    if i != n - 1:
        res.append((i + 1, j))
    return res

puzzle = HITORI_PROBLEM_3
n = len(puzzle)

mdl = cp.CpoModel()

# cellules blanches = 0 // cellules noires = 1
cells = [[cp.binary_var(name="c_"+str(i)+"_"+str(j)) for j in range(n)] for i in range(n)]

for i in range(n):
    for j in range(n):
        neighborsCells = [cells[k][l] for k,l in neighbors(i,j,n)]
        mdl.add(cp.if_then(cells[i][j]==1,cp.sum(neighborsCells)==0)) # cellules noires non adjacentes
        mdl.add(cp.if_then(cells[i][j]==0,cp.sum(neighborsCells)<len(neighborsCells))) # cellules blanches adjacentes (2 ensembles)

# chaque ligne et chaque colonne n'ont pas de nombre en commun
for i in range(n):
    values = []
    for j in range(n):
        v = puzzle[i][j]
        if v not in values:
            values.append(v)
            lineCells = [cells[i][j]]
            for j2 in range(j+1,n):
                if v == puzzle[i][j2]:
                    lineCells.append(cells[i][j2])
            if len(lineCells) > 1:
                mdl.add(cp.sum(lineCells) >= len(lineCells)-1)

for j in range(n):
    values = []
    for i in range(n):
        v = puzzle[i][j]
        if v not in values:
            values.append(v)
            lineCells = [cells[i][j]]
            for i2 in range(i+1,n):
                if v == puzzle[i2][j]:
                    lineCells.append(cells[i2][j])
            if len(lineCells) > 1:
                mdl.add(cp.sum(lineCells) >= len(lineCells)-1)

mdl.minimize(cp.sum([cp.sum(c) for c in cells]))

msol = mdl.solve()
msol.print_solution()
if msol:
    for i in range(n):
        s = ""
        for j in range(n):
            if msol[cells[i][j]] == 1:
                s += "* "
            else:
                s += str(puzzle[i][j])+" "
        print(s)