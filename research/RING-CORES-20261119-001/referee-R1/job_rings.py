"""Shared-runner job for the referee's check of RING-CORES-20261119-001 (own word enumeration, own count formula, own brute-force
cluster count on the cover, own growth; the study's ringlib.formula run only as a labelled cross-check of the formula, the object
under test; no other study code run).

Parts:
- W (per ring length L = 5, 7..14, in chunks): the referee's own enumeration of decorated ring words up to rotation and reflection;
  for every word:
  - the referee's own Theorem 3 formula (series in exact integers), against the study's ringlib.formula (cross-check);
  - the referee's rate (root of W(1/x) = 1) and Proposition 6 in exact arithmetic in Q(sqrt 5): W(1/phi) <= 1 for every piece,
    with equality exactly when every line point is spared or flanks a hung knot with two spares;
  - the even-ring piece rule read from the referee's own relayed map (DOUBLE-IDENT-R1's build): the component of each hung knot
    and of each spare;
  - for L <= 9, the brute-force count of clusters on the unrolled cover (every connected set of points holding a knot, one per
    orbit of the shift), against the formula, to round 7;
  - for L <= 10 every word, above that one word in ten (crc32), the referee's growth (FIRST-KNOT-R1 engine, the program's rule,
    the implied test read structurally for long runs) against the formula on every round, to round 30 or 3,000 junctions.
- G: completeness of the shape list.  Every connected graph of the cap study's conditions to 14 knots whose core is a cycle
  (CAP-CHAINS-R1's own enumeration, read from its referee_cap_graphs.json), every assignment of open counts in [max(1, d), 5 - deg]
  (every all-live simple start within five places; the referee's classification decides the class), mapped to a word; the set of
  words met equals the set of words with L + (hung knots) <= 14 knots.
- S (per number of knots 2..9): every simple all-live start within five places on those graphs, the referee's classification; each
  in-class start grown by the referee's engine to round 16: a ring core against the referee's formula on every round; a path or
  star core: its exact minimal recurrence (Berlekamp-Massey over Q) must be (x - 1)^k, or it closes.
- C: the touch census's non-stalling starts outside the class, and those in the class with a dead knot (every knot within five
  places): grown to round 16 or 30,000 junctions, the largest ratio of successive counts over the last three rounds.

  .venv/bin/python -B scripts/longrun.py launch research/RING-CORES-20261119-001/referee-R1/job_rings.py \\
      --out runs/referee-rings --unit referee-rings --workers 4 --case-timeout 7200 --case-mem 3G --mem-max 16G
"""
import importlib.util
import itertools
import json
import sys
import zlib
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/CAP-CHAINS-20261119-001/referee-R1", "research/WEIGHTINGS-20261119-001/referee-R1",
          "research/DOUBLE-IDENT-20261119-001/referee-R1", "research/RELAY-IDENT-20261119-001/referee-R1",
          "research/CHAIN-IDENT-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1",
          "research/BREAK-EDDIES-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
NS = 43
LENGTHS = (5, 7, 8, 9, 10, 11, 12, 13, 14)
CHUNK = 1500
PARAMS = {}


def setup(params):
    PARAMS.update(params)


# ---- words ----

def my_words(L):
    """Cyclic words over ('L', b) hung knot with b spares, ('N',) beside a hung knot, ('P', a) plain with a spares, hung knots at
    cyclic distance >= 3, up to rotation and reflection."""
    out = set()
    for mask in range(1 << L):
        S = [i for i in range(L) if mask >> i & 1]
        if any(min((x - y) % L, (y - x) % L) < 3 for x, y in itertools.combinations(S, 2)):
            continue
        near = {(s + d) % L for s in S for d in (-1, 1)}
        plain = [i for i in range(L) if i not in S and i not in near]
        for bs in itertools.product(range(3), repeat=len(S)):
            for sp in itertools.product(range(2), repeat=len(plain)):
                w = [None] * L
                for s, b in zip(S, bs):
                    w[s] = ("L", b)
                for i in near:
                    w[i] = ("N",)
                for i, a in zip(plain, sp):
                    w[i] = ("P", a)
                out.add(canon(tuple(w)))
    return sorted(out)


def canon(w):
    L = len(w)
    rots = [w[r:] + w[:r] for r in range(L)]
    return min(min(r, tuple(reversed(r))) for r in rots)


# ---- series ----

def mul(a, b):
    c = [0] * NS
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b[:NS - i]):
                if y:
                    c[i + j] += x * y
    return c


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def poly(*c):
    return list(c) + [0] * (NS - len(c))


def power(p, k):
    r = poly(1)
    for _ in range(k):
        r = mul(r, p)
    return r


def inv(p):
    q = [0] * NS
    q[0] = Fraction(1, p[0]) if p[0] != 1 else 1
    for m in range(1, NS):
        q[m] = -sum(p[k] * q[m - k] for k in range(1, m + 1))
    return q


def pieces(w):
    """(line points' spares a_k, hung knot b on edge k or None) per piece, walking two knots at a time."""
    L = len(w)
    out = []
    for s0 in ([0] if L % 2 else [0, 1]):
        line = [(s0 + 2 * k) % L for k in range(L if L % 2 else L // 2)]
        a = [w[c][1] if w[c][0] == "P" else 0 for c in line]
        hung = [w[(c + 1) % L][1] if w[(c + 1) % L][0] == "L" else None for c in line]
        out.append((line, a, hung))
    return out


def piece_series(a, hung):
    n = len(a)
    Z, ONEZ = poly(0, 1), poly(1, 1)
    lam = [poly(1) if b is None else add(poly(1), mul(Z, power(ONEZ, b))) for b in hung]
    v = [mul(mul(Z, power(ONEZ, a[k])), lam[k]) for k in range(n)]
    W = poly(1)
    for x in v:
        W = mul(W, x)
    num = [0] * NS
    for i in range(n):
        acc, prod = [0] * NS, poly(1)
        for m in range(n):
            prod = mul(prod, v[(i + m) % n])
            acc = add(acc, prod)
        num = add(num, mul(lam[(i - 1) % n], acc))
    F = mul(num, inv([1 - W[0]] + [-x for x in W[1:]]))
    for b in hung:
        if b is not None:
            F = add(F, mul(Z, power(ONEZ, b)))
    return F, W


def my_formula(w):
    tot = [0] * NS
    Ws = []
    for line, a, hung in pieces(w):
        F, W = piece_series(a, hung)
        tot = add(tot, F)
        Ws.append(W)
    return [tot[t + 1] for t in range(NS - 1)], Ws


def root(W):
    f = lambda z: sum(c * z ** i for i, c in enumerate(W) if c)  # noqa: E731
    if abs(f(1.0) - 1) < 1e-12:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 1 else (lo, mid)
    return 1 / lo


class Q5:
    """a + b sqrt 5 with rational a, b."""

    def __init__(self, a, b=0):
        self.a, self.b = Fraction(a), Fraction(b)

    def __add__(self, o):
        return Q5(self.a + o.a, self.b + o.b)

    def __mul__(self, o):
        return Q5(self.a * o.a + 5 * self.b * o.b, self.a * o.b + self.b * o.a)

    def sign_of_minus_one(self):
        """The sign of self - 1, exactly."""
        a, b = self.a - 1, self.b
        if a >= 0 and b >= 0:
            return 0 if a == 0 and b == 0 else 1
        if a <= 0 and b <= 0:
            return -1
        # a + b sqrt5 with mixed signs: compare a^2 with 5 b^2
        s = a * a - 5 * b * b
        return (1 if a > 0 else -1) if s > 0 else ((1 if b > 0 else -1) if s < 0 else 0)


def W_at_inv_phi(W):
    z0 = Q5(Fraction(-1, 2), Fraction(1, 2))
    tot, zp = Q5(0), Q5(1)
    for c in W:
        if c:
            tot = tot + Q5(c) * zp
        zp = zp * z0
    return tot


def prop6_equality_expected(a, hung):
    """Every line point spared, or flanking a hung knot with two spares (the line points on both sides of that hung knot's edge)."""
    n = len(a)
    ok = [a[k] == 1 for k in range(n)]
    for k, b in enumerate(hung):
        if b == 2:
            ok[k] = ok[(k + 1) % n] = True
    return all(ok)


# ---- realisation and growth ----

def start_of(w):
    import job_weight as JW
    L = len(w)
    e = [tuple(sorted((i, (i + 1) % L))) for i in range(L)]
    bs = []
    for c in range(L):
        if w[c][0] == "L":
            e.append((c, L + len(bs)))
            bs.append(w[c][1])
    n = L + len(bs)
    flat = JW.flat_of(n, e)
    sizes = JW.my_bare(n, flat)
    for c in range(L):
        if w[c][0] == "P":
            sizes[c] += w[c][1]
    for j, b in enumerate(bs):
        sizes[L + j] += b
    return sizes, e, flat


def piece_rule(w):
    """From the referee's own X+: for each hung knot, the parity of its component's core knots; for each spare, its knot's."""
    import job_double as JD
    sizes, e, flat = start_of(w)
    L = len(w)
    X = JD.build(sizes, flat, 2)
    find = X["find"]
    ok = True
    j = L
    for c in range(L):
        if w[c][0] == "L":
            comp = find(j)
            members = [k for k in range(L) if find(k) == comp]
            if L % 2 == 0:
                ok &= all(k % 2 != c % 2 for k in members)
            ok &= find(j) == find((c + 1) % L) == find((c - 1) % L)
            j += 1
    for k, o, R, _ in X["pend"]:
        ok &= find(o) == find(k) and R == 0
    return ok


def grow_counts(sizes, e, rounds, maxj):
    import job_cap as JC
    return JC.light_counts(sizes, e, rounds, maxj=maxj)


# ---- brute-force clusters on the cover ----

def brute(w, T):
    """Per-round counts to round T from every connected set of points holding a knot on the unrolled cover, one per orbit."""
    tot = [0] * (T + 2)
    for line, a, hung in pieces(w):
        n = len(line)
        lo, hi = -2, n + T + 2
        pts, kind, adj = [], [], defaultdict(set)
        idx = {}

        def new(k, tag, pos):
            pts.append((tag, pos))
            kind.append(k)
            return len(pts) - 1
        for x in range(lo, hi + 1):
            idx[("x", x)] = new("knot", "x", x)
        for x in range(lo, hi + 1):
            u = idx[("x", x)]
            for s in range(a[x % n]):
                sp = new("spare", "s", x)
                adj[u].add(sp)
                adj[sp].add(u)
            if x < hi:
                v = idx[("x", x + 1)]
                adj[u].add(v)
                adj[v].add(u)
                b = hung[x % n]
                if b is not None:
                    h = new("knot", "h", x)
                    for y in (u, v):
                        adj[h].add(y)
                        adj[y].add(h)
                    for s in range(b):
                        sp = new("spare", "hs", x)
                        adj[h].add(sp)
                        adj[sp].add(h)
        N = len(pts)
        # every connected set of up to T + 1 points (ESU), kept when it is an orbit's representative
        def rep(S):
            if not any(kind[v] == "knot" for v in S):
                return False
            xs = [pts[v][1] for v in S if pts[v][0] == "x"]
            if xs:
                return 0 <= min(xs) < n
            hs = [pts[v][1] for v in S if pts[v][0] == "h"]
            return 0 <= hs[0] < n
        for v in range(N):
            ext = {u for u in adj[v] if u > v}
            stack = [({v}, ext, {v} | adj[v])]
            while stack:
                S, ext, nb = stack.pop()
                if rep(S):
                    tot[len(S) - 1] += 1
                if len(S) == T + 1:
                    continue
                ext = set(ext)
                while ext:
                    u = ext.pop()
                    new_ext = ext | {y for y in adj[u] if y > v and y not in nb}
                    stack.append((S | {u}, new_ext, nb | adj[u]))
    return tot[:T + 1]


# ---- parts ----

def part_w(L, chunk):
    import importlib
    spec = importlib.util.spec_from_file_location(
        "rc_ringlib", ROOT / "proofs/RING-CORES-20261119-001A/RING-CORES-20261119-001A-P001_rings/ringlib.py")
    RLIB = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(RLIB)            # the object under test: its formula only, as a cross-check
    ws = my_words(L)
    s = Counter()
    s["words"] = len(ws)
    rates = Counter()
    fails = []
    for w in ws[chunk * CHUNK:(chunk + 1) * CHUNK]:
        s["checked"] += 1
        f, Ws = my_formula(w)
        theirs, _ = RLIB.formula(w)
        s["formula equals the study's"] += f[:40] == theirs[:40]
        x = max(root(W) for W in Ws)
        rates[round(x, 4)] += 1
        bare = all(c == ("P", 0) for c in w)
        s["bare and constant L per round"] += bare and all(v == L for v in f[:40])
        s["not bare and growing"] += (not bare) and x > 1 + 1e-9
        for (line, a, hung), W in zip(pieces(w), Ws):
            sg = W_at_inv_phi(W).sign_of_minus_one()
            s["pieces"] += 1
            s["pieces with W(1/phi) > 1"] += sg > 0
            s["pieces at phi"] += sg == 0
            s["pieces at phi as Proposition 6 says"] += (sg == 0) == prop6_equality_expected(a, hung)
        s["piece rule holds"] += piece_rule(w)
        if L <= 9:
            bc = brute(w, 7)
            s["brute-force clusters equal the formula to round 7"] += bc == f[:8]
            if bc != f[:8]:
                fails.append({"word": w, "brute": bc, "formula": f[:8]})
        if L <= 10 or zlib.crc32(repr(w).encode()) % 10 == 0:
            sizes, e, flat = start_of(w)
            cs = grow_counts(sizes, e, 30, 3000)
            num = [c for c in cs if isinstance(c, int)]
            s["grown"] += 1
            s["growth equals the formula on every round"] += num == f[:len(num)]
            s["rounds grown"] += len(num) - 1
            if num != f[:len(num)]:
                fails.append({"word": w, "growth": num[:12], "formula": f[:12]})
    return {"counts": dict(s), "rates": {str(k): v for k, v in sorted(rates.items())}, "max rate": max(rates) if rates else None,
            "failures": fails[:10]}


def word_of(n, edges, opn):
    """The word of an all-live start whose core is a cycle (None when the core is not a cycle)."""
    deg = Counter(x for e in edges for x in e)
    nbr = defaultdict(set)
    for a, b in edges:
        nbr[a].add(b)
        nbr[b].add(a)
    core = [k for k in range(n) if deg[k] >= 2]
    if not core or any(len(nbr[k] & set(core)) != 2 for k in core):
        return None
    order = [core[0]]
    prev = None
    while True:
        cur = order[-1]
        nxt = [k for k in nbr[cur] if k in core and k != prev and k != order[0]] if len(order) > 1 else sorted(nbr[cur] & set(core))[:1]
        if not nxt:
            break
        prev = cur
        order.append(nxt[0])
        if len(order) > len(core):
            return None
    if len(order) != len(core):
        return None
    w = []
    for c in order:
        leaves = [k for k in nbr[c] if deg[k] == 1]
        if leaves:
            w.append(("L", opn[leaves[0]] - 2) if len(leaves) == 1 else ("bad",))
        elif any(any(deg[k] == 1 for k in nbr[x]) for x in nbr[c] if x in core):
            w.append(("N",) if opn[c] == 3 else ("bad",))
        else:
            w.append(("P", opn[c] - 2))
    return canon(tuple(w))


def part_g():
    import job_double as JD
    import job_weight as JW
    gs = json.load(open(HERE.parents[1] / "CAP-CHAINS-20261119-001/referee-R1/referee_cap_graphs.json"))["result"]["edge lists"]
    met = set()
    s = Counter()
    for nn, lst in gs.items():
        n = int(nn)
        for e in lst:
            e = [tuple(x) for x in e]
            deg = Counter(x for ed in e for x in ed)
            eset = set(e)
            dform = [sum(deg[w] - 1 for w in range(n) if (min(k, w), max(k, w)) in eset) for k in range(n)]
            core = [k for k in range(n) if deg[k] >= 2]
            if len(core) < 3 or any(sum(1 for w in range(n) if (min(k, w), max(k, w)) in eset and deg[w] >= 2) != 2 for k in core):
                continue
            s["cycle-core graphs"] += 1
            flat = JW.flat_of(n, e)
            for opn in itertools.product(*[range(max(1, dform[k]), 5 - deg[k] + 1) for k in range(n)]):
                sizes = [deg[k] + opn[k] for k in range(n)]
                c = JD.classify(sizes, flat)
                s["assignments"] += 1
                if c not in ("in", "one loose", "none"):
                    s[f"outside the class: {c}"] += 1
                    continue
                w = word_of(n, e, opn)
                if w is None or any(x[0] == "bad" for x in w):
                    s["in the class but not a word"] += 1
                    continue
                met.add(w)
    expect = set()
    for L in LENGTHS:
        if L > 14:
            continue
        for w in my_words(L):
            if L + sum(1 for x in w if x[0] == "L") <= 14:
                expect.add(w)
    s["words met"] = len(met)
    s["words expected (L + hung knots <= 14)"] = len(expect)
    s["met but not expected"] = len(met - expect)
    s["expected but not met"] = len(expect - met)
    return dict(s)


def part_s(n):
    import job_double as JD
    import job_weight as JW
    import break_readout as BR
    gs = json.load(open(HERE.parents[1] / "CAP-CHAINS-20261119-001/referee-R1/referee_cap_graphs.json"))["result"]["edge lists"]
    s = Counter()
    bad = []
    for e in gs.get(str(n), []):
        e = [tuple(x) for x in e]
        deg = Counter(x for ed in e for x in ed)
        flat = JW.flat_of(n, e)
        for sizes in itertools.product(*[range(max(3, deg[k] + 1), 6) for k in range(n)]):
            sizes = list(sizes)
            c = JD.classify(sizes, flat)
            if c not in ("in", "one loose", "none"):
                s[c] += 1
                continue
            opn = [sizes[k] - deg[k] for k in range(n)]
            w = word_of(n, e, opn)
            cs = grow_counts(sizes, e, 16 if w is not None else 30, 6000)
            num = [x for x in cs if isinstance(x, int)]
            closed = "closed" in cs
            if w is not None:
                f, Ws = my_formula(w)
                ok = num == f[:len(num)]
                bare = all(x == ("P", 0) for x in w)
                s[f"ring core, {'bare' if bare else 'decorated'}, growth equals the formula"] += ok
                s[f"ring core, {'bare' if bare else 'decorated'}"] += 1
                if not ok:
                    bad.append({"sizes": sizes, "edges": e, "growth": num[:10], "formula": f[:10]})
            else:
                s["path or star core"] += 1
                if closed:
                    s["path or star core, closes"] += 1
                    continue
                rd = BR.read(num)
                d3 = [num[i + 3] - 3 * num[i + 2] + 3 * num[i + 1] - num[i] for i in range(len(num) - 3)]
                poly_ok = (rd is not None and rd.get("factors") == ["x - 1"]) or (len(num) >= 20 and not any(d3[-8:]))
                s["path or star core, counts polynomial (x - 1)^k"] += poly_ok
                if not poly_ok:
                    bad.append({"sizes": sizes, "edges": e, "growth": num, "recurrence": rd and rd.get("factors")})
    return {"counts": dict(s), "bad": bad[:10]}


def part_c():
    import job_double as JD
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok":
            rows += [a["key"] for a in r["result"]["arrangements"]]
    s = Counter()
    top = []
    for sizes, flat in rows:
        c = JD.classify(sizes, flat)
        n = len(sizes)
        sh = Counter()
        for (a, b), m in zip(itertools.combinations(range(n), 2), flat):
            sh[a] += m
            sh[b] += m
        dead = any(sizes[k] - sh[k] == 0 for k in range(n))
        if c == "stall" or (c in ("in", "one loose", "none") and not dead):
            continue
        group = "outside the class" if c.startswith("out") else "in the class, a dead knot"
        edges = []
        for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
            edges += [(i, j)] * m
        cs = grow_counts(sizes, edges, 16, 30000)
        num = [x for x in cs if isinstance(x, int)]
        s[group] += 1
        if len(num) >= 6 and num[-1] > 50:
            r = max(num[t] / num[t - 1] for t in range(len(num) - 3, len(num)))
            s[f"{group}: growing past 50"] += 1
            s[f"{group}: last ratios above the golden ratio"] += r > 1.6181
            top.append([round(r, 4), sizes, flat, num[-6:]])
    top.sort(reverse=True)
    return {"counts": dict(s), "fastest": top[:12]}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("G", {"part": "G"}), ("C", {"part": "C"})]
    sizes = {5: 17, 7: 60, 8: 129, 9: 248, 10: 543, 11: 1128, 12: 2551, 13: 5588, 14: 12834}
    for L in LENGTHS:
        for c in range((sizes[L] + CHUNK - 1) // CHUNK):
            allc.append((f"W-{L:02d}-{c:02d}", {"part": "W", "L": L, "chunk": c}))
    allc += [(f"S-{n:02d}", {"part": "S", "n": n}) for n in range(9, 1, -1)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "W":
        return part_w(p["L"], p["chunk"])
    if p["part"] == "G":
        return part_g()
    if p["part"] == "S":
        return part_s(p["n"])
    return part_c()
