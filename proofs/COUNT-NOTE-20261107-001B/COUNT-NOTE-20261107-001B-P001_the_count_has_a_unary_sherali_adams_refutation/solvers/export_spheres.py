import json, sys
sys.path.insert(0, "/home/jscul/p-vs-np-contact-first/proofs/TWO-ROUND-BRIDGE-20261106-001B/TWO-ROUND-BRIDGE-20261106-001B-P001_three_fold_spaces_are_an_euler_count")
import count_lib as C
out = {}
for k in range(2, 9):
    lines, signs, n = C.signed_space(C.octa_dual(k))
    out[k] = {"n": n, "lines": [list(L) for L in lines], "signs": [list(map(int, s)) for s in signs]}
json.dump(out, open("spheres.json", "w"))
print("exported", {k: (v["n"], len(v["lines"])) for k, v in out.items()})
