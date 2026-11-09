"""Checks for REROUTE-20261109-001A: why a contact's closed walks come out even without a flip. Maps are FLIP-RULE-20261109-001B's
permutations sigma of darts 0 .. 2E - 1 (contact(d) = d >> 1, alpha(d) = d xor 1, rings the cycles of sigma, faces the cycles of
sigma alpha); the contact graph has an arc contact(d) -> contact(sigma d) for every dart, and a contact persists exactly when every count
of closed walks at it is even (LOOP-NET-20261108-001A, Theorem 2 (a), at equal spacing). Readings are exact; the classification is
exhaustive to six contacts (non-degenerate maps at six, normalised by sigma(0) = 2) and sampled from seven to ten.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import collections
import hashlib
import importlib.util
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FLIP = ROOT / "experiments/FLIP-RULE-20261109-001B"
RESCUE = ROOT / "proofs/RESCUE-MAP-20261109-001A/RESCUE-MAP-20261109-001A-P001_short_loops_rescue"
SAMPLED = {7: 4000000, 8: 4000000, 9: 4000000, 10: 4000000}
SEED = 20261111
EXAMPLE = (5, 7, 11, 10, 8, 9, 3, 4, 2, 0, 6, 1)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R1 = load("run", FLIP / "FLIP-RULE-20261109-001B-E001_small_maps/run.py")
R2 = load("flip_e002", FLIP / "FLIP-RULE-20261109-001B-E002_nondegenerate_maps/run.py")
sys.path.insert(0, str(RESCUE))
import rescue_lib as RL  # noqa: E402

OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------- the contact graph and its odd arcs
def multigraph(sig):
    E = len(sig) // 2
    M = [[0] * E for _ in range(E)]
    for d in range(len(sig)):
        M[d >> 1][sig[d] >> 1] += 1
    return M


def odd_rows(sig):
    """N = the contact graph mod 2 as bit rows: an arc a -> b survives when a has one dart, not two, leading to b"""
    E = len(sig) // 2
    rows = [0] * E
    for d in range(len(sig)):
        rows[d >> 1] ^= 1 << (sig[d] >> 1)
    return rows


def doubled_pairs(sig):
    """(a, b): both darts of a lead to b, so b follows a on both of their rings"""
    return [(c, sig[2 * c] >> 1) for c in range(len(sig) // 2) if sig[2 * c] >> 1 == sig[2 * c + 1] >> 1]


def on_odd_cycle(rows, c):
    reach, frontier = 0, rows[c]
    while frontier:
        reach |= frontier
        nxt, x = 0, frontier
        while x:
            low = x & -x
            nxt |= rows[low.bit_length() - 1]
            x ^= low
        frontier = nxt & ~reach
    return bool(reach >> c & 1)


def find_aut(M, fixed):
    """an automorphism of the multigraph M (arc multiplicities kept) extending the partial map fixed, or None"""
    E = len(M)
    prof = [(sorted(M[i]), sorted(M[j][i] for j in range(E)), M[i][i]) for i in range(E)]
    pi, used = dict(fixed), set(fixed.values())
    if any(prof[a] != prof[b] for a, b in pi.items()) or any(M[a][b] != M[pi[a]][pi[b]] for a in pi for b in pi):
        return None
    order = [v for v in range(E) if v not in pi]

    def bt(i):
        if i == len(order):
            return True
        v = order[i]
        for w in range(E):
            if w in used or prof[w] != prof[v]:
                continue
            if all(M[v][a] == M[w][pi[a]] and M[a][v] == M[pi[a]][w] for a in pi):
                pi[v] = w
                used.add(w)
                if bt(i + 1):
                    return True
                del pi[v]
                used.discard(w)
        return False
    return dict(pi) if bt(0) else None


def graph_flip(M, c):
    """an automorphism of the contact graph fixing c and exchanging its two out-arcs, or its two in-arcs (neither an arc c -> c)"""
    E = len(M)
    h = [j for j in range(E) for _ in range(M[c][j])]
    t = [i for i in range(E) for _ in range(M[i][c])]
    return (c not in h and h[0] != h[1] and find_aut(M, {c: c, h[0]: h[1]}) is not None) or \
        (c not in t and t[0] != t[1] and find_aut(M, {c: c, t[0]: t[1]}) is not None)


# ---------- det(I + tN) over GF(2)[t], polynomials as bit masks
def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pdiv(a, b):
    q, db = 0, b.bit_length()
    while a and a.bit_length() >= db:
        s = a.bit_length() - db
        q ^= 1 << s
        a ^= b << s
    return q, a


def det_poly(rows, keep):
    """det(I + tN) restricted to the contacts in keep, by fraction-free elimination (Bareiss) over GF(2)[t]"""
    idx = list(keep)
    n = len(idx)
    if n == 0:
        return 1
    A = [[(1 if i == j else 0) ^ (2 if rows[a] >> b & 1 else 0) for j, b in enumerate(idx)] for i, a in enumerate(idx)]
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            for r in range(k + 1, n):
                if A[r][k]:
                    A[k], A[r] = A[r], A[k]
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                q, rem = pdiv(pmul(A[i][j], A[k][k]) ^ pmul(A[i][k], A[k][j]), prev)
                assert rem == 0
                A[i][j] = q
        prev = A[k][k]
    return A[n - 1][n - 1]


def mechanism(sig, c, rows, M):
    if R1.symmetries(sig, c)[0]:
        return "map flip"
    if not on_odd_cycle(rows, c):
        return "doubled pairs block every closed walk"
    if graph_flip(M, c):
        return "contact-graph flip"
    return "none found"


def read_map(sig, acc, theorems):
    E = len(sig) // 2
    rows, M = odd_rows(sig), multigraph(sig)
    pers = R1.persistent(sig)
    full = det_poly(rows, range(E))
    for c in range(E):
        crit = det_poly(rows, [x for x in range(E) if x != c]) == full
        blocked = not on_odd_cycle(rows, c)
        gflip = graph_flip(M, c)
        theorems["criterion holds"] += crit == pers[c]
        theorems["contacts read"] += 1
        theorems["blocked contacts"] += blocked
        theorems["blocked and persistent"] += blocked and pers[c]
        theorems["contact-graph flips"] += gflip
        theorems["contact-graph flip and persistent"] += gflip and pers[c]
        if pers[c]:
            s, h = R2.sends_hears(sig, c)
            acc[("sends and hears" if s and h else "silent or deaf") + ": " + mechanism(sig, c, rows, M)] += 1


def exhaustive_job(args):
    E, first, nondeg_only = args
    n = 2 * E
    acc, dacc, th = collections.Counter(), collections.Counter(), collections.Counter()
    maps = dmaps = 0
    fixed = {0: first[0], 1: first[1]}
    free = [d for d in range(n) if d not in fixed]
    targets = [x for x in range(n) if x not in fixed.values()]
    for p in itertools.permutations(targets):
        sig = [0] * n
        for d, x in fixed.items():
            sig[d] = x
        for d, x in zip(free, p):
            sig[d] = x
        sig = tuple(sig)
        if nondeg_only and not R2.nondegenerate(sig):
            continue
        if not R1.valid(sig):
            continue
        nd = nondeg_only or R2.nondegenerate(sig)
        maps += nd
        dmaps += not nd
        read_map(sig, acc if nd else dacc, th)
    return E, (maps, dmaps), acc, dacc, th


def sampled_job(args):
    E, draws, seed = args
    rng = random.Random(seed)
    n = 2 * E
    acc, th = collections.Counter(), collections.Counter()
    maps = 0
    for _ in range(draws):
        p = list(range(n))
        rng.shuffle(p)
        sig = tuple(p)
        if not R2.nondegenerate(sig) or not R1.valid(sig):
            continue
        maps += 1
        read_map(sig, acc, th)
    return E, (maps, 0), acc, collections.Counter(), th


def closed_walks(sig, c, length):
    """closed walks at c as dart sequences d1 .. dk: contact(d1) = c, contact(sigma d_i) = contact(d_i+1), contact(sigma dk) = c"""
    res = []

    def go(path):
        last = path[-1]
        nxt = sig[last] >> 1
        if len(path) == length:
            if nxt == c:
                res.append(tuple(path))
            return
        for d in (2 * nxt, 2 * nxt + 1):
            go(path + [d])
    for d in (2 * c, 2 * c + 1):
        go([d])
    return res


def lattice_torus(kind, B):
    Q = RL.Quotient(B)
    N = abs(B[0][0] * B[1][1] - B[0][1] * B[1][0])
    pts = sorted({Q.red((i, j)) for i in range(-2 * N, 2 * N + 1) for j in range(-2 * N, 2 * N + 1)})
    if kind == "square":
        dirs = RL.DIRS["square"]
        eid, n = {}, 0
        for v in pts:
            for d in dirs[:2]:
                w = Q.red((v[0] + d[0], v[1] + d[1]))
                if w == v:
                    return None
                eid[(v, d)] = n
                eid[(w, (-d[0], -d[1]))] = n
                n += 1
        # darts: (edge, 0) at edges' first end v, (edge, 1) at w
        dart = {}
        for v in pts:
            for d in dirs:
                e = eid[(v, d)]
                dart[(v, d)] = 2 * e + (0 if d in dirs[:2] else 1)
        sig = [None] * (2 * n)
        for v in pts:
            for i, d in enumerate(dirs):
                sig[dart[(v, d)]] = dart[(v, dirs[(i + 1) % 4])]
        return tuple(sig)
    # honeycomb: A(p) meets B(p), B(p - e1), B(p - e2) by edges e_k(p), dart 2e at A, 2e + 1 at B
    eid = {}
    for p in pts:
        for k in range(3):
            eid[(k, p)] = len(eid)
    sig = [None] * (2 * len(eid))
    for p in pts:
        for k in range(3):
            sig[2 * eid[(k, p)]] = 2 * eid[((k + 1) % 3, p)]
    for p in pts:
        # B(q) holds e_0(q), e_1(q + e1), e_2(q + e2)
        lst = [eid[(0, p)], eid[(1, Q.red((p[0] + 1, p[1])))], eid[(2, Q.red((p[0], p[1] + 1)))]]
        if len(set(lst)) < 3:
            return None
        for i in range(3):
            sig[2 * lst[i] + 1] = 2 * lst[(i + 1) % 3] + 1
    if any(s is None for s in sig):
        return None
    return tuple(sig)


def hnf(N):
    for p in range(1, N + 1):
        if N % p == 0:
            for q in range(p):
                yield ((p, 0), (q, N // p))


def contains(B, v):
    (a, b), (c, d) = B
    det = a * d - b * c
    return (v[0] * d - v[1] * c) % det == 0 and (v[1] * a - v[0] * b) % det == 0


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    # 1. the six-contact example: doubled pairs pair its closed walks
    sig = EXAMPLE
    E = len(sig) // 2
    rings = R2.cycles(sig)  # cycle lengths
    faces = R2.cycles([sig[d ^ 1] for d in range(len(sig))])
    genus = (2 - (len(rings) - E + len(faces))) // 2
    pairs = doubled_pairs(sig)
    pairdarts = {d for a, b in pairs for d in (2 * a, 2 * a + 1)}
    M = multigraph(sig)
    counts, ok, toggled = [], True, True
    P = [[int(i == j) for j in range(E)] for i in range(E)]
    for k in range(1, 13):
        P = [[sum(P[i][m] * M[m][j] for m in range(E)) for j in range(E)] for i in range(E)]
        walks = closed_walks(sig, 0, k)
        counts.append(len(walks))
        ok &= len(walks) == P[0][0]
        ws = set(walks)
        for w in walks:
            i = next((i for i, d in enumerate(w) if d in pairdarts), None)
            if i is None:
                toggled = False
                break
            w2 = w[:i] + (w[i] ^ 1,) + w[i + 1:]
            toggled &= w2 in ws and w2 != w
    check("1_the_six_contact_example_is_paired_by_two_doubled_pairs",
          ok and toggled and sorted(pairs) == [(1, 5), (2, 4)] and genus == 2 and R2.nondegenerate(sig) and R1.persistent(sig)[0]
          and R2.sends_hears(sig, 0) == (True, True) and not R1.symmetries(sig, 0)[0] and not graph_flip(M, 0)
          and not on_odd_cycle(odd_rows(sig), 0),
          {"rings (sizes)": sorted(rings), "faces (sizes)": sorted(faces), "genus": genus,
           "doubled pairs (a, b): both darts of a lead to b": pairs, "closed walks at contact 0, lengths 1 to 12": counts,
           "every closed walk uses a doubled pair, and toggling the first one is a fixed-point-free involution": toggled,
           "no map flip, no contact-graph flip": True})

    # 2-4: every map of up to five contacts, every non-degenerate map of six (sigma(0) = 2), samples from seven to ten
    jobs = []
    for E in range(1, 6):
        n = 2 * E
        jobs += [(E, (a, b), False) for a in range(n) for b in range(n) if a != b]
    jobs += [(6, (2, x), True) for x in range(12) if x != 2]
    with Pool(16) as pool:
        ex = pool.map(exhaustive_job, jobs, chunksize=1)
        sm = pool.map(sampled_job, [(E, draws // 16, SEED + 100 * E + i) for E, draws in SAMPLED.items() for i in range(16)], chunksize=1)
    table = collections.defaultdict(lambda: {"maps": 0, "persistent contacts": collections.Counter()})
    th = collections.Counter()
    for E, maps, acc, dacc, t in ex:
        key = "exhaustive, E = %d%s" % (E, " (non-degenerate, sigma(0) = 2)" if E == 6 else " (every map; non-degenerate maps)")
        table[key]["maps"] += maps[0]
        table[key]["persistent contacts"].update(acc)
        if E < 6:
            table["exhaustive, E = %d (every map; degenerate maps)" % E]["maps"] += maps[1]
            table["exhaustive, E = %d (every map; degenerate maps)" % E]["persistent contacts"].update(dacc)
        th.update(t)
    for E, maps, acc, dacc, t in sm:
        key = "sampled, E = %d (non-degenerate, %d draws)" % (E, SAMPLED[E])
        table[key]["maps"] += maps[0]
        table[key]["persistent contacts"].update(acc)
        th.update(t)
    table = {k: {"maps": v["maps"], "persistent contacts": dict(sorted(v["persistent contacts"].items()))} for k, v in sorted(table.items())}
    check("2_criterion_persistence_iff_deleting_the_contact_keeps_det", th["criterion holds"] == th["contacts read"],
          {"contacts read": th["contacts read"], "criterion agrees": th["criterion holds"]})
    check("3_both_pairings_imply_persistence",
          th["blocked contacts"] == th["blocked and persistent"] and th["contact-graph flips"] == th["contact-graph flip and persistent"],
          {k: th[k] for k in ("blocked contacts", "blocked and persistent", "contact-graph flips", "contact-graph flip and persistent")})
    first_none = min((int(k.split("E = ")[1].split()[0]) for k, v in table.items()
                      if "degenerate maps)" not in k.replace("non-degenerate", "") and v["persistent contacts"].get("sends and hears: none found")),
                     default=None)
    small_none = sum(v["persistent contacts"].get("sends and hears: none found", 0) for k, v in table.items()
                     if int(k.split("E = ")[1].split()[0]) <= 6 and "degenerate maps)" not in k.replace("non-degenerate", ""))
    check("4_classification_none_found_first_at_seven_contacts", first_none == 7 and small_none == 0,
          {"first size with a persistent contact that sends and hears and has no pairing found": first_none, "table": table})

    # 5. LATTICE-REACH's digon tori: the configuration is a doubled pair, and every face keeps the lattice's size
    info5, ok5 = collections.Counter(), True
    for N in range(2, 31):
        for B in hnf(N):
            for kind, units, fsize in (("square", [(1, 1), (1, -1)], 4), ("honeycomb", [(1, 0), (0, 1), (1, -1)], 6)):
                if not any(contains(B, u) for u in units):
                    continue
                s = lattice_torus(kind, B)
                if s is None:
                    continue
                fs = set(R2.cycles([s[d ^ 1] for d in range(len(s))]))
                dp = doubled_pairs(s)
                info5[kind + " tori"] += 1
                info5[kind + " tori with every face of %d sides" % fsize] += fs == {fsize}
                info5[kind + " tori with a doubled pair"] += bool(dp)
                ok5 &= fs == {fsize} and bool(dp)
    check("5_lattice_reach_digons_are_doubled_pairs_not_faces", ok5 and info5["square tori"] > 0 and info5["honeycomb tori"] > 0, dict(info5))

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "REROUTE-20261109-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
