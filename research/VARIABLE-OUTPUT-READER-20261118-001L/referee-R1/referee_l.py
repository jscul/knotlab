"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001L (own code, on the referee's 001F/001G-R1 machinery; histories read from the
study's JSON files as data; no Codex code imported or run).

  ../../../.venv/bin/python -B referee_l.py <part> > referee_l_<part>.json      (from this directory)

The binary-third family: a ternary seed; the first two additions unary with three fresh; exactly one further addition with two
parents and three fresh (B); every other addition two- or three-parent with two fresh.  The full law: one to three parents, two or
three fresh.  K(x, y) is the least bond size through x and y (D = K - 1); "through D = d" means the table clipped at K = d + 1.

Parts:
  frontier  the loose-holder records, built and closed independently: each live holder's loose count, the adjacencies among live
            holders, and the distinct neighbourhoods (projected to the live holders, at least two) of exhausted holders; the phase
            and the shrinks before B.  Canonical up to renaming the live holders.  Every transition is also made on a literal
            representative, whose record is rebuilt from scratch and whose literal parent roster is compared with the record's.
  w20       the width-20 cross witness and self witness, and the width-26 control.
  w32       the width-32 empty-menu pair.
  cont28    001K's exact width-28 pair: every common first move, every common second move, a third step, the six-step triple, the
            full-law examples (unary and three-output first steps, and the width-46 continuation).
"""
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001G/referee-R1"))
import referee_f as F  # noqa: E402
import referee_g as RG  # noqa: E402

STUDY = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001L/VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third"
K001 = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001K/VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh"


def pc(x):
    return bin(x).count("1")


# ---------------------------------------------------------------- family membership and tables on names


def profile(J):
    fresh = [sum(1 for x in S if all(x not in Q for Q in J[:k])) for k, S in enumerate(J)]
    parents = [len(S) - f for S, f in zip(J, fresh)]
    return fresh, parents


def in_family(J):
    fresh, parents = profile(J)
    if len(J[0]) != 3 or fresh[1:3] != [3, 3] or parents[1:3] != [1, 1]:
        return False
    rest = list(zip(fresh[3:], parents[3:]))
    three = [x for x in rest if x[0] == 3]
    return len(three) == 1 and three[0][1] == 2 and all(f == 2 and p in (2, 3) for f, p in rest if f != 3)


def table(J):
    n = 1 + max(max(S) for S in J)
    K, bonds = F.bond_table(J, n)
    return K, n, bonds


def span(J):
    basis = {}
    for S in J:
        r = sum(1 << x for x in S)
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    # reduced echelon form, so that equal spaces give equal bases
    for p in sorted(basis):
        for q in basis:
            if q != p and basis[q] >> p & 1:
                basis[q] ^= basis[p]
    return frozenset(basis.values())


def menu(J):
    T = F.from_supports(J)
    return {frozenset(t) for t in F.legal_triples(T, J)}


def least_bond_through(J, triple):
    """Least size of a bond containing all three distinctions (shores enumerated as in bond_table)."""
    n = len(J)
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    star = [sum(1 << x for x in S) for S in J]
    adj = [0] * n
    haslo = 0
    for x, ks in owner.items():
        if len(ks) == 2:
            adj[ks[0]] |= 1 << ks[1]
            adj[ks[1]] |= 1 << ks[0]
        else:
            haslo |= 1 << ks[0]
    full = (1 << n) - 1

    def grow(seed, U):
        comp = seed
        while True:
            new = comp
            m = comp
            while m:
                low = m & -m
                new |= adj[low.bit_length() - 1] & U
                m ^= low
            if new == comp:
                return comp
            comp = new
    need = sum(1 << x for x in triple)
    best = None
    word = [0] * (1 << n)
    for U in range(1, 1 << n):
        low = U & -U
        word[U] = word[U ^ low] ^ star[low.bit_length() - 1]
        if word[U] & need != need:
            continue
        if grow(low, U) != U:
            continue
        O = full & ~U
        if grow(O & haslo, O) != O:
            continue
        s = pc(word[U])
        best = s if best is None else min(best, s)
    return best


def pairs_equal(K1, K2, p, L=None):
    """Number of pairs x < y with K1[x][y] == K2[p x][p y] (both clipped at L when given)."""
    A = F.clip(K1, L) if L else K1
    B = F.clip(K2, L) if L else K2
    Bp = B[np.ix_(p, p)]
    iu = np.triu_indices(len(K1), 1)
    return int((A[iu] == Bp[iu]).sum())


# ---------------------------------------------------------------- the frontier records


def canon(loose, adj, nb):
    """Canonical code of a record under renaming its live holders."""
    m = len(loose)
    col = [hash((loose[v], pc(adj[v]), tuple(sorted(pc(N) for N in nb if N >> v & 1)))) for v in range(m)]
    for _ in range(3):
        col = [hash((col[v], tuple(sorted(col[u] for u in range(m) if adj[v] >> u & 1)),
                     tuple(sorted(tuple(sorted(col[u] for u in range(m) if N >> u & 1)) for N in nb if N >> v & 1))))
               for v in range(m)]
    cells = defaultdict(list)
    for v in range(m):
        cells[col[v]].append(v)
    keys = sorted(cells)
    best = None
    for choice in itertools.product(*(itertools.permutations(cells[k]) for k in keys)):
        order = [v for c in choice for v in c]
        pos = {v: i for i, v in enumerate(order)}

        def rm(mask):
            return sum(1 << pos[u] for u in range(m) if mask >> u & 1)
        code = (tuple(loose[v] for v in order), tuple(rm(adj[v]) for v in order), tuple(sorted(rm(N) for N in nb)))
        if best is None or code < best[0]:
            best = (code, order)
    return best


def rec_pair_ok(adj, nb, a, b, m):
    need = 1 << a | 1 << b
    return any(adj[w] & need == need for w in range(m) if w != a and w != b) or any(N & need == need for N in nb)


def rec_triple_ok(adj, nb, P, m):
    a, b, c = P
    if not (rec_pair_ok(adj, nb, a, b, m) and rec_pair_ok(adj, nb, a, c, m) and rec_pair_ok(adj, nb, b, c, m)):
        return False
    need = 1 << a | 1 << b | 1 << c
    return not any(adj[w] & need == need for w in range(m) if w not in P) and not any(N & need == need for N in nb)


def rec_moves(state):
    """(parents, fresh, next phase, shrinks before B) for every family move of a record (phase, tb, loose, adj, nb)."""
    phase, tb, loose, adj, nb = state
    m = len(loose)
    live = [v for v in range(m) if loose[v]]
    out = []
    if phase in (0, 1):
        return [((v,), 3, phase + 1, tb) for v in live]
    for P in itertools.combinations(live, 2):
        if rec_pair_ok(adj, nb, P[0], P[1], m):
            out.append((P, 2, phase, tb))
            if phase == 2:
                out.append((P, 3, 3, tb))
    for P in itertools.combinations(live, 3):
        if rec_triple_ok(adj, nb, P, m):
            out.append((P, 2, phase, tb + (phase == 2)))
    return out


def rec_step(state, P, fresh, phase2, tb2):
    phase, tb, loose, adj, nb = state
    m = len(loose)
    loose = list(loose) + [fresh]
    adj = list(adj) + [sum(1 << p for p in P)]
    for p in P:
        adj[p] |= 1 << m
        loose[p] -= 1
    gone = [p for p in P if loose[p] == 0]
    nbs = set(nb) | {adj[x] for x in gone}
    keep = [v for v in range(m + 1) if loose[v]]
    pos = {v: i for i, v in enumerate(keep)}

    def rm(mask):
        return sum(1 << pos[u] for u in keep if mask >> u & 1)
    nb2 = frozenset(x for x in (rm(N) for N in nbs) if pc(x) >= 2)
    return (phase2, tb2, tuple(loose[v] for v in keep), tuple(rm(adj[v]) for v in keep), nb2), keep


def record_of(T, phase, tb):
    """The record of a literal presentation, from scratch: live holders, their adjacencies, exhausted neighbourhoods."""
    n, adj, loose = T
    live = [v for v in range(n) if loose[v]]
    pos = {v: i for i, v in enumerate(live)}

    def rm(mask):
        return sum(1 << pos[u] for u in live if mask >> u & 1)
    nb = frozenset(x for x in (rm(adj[v]) for v in range(n) if not loose[v]) if pc(x) >= 2)
    return (phase, tb, tuple(loose[v] for v in live), tuple(rm(adj[v]) for v in live), nb), live


def key_of(state):
    phase, tb, loose, adj, nb = state
    code, order = canon(loose, adj, nb)
    return (phase, tb, code), order


def literal_moves(T, phase):
    """Family moves on a literal presentation by its own legality test, as (sorted parent sites, fresh)."""
    out = set()
    for P in F.moves(T):
        if phase in (0, 1):
            if len(P) == 1:
                out.add((P, 3))
            continue
        if len(P) in (2, 3):
            out.add((P, 2))
        if len(P) == 2 and phase == 2:
            out.add((P, 3))
    return out


def part_frontier():
    start = (0, 0, (3,), (0,), frozenset())
    k0, order0 = key_of(start)
    seen = {k0: 0}
    rep = {k0: (start, F.seed(), [0])}        # record state, literal presentation, live holder -> literal site
    q = deque([k0])
    transitions = 0
    by_kind = Counter()
    mismatch_roster = mismatch_record = 0
    succ = defaultdict(list)                  # key -> list of (parents arity, fresh, successor key)
    while q:
        k = q.popleft()
        state, T, live = rep[k]
        phase = state[0]
        mv = rec_moves(state)
        # the record's roster against the literal rule on the representative
        lit = literal_moves(T, phase)
        mine = {(tuple(sorted(live[p] for p in P)), f) for P, f, _, _ in mv}
        mismatch_roster += lit != mine
        for P, f, ph2, tb2 in mv:
            s2, keep = rec_step(state, P, f, ph2, tb2)
            T2 = F.add(T, tuple(sorted(live[p] for p in P)), f)
            live2 = [live[v] if v < len(live) else T[0] for v in keep]
            # rebuild the record from the literal successor and compare canonical forms
            r2, lv2 = record_of(T2, ph2, tb2)
            k2, _ = key_of(s2)
            mismatch_record += key_of(r2)[0] != k2 or sorted(lv2) != sorted(live2)
            transitions += 1
            by_kind[(len(P), f)] += 1
            succ[k].append((len(P), f, k2))
            if k2 not in seen:
                seen[k2] = seen[k] + 1
                rep[k2] = (s2, T2, live2)
                q.append(k2)
    rows = defaultdict(lambda: {"records": 0, "with a legal triple": 0, "earliest width": None, "first positive width": None})
    pre = 0
    positive5 = []
    four = []
    for k, d in seen.items():
        state, T, live = rep[k]
        phase, tb, loose = state[0], state[1], state[2]
        if phase < 3:
            pre += phase == 2
            continue
        t = 8 - sum(loose)
        r = rows[(tb, t)]
        r["records"] += 1
        w = F.width(T)
        has = any(len(P) == 3 for P, f, _, _ in rec_moves(state))
        r["with a legal triple"] += has
        r["earliest width"] = w if r["earliest width"] is None else min(r["earliest width"], w)
        if has:
            r["first positive width"] = w if r["first positive width"] is None else min(r["first positive width"], w)
        if t == 3 and has:
            positive5.append(k)
        if t == 4:
            four.append(k)
    # predecessors of the positive five-loose records along binary two-fresh moves from five-loose records
    pred = Counter()
    for k, lst in succ.items():
        st = rep[k][0]
        if st[0] == 3 and 8 - sum(st[2]) == 3:
            for a, f, k2 in lst:
                if k2 in positive5 and a == 2:
                    pred[k2] += 1
    out = {
        "records": len(seen), "transitions": transitions,
        "transitions by (parents, fresh)": {f"{a},{f}": c for (a, f), c in sorted(by_kind.items())},
        "literal parent roster differs from the record's (records)": mismatch_roster,
        "literal successor's rebuilt record differs (transitions)": mismatch_record,
        "records before B with both unary additions made": pre,
        "after B, by (shrinks before B, total shrinks)": {f"{tb},{t}": v for (tb, t), v in sorted(rows.items())},
        "largest total shrinks": max(t for (tb, t) in rows),
        "positive five-loose records": [{"loose counts": rep[k][0][2], "first width": F.width(rep[k][1]),
                                         "binary predecessors at five loose": pred[k],
                                         "moves": [(a, f) for a, f, _ in succ[k]],
                                         "successors keep a legal triple": [any(len(P) == 3 for P, *_ in rec_moves(rep[k2][0]))
                                                                            for a, f, k2 in succ[k]],
                                         "representative supports": F.supports(rep[k][1])[0]} for k in positive5],
        "four-loose records": [{"loose counts": rep[k][0][2], "moves": [(a, f) for a, f, _ in succ[k]],
                                "successors are the same record": all(k2 == k for _, _, k2 in succ[k])} for k in four],
    }
    return out


# ---------------------------------------------------------------- the witnesses


def part_w20():
    d = json.load(open(STUDY / "census.json"))
    out = {}
    for name in ("first_D3_menu_witness", "first_D3_self_witness"):
        w = d[name]
        JL, okL, TL, _ = RG.replay(w["left"]["chronological_supports"])
        JR, okR, TR, _ = RG.replay(w["right"]["chronological_supports"])
        KL, n, _ = table(JL)
        KR, _, _ = table(JR)
        p = w["permutation"]
        mL, mR = menu(JL), menu(JR)
        img = lambda s: frozenset(p[x] for x in s)  # noqa: E731
        sL = {frozenset(S) for S in JL}
        sR = {frozenset(S) for S in JR}
        r = {"width": n, "legal and in the family": [okL and in_family(JL), okR and in_family(JR)],
             "pairs": n * (n - 1) // 2,
             "pairs equal under the permutation through D = 3": pairs_equal(KL, KR, p, 4),
             "pairs equal through D = 4": pairs_equal(KL, KR, p, 5), "pairs equal in full": pairs_equal(KL, KR, p),
             "menus (left, right)": [sorted(sorted(t) for t in mL), sorted(sorted(t) for t in mR)],
             "transported left menu equals right menu": {img(t) for t in mL} == mR,
             "left supports carried onto right supports": {img(S) for S in sL} == sR,
             "moved supports": sorted(sorted(S) for S in {img(S) for S in sL} - sR)}
        mk = w["marked_example"]
        r["marked: left legal, right legal"] = [frozenset(mk["left"]) in mL, frozenset(mk["right"]) in mR]
        r["least bond through the marked triple (left, right)"] = [least_bond_through(JL, mk["left"]), least_bond_through(JR, mk["right"])]
        for L in (4, 5):
            gens, nq, capped, q = F.generators(F.clip(KL, L))
            r[f"left table through D = {L - 1}: every symmetry keeps the menu, the supports"] = [
                F.keeps(gens, mL) if mL else True, F.keeps(gens, sL)]
        if name == "first_D3_menu_witness":
            r["right table through D = 4: every symmetry keeps the menu, the supports"] = [
                F.keeps(F.generators(F.clip(KR, 5))[0], mR), F.keeps(F.generators(F.clip(KR, 5))[0], sR)]
            r["isometric through D = 4 at all"] = F.isometric(F.clip(KL, 5), F.clip(KR, 5)) is not None
        out[name] = r
    c = d["width26_lower_control"]
    J, ok, T, _ = RG.replay(c["literal_witness"]["chronological_supports"])
    K, n, _ = table(J)
    p = c["permutation"]
    m = menu(J)
    out["width26_lower_control"] = {
        "legal": ok, "in this family": in_family(J), "width": n,
        "pairs changed by the swap through D = 3, 4, 5 and in full": [n * (n - 1) // 2 - pairs_equal(K, K, p, L) for L in (4, 5, 6)]
        + [n * (n - 1) // 2 - pairs_equal(K, K, p)],
        "menu": sorted(sorted(t) for t in m), "mark legal, image legal": [frozenset(c["legal_mark"]) in m, frozenset(c["forbidden_image"]) in m]}
    return out


def part_w32():
    d = json.load(open(STUDY / "empty_witness.json"))
    pre = d["common_prefix"]
    sides = []
    for fj in d["final_joins"]:
        S = fj["support"] if isinstance(fj, dict) and "support" in fj else (fj["inputs"] + fj["outputs"] if isinstance(fj, dict) else fj)
        J, ok, T, _ = RG.replay(pre + [S])
        K, n, bonds = table(J)
        sides.append((J, ok, K, n, bonds))
    (J1, ok1, K1, n, b1), (J2, ok2, K2, _, b2) = sides
    sw = d["support_isomorphism_also_preserving_table"]
    Jp, okp, Tp, _ = RG.replay(pre)
    return {"width": n, "legal and in the family": [ok1 and in_family(J1), ok2 and in_family(J2)],
            "final supports": [sorted(J1[-1]), sorted(J2[-1])],
            "prefix menu": sorted(sorted(t) for t in menu(Jp)),
            "pairs equal on the same names": pairs_equal(K1, K2, list(range(n))), "pairs": n * (n - 1) // 2,
            "equation spaces equal": span(J1) == span(J2), "rank": len(span(J1)), "allowed states": 2 ** (n - len(span(J1))),
            "bonds (left, right)": [b1, b2], "menus": [sorted(sorted(t) for t in menu(J1)), sorted(sorted(t) for t in menu(J2))],
            "supports equal as sets": {frozenset(S) for S in J1} == {frozenset(S) for S in J2},
            "the swap carries left supports onto right": {frozenset(sw[x] for x in S) for S in J1} == {frozenset(S) for S in J2},
            "the swap preserves the left table": pairs_equal(K1, K1, sw) == n * (n - 1) // 2}


# ---------------------------------------------------------------- 001K's exact width-28 pair continued


def holders(J):
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    return owner


def common_moves(J1, J2, nfresh=2, arities=(2, 3)):
    """Input sets legal on both sides on the same names (the narrow law by default)."""
    out = []
    o1, o2 = holders(J1), holders(J2)
    T1, T2 = F.from_supports(J1), F.from_supports(J2)
    l1 = sorted(x for x, ks in o1.items() if len(ks) == 1)
    for r in arities:
        for X in itertools.combinations(l1, r):
            if any(len(o2.get(x, [])) != 1 for x in X):
                continue
            P1 = tuple(sorted(o1[x][0] for x in X))
            P2 = tuple(sorted(o2[x][0] for x in X))
            if len(set(P1)) == r and len(set(P2)) == r and F.legal_sites(T1, P1) and F.legal_sites(T2, P2):
                out.append(X)
    return out


def separation(K1, K2):
    """Number of differing pairs, and the least D at which the identity-clipped tables differ."""
    n = len(K1)
    iu = np.triu_indices(n, 1)
    diff = int((K1[iu] != K2[iu]).sum())
    first = None
    for L in range(2, 20):
        if (F.clip(K1, L)[iu] != F.clip(K2, L)[iu]).any():
            first = L - 1
            break
    return diff, first


def extend(J, X, f, nxt):
    return J + [sorted(list(X) + list(range(nxt, nxt + f)))], nxt + f


def part_cont28():
    d = json.load(open(K001 / "high_check.json"))
    pre = d["prefix_junctions"]
    JL = pre + [d["transition"][0]["cap_inputs"] + d["transition"][0]["cap_outputs"]]
    JR = pre + [d["transition"][1]["cap_inputs"] + d["transition"][1]["cap_outputs"]]
    JL, okL, _, _ = RG.replay(JL)
    JR, okR, _, _ = RG.replay(JR)
    out = {"base legal": [okL, okR]}
    KL, n, _ = table(JL)
    KR, _, _ = table(JR)
    out["base: pairs equal / pairs"] = [pairs_equal(KL, KR, list(range(n))), n * (n - 1) // 2]
    first = common_moves(JL, JR)
    out["common narrow first moves"] = [list(X) for X in first]
    rows = []
    seconds = []
    for X in first:
        A, nx = extend(JL, X, 2, 28)
        B, _ = extend(JR, X, 2, 28)
        Ka, m, _ = table(A)
        Kb, _, _ = table(B)
        diff, fd = separation(Ka, Kb)
        named = [[x, y, int(Ka[x][y]), int(Kb[x][y])] for x in range(m) for y in range(x + 1, m) if Ka[x][y] != Kb[x][y]]
        rows.append({"inputs": list(X), "pairs": m * (m - 1) // 2, "differing": diff, "first differing D": fd, "entries (x, y, K left, K right)": named})
        for Y in common_moves(A, B):
            A2, _ = extend(A, Y, 2, 30)
            B2, _ = extend(B, Y, 2, 30)
            Ka2, _, _ = table(A2)
            Kb2, _, _ = table(B2)
            seconds.append((list(X), list(Y), separation(Ka2, Kb2)))
    out["first moves"] = rows
    out["common second moves"] = {"histories": len(seconds),
                                  "differing pairs (min, max)": [min(s[2][0] for s in seconds), max(s[2][0] for s in seconds)],
                                  "first differing D (counts)": dict(Counter(s[2][1] for s in seconds))}
    # a third common step from every common second step after the first move (23, 25)
    A, _ = extend(JL, (23, 25), 2, 28)
    B, _ = extend(JR, (23, 25), 2, 28)
    thirds = []
    for Y in common_moves(A, B):
        A2, _ = extend(A, Y, 2, 30)
        B2, _ = extend(B, Y, 2, 30)
        for Z in common_moves(A2, B2):
            A3, _ = extend(A2, Z, 2, 32)
            B3, _ = extend(B2, Z, 2, 32)
            Ka3, _, _ = table(A3)
            Kb3, _, _ = table(B3)
            thirds.append(separation(Ka3, Kb3))
    out["common third moves after (23, 25)"] = {"histories": len(thirds), "differing pairs (min, max)": [min(t[0] for t in thirds), max(t[0] for t in thirds)],
                                                "first differing D (counts)": dict(Counter(t[1] for t in thirds))}
    out["binary menus after (23, 25)"] = [sorted(sorted(t) for t in F.legal_menu(F.from_supports(A), A, 2)),
                                          sorted(sorted(t) for t in F.legal_menu(F.from_supports(B), B, 2))]
    # the six-step history to a legal triple at width 40
    c = json.load(open(STUDY / "continuation.json"))
    fp = c["narrow_individual_closure"]["first_positive"]
    res = []
    for J0, seq, mark in ((JL, fp["left_input_sequence"], fp["left_legal_mark"]), (JR, fp["right_input_sequence"], fp["right_legal_mark"])):
        J, nx = J0, 28
        for X in seq:
            J, nx = extend(J, X, 2, nx)
        J, ok, _, _ = RG.replay(J)
        res.append({"legal": ok, "width": nx, "mark legal": frozenset(mark) in menu(J), "triples": len(menu(J))})
    out["six-step triple"] = res
    # full law: first steps
    o1, o2 = holders(JL), holders(JR)
    out["full law: loose on one side only"] = [sorted(x for x in o1 if len(o1[x]) == 1 and len(o2[x]) != 1),
                                               sorted(x for x in o2 if len(o2[x]) == 1 and len(o1[x]) != 1)]
    un = []
    for X in common_moves(JL, JR, arities=(1,)):
        for f in (2, 3):
            A, _ = extend(JL, X, f, 28)
            B, _ = extend(JR, X, f, 28)
            un.append([list(X), f, separation(table(A)[0], table(B)[0])[0]])
    out["full law: common unary first steps (inputs, fresh, differing pairs)"] = un
    b3 = []
    for X in common_moves(JL, JR, arities=(2,)):
        A, _ = extend(JL, X, 3, 28)
        B, _ = extend(JR, X, 3, 28)
        Ka, m, _ = table(A)
        Kb, _, _ = table(B)
        b3.append([list(X), separation(Ka, Kb)[0], sorted({(int(Ka[x][y]), int(Kb[x][y])) for x in range(m) for y in range(x + 1, m) if Ka[x][y] != Kb[x][y]})])
    out["full law: common binary three-output first steps (inputs, differing pairs, K pairs)"] = b3
    # the width-46 continuation
    w46 = c["full_law_identity_equal_with_legal_triples"]
    sides = []
    for J0 in (JL, JR):
        J, nx = J0, 28
        for X, f in w46["inputs_and_output_counts"]:
            J, nx = extend(J, X, f, nx)
        J, ok, _, _ = RG.replay(J)
        K, m, _ = table(J)
        sides.append((J, ok, K, m))
    (A, okA, Ka, m), (B, okB, Kb, _) = sides
    sw = list(range(m))
    sw[21], sw[22] = 22, 21
    out["width 46"] = {"legal under the full law": [okA, okB], "width": m, "pairs": m * (m - 1) // 2,
                       "pairs equal on the same names": pairs_equal(Ka, Kb, list(range(m))),
                       "equation spaces equal": span(A) == span(B),
                       "supports that differ": sorted(sorted(S) for S in {frozenset(S) for S in A} ^ {frozenset(S) for S in B}),
                       "menus equal": menu(A) == menu(B), "legal triples": sorted(sorted(t) for t in menu(A)),
                       "forbidden control legal": frozenset(w46["forbidden_control"]) in menu(A),
                       "(21 22) is a symmetry of the left table": pairs_equal(Ka, Ka, sw) == m * (m - 1) // 2,
                       "(21 22) carries left supports onto right": {frozenset(sw[x] for x in S) for S in A} == {frozenset(S) for S in B},
                       "in the binary-third family": in_family(A)}
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"frontier": part_frontier, "w20": part_w20, "w32": part_w32, "cont28": part_cont28}[part](), indent=1, default=str))
