"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001N (own code, on the referee's 001F/001G/001L-R1 machinery; histories read from
the study's JSON files as data; no Codex code imported or run).

  ../../../.venv/bin/python -B referee_n.py <part> > referee_n_<part>.json      (from this directory)

The four-addition family: a ternary seed (the only three-place site); the first two additions unary with three fresh; exactly two
further three-fresh additions with one, two or three parents; every other addition two- or three-parent with two fresh.

Parts:
  w23   the width-23 swap (12 18): the history, the tables through D = 4, 5 and in full, the verdicts, the least bonds through the
        marks, whether every symmetry of the table through D = 4 and D = 5 keeps the menu and the supports.
  w31   the width-31 pair: legality and membership, the tables on the same names, the equation spaces and the named state, the
        menus, the hidden junction's role, the swap (26 27); the old prefix's own family and menu; every possible fourth junction on
        the old prefix (every legal parent group of one, two or three holders, every choice of loose distinctions, three fresh
        named 28, 29, 30) against the given table, on the same names and up to renaming; the table's own symmetries; the D = 3
        control (24 25); and every common two-output continuation to depth two, compared on named menus.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001L/referee-R1"))
import referee_l as L  # noqa: E402

F, RG = L.F, L.RG
STUDY = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents"


def in_four(J):
    fresh, parents = L.profile(J)
    if len(J[0]) != 3 or fresh[1:3] != [3, 3] or parents[1:3] != [1, 1]:
        return False
    rest = list(zip(fresh[3:], parents[3:]))
    three = [x for x in rest if x[0] == 3]
    return len(three) == 2 and all(1 <= p <= 3 for f, p in three) and all(f == 2 and p in (2, 3) for f, p in rest if f != 3)


def part_w23():
    w = json.load(open(STUDY / "census.json"))["witnesses"]["D4"]
    J, ok, _, _ = RG.replay(w["left"]["chronological_supports"])
    K, n, _ = L.table(J)
    p = w["permutation"]
    m = L.menu(J)
    S = {frozenset(s) for s in J}
    out = {"width": n, "legal": ok, "in the four-addition family": in_four(J), "fourth site": sorted(J[-1]),
           "pairs": n * (n - 1) // 2,
           "pairs equal under (12 18) through D = 4, D = 5 and in full": [L.pairs_equal(K, K, p, 5), L.pairs_equal(K, K, p, 6), L.pairs_equal(K, K, p)],
           "menu": sorted(sorted(t) for t in m),
           "(15, 18, 19) legal, (12, 15, 19) legal": [frozenset((15, 18, 19)) in m, frozenset((12, 15, 19)) in m],
           "D(9, 12), D(9, 18)": [int(K[9][12]) - 1, int(K[9][18]) - 1],
           "least bond through (15, 18, 19), (12, 15, 19)": [L.least_bond_through(J, (15, 18, 19)), L.least_bond_through(J, (12, 15, 19))],
           "the swap moves the fourth site": frozenset(p[x] for x in J[-1]) not in S}
    for c in (5, 6):
        g = F.generators(F.clip(K, c))[0]
        out[f"through D = {c - 1}: every symmetry keeps the menu, the supports"] = [F.keeps(g, m), F.keeps(g, S)]
    return out


def part_w31():
    d = json.load(open(STUDY / "frontier.json"))["width_31_direct_role"]
    pre = d["old_prefix"]
    JL, okL, _, _ = RG.replay(pre + [d["left_fourth_support"]])
    JR, okR, _, _ = RG.replay(pre + [d["right_fourth_support"]])
    KL, n, _ = L.table(JL)
    KR, _, _ = L.table(JR)
    mL, mR = L.menu(JL), L.menu(JR)
    hidden = sorted(JL[-1])
    out = {"width": n, "legal": [okL, okR], "in the four-addition family": [in_four(JL), in_four(JR)],
           "fourth supports": [sorted(JL[-1]), sorted(JR[-1])],
           "pairs equal on the same names": [L.pairs_equal(KL, KR, list(range(n))), n * (n - 1) // 2],
           "equation spaces equal": L.span(JL) == L.span(JR),
           "state with ones at 24, 25, 27 allowed (left, right)": [L.allowed(JL, [24, 25, 27]) if hasattr(L, "allowed") else
                                                                   all(len(set(S) & {24, 25, 27}) % 2 == 0 for S in JL),
                                                                   all(len(set(S) & {24, 25, 27}) % 2 == 0 for S in JR)],
           "menus": [sorted(sorted(t) for t in mL), sorted(sorted(t) for t in mR)], "menus equal": mL == mR}
    own = defaultdict(list)
    for k, S in enumerate(JL):
        for x in S:
            own[x].append(k)
    out["the hidden junction holds a loose input of every legal triple"] = all(any(own[x] == [len(JL) - 1] for x in t) for t in mL)
    sw = list(range(n))
    sw[26], sw[27] = 27, 26
    out["(26 27) carries left supports onto right"] = {frozenset(sw[x] for x in S) for S in JL} == {frozenset(S) for S in JR}
    out["(26 27) is a symmetry of the left table"] = L.pairs_equal(KL, KL, sw) == n * (n - 1) // 2
    out["least bond through (15, 26, 28) left, right"] = [L.least_bond_through(JL, (15, 26, 28)), L.least_bond_through(JR, (15, 26, 28))]
    out["least bond through (17, 25, 28) left, right"] = [L.least_bond_through(JL, (17, 25, 28)), L.least_bond_through(JR, (17, 25, 28))]
    # the old prefix
    Jp, okp, Tp, _ = RG.replay(pre)
    fp, pp = L.profile(Jp)
    three = [(f, q) for f, q in zip(fp[3:], pp[3:]) if f == 3]
    mp = L.menu(Jp)
    out["old prefix"] = {"width": 1 + max(max(s) for s in Jp), "legal": okp, "three-fresh additions after the first two (fresh, parents)": three,
                         "in 001L's binary-third family": L.in_family(Jp), "menu": sorted(sorted(t) for t in mp)}
    # every possible fourth junction with three fresh outputs on the old prefix
    owner = defaultdict(list)
    for k, S in enumerate(Jp):
        for x in S:
            owner[x].append(k)
    loose = defaultdict(list)
    for x, ks in owner.items():
        if len(ks) == 1:
            loose[ks[0]].append(x)
    cands = same_names = isometric = 0
    named = []
    sym_menus = Counter()
    for r in (1, 2, 3):
        for P in itertools.combinations(sorted(loose), r):
            if not F.legal_sites(Tp, P):
                continue
            for X in itertools.product(*(loose[q] for q in P)):
                cands += 1
                J = Jp + [sorted(list(X) + [28, 29, 30])]
                K, _, _ = L.table(J)
                if L.pairs_equal(KL, K, list(range(n))) == n * (n - 1) // 2:
                    same_names += 1
                    named.append(sorted(J[-1]))
                g = F.isometric(KL, K)
                if g is not None:
                    isometric += 1
                    sym_menus[str(sorted(sorted(frozenset(g[x] for x in t)) for t in mL) == sorted(sorted(t) for t in L.menu(J)))] += 1
    out["fourth junctions on the old prefix (three fresh)"] = {"candidates": cands, "same table on the same names": same_names,
                                                                "their supports": named, "isometric tables (any renaming)": isometric,
                                                                "... the isometry carries the menu onto the candidate's": dict(sym_menus)}
    gens = F.generators(KL)[0]
    out["full-table symmetries keep the left menu"] = F.keeps(gens, mL)
    out["full-table symmetries keep the left supports"] = F.keeps(gens, {frozenset(S) for S in JL})
    for c in (5, 6):
        g = F.generators(F.clip(KL, c))[0]
        out[f"through D = {c - 1}: every symmetry keeps the menu"] = F.keeps(g, mL)
    q = list(range(n))
    q[24], q[25] = 25, 24
    out["(24 25): pairs equal through D = 3, D = 4 and in full"] = [L.pairs_equal(KL, KL, q, 4), L.pairs_equal(KL, KL, q, 5), L.pairs_equal(KL, KL, q)]
    out["(17, 25, 28) legal, (17, 24, 28) legal"] = [frozenset((17, 25, 28)) in mL, frozenset((17, 24, 28)) in mL]
    # common two-output continuations, depth one and two, on the same names
    rows = Counter()
    for X in L.common_moves(JL, JR):
        A, nx = L.extend(JL, X, 2, 31)
        B, _ = L.extend(JR, X, 2, 31)
        rows["depth 1"] += 1
        rows["depth 1, named menus equal"] += L.menu(A) == L.menu(B)
        for Y in L.common_moves(A, B):
            A2, _ = L.extend(A, Y, 2, nx)
            B2, _ = L.extend(B, Y, 2, nx)
            rows["depth 2"] += 1
            rows["depth 2, named menus equal"] += L.menu(A2) == L.menu(B2)
    out["common two-output continuations"] = dict(rows)
    return out


if __name__ == "__main__":
    print(json.dumps({"w23": part_w23, "w31": part_w31}[sys.argv[1]](), indent=1, default=str))
