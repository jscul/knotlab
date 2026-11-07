import json, threading, time
from pysat.solvers import Solver
data = json.load(open("spheres.json"))
for k in sorted(data, key=int):
    d = data[k]
    cl = []
    for L, sg in zip(d["lines"], d["signs"]):
        lits = [(p + 1) * (-1 if s else 1) for p, s in zip(L, sg)]
        cl.append(lits); cl.append([-x for x in lits])
    t0 = time.time()
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        timer = threading.Timer(600, S.interrupt)
        timer.start()
        r = S.solve_limited(expect_interrupt=True)
        timer.cancel()
        st = S.accum_stats()
    dt = time.time() - t0
    res = "UNSAT" if r is False else ("SAT" if r else "TIMEOUT")
    print("k", k, "n", d["n"], "result", res, "conflicts", st.get("conflicts"), "time %.2f s" % dt, flush=True)
    if r is None:
        break
