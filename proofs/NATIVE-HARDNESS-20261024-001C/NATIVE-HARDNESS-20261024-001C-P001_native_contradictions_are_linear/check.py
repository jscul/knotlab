#!/usr/bin/env python3
"""Check of NATIVE-HARDNESS-20261024-001C-P001 (standard library only, seed 20261024).

Networks: knots (three-place relations with every pair of places unconstrained) whose slots are paired into internal edges between
distinct knots or left as legs, pinned to 0 or 1 or unpinned. Encoding: one clause per excluded tuple of each knot, pinned values
substituted. Checks:
- Theorem 1 (half rule): in random unsatisfiable connected closed networks, every knot whose removal keeps the network connected has a
  parity relation as its face on its internal edges (a constant, a wire or a parity knot), and the rest allows exactly the
  complementary relation;
- Theorem 2 (linear blocks): in random unsatisfiable networks, every 2-edge-connected component, with each bridge leaving it pinned to
  the value forced by the far side, has only parity faces and is an unsatisfiable system of parity equations;
- Corollary 3: the decision procedure (peel unpinned legs; along the bridge tree, a component is satisfiable if a child side allows
  both values or a knot allows more than half of its component-edge states, and otherwise by Gaussian elimination) agrees with a
  solver on random networks of mixed laws with pinned and unpinned legs, connected or not.
Controls: with hubs (not-all-equal on all ten triples of five places) a knot whose removal keeps the network connected allows six of
eight states, yet the network is unsatisfiable; a knot that is a cut vertex can allow more than half in an unsatisfiable network; the
procedure without its Gaussian step, or with the half rule reversed, disagrees with the solver.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))


def knots():
    out = []
    for m in range(256):
        R = frozenset(CUBE[i] for i in range(8) if m >> i & 1)
        if 0 < len(R) < 8 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def excluded(R):
    return [t for t in CUBE if t not in R]


def is_parity(R):
    return len(excluded(R)) == 4


def clauses_of(scopes, pins, Rs, keep=None):
    out = []
    for k, (sc, R) in enumerate(zip(scopes, Rs)):
        if keep is not None and k not in keep:
            continue
        for t in excluded(R):
            if any(v in pins and pins[v] != b for v, b in zip(sc, t)):
                continue
            out.append([v if b == 0 else -v for v, b in zip(sc, t) if v not in pins])
    return out


def satisfiable(clauses):
    if any(not c for c in clauses):
        return False
    return _dpll([list(c) for c in clauses], {})


def _dpll(clauses, assign):
    while True:
        unit, new = None, []
        for c in clauses:
            rest, done = [], False
            for lit in c:
                a = assign.get(abs(lit))
                if a is None:
                    rest.append(lit)
                elif (lit > 0) == a:
                    done = True
                    break
            if done:
                continue
            if not rest:
                return False
            if len(rest) == 1 and unit is None:
                unit = rest[0]
            new.append(rest)
        clauses = new
        if unit is None:
            break
        assign = dict(assign)
        assign[abs(unit)] = unit > 0
    if not clauses:
        return True
    count = {}
    for c in clauses:
        for lit in c:
            count[abs(lit)] = count.get(abs(lit), 0) + 1
    v = max(count, key=count.get)
    return any(_dpll(clauses, {**assign, v: val}) for val in (True, False))


def random_network(rng, n, L, free_prob=0.0, connected=True):
    """no loops; L legs, each pinned at random or (with probability free_prob) unpinned"""
    while True:
        slots = [(v, p) for v in range(n) for p in range(3)]
        rng.shuffle(slots)
        legs, rest = slots[:L], slots[L:]
        pairs = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]
        if any(a[0] == b[0] for a, b in pairs):
            continue
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for a, b in pairs:
            parent[find(a[0])] = find(b[0])
        if connected and len({find(v) for v in range(n)}) != 1:
            continue
        var, nv, pins = {}, 0, {}
        for a, b in pairs:
            nv += 1
            var[a] = var[b] = nv
        for s in legs:
            nv += 1
            var[s] = nv
            if rng.random() >= free_prob:
                pins[nv] = rng.randint(0, 1)
        return [tuple(var[(v, p)] for p in range(3)) for v in range(n)], pins


def occurrences(scopes):
    occ = {}
    for k, sc in enumerate(scopes):
        for v in sc:
            occ.setdefault(v, []).append(k)
    return occ


def bridges(nodes, E):
    adj = {k: [] for k in nodes}
    for v, (a, b) in E.items():
        adj[a].append((b, v))
        adj[b].append((a, v))
    disc, low, out, clock = {}, {}, set(), [0]

    def dfs(u, pe):
        disc[u] = low[u] = clock[0]
        clock[0] += 1
        for w, e in adj[u]:
            if e == pe:
                continue
            if w in disc:
                low[u] = min(low[u], disc[w])
            else:
                dfs(w, e)
                low[u] = min(low[u], low[w])
                if low[w] > disc[u]:
                    out.add(e)
    for s in nodes:
        if s not in disc:
            dfs(s, None)
    return out


def components(nodes, E, br):
    parent = {k: k for k in nodes}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for v, (a, b) in E.items():
        if v not in br:
            parent[find(a)] = find(b)
    comps = {}
    for k in nodes:
        comps.setdefault(find(k), set()).add(k)
    return comps, {k: find(k) for k in nodes}


def face(R, sc, pins):
    """face of knot R on its unpinned slots: (list of variables, set of allowed tuples)"""
    ins = [i for i, v in enumerate(sc) if v not in pins]
    allowed = {tuple(t[i] for i in ins) for t in R if all(t[i] == pins[v] for i, v in enumerate(sc) if v in pins)}
    return [sc[i] for i in ins], allowed


def parity_class(allowed, d):
    """the parity (0 or 1) if `allowed` is one parity class of {0,1}^d, else None"""
    pars = {sum(t) % 2 for t in allowed}
    return pars.pop() if len(allowed) == 2 ** (d - 1) and len(pars) == 1 else None


def gaussian_consistent(rows):
    pivots = {}
    for vs, rhs in rows:
        vs = set(vs)
        while vs:
            p = max(vs)
            if p not in pivots:
                pivots[p] = (vs, rhs)
                break
            pv, pr = pivots[p]
            vs ^= pv
            rhs ^= pr
        else:
            if rhs:
                return False
    return True


def decide(scopes, pins, Rs, mode="exact"):
    """Corollary 3. mode 'no-gauss' declares every all-half component satisfiable; 'reversed-half' declares a component with a knot
    allowing more than half unsatisfiable (controls)."""
    occ = occurrences(scopes)
    n = len(scopes)
    loose = {v for v, ks in occ.items() if len(ks) == 1 and v not in pins}
    alive = set(range(n))
    stack = [k for k in alive if any(v in loose for v in scopes[k])]
    while stack:
        k = stack.pop()
        if k not in alive:
            continue
        alive.discard(k)
        for v in scopes[k]:
            for j in occ[v]:
                if j in alive:
                    loose.add(v)
                    stack.append(j)
    if not alive:
        return True
    E = {v: tuple(ks) for v, ks in occ.items() if len(ks) == 2 and ks[0] in alive and ks[1] in alive}
    br = bridges(sorted(alive), E)
    comps, comp_of = components(sorted(alive), E, br)
    ends = {f: E[f] for f in br}
    memo = {}

    def child_values(C_id, parent_bridge):
        out = {}
        for g, (a, b) in ends.items():
            if g == parent_bridge or C_id not in (comp_of[a], comp_of[b]):
                continue
            other = comp_of[b] if comp_of[a] == C_id else comp_of[a]
            out[g] = side(g, other)
        return out

    def side(f, C_id):
        if (f, C_id) not in memo:
            kids = child_values(C_id, f)
            memo[(f, C_id)] = {c for c in (0, 1) if component_satisfiable(C_id, {**pins, f: c}, kids)}
        return memo[(f, C_id)]

    def component_satisfiable(C_id, p, kids):
        p = dict(p)
        for g, vals in kids.items():
            if len(vals) == 2:
                return True              # a knot of the component has an unconstrained slot: peel (K2)
            if not vals:
                return False             # only reachable under the control mutations: a side allowing no value
            (p[g],) = vals
        rows, more_than_half = [], False
        for k in comps[C_id]:
            vs, allowed = face(Rs[k], scopes[k], p)
            d = len(vs)
            if d == 0:
                if not allowed:
                    return False
                continue
            if len(allowed) > 2 ** (d - 1):
                more_than_half = True
                continue
            rows.append((vs, parity_class(allowed, d)))
        if more_than_half:
            return mode != "reversed-half"
        if mode == "no-gauss":
            return True
        return gaussian_consistent(rows)

    cparent = {k: k for k in alive}

    def cfind(a):
        while cparent[a] != a:
            cparent[a] = cparent[cparent[a]]
            a = cparent[a]
        return a
    for v, (a, b) in E.items():
        cparent[cfind(a)] = cfind(b)
    roots = {}
    for c in comps:
        roots.setdefault(cfind(c), c)
    return all(component_satisfiable(r, pins, child_values(r, None)) for r in roots.values())


def connected_without(nodes, E, k):
    rest = [v for v in nodes if v != k]
    if not rest:
        return True
    adj = {v: set() for v in rest}
    for _, (a, b) in E.items():
        if a != k and b != k:
            adj[a].add(b)
            adj[b].add(a)
    seen, stack = {rest[0]}, [rest[0]]
    while stack:
        u = stack.pop()
        for w in adj[u] - seen:
            seen.add(w)
            stack.append(w)
    return len(seen) == len(rest)


def leg_values(scopes, pins, Rs, keep, legs):
    base = clauses_of(scopes, pins, Rs, keep)
    return {t for t in itertools.product((0, 1), repeat=len(legs))
            if satisfiable(base + [[v] if b else [-v] for v, b in zip(legs, t)])}


def half_rule_and_blocks(rng, K):
    PAR = [R for R in K if is_parity(R)]
    out = {"unsatisfiable connected closed networks": 0, "knots whose removal keeps the network connected": 0,
           "with a parity face and the complementary rest": 0, "2-edge-connected components": 0,
           "components that are unsatisfiable parity systems": 0}
    while out["unsatisfiable connected closed networks"] < 600:
        n = rng.randint(2, 10)
        L = rng.randint(0, n + 2)
        if (3 * n - L) % 2:
            L += 1
        if L > 3 * n - 2:
            continue
        scopes, pins = random_network(rng, n, L)
        mix = rng.random()
        Rs = [rng.choice(PAR) if rng.random() < mix else rng.choice(K) for _ in range(n)]
        if satisfiable(clauses_of(scopes, pins, Rs)):
            continue
        out["unsatisfiable connected closed networks"] += 1
        occ = occurrences(scopes)
        E = {v: tuple(ks) for v, ks in occ.items() if len(ks) == 2}
        nodes = list(range(n))
        for k in nodes:
            if not connected_without(nodes, E, k):
                continue
            out["knots whose removal keeps the network connected"] += 1
            vs, allowed = face(Rs[k], scopes[k], pins)
            d = len(vs)
            Q = leg_values(scopes, pins, Rs, set(nodes) - {k}, vs) if d else {()}
            pc = parity_class(allowed, d) if d else None
            if d and pc is not None and Q == {t for t in itertools.product((0, 1), repeat=d) if sum(t) % 2 != pc}:
                out["with a parity face and the complementary rest"] += 1
        br = bridges(nodes, E)
        comps, comp_of = components(nodes, E, br)
        for cid, C in comps.items():
            out["2-edge-connected components"] += 1
            p = dict(pins)
            forced = True
            for f in br:
                a, b = E[f]
                if (comp_of[a] == cid) == (comp_of[b] == cid):
                    continue
                outside = b if comp_of[a] == cid else a
                vals = leg_values(scopes, pins, Rs, far_side(E, f, outside), [f])
                if len(vals) != 1:
                    forced = False
                    break
                p[f] = next(iter(vals))[0]
            if not forced:
                continue
            faces = [face(Rs[k], scopes[k], p) for k in C]
            rows = [(vs, parity_class(al, len(vs))) for vs, al in faces if vs]
            parity_faces = all(pc is not None for _, pc in rows)
            unsat = not satisfiable(clauses_of(scopes, p, Rs, C))
            linear_unsat = any(not al for vs, al in faces if not vs) or (parity_faces and not gaussian_consistent(rows))
            if parity_faces and unsat and linear_unsat:
                out["components that are unsatisfiable parity systems"] += 1
    return out


def far_side(E, f, start):
    """knots reachable from `start` without using edge f"""
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for v, (a, b) in E.items():
            if v == f:
                continue
            for x, y in ((a, b), (b, a)):
                if x == u and y not in seen:
                    seen.add(y)
                    stack.append(y)
    return seen


def procedure_checks(rng, K):
    PAR = [R for R in K if is_parity(R)]
    out = {"networks": 0, "unsatisfiable": 0, "procedure agrees": 0, "without the Gaussian step agrees": 0,
           "with the half rule reversed agrees": 0}
    for _ in range(20000):
        n = rng.randint(1, 12)
        L = 3 if n == 1 else rng.randint(0, n + 2)   # a single knot with fewer legs could only carry a loop
        if (3 * n - L) % 2:
            L += 1
        if L > 3 * n:
            continue
        scopes, pins = random_network(rng, n, L, free_prob=rng.choice((0.0, 0.0, 0.1)), connected=rng.random() < 0.8)
        mix = rng.random()
        Rs = [rng.choice(PAR) if rng.random() < mix else rng.choice(K) for _ in range(n)]
        truth = satisfiable(clauses_of(scopes, pins, Rs))
        out["networks"] += 1
        out["unsatisfiable"] += not truth
        out["procedure agrees"] += decide(scopes, pins, Rs) == truth
        out["without the Gaussian step agrees"] += decide(scopes, pins, Rs, "no-gauss") == truth
        out["with the half rule reversed agrees"] += decide(scopes, pins, Rs, "reversed-half") == truth
    return out


def controls(K, proc):
    nae = frozenset(t for t in CUBE if 0 < sum(t) < 3)
    triples = list(itertools.combinations(range(1, 6), 3))
    hub_unsat = not satisfiable(clauses_of(triples, {}, [nae] * 10))
    R = frozenset(t for t in CUBE if t not in {(0, 0, 0), (1, 1, 0)})
    # knot 0 on (x, y, z) = (1, 2, 3); pendant knots force each to 0; knot 0 is a cut vertex allowing six of eight states
    scopes = [(1, 2, 3), (1, 4, 5), (2, 6, 7), (3, 8, 9)]
    pins = {4: 1, 6: 1, 8: 1, 5: 0, 7: 0, 9: 0}
    cut_unsat = not satisfiable(clauses_of(scopes, pins, [R] * 4))
    return {"with hubs a non-cut knot allowing six of eight states sits in an unsatisfiable network": hub_unsat,
            "a cut-vertex knot allowing six of eight states sits in an unsatisfiable network": cut_unsat,
            "the procedure without its Gaussian step disagrees with the solver": proc["without the Gaussian step agrees"]
            < proc["networks"],
            "the procedure with the half rule reversed disagrees with the solver": proc["with the half rule reversed agrees"]
            < proc["networks"]}


def main() -> int:
    sys.setrecursionlimit(10000)
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    K = knots()
    half = half_rule_and_blocks(rng, K)
    proc = procedure_checks(rng, K)
    ctl = controls(K, proc)
    ok = (half["knots whose removal keeps the network connected"] == half["with a parity face and the complementary rest"] > 0
          and half["2-edge-connected components"] == half["components that are unsatisfiable parity systems"] > 0
          and proc["procedure agrees"] == proc["networks"] and proc["unsatisfiable"] > 0
          and all(ctl.values()))
    result["checks"] = {"half rule and linear blocks": half, "decision procedure": proc}
    result["controls"] = ctl
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": ctl}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
