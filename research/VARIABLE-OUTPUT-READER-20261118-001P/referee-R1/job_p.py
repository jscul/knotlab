"""Shared-runner job for the referee's check of VARIABLE-OUTPUT-READER-20261118-001P (own code: the referee's 001F serial-law engine
and exact bond tables, and its 001O one-spent family generator; none of the study's C++ or Python is run or imported).

Parts:
- E: the width-31 example of controls.md, replayed on its literal names: each chronological support is a lawful serial join (its
  inputs loose at distinct earlier junctions that pass the parent test, two or three fresh outputs, the one-spent family's moves);
  the same for the rival with 23 replaced by 25 at the six-place junction, and with 23 replaced by 26; their legal triples; the
  readings K = D + 1 the note quotes; and the number of the 465 pair entries that differ through D = 4, through D = 5 and in full.
- S (per width 31, 33): every physical one-spent member (the referee's 001O generator, regenerated here with the width bound), and
  for each with a legal triple and one six-place junction H (its loose pair F, its four other names A):
  - one-attachment exchanges as the sweep counts them (remove one name of A, add one name loose at another junction), split by
    whether the added name has the removed one's small holder, with the funnel of necessary conditions read from the source
    table alone: four distinct holders; K(z, a) = K(z, b) = 6 for F = {a, b}; K <= 6 to all three retained names;
  - every overlapping replacement A' (any 1 to 4 names exchanged): four distinct small holders, every pair of F + A' at K <= 6 in
    the source (a lawful rival's six-place star is a bond, so a match through D = 5 needs this); each survivor other than A has
    its rival table computed and compared through D = 5 on the same names.

  .venv/bin/python -B scripts/longrun.py launch research/VARIABLE-OUTPUT-READER-20261118-001P/referee-R1/job_p.py \\
      --out runs/referee-vor-p --unit referee-vor-p --workers 4 --case-timeout 14400 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
PARAMS = {}

EXAMPLE = [(0, 1, 2), (0, 3, 4, 5), (3, 6, 7, 8), (1, 6, 9, 10, 11), (4, 9, 12, 13), (7, 12, 14, 15), (10, 14, 16, 25),
           (2, 16, 17, 18), (5, 17, 19, 20), (8, 19, 21, 22), (11, 18, 21, 23, 26), (13, 20, 23, 24, 27, 28), (15, 22, 24, 29, 30)]


def setup(params):
    PARAMS.update(params)


def owners(J):
    own = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            own[x].append(k)
    return own


def replay(J):
    """Is the chronological list a lawful serial history?  Returns (lawful, per-step (parents, fresh))."""
    import referee_f as F
    steps = []
    for k in range(1, len(J)):
        pre = [list(S) for S in J[:k]]
        T = F.from_supports(pre)
        own = owners(pre)
        ins = [x for x in J[k] if x in own]
        if any(len(own[x]) != 1 for x in ins):
            return False, steps
        P = tuple(own[x][0] for x in ins)
        fresh = len(J[k]) - len(ins)
        ok = F.legal_sites(T, P) and fresh in (2, 3) and len(ins) in (1, 2, 3)
        steps.append((list(map(int, P)), int(fresh), bool(ok)))
        if not ok:
            return False, steps
    return True, steps


def part_e():
    import referee_f as F
    out = {}
    rows = {}
    for name, swap in (("source", None), ("rival 23 -> 25", (23, 25)), ("rival 23 -> 26", (23, 26))):
        J = [tuple(sorted(swap[1] if (x == swap[0] and k == 11) else x for x in S)) if swap else S for k, S in enumerate(EXAMPLE)]
        ok, steps = replay(J)
        n = 31
        K, _ = F.bond_table([list(S) for S in J], n)
        T = F.from_supports([list(S) for S in J])
        lt = sorted(sorted(t) for t in F.legal_triples(T, [list(S) for S in J]))
        rows[name] = K
        out[name] = {"lawful in this order": ok, "steps (parents, fresh, legal)": steps, "legal triples": lt,
                     "six-place junctions": [list(S) for S in J if len(S) == 6]}
    K0 = rows["source"]
    out["readings in the source, K"] = {f"{a},{b}": int(K0[a][b]) for a, b in ((27, 25), (28, 25), (13, 25), (20, 25), (24, 25))}
    for name in ("rival 23 -> 25", "rival 23 -> 26"):
        K1 = rows[name]
        pairs = list(itertools.combinations(range(31), 2))
        clip = lambda v, c: v if v <= c else c + 1  # noqa: E731
        out[f"{name}: pairs"] = len(pairs)
        out[f"{name}: entries differing through D = 4"] = int(sum(clip(K0[a][b], 5) != clip(K1[a][b], 5) for a, b in pairs))
        out[f"{name}: entries differing through D = 5"] = int(sum(clip(K0[a][b], 6) != clip(K1[a][b], 6) for a, b in pairs))
        out[f"{name}: entries differing in full"] = int(sum(K0[a][b] != K1[a][b] for a, b in pairs))
    return out


def generate(wmax):
    """The referee's 001O one-spent generator, regenerated to width wmax, physical types (one process)."""
    os.environ["WMAX"] = str(wmax)
    sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001O/referee-R1"))
    import importlib
    import family_o as FO
    importlib.reload(FO)
    import referee_f as F
    import networkx as nx
    level = [(F.seed(), 0, 0, -1, 0)]
    members = defaultdict(list)
    while level:
        kids = [c for s in level for c in FO.children(s)]
        buckets = defaultdict(list)
        for c in kids:
            buckets[FO.key(c)].append(c)
        level = [s for b in buckets.values() for s in FO.dedup(b)]
        for s in level:
            if s[2] == 2 and s[4] == 1:
                members[F.width(s[0])].append(s[0])
    T = members.get(wmax, [])
    by = defaultdict(list)
    for t in T:
        by[F.wl(t)].append(t)
    reps = []
    for b in by.values():
        local = []
        for t in b:
            G = F.graph(t)
            if not any(nx.is_isomorphic(G, H, node_match=F.nm) for H in local):
                local.append(G)
                reps.append(t)
    return reps


def part_s(w):
    import referee_f as F
    reps = generate(w)
    s = Counter()
    s["physical members"] = len(reps)
    survivors = []
    for T in reps:
        J, n = F.supports(T)
        lt = F.legal_triples(T, J)
        if not lt:
            continue
        s["with a legal triple"] += 1
        six = [k for k, S in enumerate(J) if len(S) == 6]
        if len(six) != 1:
            s["live with two six-place junctions"] += 1
            continue
        H = six[0]
        own = owners(J)
        Fl = [x for x in J[H] if len(own[x]) == 1]
        A = [x for x in J[H] if len(own[x]) == 2]
        if len(Fl) != 2 or len(A) != 4:
            s["six-place junction not two loose and four attached"] += 1
            continue
        K, _ = F.bond_table(J, n)
        holder = {x: [k for k in own[x] if k != H][0] for x in A}
        loose_out = [x for x, ks in own.items() if len(ks) == 1 and ks[0] != H]
        for x in loose_out:
            holder[x] = own[x][0]
        a, b = Fl
        # the sweep's one-attachment exchanges and its funnel
        for r in A:
            kept = [x for x in A if x != r]
            for z in loose_out:
                same = holder[z] == holder[r]
                tag = "same holder" if same else "different holder"
                s[f"one exchange, {tag}"] += 1
                hs = {holder[x] for x in kept} | {holder[z]}
                if len(hs) != 4:
                    continue
                s[f"one exchange, {tag}, four distinct holders"] += 1
                if not (K[z][a] == 6 and K[z][b] == 6):
                    continue
                s[f"one exchange, {tag}, K = 6 to both of F"] += 1
                if all(K[z][x] <= 6 for x in kept):
                    s[f"one exchange, {tag}, K <= 6 to all three retained"] += 1
        # every overlapping replacement
        pool = A + loose_out
        for Ap in itertools.combinations(pool, 4):
            if set(Ap) == set(A) or not set(Ap) & set(A):
                continue
            if len({holder[x] for x in Ap}) != 4:
                continue
            s["overlapping replacements, four distinct holders"] += 1
            star = list(Fl) + list(Ap)
            if all(K[x][y] <= 6 for x, y in itertools.combinations(star, 2)):
                s["... every pair of the new star at K <= 6 in the source"] += 1
                J2 = [list(S) for S in J]
                J2[H] = sorted(star)
                K2, _ = F.bond_table(J2, n)
                same = all(min(K[x][y], 7) == min(K2[x][y], 7) for x, y in itertools.combinations(range(n), 2))
                s["... rival table equal through D = 5"] += same
                if same:
                    survivors.append({"supports": J, "rival six-place star": star})
    return {"counts": {k: int(v) for k, v in s.items()}, "matches through D = 5": json.loads(json.dumps(survivors[:10], default=int))}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("E", {"part": "E"})] + [(f"S-{w}", {"part": "S", "w": w}) for w in (33, 31)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "E":
        return part_e()
    return part_s(p["w"])
