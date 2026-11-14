"""Completion pass (agreed with the coordinator before the run): on the travelling new-kind bases of the counted prefixes whose second
direction is forced but not certified by the main arm's certificates (tori, strips periodic across), try certificates repeating with
periods P along and Q across outside a finite box on all four sides (two copies of each tail block constrained equal; sound).

    .venv/bin/python -B research/WEIGHTS-20261112-001/completion.py
Output: research/WEIGHTS-20261112-001/completion.json
"""
import importlib.util
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
spec = importlib.util.spec_from_file_location("w", os.path.join(ROOT, "experiments/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts/census.py"))
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)
S, C, T, F = W.S, W.C, W.T, W.S.F
from pysat.solvers import Minisat22  # noqa: E402


class Eventual4:
    def __init__(self, fr, X0, X1, Y0, Y1, P, Q):
        self.b = (X0, X1, Y0, Y1, P, Q)
        A_, B_ = range(X0 - 2 * P, X1 + 2 * P), range(Y0 - 2 * Q, Y1 + 2 * Q)
        idx = {(a, b): i + 1 for i, (a, b) in enumerate(itertools.product(A_, B_))}
        cl = []
        for a, b in idx:
            z = fr.cell(a, b)
            for k in fr.kinds:
                pts = [fr.co((z[0] + dx, z[1] + dy)) for dx, dy in k]
                if all(q in idx for q in pts):
                    v = [idx[q] for q in pts]
                    cl += [v, [-w for w in v]]
        for a0 in (X0 - 2 * P, X1):
            for a in range(a0, a0 + P):
                for b in B_:
                    cl += [[idx[(a, b)], -idx[(a + P, b)]], [-idx[(a, b)], idx[(a + P, b)]]]
        for b0 in (Y0 - 2 * Q, Y1):
            for b in range(b0, b0 + Q):
                for a in A_:
                    cl += [[idx[(a, b)], -idx[(a, b + Q)]], [-idx[(a, b)], idx[(a, b + Q)]]]
        self.idx, self.s = idx, Minisat22(bootstrap_with=cl)
        self.ok = self.s.solve()

    def carries(self, cells, p):
        lits = [self.idx[c] * (1 if v else -1) for c, v in zip(cells, p)]
        return not any(-l in lits for l in lits) and self.s.solve(assumptions=lits)


def try_cert(kinds, A, p, tt, fl):
    tp, g, u = T.frame(tt)
    fr = T.Frame(kinds, tp, u)
    cells = [fr.co(c) for c in A] + [fr.co((c[0] + tt[0], c[1] + tt[1])) for c in A]
    vals = list(p) + [v ^ fl for v in p]
    X0, X1 = min(a for a, _ in cells) - 2, max(a for a, _ in cells) + 3
    Y0, Y1 = min(b for _, b in cells) - 2, max(b for _, b in cells) + 3
    s = F.along_span(fr)
    for P in range(max(1, s), 2 * s + 5):
        for Q in range(2, 17):
            e = Eventual4(fr, X0, X1, Y0, Y1, P, Q)
            if not e.ok:
                e.s.delete()
                continue
            Acells = cells[:len(A)]
            ok = e.carries(cells, vals) and all(e.carries(Acells, (0,) + q) for q in itertools.product((0, 1), repeat=len(A) - 1))
            e.s.delete()
            if ok:
                return {"P": P, "Q": Q}
    return None


def main():
    summ = json.load(open(os.path.join(HERE, "summary.json")))
    O = os.path.join(ROOT, "artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts")
    recs = {}
    for line in open(os.path.join(O, "census.jsonl")):
        r = json.loads(line)
        if "beta" in r:
            recs[(r["beta"], r["sample"])] = r
    for line in open(os.path.join(O, "resume_census", "results.jsonl")):
        r = json.loads(line)
        if r.get("status") == "ok":
            recs[(r["result"]["beta"], r["result"]["sample"])] = r["result"]
    out = []
    for beta in (0, 1, 2):
        stop = summ[str(beta)]["stopping index"]
        for i in range(stop + 1):
            for rr, v in recs.get((beta, i), {"by r": {}})["by r"].items():
                if v["class"] != "travels" or v["stratum"] != "new kinds":
                    continue
                m = v.get("main", {})
                if m.get("rank certified") == 2 or m.get("rank forced") != 2:
                    continue
                kinds = [tuple(map(tuple, k)) for k in v["kinds"]]
                cert = [tuple(d) for d in m["certified directions"]]
                unc = [tuple(d) for d in m["forced, uncertified"]]
                idx, cl = C.window(kinds, (-30, 30, -30, 30))
                s = Minisat22(bootstrap_with=cl)
                got = None
                for size in range(2, 5):
                    for A in itertools.combinations(S.BOX3, size):
                        if (0, 0) not in A:
                            continue
                        for tail in itertools.product((0, 1), repeat=size - 1):
                            pp = (0,) + tail
                            assum = [idx[c] * (1 if x else -1) for c, x in zip(A, pp)]
                            if not s.solve(assumptions=assum):
                                continue
                            for d in unc:
                                if cert and all(d[0] * c[1] - d[1] * c[0] == 0 for c in cert):
                                    continue
                                for k in (1, 2, 3, 4):
                                    tt = (d[0] * k, d[1] * k)
                                    for fl in (0, 1):
                                        if all(not s.solve(assumptions=assum + [idx[(c[0] + tt[0], c[1] + tt[1])] * (-1 if (x ^ fl) else 1)]) for c, x in zip(A, pp)):
                                            cc = try_cert(kinds, A, pp, tt, fl)
                                            if cc:
                                                got = {"direction": list(d), "k": k, "A": [list(c) for c in A], "p": list(pp), "certificate": cc}
                                                break
                                    if got:
                                        break
                                if got:
                                    break
                            if got:
                                break
                        if got:
                            break
                    if got:
                        break
                s.delete()
                out.append({"beta": beta, "sample": i, "r": rr, "certified now": got is not None, "detail": got})
                print(out[-1], flush=True)
    json.dump(out, open(os.path.join(HERE, "completion.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
