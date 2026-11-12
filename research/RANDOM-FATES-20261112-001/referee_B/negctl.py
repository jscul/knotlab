import sys; sys.path.insert(0, '.')
from t1_check import check
for n, E in [(6, [(0,1,2),(2,3,4),(4,5,0)]), (5, [(0,1,2),(0,1,3),(0,1,4)]), (7,[(0,1,2),(2,3,4),(4,5,6),(6,0,3)])]:
    st = {"graphs": 0, "pairs": 0, "bonds": 0, "chains": 0, "by_d": {}, "bond_eq_leafset": 0, "max_hub": 0}
    try:
        v = check(n, E, st)
    except Exception as ex:
        v = ['exception', repr(ex)]
    print(E, v[:6])
