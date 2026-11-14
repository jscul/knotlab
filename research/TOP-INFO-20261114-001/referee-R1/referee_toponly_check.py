"""Referee's own check of Codex's top-only bond in fea4933ecaf1 (TOP-INFO-R1): unfold the family from its census key to a finite
depth (leaves unconstrained, a relaxation whose projections decrease to the usual limit), and compute the projections of
{main port 1, main own 8, one own distinction of the target copy on S-call word [1,1,1]} by SAT, at several truncation depths."""
import itertools, json, sys
from pysat.solvers import Glucose4
key = json.loads('[[3,0,[["K",[0,1,2]],["SELF",[0,1,2]],["K",[0,2,1]],["SELF",[1,0,2]],["SELF",[0,1,2]]]],[3,4,[["SELF",[6,2,3]],["K",[3,0,4]],["K",[1,0,4]],[0,[6,0,1]],[0,[0,5,4]],[0,[1,4,0]],[0,[3,5,4]],["SELF",[6,4,5]]]],[3,6,[[1,[8,1,6]]]]]')
def nae(cl, a, b, c):
    cl.append([a, b, c]); cl.append([-a, -b, -c])
def run(Dtot):
    nv = [0]
    def new():
        nv[0] += 1; return nv[0]
    cl = []
    main = [new() for _ in range(9)]
    target = {}
    def build(defn, ports, depth, word):
        nports, nown, body = key[defn]
        pos = list(ports) + [new() for _ in range(nown)]
        if defn == 1 and word == (1, 1, 1):
            target['own'] = pos[3:]
        scall = 0
        for item in body:
            if item[0] == "K":
                nae(cl, *[pos[i] for i in item[1]])
            elif item[0] == "SELF":
                if defn == 0:
                    continue  # def 0 has no own distinctions: its SELF copies repeat the same knot on its ports
                if depth < Dtot:
                    build(defn, [pos[i] for i in item[1]], depth + 1, word + (scall,) if word is not None else None)
                scall += 1
            else:
                build(item[0], [pos[i] for i in item[1]], depth, None)
    # main = definition 2; its call to S starts the S-word at absolute depth 1
    nports, nown, body = key[2]
    for item in body:
        build(item[0], [main[i] for i in item[1]], 1, ())
    res = []
    for k, t in enumerate(target.get('own', [])):
        idx = [main[1], main[8], t]
        with Glucose4(bootstrap_with=cl) as s:
            def allowed(vs):
                return [bits for bits in itertools.product((0, 1), repeat=len(vs))
                        if s.solve(assumptions=[v if b else -v for v, b in zip(vs, bits)])]
            tri = allowed(idx)
            pairs = [len(allowed(list(p))) for p in itertools.combinations(idx, 2)]
        res.append({"target_own_position": 3 + k, "triple_allowed": len(tri), "pairs_allowed": pairs,
                    "bond": len(tri) < 8 and all(p == 4 for p in pairs)})
    return {"Dtot": Dtot, "vars": nv[0], "clauses": len(cl), "results": res}
for D in (4, 6, 8, 10):
    print(json.dumps(run(D)), flush=True)
