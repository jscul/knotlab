"""Shared-runner job for the referee's check of LATER-BOND-READING-20261119-001 (Codex), with the referee's own code: its
EXPLOSIVE-R1 grower (the program's rule), its exact least-bond MILP (bondmilp.py, checked against enumeration), its own branch
compression and shore enumeration, and GROWN-END-READING-R1's 239-junction construction.  Codex's start and permutation are read
from its artifact as data; none of its code is run.

Parts:
- S104: the 104-junction stage regrown from the literal start (sizes at ages 0, 1, 2; equal to the literal round additions); the
  exchange (the involution of full_group.maps[14], a <-> c) fixes every distinction of every live junction and changes the
  equations at ages 1 and 2 (with a certificate); the named entries by MILP on the literal graphs: K(4,10), K(10,16) at ages 1, 2;
  the quartets {0,3,24,26} -> {12,15,24,26} and {3,4,6,10} -> {6,10,15,16}.
- C104: the referee's own compression of the age-1 stage: the 20 starting junctions with no loose distinction are the core; every
  other component (with the exterior) is a branch meeting the core at one junction, replaced by one virtual link weighted by its
  maximum flow; every bond of the compressed host by shore enumeration; every compressed set of one to three bundle classes
  holding a moved class compared with its image, for all 24 listed maps; for the maps changing the equations, a four-class
  witness; the number of four-class sets the exchange changes.
- L104 (chunks): literal MILP comparisons on the age-1 stage, independent of the compression: every pair of bundles holding a moved
  bundle against its image; 2,000 random triples holding a moved distinction; and for 300 random core-only pairs and triples, the
  literal value against the compressed one.
- CONS-r (r = 2, 3, 4): the all-size family of constructive-proof.md, compressed (each branch a virtual link of weight M at age 1
  and 1 at age 2), its parameters from the text: the (r+1)-mark query finite and its image absent; the age-2 red pair 3L against
  its image; every set of at most r classes holding a moved class (r = 2, 3; a sample of 3,000 at r = 4) against its image, and
  its value below sM; the hubs' separating cost sM by maximum flow.
- G239: the 239-junction start grown to age 12: the separating cost of the growing part between its two attachment junctions
  (maximum flow) at every age, the equation change at every age, and the four-name query {y(2,8), uw(8,(2,8)), uw(0,(0,8)),
  uw(8,(0,8))} against its image by MILP at age 1.

  .venv/bin/python -B scripts/longrun.py launch research/LATER-BOND-READING-20261119-001/referee-R1/job_lbr.py \\
      --out runs/referee-lbr --unit referee-lbr --workers 3 --case-timeout 14400 --case-mem 3G --mem-max 10G
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/EXPLOSIVE-20261119-001/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/GROWN-END-READING-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
sys.path.insert(0, str(HERE))
ART = ROOT / "artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group_104.json"
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def rank(rows):
    basis, r = {}, 0
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p not in basis:
                basis[p] = x
                r += 1
                break
            x ^= basis[p]
    return r


def owners(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for x in s:
            own[x].append(j)
    return own


def graph(S):
    """Wired graph of a stage: vertices the junctions and the exterior (index len(S)); bundles of distinctions with the same
    holders.  Returns (n, bundles [(u, v, weight)], bundle of each distinction, distinctions of each bundle)."""
    own = owners(S)
    O = len(S)
    key = defaultdict(list)
    for x, js in own.items():
        key[tuple(sorted(js)) if len(js) == 2 else (js[0], O)].append(x)
    items = sorted(key.items())
    bundles = [(k[0], k[1], len(v)) for k, v in items]
    bof = {x: i for i, (k, v) in enumerate(items) for x in v}
    return O + 1, bundles, bof, [v for k, v in items]


def stages104():
    import job_expl as JX
    d = json.load(open(ART))
    G = JX.grower([list(s) for s in d["literal_start"]])
    st = [[sorted(s) for s in G.bits]]
    for _ in range(2):
        assert G.step(JX.floored, None, None) == "ok"
        st.append([sorted(s) for s in G.bits])
    pi = dict(map(tuple, d["full_group"]["maps"][14]["map"]))
    return d, st, pi


def part_s104():
    import bondmilp as B
    import job_ger as JG
    d, st, pi = stages104()
    out = {"sizes (junctions, distinctions) at ages 0, 1, 2": [[len(s), len({x for q in s for x in q})] for s in st]}
    lit = [sorted(q) for q in d["literal_start"]] + [sorted(q) for q in d["literal_round_additions"][0]]
    out["age 1 equals the literal start plus the literal round"] = sorted(map(tuple, lit)) == sorted(map(tuple, st[1]))
    out["the exchange is an involution"] = all(pi.get(pi[x], pi[x]) == x for x in pi)
    for k in (1, 2):
        S = st[k]
        own = owners(S)
        live = [j for j, q in enumerate(S) if any(len(own[x]) == 1 for x in q)]
        fixed = {x for j in live for x in S[j]}
        f = lambda x: pi.get(x, x)  # noqa: E731
        rows = [sum(1 << x for x in q) for q in S]
        r0 = rank(rows)
        moved_eq = [j for j, q in enumerate(S) if rank(rows + [sum(1 << f(x) for x in q)]) > r0]
        row = {"distinctions at live junctions": len(fixed), "all fixed": all(f(x) == x for x in fixed),
               "junction equations whose image leaves the span": moved_eq}
        if moved_eq:
            img = sum(1 << f(x) for x in S[moved_eq[0]])
            cert = JG.solve_even(S, img, len({x for q in S for x in q}))
            row["certificate size"] = None if cert is None else bin(cert).count("1")
        n, bd, bof, members = graph(S)
        for q in ([4, 10], [10, 16]):
            v, y = B.least_bond(n, bd, [bof[x] for x in q])
            row[f"K{tuple(q)}"] = v
        if k == 1:
            for q in ([0, 3, 24, 26], [12, 15, 24, 26], [3, 4, 6, 10], [6, 10, 15, 16]):
                v, y = B.least_bond(n, bd, [bof[x] for x in q])
                row[f"K{tuple(q)}"] = v
        out[f"age {k}"] = row
    return out


# ---- compression ----

def compress(S, core):
    """Core vertices kept; each other component of the wired graph minus the core and the exterior is a branch, which must meet
    the core at exactly one junction; it becomes a virtual link (that junction, exterior) weighted by its maximum flow."""
    import networkx as nx
    n, bd, bof, members = graph(S)
    O = n - 1
    core = set(core)
    rest = nx.Graph()
    rest.add_nodes_from(v for v in range(n - 1) if v not in core)
    for u, v, w in bd:
        if u not in core and v not in core and u != O and v != O:
            rest.add_edge(u, v)
    branches = []
    for comp in nx.connected_components(rest):
        att = {u if u in core else v for u, v, w in bd if (u in comp) != (v in comp) and (u in core or v in core)}
        assert len(att) == 1, att
        a = att.pop()
        F = nx.Graph()
        for u, v, w in bd:
            if (u in comp or u in (a, O)) and (v in comp or v in (a, O)) and not (u == a and v == O):
                if F.has_edge(u, v):
                    F[u][v]["capacity"] += w
                else:
                    F.add_edge(u, v, capacity=w)
        branches.append({"attach": a, "sites": sorted(comp), "capacity": nx.maximum_flow_value(F, a, O)})
    cidx = {v: i for i, v in enumerate(sorted(core))}
    hostO = len(cidx)
    hb, hmap = [], {}
    for i, (u, v, w) in enumerate(bd):
        if u in core and v in core:
            hmap[i] = len(hb)
            hb.append((cidx[u], cidx[v], w))
        elif (u in core and v == O) or (v in core and u == O):
            hmap[i] = len(hb)
            hb.append((cidx[u if u in core else v], hostO, w))
    for b in branches:
        b["link"] = len(hb)
        hb.append((cidx[b["attach"]], hostO, b["capacity"]))
    return {"n": hostO + 1, "bundles": hb, "map": hmap, "branches": branches, "literal": (n, bd, bof, members)}


def all_bonds(n, bundles):
    """Every bond of a small graph: shores S without the last vertex (the exterior), both shores connected; (weight, class mask)."""
    import numpy as np
    m = n - 1
    adj = [0] * n
    for u, v, w in bundles:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1

    def conn(S):
        start = S & -S
        seen = start
        frontier = start
        while frontier:
            nxt = 0
            f = frontier
            while f:
                low = f & -f
                nxt |= adj[low.bit_length() - 1]
                f ^= low
            nxt &= S & ~seen
            seen |= nxt
            frontier = nxt
        return seen == S
    wts, masks = [], []
    bw = [(u, v, w) for u, v, w in bundles]
    for S in range(1, 1 << m):
        if not conn(S) or not conn(full & ~S):
            continue
        tot, mk = 0, 0
        for i, (u, v, w) in enumerate(bw):
            if ((S >> u) & 1) != ((S >> v) & 1):
                tot += w
                mk |= 1 << i
        wts.append(tot)
        masks.append(mk)
    order = sorted(range(len(wts)), key=lambda i: wts[i])
    return [wts[i] for i in order], [masks[i] for i in order]


class Reader:
    """Least bond weight holding a set of classes, from the sorted bond list (masks may exceed 64 bits: split into words)."""

    def __init__(self, wts, masks, nb):
        import numpy as np
        self.w = np.array(wts)
        self.words = (nb + 62) // 63
        self.M = np.array([[(mk >> (63 * k)) & ((1 << 63) - 1) for k in range(self.words)] for mk in masks], dtype=np.int64)

    def K(self, classes):
        import numpy as np
        need = [0] * self.words
        for c in classes:
            need[c // 63] |= 1 << (c % 63)
        ok = np.ones(len(self.w), dtype=bool)
        for k in range(self.words):
            if need[k]:
                ok &= (self.M[:, k] & need[k]) == need[k]
        idx = np.flatnonzero(ok)
        return int(self.w[idx[0]]) if len(idx) else None


def part_c104():
    d, st, pi = stages104()
    S = st[1]
    C = compress(S, range(20))
    n, bd, bof, members = C["literal"]
    hb = C["bundles"]
    wts, masks = all_bonds(C["n"], hb)
    R = Reader(wts, masks, len(hb))
    out = {"compressed host (vertices, classes, bonds)": [C["n"], len(hb), len(wts)],
           "branch capacities": sorted(Counter(b["capacity"] for b in C["branches"]).items())}
    rows = [sum(1 << x for x in q) for q in S]
    r0 = rank(rows)
    res = []
    for mi, m in enumerate(d["full_group"]["maps"]):
        f = dict(map(tuple, m["map"]))
        # class map: the image of a class is the class of the image of any of its distinctions; check it is well defined
        cmap, ok = {}, True
        for lit_b, xs in enumerate(members):
            if lit_b not in C["map"]:
                continue
            imgs = {C["map"].get(bof[f.get(x, x)]) for x in xs}
            if len(imgs) != 1 or None in imgs:
                ok = False
            cmap[C["map"][lit_b]] = imgs.pop()
        for b in C["branches"]:
            cmap[b["link"]] = b["link"]
        moved = [c for c in cmap if cmap[c] != c]
        carries = rank(rows + [sum(1 << f.get(x, x) for x in q) for q in S]) == r0
        diff = Counter()
        for k in (1, 2, 3):
            for T in itertools.combinations(range(len(hb)), k):
                if not any(c in moved for c in T):
                    continue
                if R.K(T) != R.K([cmap[c] for c in T]):
                    diff[k] += 1
        row = {"map": mi, "class map well defined": ok, "moved classes": len(moved), "carries the equations": carries,
               "changed sets of 1, 2, 3 classes": [diff[1], diff[2], diff[3]]}
        if not carries:
            w4 = None
            for T in itertools.combinations(range(len(hb)), 4):
                if any(c in moved for c in T) and R.K(T) != R.K([cmap[c] for c in T]):
                    w4 = [list(T), R.K(T), R.K([cmap[c] for c in T])]
                    break
            row["a changed set of 4 classes"] = w4
        res.append(row)
    out["maps"] = res
    # how many four-class sets the specified exchange changes
    f = pi
    cmap = {}
    for lit_b, xs in enumerate(members):
        if lit_b in C["map"]:
            cmap[C["map"][lit_b]] = C["map"][bof[f.get(xs[0], xs[0])]]
    for b in C["branches"]:
        cmap[b["link"]] = b["link"]
    moved = {c for c in cmap if cmap[c] != c}
    cnt, tot = 0, 0
    for T in itertools.combinations(range(len(hb)), 4):
        tot += 1
        if moved & set(T) and R.K(T) != R.K([cmap[c] for c in T]):
            cnt += 1
    out["the exchange: four-class sets, changed"] = [tot, cnt]
    return out


def part_l104(chunk, chunks):
    import bondmilp as B
    d, st, pi = stages104()
    S = st[1]
    n, bd, bof, members = graph(S)
    f = lambda x: pi.get(x, x)  # noqa: E731
    rep = [xs[0] for xs in members]
    moved_b = sorted({bof[x] for x in pi})
    s = Counter()
    bad = []
    tasks = []
    for mb in moved_b:
        for ob in range(len(bd)):
            if ob != mb:
                tasks.append(("pair", [members[mb][0], rep[ob]] if ob != mb else None))
    rng = random.Random(104)
    allx = sorted({x for q in S for x in q})
    for _ in range(2000):
        x = rng.choice(sorted(pi))
        y, z = rng.sample([a for a in allx if a != x], 2)
        tasks.append(("triple", [x, y, z]))
    C = compress(S, range(20))
    hb = C["bundles"]
    wts, masks = all_bonds(C["n"], hb)
    R = Reader(wts, masks, len(hb))
    corex = [x for x in allx if bof[x] in C["map"] and bd[bof[x]][0] < 20 and bd[bof[x]][1] < 20]
    for _ in range(150):
        tasks.append(("core pair", rng.sample(corex, 2)))
        tasks.append(("core triple", rng.sample(corex, 3)))
    for kind, q in tasks[chunk::chunks]:
        a, _ = B.least_bond(n, bd, [bof[x] for x in q])
        if kind.startswith("core"):
            c = R.K(sorted({C["map"][bof[x]] for x in q}))
            s[kind + ": literal equals compressed"] += a == c
            s[kind] += 1
            if a != c:
                bad.append([kind, q, a, c])
            continue
        b, _ = B.least_bond(n, bd, [bof[f(x)] for x in q])
        s[kind] += 1
        s[kind + ": equal to the image"] += a == b
        if a != b:
            bad.append([kind, q, a, b])
    return {"counts": dict(s), "differences": bad[:10]}


# ---- the all-size family ----

def family(r, age):
    """Compressed host of constructive-proof.md's family: outer vertices R, B, O and I = r - 1 anchors (v first); four specials
    a, b (red), c, d (blue): L to the hub, L to v, one to each other anchor; s shields of each colour: M to the hub, one to each
    anchor, a virtual link to O of weight M (age 1) or 1 (age 2).  Returns (n, bundles, names, parameters)."""
    I = r - 1
    s = 4 * (r + 2)
    L = s * r
    M = 8 * s
    R_, B_, O = 0, 1, 2
    anchors = list(range(3, 3 + I))
    v = anchors[0]
    nid = 3 + I
    names, bd = {}, []

    def link(x, y, w, name):
        names[name] = len(bd)
        bd.append((x, y, w))
    specials = {}
    for k, (nm, hub) in enumerate((("a", R_), ("b", R_), ("c", B_), ("d", B_))):
        specials[nm] = nid
        link(nid, hub, L, (nm, "hub"))
        link(nid, v, L, (nm, "v"))
        for an in anchors[1:]:
            link(nid, an, 1, (nm, an))
        nid += 1
    shields = {"red": [], "blue": []}
    for col, hub in (("red", R_), ("blue", B_)):
        for i in range(s):
            shields[col].append(nid)
            link(nid, hub, M, (col, i, "hub"))
            for an in anchors:
                link(nid, an, 1, (col, i, an))
            link(nid, O, M if age == 1 else 1, (col, i, "branch"))
            nid += 1
    # the exchange a <-> c on names
    pi = {}
    for (x, *rest), i in names.items():
        if x in ("a", "c"):
            y = "c" if x == "a" else "a"
            pi[i] = names[(y, *rest)]
    return nid, bd, names, pi, {"r": r, "I": I, "s": s, "L": L, "M": M}


def part_cons(r):
    import networkx as nx
    import bondmilp as B
    out = {}
    n, bd, names, pi, P = family(r, 1)
    out["parameters"] = P
    Gf = nx.Graph()
    for u, v, w in bd:
        if Gf.has_edge(u, v):
            Gf[u][v]["capacity"] += w
        else:
            Gf.add_edge(u, v, capacity=w)
    out["hub R to O, hub B to O, R to B (maximum flow) and sM"] = [nx.maximum_flow_value(Gf, 0, 2), nx.maximum_flow_value(Gf, 1, 2),
                                                                  nx.maximum_flow_value(Gf, 0, 1), P["s"] * P["M"]]
    anchors = list(range(3, 3 + P["I"]))
    q = [names[("red", 0, "hub")], names[("red", 0, anchors[0])]] + [names[("c", "v")]] + [names[("c", an)] for an in anchors[1:]]
    a1, _ = B.least_bond(n, bd, q)
    a2, _ = B.least_bond(n, bd, [pi.get(x, x) for x in q])
    out["the (r+1)-mark query and its image"] = [len(q), a1, a2]
    n2, bd2, names2, pi2, _ = family(r, 2)
    p = [names2[("a", "hub")], names2[("b", "hub")]]
    b1, _ = B.least_bond(n2, bd2, p)
    b2, _ = B.least_bond(n2, bd2, [pi2.get(x, x) for x in p])
    out["age 2: the red pair, its image, 3L, 4L"] = [b1, b2, 3 * P["L"], 4 * P["L"]]
    # sets of at most r classes holding a moved class: one representative per shield type is enough up to the symmetry that
    # permutes shields of one colour (it commutes with the exchange and fixes the readings); use shields 0..r of each colour
    keep = {i for nm, i in names.items() if nm[0] in ("a", "b", "c", "d") or nm[1] <= r}
    moved = sorted(pi)
    cls = sorted(keep)
    s = Counter()
    bad = []
    rng = random.Random(r)
    sets = []
    for k in range(1, r + 1):
        for rest in itertools.combinations([c for c in cls], k - 1):
            for m in moved:
                if m in rest or any(c in moved and c < m for c in rest):
                    continue
                sets.append(tuple(sorted((m,) + rest)))
    sets = sorted(set(sets))
    if r >= 4:
        sets = rng.sample(sets, min(3000, len(sets)))
    worst = 0
    for T in sets:
        x, _ = B.least_bond(n, bd, list(T))
        y, _ = B.least_bond(n, bd, [pi.get(c, c) for c in T])
        s["sets"] += 1
        s["equal to the image"] += x == y
        if x is not None:
            worst = max(worst, x)
        if x != y and len(bad) < 5:
            bad.append([T, x, y])
    out["sets of at most r classes with a moved class"] = dict(s)
    out["largest value among them, and sM"] = [worst, P["s"] * P["M"]]
    out["differences"] = bad
    return out


# ---- the 239-junction stage to age 12 ----

def part_g239():
    import networkx as nx
    import job_expl as JX
    import job_ger as JG
    import bondmilp as B
    stars, labels, idx = JG.big_start()
    sig = {i: idx[JG.sigma_name(x)] for i, x in enumerate(labels)}
    s_, t_ = 0, JG.N + JG.PID[(0, 1)]
    G = JX.grower([list(q) for q in stars])
    out = []
    for age in range(13):
        S = [sorted(q) for q in G.bits]
        own = owners(S)
        Q = set(range(JG.UJ, len(S)))       # U, V and every grown junction
        F = nx.Graph()
        for x, js in own.items():
            ends = (js[0], js[1]) if len(js) == 2 else (js[0], "o")
            inQ = [e for e in ends if e == "o" or e in Q]
            if not inQ:
                continue                    # a core distinction
            a, b = ends
            if F.has_edge(a, b):
                F[a][b]["capacity"] += 1
            else:
                F.add_edge(a, b, capacity=1)
        lam = nx.maximum_flow_value(F, s_, t_)
        rows = [sum(1 << x for x in q) for q in S]
        img = sum(1 << sig.get(x, x) for x in S[JG.H0])
        row = {"age": age, "junctions": len(S), "distinctions": len(own), "separating cost of the growing part": lam,
               "h0's image outside the span": rank(rows + [img]) > rank(rows)}
        if age == 1:
            n, bd, bof, members = graph(S)
            q = [idx[("y", (2, 8))], idx[("uw", 8, (2, 8))], idx[("uw", 0, (0, 8))], idx[("uw", 8, (0, 8))]]
            a, _ = B.least_bond(n, bd, [bof[x] for x in q])
            b, _ = B.least_bond(n, bd, [bof[sig.get(x, x)] for x in q])
            row["four-name query and its image"] = [a, b]
        out.append(row)
        if age < 12 and G.step(JX.floored, None, None) != "ok":
            break
    return out


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("S104", {"part": "S104"}), ("C104", {"part": "C104"}), ("G239", {"part": "G239"})]
    allc += [(f"CONS-{r}", {"part": "CONS", "r": r}) for r in (2, 3, 4)]
    allc += [(f"L104-{c:02d}", {"part": "L104", "c": c, "of": 12}) for c in range(12)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    k = p["part"]
    if k == "S104":
        r = part_s104()
    elif k == "C104":
        r = part_c104()
    elif k == "G239":
        r = {"ages": part_g239()}
    elif k == "CONS":
        r = part_cons(p["r"])
    else:
        r = part_l104(p["c"], p["of"])
    return json.loads(json.dumps(r, default=lambda o: int(o) if hasattr(o, "__int__") else str(o)))
