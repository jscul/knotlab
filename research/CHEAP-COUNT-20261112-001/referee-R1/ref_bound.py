"""CHEAP-COUNT-R1: does any parity gadget have at most 9 knots, for any number of fresh distinctions?

In a gadget with the fewest knots, every fresh distinction lies in at least two knots (a knot whose only fresh distinction lies in
no other knot never constrains anything and could be deleted) and every named one in at least one (else the relation would not
depend on it). So 3m >= 4 + 2f', and m <= 9 needs at most f' = 11 fresh distinctions used. One SAT query with 11 fresh distinctions
and at most 9 knots therefore decides every f. The referee's own encoding: selector per knot; each odd named state is refuted by a
chosen knot for every fresh assignment; each even one has its own existential fresh assignment.
  ref_bound.py F M  ->  prints SAT/UNSAT and writes result_bound_<F>_<M>.json
"""
import itertools, json, sys, time
from pathlib import Path
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

F, M = int(sys.argv[1]), int(sys.argv[2])
n = 4 + F
knots = [k for k in itertools.combinations(range(n), 3) if any(v >= 4 for v in k)]
sel = {k: i + 1 for i, k in enumerate(knots)}
top = len(knots)
cl = []
for named in itertools.product((0, 1), repeat=4):
    if sum(named) % 2 == 1:
        for fr in itertools.product((0, 1), repeat=F):
            x = named + fr
            cl.append([sel[k] for k in knots if x[k[0]] == x[k[1]] == x[k[2]]])
    else:
        var = {}
        for v in range(4, n):
            top += 1
            var[v] = top
        for k in knots:
            pos, neg, sat_pos, sat_neg = [], [], False, False
            for v in k:
                if v < 4:
                    sat_pos |= named[v] == 1
                    sat_neg |= named[v] == 0
                else:
                    pos.append(var[v]); neg.append(-var[v])
            if not sat_pos:
                cl.append([-sel[k]] + pos)
            if not sat_neg:
                cl.append([-sel[k]] + neg)
enc = CardEnc.atmost(lits=list(sel.values()), bound=M, top_id=top, encoding=EncType.seqcounter)
t0 = time.time()
with Solver(name="cadical153", bootstrap_with=cl + enc.clauses) as s:
    ok = s.solve()
    g = [k for k in knots if sel[k] in set(l for l in s.get_model() if l > 0)] if ok else None
res = dict(F=F, M=M, sat=ok, gadget=g, seconds=round(time.time() - t0, 1))
print(json.dumps(res))
json.dump(res, open(Path(__file__).with_name(f"result_bound_{F}_{M}.json"), "w"), indent=1)
