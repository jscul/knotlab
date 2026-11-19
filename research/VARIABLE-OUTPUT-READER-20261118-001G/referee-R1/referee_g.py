"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001G (own code, on the referee's 001F-R1 machinery: shore-enumerated bond
tables, exact twin-quotient symmetries; none of the study's checkers are imported; the histories are read from checks.json and
six_check.json as data).

  ../../../.venv/bin/python -B referee_g.py <part> [args] > referee_g_<part>.json      (from this directory)

Parts:
  witnesses   every named pair of the study, replayed from the seed under the referee's law check: the width-27 rank gap (two
              three-fresh joins), the width-26 and width-27 three- and four-addition pairs, the width-29 common attachment, the
              width-15 and width-18 swaps; for each, the clipped tables compared on the same names at every horizon, the first
              horizon that separates them, the marked triple's two verdicts, ranks, and the named pair values; and one size past
              the study: the width-29 pair with one more matched unary three-fresh join (five three-fresh joins, width 32).
  cutoff W    the cutoff table, exhaustively at widths 15..W: for every presentation H whose junctions all have at most four
              distinctions (s three-fresh joins), at its stated horizon L(s) (K through 4, 5, 6 for s <= 1, s = 2, s >= 3): no
              other presentation of the same width has a clipped table isometric to H's, and every symmetry of H's clipped table
              keeps H's junction supports (so every rival, of any arity, has H's junctions); and at L(s) - 1 how often either
              fails and how often a triple verdict flips.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
import referee_f as F  # noqa: E402

FAM = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001G/VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh"


def replay(steps):
    """steps: list of supports in birth order, the first the seed.  Returns (supports, legal, site graph, s)."""
    J = [sorted(steps[0])]
    legal = len(steps[0]) == 3
    s = 0
    for S in steps[1:]:
        T = F.from_supports(J)
        owner = defaultdict(list)
        for k, Q in enumerate(J):
            for x in Q:
                owner[x].append(k)
        old = [x for x in S if x in owner]
        fresh = [x for x in S if x not in owner]
        P = tuple(sorted(owner[x][0] for x in old))
        legal &= all(len(owner[x]) == 1 for x in old) and len(set(P)) == len(P) and 1 <= len(P) <= 3
        legal &= F.legal_sites(T, P) and len(fresh) in (2, 3)
        s += len(fresh) == 3
        J.append(sorted(S))
    return J, legal, F.from_supports(J), s


def rank(J):
    basis = {}
    for S in J:
        r = sum(1 << x for x in S)
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return len(basis)


def compare(name, src_steps, riv_steps=None, swap=None, mark=None, pairs=()):
    J1, ok1, T1, s1 = replay(src_steps)
    if swap is not None:
        J2 = [sorted(swap.get(x, x) for x in S) for S in J1]
        ok2, T2, s2 = ok1, F.from_supports(J2), s1
    else:
        J2, ok2, T2, s2 = replay(riv_steps)
    n1 = 1 + max(max(S) for S in J1)
    n2 = 1 + max(max(S) for S in J2)
    K1, b1 = F.bond_table(J1, n1)
    K2, b2 = F.bond_table(J2, n2)
    out = {"case": name, "width": [n1, n2], "histories legal": [ok1, ok2], "three-fresh joins": [s1, s2],
           "largest junction": [max(map(len, J1)), max(map(len, J2))], "ranks": [rank(J1), rank(J2)], "bonds": [b1, b2]}
    if n1 == n2:
        n = n1
        pairs_all = n * (n - 1) // 2
        eq = {}
        for L in range(3, 16):
            C1, C2 = F.clip(K1, L), F.clip(K2, L)
            eq[L] = int(sum(C1[x][y] == C2[x][y] for x in range(n) for y in range(x + 1, n)))
        out["pairs"] = pairs_all
        out["pairs equal on the same names, clipped through K = L"] = eq
        out["largest L with every pair equal"] = max([L for L in eq if eq[L] == pairs_all], default=None)
        out["full tables equal on the same names"] = bool((K1 == K2).all())
        h1 = Counter(int(K1[x][y]) for x in range(n) for y in range(x + 1, n))
        h2 = Counter(int(K2[x][y]) for x in range(n) for y in range(x + 1, n))
        out["full K histograms differ"] = h1 != h2
    if mark is not None:
        l1, l2 = F.legal_triples(T1, J1), F.legal_triples(T2, J2)
        m = frozenset(mark)
        out["mark"] = mark
        out["mark legal in source / rival"] = [m in l1, m in l2]
        out["legal triples"] = [len(l1), len(l2)]
    for (x, y) in pairs:
        out[f"K({x}, {y}) source / rival"] = [int(K1[x][y]), int(K2[x][y])]
    return out, (J1, J2)


def steps_from_history(h):
    return [x["support"] for x in h]


def part_witnesses():
    chk = json.load(open(FAM / "checks.json"))["width_27_rank_gap_at_equal_short_observation"]
    six = json.load(open(FAM / "six_check.json"))
    res = []
    hs = [x["operands"] + x["fresh"] for x in chk["original"]["history"]]
    hr = [x["operands"] + x["fresh"] for x in chk["all_two_fresh_rival"]["history"]]
    r, _ = compare("width 27: two three-fresh joins against an all-two-fresh rival", hs, hr, mark=chk["opposing_mark"],
                   pairs=[tuple(chk["cap_fresh_output_pair"]["pair"]), tuple(chk["named_pair_disagreement"]["pair"])])
    res.append(r)
    for c in six["cases"]:
        r, _ = compare(f"width {c['width']}: {c['case']}", steps_from_history(c["source"]["history"]),
                       steps_from_history(c["rival"]["history"]), mark=c["opposite_triple_verdict"]["mark"],
                       pairs=[tuple(p["pair"]) for p in ([c["late_parent_and_auxiliary_root"]] if c.get("late_parent_and_auxiliary_root") else []) + c.get("two_nonroot_children", [])])
        res.append(r)
    c = six["common_attachment_control"]
    src, riv = steps_from_history(c["source"]["history"]), steps_from_history(c["rival"]["history"])
    r, _ = compare(f"width {c['width']}: {c['case']}", src, riv, mark=c["opposite_triple_verdict"]["mark"])
    res.append(r)
    # one size past: one more matched unary three-fresh join on z's loose output 28 (not a mark), on both sides
    r, _ = compare("one size past: width 32, five three-fresh joins (unary three-fresh join on bit 28 on both sides)",
                   src + [[28, 29, 30, 31]], riv + [[28, 29, 30, 31]], mark=c["opposite_triple_verdict"]["mark"])
    res.append(r)
    for c in six["lower_cutoff_controls"]:
        a, b = c["transposed"]
        r, _ = compare(f"width {c['width']}: swap ({a} {b})", steps_from_history(c["presentation"]["history"]),
                       swap={a: b, b: a}, mark=c["legal_mark"])
        r["image of the mark legal"] = None
        J1, ok, T1, s = replay(steps_from_history(c["presentation"]["history"]))
        r["image of the mark legal"] = frozenset(c["forbidden_image"]) in F.legal_triples(T1, J1)
        res.append(r)
    return res


# ---------------------------------------------------------------- exhaustive cutoff table


def horizon(s):
    return 4 if s <= 1 else 5 if s == 2 else 6


def _prep(args):
    T, Ls = args
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    small = max(map(len, J)) <= 4
    s = n - 1 - 2 * T[0]
    return {"T": T, "small": small, "s": s, "inv": {L: F.invariant(F.clip(K, L)) for L in Ls}}


def _self_check(args):
    T, L = args
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    C = F.clip(K, L)
    gens, nq, capped, q = F.generators(C)
    stars = {frozenset(S) for S in J}
    legal = F.legal_triples(T, J)
    return {"keeps stars": F.keeps(gens, stars), "keeps triples": F.keeps(gens, legal) if legal else True, "capped": capped}


def _cross_check(args):
    """H against every rival in its bucket at horizon L: is any rival's clipped table isometric to H's, and does that isometry
    carry H's legal triples onto the rival's?"""
    H, rivals, L = args
    JH, n = F.supports(H)
    CH = F.clip(F.bond_table(JH, n)[0], L)
    lh = F.legal_triples(H, JH)
    iso = flips = 0
    for R in rivals:
        JR, _ = F.supports(R)
        CR = F.clip(F.bond_table(JR, n)[0], L)
        p = F.isometric(CH, CR)
        if p is None:
            continue
        iso += 1
        lr = F.legal_triples(R, JR)
        flips += {frozenset(p[x] for x in t) for t in lh} != lr
    return iso, flips


def part_cutoff(wmax=21, wmin=15):
    levels = F.census(wmax)
    out = {}
    with Pool(20) as pool:
        for w in range(wmin, wmax + 1):
            Ls = (3, 4, 5, 6)
            rows = pool.map(_prep, [(T, Ls) for T in levels[w]], chunksize=32)
            buckets = {L: defaultdict(list) for L in Ls}
            for i, r in enumerate(rows):
                for L in Ls:
                    buckets[L][r["inv"][L]].append(i)
            stats = defaultdict(Counter)
            small = [i for i, r in enumerate(rows) if r["small"]]
            for i in small:
                stats[rows[i]["s"]]["small-arity presentations"] += 1
            for label, shift in (("at the stated horizon", 0), ("one below it", -1)):
                jobs_self, jobs_cross, keys = [], [], []
                for i in small:
                    L = horizon(rows[i]["s"]) + shift
                    jobs_self.append((rows[i]["T"], L))
                    rivals = [rows[k]["T"] for k in buckets[L][rows[i]["inv"][L]] if k != i]
                    if shift:
                        stats[rows[i]["s"]][f"{label}: rivals sharing the invariant (only the first 30 tested)"] += len(rivals)
                        rivals = rivals[:30]
                    jobs_cross.append((rows[i]["T"], rivals, L))
                    keys.append(i)
                selfs = pool.map(_self_check, jobs_self, chunksize=16)
                cross = pool.map(_cross_check, jobs_cross, chunksize=16)
                for i, a, (iso, flips) in zip(keys, selfs, cross):
                    st = stats[rows[i]["s"]]
                    st[f"{label}: a clipped-table symmetry moves a junction support"] += not a["keeps stars"]
                    st[f"{label}: a clipped-table symmetry moves a legal triple to a forbidden one"] += not a["keeps triples"]
                    st[f"{label}: rivals with an isometric clipped table"] += iso
                    st[f"{label}: ... whose isometry changes a triple verdict"] += flips
                    st[f"{label}: symmetry searches capped"] += a["capped"]
            out[f"width {w}"] = {f"s = {s} (stated horizon K through {horizon(s)})": dict(v) for s, v in sorted(stats.items())}
            print(w, json.dumps(out[f"width {w}"]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    args = [int(a) for a in sys.argv[2:]]
    print(json.dumps({"witnesses": part_witnesses, "cutoff": part_cutoff}[part](*args), indent=1, default=str))
