"""Referee R1 for TOUCH-CENSUS-20261118-001 (own code; the study's arrlib.py, job.py, merge.py and the FIRST-KNOT / FRESH-COUNT
libraries are not imported; the study's per-arrangement readings are read from its run's results.jsonl, as data, for comparison).

  ../../../.venv/bin/python -B referee_touch.py <part> > referee_touch_<part>.json      (from this directory)

An arrangement: n knots with sizes 3..5 and a multiplicity for each pair (shared distinctions), every knot's degree at most its size,
connected; the same arrangement under a renaming of the knots.  Growth: the referee's FIRST-KNOT-R1 engine (the complete-round
joining rule, GF(2) implied parity, the fewest rule).

Parts:
  count    the number of distinct arrangements per n by Burnside's lemma over the symmetric group (connected descriptions fixed by
           each permutation, by cycle type), a method independent of the study's canonical form; and the number of labelled
           descriptions (knots labelled), against the study's 3, 22, 154, 1,760, 24,502 and its labelled weights.
  rings    the seven faster-than-power rings (and the two four-place rings) grown as far as 60,000 junctions: per-round counts, the
           ratio trend, the best linear recurrence with integer coefficients, log-log and log-linear fits.
  sample   the study's readings against the referee's: every arrangement the study read as 3, 4, 6 or unsettled, every P1b exception,
           and 1,500 random others, grown to 45 rounds (12,000 junctions), read with a 12-round window; agreement table.
  missing  the arrangements the study's run had not read when this referee ran (the enumeration by the study's key format, the
           read keys subtracted), grown and read as in sample.
  six      a sample of six-knot arrangements: eight Metropolis chains uniform over labelled descriptions (symmetric moves on
           one multiplicity or one size, feasible states only), 1,200 samples, importance-weighted to distinct arrangements by
           |Aut| / n!; grown to 40 rounds (12,000 junctions) and read as in sample.
"""
import itertools
import json
import math
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/FRESH-COUNT-20261118-001/referee-R1"))
import referee_first as RFK  # noqa: E402

RESULTS = ROOT / "runs/touch-census/results.jsonl"


# ---------------- counting ----------------

def cycles(perm):
    seen, out = set(), []
    for i in range(len(perm)):
        if i not in seen:
            c = []
            j = i
            while j not in seen:
                seen.add(j)
                c.append(j)
                j = perm[j]
            out.append(c)
    return out


def connected(n, M):
    seen, st = {0}, [0]
    while st:
        x = st.pop()
        for y in range(n):
            if M[x][y] and y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == n


def fixed_connected(perm):
    """Connected descriptions (sizes, multiplicities) fixed by perm: sizes constant on its cycles, multiplicities on its pair orbits."""
    n = len(perm)
    vc = cycles(perm)
    pairs = list(itertools.combinations(range(n), 2))
    seen, porbits = set(), []
    for p in pairs:
        if p in seen:
            continue
        orb = []
        q = p
        while q not in seen:
            seen.add(q)
            orb.append(q)
            q = tuple(sorted((perm[q[0]], perm[q[1]])))
        porbits.append(orb)
    count = 0
    for sz in itertools.product((3, 4, 5), repeat=len(vc)):
        sizes = [0] * n
        for c, s in zip(vc, sz):
            for v in c:
                sizes[v] = s
        M = [[0] * n for _ in range(n)]
        deg = [0] * n

        def rec(k):
            nonlocal count
            if k == len(porbits):
                if connected(n, M):
                    count += 1
                return
            orb = porbits[k]
            # multiplicity m on every pair of the orbit; each vertex gains m per incidence
            inc = Counter(v for p in orb for v in p)
            m = 0
            while all(deg[v] + m * inc[v] <= sizes[v] for v in inc):
                for i, j in orb:
                    M[i][j] = M[j][i] = m
                for v in inc:
                    deg[v] += m * inc[v]
                rec(k + 1)
                for v in inc:
                    deg[v] -= m * inc[v]
                m += 1
            for i, j in orb:
                M[i][j] = M[j][i] = 0
        rec(0)
    return count


def part_count():
    out = {}
    for n in range(1, 6):
        total = Fraction(0)
        ident = None
        by_type = {}
        for perm in itertools.permutations(range(n)):
            ct = tuple(sorted(len(c) for c in cycles(perm)))
            if ct not in by_type:
                by_type[ct] = fixed_connected(perm)
            total += by_type[ct]
            if all(perm[i] == i for i in range(n)):
                ident = by_type[ct]
        out[n] = {"distinct arrangements (Burnside)": str(total / math.factorial(n)), "labelled descriptions": ident}
    study = {1: 3, 2: 22, 3: 154, 4: 1760, 5: 24502}
    out["study's distinct counts"] = study
    out["agree"] = all(out[n]["distinct arrangements (Burnside)"] == str(study[n]) for n in range(1, 6))
    return out


# ---------------- growth ----------------

def stars(sizes, M):
    n = len(sizes)
    S = [[] for _ in range(n)]
    b = 0
    for i, j in itertools.combinations(range(n), 2):
        for _ in range(M[i][j]):
            S[i].append(b)
            S[j].append(b)
            b += 1
    for i in range(n):
        while len(S[i]) < sizes[i]:
            S[i].append(b)
            b += 1
    return S


def key_to(sizes, flat):
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        M[i][j] = M[j][i] = m
    return list(sizes), M


def grow(sizes, M, rounds=45, maxj=12000):
    G = RFK.Start(stars(sizes, M))
    outcome = "alive"
    for _ in range(rounds):
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            outcome = r
            break
        if len(G.bits) > maxj:
            outcome = "big"
            break
    return G, outcome


def read_dim(counts, outcome, window=12):
    """0 if closed; None on a stall; else d + 1 for the least d whose d-th differences of the per-round counts are constant and
    nonzero over the last `window` rounds; 'unsettled' if none up to d = window - 3."""
    if outcome == "closed":
        return 0
    if outcome == "stall":
        return None
    w = counts[1:][-window:]
    if len(w) < window:
        return "short"
    d = w
    for k in range(0, window - 2):
        if len(d) >= 3 and len(set(d)) == 1 and d[0] != 0:
            return k + 1
        d = [d[i + 1] - d[i] for i in range(len(d) - 1)]
    return "unsettled"


def study_rows():
    rows = []
    for line in open(RESULTS):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        rows.extend(r["result"]["arrangements"])
    return rows


def one(row):
    sizes, flat = row["key"]
    s, M = key_to(sizes, flat)
    G, outcome = grow(s, M)
    c = G.counts()
    mine = read_dim(c, outcome)
    return {"key": row["key"], "study dim": row["dim"] if row["outcome"] != "stall" else "stall",
            "study outcome": row["outcome"], "referee outcome": outcome, "referee dim": mine if outcome != "stall" else "stall",
            "rounds": G.rounds, "last counts": c[-6:]}


def part_sample(workers=16):
    from multiprocessing import Pool
    rows = study_rows()
    rng = random.Random("referee-touch-sample")
    special = [r for r in rows if r["dim"] in (3, 4, 6) or (r["dim"] is None and r["outcome"] != "stall")
               or (r["any_birth"] and r["dim"] not in (None,) and r["rule"] != r["dim"] and r["outcome"] != "closed")]
    others = [r for r in rows if r not in special]
    pick = special + rng.sample(others, 1500)
    with Pool(workers) as P:
        res = P.map(one, pick, chunksize=4)
    agree = Counter()
    disagree = []
    for r in res:
        a, b = r["study dim"], r["referee dim"]
        agree[f"study {a} / referee {b}"] += 1
        if a != b and len(disagree) < 40:
            disagree.append(r)
    return {"study rows read": len(rows), "compared": len(res), "special cases": len(special), "table": dict(sorted(agree.items(), key=str)),
            "disagreements (first 40)": disagree}


def ring_keys(rows):
    out = []
    for r in rows:
        if r["dim"] == 6 or (r["dim"] is None and r["outcome"] not in ("stall", "closed")):
            out.append(r["key"])
    # the two rings of five four-place knots (one-dimensional, birthless), for contrast
    for r in rows:
        sizes, flat = r["key"]
        if list(sizes) == [4, 4, 4, 4, 4] and not r["any_birth"] and r["outcome"] not in ("stall", "closed"):
            out.append(r["key"])
    return out


def recurrence(c, order_max=6):
    """The shortest linear recurrence c[t] = sum a_i c[t - i] with rational coefficients fitting every term past a burn-in, by
    solving on the last terms and checking the rest; returns (order, coefficients, largest root modulus) or None."""
    import numpy as np
    for k in range(1, order_max + 1):
        if len(c) < 3 * k + 4:
            break
        tail = c[-(2 * k + 6):]
        A = np.array([[tail[t - i] for i in range(1, k + 1)] for t in range(k, len(tail))], dtype=float)
        y = np.array([tail[t] for t in range(k, len(tail))], dtype=float)
        coef, res, rank, _ = np.linalg.lstsq(A, y, rcond=None)
        rc = [round(x) for x in coef]
        if all(sum(rc[i - 1] * tail[t - i] for i in range(1, k + 1)) == tail[t] for t in range(k, len(tail))):
            roots = np.roots([1] + [-x for x in rc])
            return {"order": k, "integer coefficients": rc, "largest root modulus": round(float(max(abs(roots))), 4)}
    return None


def part_rings():
    rows = study_rows()
    out = {}
    for key in ring_keys(rows):
        sizes, flat = key
        s, M = key_to(sizes, flat)
        G, outcome = grow(s, M, rounds=80, maxj=60000)
        c = G.counts()[1:]
        ratios = [round(c[t] / c[t - 1], 3) for t in range(1, len(c)) if c[t - 1]]
        rec = recurrence(c)
        lin = None
        if len(c) > 10 and min(c[-10:]) > 0:
            import numpy as np
            t = np.arange(len(c) - 10, len(c)) + 1
            y = np.log(np.array(c[-10:], dtype=float))
            lin = {"log-linear slope (log ratio per round)": round(float(np.polyfit(t, y, 1)[0]), 4),
                   "log-log slope": round(float(np.polyfit(np.log(t), y, 1)[0]), 3)}
        out[json.dumps(key)] = {"outcome": outcome, "rounds": G.rounds, "junctions": len(G.bits), "per-round counts": c,
                                "ratios (last 12)": ratios[-12:], "recurrence": rec, "fits (last 10 rounds)": lin,
                                "offshoots per round (last 8)": G.offshoots()[-8:]}
        print(key, outcome, G.rounds, ratios[-4:], rec, file=sys.stderr, flush=True)
    return out


# ---------------- six knots ----------------

def aut_count(sizes, M):
    n = len(sizes)
    return sum(1 for p in itertools.permutations(range(n))
               if all(sizes[p[i]] == sizes[i] for i in range(n)) and all(M[p[i]][p[j]] == M[i][j] for i in range(n) for j in range(n)))


def six_chain(n_samples, seed, burn=5000, thin=300):
    """A Metropolis chain uniform over labelled six-knot descriptions (sizes 3..5, multiplicities, degree <= size, connected):
    symmetric moves (one multiplicity +-1, or one size +-1), accepted when the result is feasible."""
    rng = random.Random(f"referee-touch-six-chain-{seed}")
    n = 6
    sizes = [5] * n
    M = [[0] * n for _ in range(n)]
    for i in range(n - 1):
        M[i][i + 1] = M[i + 1][i] = 1          # a path: feasible and connected
    pairs = list(itertools.combinations(range(n), 2))
    out = []
    step = 0
    while len(out) < n_samples:
        step += 1
        if rng.random() < 0.7:
            i, j = rng.choice(pairs)
            m = M[i][j] + rng.choice((-1, 1))
            if m >= 0:
                old = M[i][j]
                M[i][j] = M[j][i] = m
                if not (sum(M[i]) <= sizes[i] and sum(M[j]) <= sizes[j] and connected(n, M)):
                    M[i][j] = M[j][i] = old
        else:
            i = rng.randrange(n)
            sz = sizes[i] + rng.choice((-1, 1))
            if 3 <= sz <= 5 and sum(M[i]) <= sz:
                sizes[i] = sz
        if step > burn and step % thin == 0:
            out.append((list(sizes), [row[:] for row in M]))
    return out


def six_one(desc):
    sizes, M = desc
    G, outcome = grow(sizes, M, rounds=40, maxj=12000)
    d = read_dim(G.counts(), outcome)
    return {"dim": d if outcome != "stall" else "stall", "weight to distinct": aut_count(sizes, M) / math.factorial(6),
            "sizes": sizes, "outcome": outcome}


def part_six(n=1200, workers=16):
    from multiprocessing import Pool
    descs = [d for c in range(8) for d in six_chain(n // 8, c)]
    with Pool(workers) as P:
        res = P.map(six_one, descs, chunksize=4)
    lab = Counter(str(r["dim"]) for r in res)
    dist = defaultdict(float)
    for r in res:
        dist[str(r["dim"])] += r["weight to distinct"]
    tot = sum(dist.values())
    grow_lab = {k: v for k, v in lab.items() if k not in ("stall", "0")}
    grow_dist = {k: v for k, v in dist.items() if k not in ("stall", "0")}
    return {"sampled (uniform over labelled descriptions)": n, "by labelled weight": dict(sorted(lab.items())),
            "share of growing that are two-dimensional (labelled)": round(lab.get("2", 0) / max(1, sum(grow_lab.values())), 3),
            "by distinct weight (importance-weighted shares)": {k: round(v / tot, 4) for k, v in sorted(dist.items())},
            "share of growing that are two-dimensional (distinct)": round(dist.get("2", 0) / max(1e-12, sum(grow_dist.values())), 3)}


def all_keys(nmax=5):
    """Every distinct arrangement as its least relabelling (sizes, upper-triangle multiplicities), the study's key format."""
    out = set()
    for n in range(1, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        perms = list(itertools.permutations(range(n)))
        for sizes in itertools.combinations_with_replacement((3, 4, 5), n):
            M = [[0] * n for _ in range(n)]
            deg = [0] * n

            def rec(k):
                if k == len(pairs):
                    if connected(n, M):
                        out.add(min((tuple(sizes[p[i]] for i in range(n)), tuple(M[p[i]][p[j]] for i, j in pairs)) for p in perms))
                    return
                i, j = pairs[k]
                for m in range(0, min(sizes[i] - deg[i], sizes[j] - deg[j]) + 1):
                    M[i][j] = M[j][i] = m
                    deg[i] += m
                    deg[j] += m
                    rec(k + 1)
                    deg[i] -= m
                    deg[j] -= m
                M[i][j] = M[j][i] = 0
            rec(0)
    return out


def missing_one(key):
    sizes, flat = key
    s, M = key_to(sizes, flat)
    G, outcome = grow(s, M, rounds=45, maxj=12000)
    c = G.counts()
    d = read_dim(c, outcome)
    ratio = round(c[-1] / c[-2], 3) if len(c) > 2 and c[-2] else None
    return {"key": [list(sizes), list(flat)], "outcome": outcome, "dim": d if outcome != "stall" else "stall", "rounds": G.rounds,
            "last counts": c[-5:], "last ratio": ratio}


def part_missing(workers=16):
    """The arrangements the study's run has not read yet, grown by the referee."""
    from multiprocessing import Pool
    keys = all_keys()
    read = {(tuple(r["key"][0]), tuple(r["key"][1])) for r in study_rows()}
    miss = sorted(keys - read)
    with Pool(workers) as P:
        res = P.map(missing_one, miss, chunksize=1)
    return {"all distinct arrangements (referee's enumeration)": len(keys), "read by the study's run": len(read & keys),
            "read keys not in the referee's enumeration": len(read - keys), "missing": len(miss),
            "missing, by outcome": dict(Counter(str(r["dim"]) for r in res)), "rows": res}


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"count": part_count, "rings": part_rings, "sample": part_sample, "six": part_six, "missing": part_missing}[part](), indent=1, default=str))
