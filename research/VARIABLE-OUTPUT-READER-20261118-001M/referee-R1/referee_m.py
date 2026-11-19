"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001M (own code, on the referee's 001F/001G/001L-R1 machinery; histories read from
the study's JSON files as data; no Codex code imported or run).

  ../../../.venv/bin/python -B referee_m.py <part> > referee_m_<part>.json      (from this directory)

The unary-third family: a ternary seed; the first two additions unary with three fresh; exactly one further unary three-fresh
addition, at any later time and any loose holder; every other addition two- or three-parent with two fresh.

Parts:
  frontier  the loose-holder records (as in the referee's 001L frontier), with the unary third: every transition also made on a
            literal representative and its record rebuilt; the largest number of shrinks, the least loose count, the five-loose
            records' menus, and whether a positive six-loose record needs the unary third before every shrink.
  w22       the width-22 swap (12 18) and the width-28 J control (19 20).
  w32       the width-32 pair: tables, allowed states, supports, triple menus and two-parent menus on the same names.
  cont46    001L's width-46 continuation of 001K's width-28 pair, one step further: each of its eight legal triples joined with two
            or three fresh distinctions (widths 48 and 49) on both sides; the tables on the same names and the next triple menus.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001L/referee-R1"))
import referee_l as L  # noqa: E402

F, RG = L.F, L.RG
STUDY = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001M/VARIABLE-OUTPUT-READER-20261118-001M-P001_unary_third"


def in_family(J):
    fresh, parents = L.profile(J)
    if len(J[0]) != 3 or fresh[1:3] != [3, 3] or parents[1:3] != [1, 1]:
        return False
    rest = list(zip(fresh[3:], parents[3:]))
    three = [x for x in rest if x[0] == 3]
    return len(three) == 1 and three[0][1] == 1 and all(f == 2 and p in (2, 3) for f, p in rest if f != 3)


# ---------------------------------------------------------------- the frontier with a unary third


def rec_moves(state):
    phase, tb, loose, adj, nb = state
    m = len(loose)
    live = [v for v in range(m) if loose[v]]
    if phase in (0, 1):
        return [((v,), 3, phase + 1, tb) for v in live]
    out = []
    if phase == 2:
        out += [((v,), 3, 3, tb) for v in live]
    for P in itertools.combinations(live, 2):
        if L.rec_pair_ok(adj, nb, P[0], P[1], m):
            out.append((P, 2, phase, tb))
    for P in itertools.combinations(live, 3):
        if L.rec_triple_ok(adj, nb, P, m):
            out.append((P, 2, phase, tb + (phase == 2)))
    return out


def literal_moves(T, phase):
    out = set()
    for P in F.moves(T):
        if phase in (0, 1):
            if len(P) == 1:
                out.add((P, 3))
            continue
        if len(P) in (2, 3):
            out.add((P, 2))
        if len(P) == 1 and phase == 2:
            out.add((P, 3))
    return out


def part_frontier():
    start = (0, 0, (3,), (0,), frozenset())
    k0, _ = L.key_of(start)
    seen = {k0: 0}
    rep = {k0: (start, F.seed(), [0])}
    q = deque([k0])
    transitions = 0
    by_kind = Counter()
    bad_roster = bad_record = 0
    succ = defaultdict(list)
    while q:
        k = q.popleft()
        state, T, live = rep[k]
        mv = rec_moves(state)
        mine = {(tuple(sorted(live[p] for p in P)), f) for P, f, _, _ in mv}
        bad_roster += literal_moves(T, state[0]) != mine
        for P, f, ph2, tb2 in mv:
            s2, keep = L.rec_step(state, P, f, ph2, tb2)
            T2 = F.add(T, tuple(sorted(live[p] for p in P)), f)
            live2 = [live[v] if v < len(live) else T[0] for v in keep]
            r2, lv2 = L.record_of(T2, ph2, tb2)
            k2, _ = L.key_of(s2)
            bad_record += L.key_of(r2)[0] != k2 or sorted(lv2) != sorted(live2)
            transitions += 1
            by_kind[(len(P), f)] += 1
            succ[k].append((len(P), f, k2))
            if k2 not in seen:
                seen[k2] = seen[k] + 1
                rep[k2] = (s2, T2, live2)
                q.append(k2)
    rows = defaultdict(lambda: {"records": 0, "with a legal triple": 0, "earliest width": None, "first positive width": None})
    pre = 0
    five_pos = six_pos_tb = 0
    min_loose = 99
    for k in seen:
        state, T, live = rep[k]
        phase, tb, loose = state[0], state[1], state[2]
        if phase < 3:
            pre += phase == 2
            continue
        t = 9 - sum(loose)
        min_loose = min(min_loose, sum(loose))
        r = rows[(tb, t)]
        r["records"] += 1
        w = F.width(T)
        has = any(len(P) == 3 for P, *_ in rec_moves(state))
        r["with a legal triple"] += has
        r["earliest width"] = w if r["earliest width"] is None else min(r["earliest width"], w)
        if has:
            r["first positive width"] = w if r["first positive width"] is None else min(r["first positive width"], w)
        five_pos += sum(loose) == 5 and has
        six_pos_tb += sum(loose) == 6 and has and tb > 0
    return {"records": len(seen), "transitions": transitions,
            "transitions by (parents, fresh)": {f"{a},{f}": c for (a, f), c in sorted(by_kind.items())},
            "literal parent roster differs from the record's (records)": bad_roster,
            "literal successor's rebuilt record differs (transitions)": bad_record,
            "records before the unary third with both early unary additions made": pre,
            "after the unary third, by (shrinks before it, total shrinks)": {f"{a},{b}": v for (a, b), v in sorted(rows.items())},
            "largest total shrinks": max(t for (_, t) in rows), "least loose count after the unary third": min_loose,
            "five-loose records with a legal triple": five_pos,
            "positive six-loose records with a shrink before the unary third": six_pos_tb}


# ---------------------------------------------------------------- the witnesses


def part_w22():
    d = json.load(open(STUDY / "census.json"))
    w = d["witnesses"]["first_D3_opposition"]
    JL, okL, _, _ = RG.replay(w["left"]["chronological_supports"])
    JR, okR, _, _ = RG.replay(w["right"]["chronological_supports"])
    KL, n, _ = L.table(JL)
    KR, _, _ = L.table(JR)
    p = w["permutation"]
    mL, mR = L.menu(JL), L.menu(JR)
    sL = {frozenset(S) for S in JL}
    out = {"width": n, "legal and in the family": [okL and in_family(JL), okR and in_family(JR)],
           "the two histories are one": JL == JR, "pairs": n * (n - 1) // 2,
           "pairs equal under the swap through D = 3, 4 and in full": [L.pairs_equal(KL, KR, p, 4), L.pairs_equal(KL, KR, p, 5),
                                                                     L.pairs_equal(KL, KR, p)],
           "menu": sorted(sorted(t) for t in mL), "mark (15, 18, 19) legal, image (12, 15, 19) legal":
               [frozenset((15, 18, 19)) in mL, frozenset((12, 15, 19)) in mR],
           "K(9, 12), K(9, 18)": [int(KL[9][12]), int(KL[9][18])],
           "least bond through the mark and its image": [L.least_bond_through(JL, (15, 18, 19)), L.least_bond_through(JL, (12, 15, 19))],
           "the swap moves a support": {frozenset(p[x] for x in S) for S in JL} != sL}
    for Lc in (4, 5):
        gens = F.generators(F.clip(KL, Lc))[0]
        out[f"table through D = {Lc - 1}: every symmetry keeps the menu, the supports"] = [F.keeps(gens, mL), F.keeps(gens, sL)]
    c = d["unary_append_J_control"]
    J, ok, _, _ = RG.replay(c["history"]["chronological_supports"])
    K, n2, _ = L.table(J)
    q = c["permutation"]
    m = L.menu(J)
    out["width-28 J control"] = {"legal": ok, "in the family": in_family(J), "width": n2,
                                 "pairs changed through D = 3, 4, 5 and in full": [n2 * (n2 - 1) // 2 - L.pairs_equal(K, K, q, Lc) for Lc in (4, 5, 6)]
                                 + [n2 * (n2 - 1) // 2 - L.pairs_equal(K, K, q)],
                                 "mark legal, image legal": [frozenset(c["legal_mark"]) in m, frozenset(c["forbidden_image"]) in m]}
    return out


def part_w32():
    e = json.load(open(STUDY / "examples.json"))["first_complement"]
    pre = e["common_prefix"]
    sides = []
    for X in e["chosen"]:
        J, ok, _, _ = RG.replay(pre + [list(X) + e["new_outputs"]])
        K, n, bonds = L.table(J)
        T = F.from_supports(J)
        sides.append((J, ok, K, n, {frozenset(t) for t in F.legal_menu(T, J, 2)}))
    (J1, ok1, K1, n, p1), (J2, ok2, K2, _, p2) = sides
    return {"width": n, "legal and in the family": [ok1 and in_family(J1), ok2 and in_family(J2)],
            "final supports": [sorted(J1[-1]), sorted(J2[-1])],
            "pairs equal on the same names": L.pairs_equal(K1, K2, list(range(n))), "pairs": n * (n - 1) // 2,
            "equation spaces equal": L.span(J1) == L.span(J2), "rank": len(L.span(J1)),
            "triple menus": [sorted(sorted(t) for t in L.menu(J1)), sorted(sorted(t) for t in L.menu(J2))],
            "two-parent menus": [sorted(sorted(t) for t in p1), sorted(sorted(t) for t in p2)],
            "(25, 27) a legal pair on each side": [frozenset((25, 27)) in p1, frozenset((25, 27)) in p2]}


def _cont(args):
    side, J = args
    J, ok, _, _ = RG.replay(J)
    K, n, _ = L.table(J)
    return side, ok, K, n, L.menu(J)


def part_cont46():
    d = json.load(open(L.K001 / "high_check.json"))
    pre = d["prefix_junctions"]
    base = []
    for tr in d["transition"]:
        J, _, _, _ = RG.replay(pre + [tr["cap_inputs"] + tr["cap_outputs"]])
        base.append(J)
    c = json.load(open(L.STUDY / "continuation.json"))["full_law_identity_equal_with_legal_triples"]
    w46 = []
    for J0 in base:
        J, nx = J0, 28
        for X, f in c["inputs_and_output_counts"]:
            J, nx = L.extend(J, X, f, nx)
        w46.append(J)
    triples = sorted(sorted(t) for t in L.menu(w46[0]))
    jobs = []
    for t in triples:
        for f in (2, 3):
            for side in (0, 1):
                J, _ = L.extend(w46[side], t, f, 46)
                jobs.append(((tuple(t), f, side), J))
    with Pool(8) as pool:
        res = pool.map(_cont, jobs, chunksize=1)
    by = defaultdict(dict)
    for (t, f, side), ok, K, n, m in res:
        by[(t, f)][side] = (ok, K, n, m)
    rows = []
    for (t, f), v in sorted(by.items()):
        (okA, KA, n, mA), (okB, KB, _, mB) = v[0], v[1]
        rows.append({"triple": list(t), "fresh": f, "width": n, "legal both sides": okA and okB,
                     "pairs equal on the same names": L.pairs_equal(KA, KB, list(range(n))), "pairs": n * (n - 1) // 2,
                     "next triple menus": [len(mA), len(mB)]})
    return {"base triples at width 46": triples, "continuations": len(rows),
            "all legal": all(r["legal both sides"] for r in rows),
            "all tables equal": all(r["pairs equal on the same names"] == r["pairs"] for r in rows),
            "all next menus empty": all(r["next triple menus"] == [0, 0] for r in rows), "rows": rows}


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"frontier": part_frontier, "w22": part_w22, "w32": part_w32, "cont46": part_cont46}[part](), indent=1,
                     default=str))
