"""toy_phase.py: the model against Spekkens's toy theory and the phase groups (TOY-PHASE-20261127-001).

Exact checks of the frozen predictions G and P1-P6 in README.md. Run from the repository root:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 prlimit --as=1073741824 -- \
        .venv/bin/python -B research/TOY-PHASE-20261127-001/toy_phase.py

Writes results.json next to this file and prints one line per prediction. Toy-theory work is exact (bit masks and
fractions); qubit work uses complex matrices whose entries are small integers, i or 1/sqrt(2), checked to 1e-12 and
reported as fractions with denominator at most 64. Nothing here imports the birth-sign study's code: its constructions
are rebuilt from its stated definitions (a question is a pair (change, value): multiply by the sign of the value, then
apply the change), and the gate compares the rebuilt tables with its published scores.
"""
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "FORBID-EDITS-20261126-001"))
import forbid  # the archived ordinary engine, as in the no-whole-state fixture

TOL = 1e-12
BITS3 = tuple(itertools.product((0, 1), repeat=3))
QUESTIONS = ((1, 0), (0, 1), (1, 1))  # the toy bit's q, p and q + p, as (q-coefficient, p-coefficient)


def par(x):
    return bin(x).count("1") % 2


def frac(x, den=64):
    f = Fraction(x).limit_denominator(den)
    assert abs(float(f) - x) < TOL, x
    return f


# ---------------------------------------------------------------- toy theory on n toy bits
# An underlying state is a 2n-bit mask: bit 2j is q_j and bit 2j+1 is p_j. A question is a mask of the same shape:
# its answer on a state is the parity of their overlap.

def place(question, j):
    a, b = question
    return (a << (2 * j)) | (b << (2 * j + 1))


def swap_halves(v, n):
    out = 0
    for j in range(n):
        out |= ((v >> (2 * j + 1)) & 1) << (2 * j) | ((v >> (2 * j)) & 1) << (2 * j + 1)
    return out


def bracket(u, v, n):
    """The toy theory's bracket: sum over toy bits of a_j b'_j + a'_j b_j, mod 2 (Spekkens 2016)."""
    return par(u & swap_halves(v, n))


def rank(vectors):
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def support(laws, n):
    return [lam for lam in range(1 << (2 * n)) if all(par(u & lam) == r for u, r in laws)]


def is_toy_state(laws, n):
    """Valid toy state: consistent, with pairwise commuting known questions; pure when they span n dimensions."""
    us = [u for u, _ in laws]
    commuting = all(bracket(u, v, n) == 0 for u, v in itertools.combinations(us, 2))
    return {"commuting": commuting, "rank": rank(us), "support": len(support(laws, n)),
            "pure": commuting and rank(us) == n and len(support(laws, n)) == 1 << n}


def pure_toy_states(n):
    """Every pure toy state of n toy bits: an n-dimensional set of pairwise commuting questions with its answers."""
    spans = set()
    nonzero = range(1, 1 << (2 * n))
    for basis in itertools.combinations(nonzero, n):
        if rank(basis) < n or any(bracket(u, v, n) for u, v in itertools.combinations(basis, 2)):
            continue
        spans.add(frozenset(sum_masks(basis, c) for c in itertools.product((0, 1), repeat=n)))
    states = []
    for span in sorted(spans, key=sorted):
        basis = [v for v in sorted(span) if v]
        gens = []
        for v in basis:
            if rank(gens + [v]) > len(gens):
                gens.append(v)
        for answers in itertools.product((0, 1), repeat=n):
            states.append(tuple(zip(gens, answers)))
    return spans, states


def sum_masks(basis, coefficients):
    out = 0
    for v, c in zip(basis, coefficients):
        if c:
            out ^= v
    return out


# ---------------------------------------------------------------- qubits

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
Y = 1j * X @ Z
S = np.diag([1, 1j])


def kron(*ms):
    out = np.array([[1]], dtype=complex)
    for m in ms:
        out = np.kron(out, m)
    return out


def on(op, j, n):
    return kron(*[op if k == j else I2 for k in range(n)])


def close(a, b):
    return np.allclose(a, b, atol=TOL)


# ---------------------------------------------------------------- the closure (gate G)

def the_closure():
    ring3 = ((0, 1, 2), (1, 3, 4), (3, 0, 5))
    stage, info = forbid.grow(ring3, "parity", "ordinary", forbid.ENGINE)
    knots = [tuple(sorted(k)) for k in stage]
    holders = {d: [k for k in knots if d in k] for d in range(6)}
    pairs = [p for p in itertools.combinations(range(6), 2) if not any(set(p) <= set(k) for k in knots)]
    # reader i: the shared distinction parent i does not hold, then parent i's loose distinction
    parents = [tuple(sorted(r)) for r in ring3]
    shared = sorted(d for d in range(6) if sum(d in r for r in ring3) == 2)
    readers = []
    for r in ring3:
        s = next(d for d in shared if d not in r)
        loose = next(d for d in r if sum(d in q for q in ring3) == 1)
        readers.append((s, loose))
    gate = {
        "knots": knots, "closing knot": knots[-1], "births": len(info["births"]),
        "every two knots share one distinction": all(len(set(a) & set(b)) == 1
                                                      for a, b in itertools.combinations(knots, 2)),
        "every distinction held twice": all(len(h) == 2 for h in holders.values()),
        "pairs no knot holds together": pairs, "readers (s_i, l_i)": readers,
        "readers are those pairs": sorted(tuple(sorted(r)) for r in readers) == sorted(pairs),
        "parents": parents,
    }
    return knots, readers, gate


def allowed_words(knots, laws):
    return [w for w in range(64) if all(par(w & sum(1 << d for d in k)) == laws[i] for i, k in enumerate(knots))]


def contexts(readers):
    """Setting 0 reads s_i, setting 1 reads l_i; scored when one or three readers use setting 1."""
    return {s: [readers[i][s[i]] for i in range(3)] for s in BITS3}


def target(settings):
    changed = sum(settings)
    if changed not in (1, 3):
        return [Fraction(1, 8)] * 8
    required = int(changed == 3)
    return [Fraction(int(sum(a) % 2 == required), 4) for a in BITS3]


def table_of_words(words, readers):
    """The 64 reading probabilities of a uniform weighting on 6-bit words."""
    out = {}
    for s, reads in contexts(readers).items():
        counts = [0] * 8
        for w in words:
            counts[BITS3.index(tuple((w >> d) & 1 for d in reads))] += 1
        out[s] = [Fraction(c, len(words)) for c in counts]
    return out


def score(table):
    win = Fraction(0)
    matches = 0
    for s, row in table.items():
        t = target(s)
        matches += sum(p == q for p, q in zip(row, t))
        if sum(s) in (1, 3):
            win += sum(p for p, q in zip(row, t) if q) / 4
    return win, matches


# ---------------------------------------------------------------- P1: one knot is one toy bit

def knot_states(law, kind):
    if kind == "parity":
        return [w for w in itertools.product((0, 1), repeat=3) if sum(w) % 2 == law]
    return [w for w in itertools.product((0, 1), repeat=3) if len(set(w)) > 1]  # not-all-equal


def allowed_changes(states):
    ss = set(states)
    return [c for c in itertools.product((0, 1), repeat=3)
            if any(c) and all(tuple(a ^ b for a, b in zip(w, c)) in ss for w in states)]


def p1():
    out = {}
    for law in (0, 1):
        states = knot_states(law, "parity")
        for x, y in itertools.permutations(range(3), 2):
            under = {w: (w[x], w[y]) for w in states}           # (q, p)
            bijective = sorted(under.values()) == sorted(itertools.product((0, 1), repeat=2))
            inverse = {qp: w for w, qp in under.items()}
            # each distinction as an affine question of (q, p)
            questions = []
            for d in range(3):
                found = [(qa, pb, c) for qa, pb in itertools.product((0, 1), repeat=2) for c in (0, 1)
                         if (qa, pb) != (0, 0) and all(w[d] == (qa * q + pb * p + c) % 2 for w, (q, p) in under.items())]
                questions.append(found)
            linear = [f[0][:2] for f in questions if len(f) == 1]
            # allowed changes as shifts of (q, p), and incidences
            shifts = {}
            for ch in allowed_changes(states):
                moved = {under[w]: under[tuple(a ^ b for a, b in zip(w, ch))] for w in states}
                t = {((q2 - q) % 2, (p2 - p) % 2) for (q, p), (q2, p2) in moved.items()}
                shifts[ch] = t.pop() if len(t) == 1 else None
            incidence = all(ch[d] == (questions[d][0][0] * t[0] + questions[d][0][1] * t[1]) % 2
                            for ch, t in shifts.items() if t for d in range(3))
            reads = {(d, v): sorted(under[w] for w in states if w[d] == v) for d in range(3) for v in (0, 1)}
            pure = all(len(v) == 2 and len({(questions[d][0][0] * q + questions[d][0][1] * p) % 2 for q, p in v}) == 1
                       for (d, _), v in reads.items())
            sum_rule = all((w[0] + w[1] + w[2]) % 2 == law for w in states)
            out[f"law {law}, coordinates {'ABc'[x]}{'ABc'[y]}"] = {
                "bijective": bijective, "distinctions are the three questions": sorted(linear) == sorted(QUESTIONS),
                "nonzero allowed changes": len(shifts),
                "changes are the three nonzero shifts": sorted(t for t in shifts.values() if t) ==
                                                        sorted({(1, 0), (0, 1), (1, 1)}),
                "incidence kept": incidence, "six one-read states are pure toy states": pure,
                "each distinction the sum of the other two": sum_rule, "inverse defined": len(inverse) == 4}
    nae = knot_states(None, "nae")
    out["control: not-all-equal"] = {
        "allowed states": len(nae), "nonzero allowed changes": len(allowed_changes(nae)),
        "c a function of A and B": all(len({w[2] for w in nae if w[:2] == ab}) == 1
                                       for ab in itertools.product((0, 1), repeat=2) if any(w[:2] == ab for w in nae))}
    holds = all(v["bijective"] and v["distinctions are the three questions"] and v["nonzero allowed changes"] == 3
                and v["changes are the three nonzero shifts"] and v["incidence kept"]
                and v["six one-read states are pure toy states"] and v["each distinction the sum of the other two"]
                for k, v in out.items() if k.startswith("law"))
    control_fails = (out["control: not-all-equal"]["allowed states"] == 6
                     and out["control: not-all-equal"]["nonzero allowed changes"] == 1
                     and not out["control: not-all-equal"]["c a function of A and B"])
    return holds and control_fails, out


# ---------------------------------------------------------------- P2: the phase on one knot

def p2():
    states = knot_states(0, "parity")                     # (A, B, c), A + B + c = 0
    perms = [dict(zip(states, img)) for img in itertools.permutations(states)]
    keep_a = [s for s in perms if all(s[w][0] == w[0] for w in states)]

    def compose(f, g):
        return {w: f[g[w]] for w in states}

    ident = {w: w for w in states}
    orders = []
    for s in keep_a:
        k, cur = 1, s
        while cur != ident:
            cur, k = compose(s, cur), k + 1
        orders.append(k)
    closed = all(compose(f, g) in keep_a for f in keep_a for g in keep_a)

    def carries(s, frm, to):   # the read frm, after s, is the read to (exactly / up to relabelling)
        diff = {(s[w][frm] - w[to]) % 2 for w in states}
        return "exactly" if diff == {0} else "relabelled" if diff == {1} else None

    rows = []
    allowed = allowed_changes(states)
    for s in keep_a:
        is_change = [c for c in allowed + [(0, 0, 0)]
                     if all(s[w] == tuple(a ^ b for a, b in zip(w, c)) for w in states)]
        rows.append({"map": {"".join(map(str, w)): "".join(map(str, s[w])) for w in states},
                     "order": orders[keep_a.index(s)], "B-read to c-read": carries(s, 1, 2),
                     "B-read to B-read": carries(s, 1, 1),
                     "is an allowed change": ["".join(map(str, c)) for c in is_change]})
    # the qubit: A <-> Z, B <-> X, c <-> Y
    qubit = {"S X S^dagger = Y": bool(close(S @ X @ S.conj().T, Y)), "S^2 = Z": bool(close(S @ S, Z)),
             "Z X Z = -X": bool(close(Z @ X @ Z, -X)),
             "order of S": next(k for k in range(1, 9) if close(np.linalg.matrix_power(S, k), I2))}
    carriers = [r for r in rows if r["B-read to c-read"]]
    own = [r for r in rows if r["is an allowed change"]]
    holds = (len(perms) == 24 and len(keep_a) == 4 and closed and max(orders) <= 2 and sorted(orders) == [1, 2, 2, 2]
             and len(carriers) == 2 and sorted(r["B-read to c-read"] for r in carriers) == ["exactly", "relabelled"]
             and len(own) == 2 and all(r["B-read to c-read"] is None for r in own)
             and qubit["S X S^dagger = Y"] and qubit["S^2 = Z"] and qubit["Z X Z = -X"] and qubit["order of S"] == 4)
    return holds, {"permutations": len(perms), "keeping A": len(keep_a), "closed under composition": closed,
                   "elements": rows, "qubit": qubit}


# ---------------------------------------------------------------- P3: the closure is a toy state

def map_r(readers, assignment):
    """Distinction d of reader j -> the chosen toy question placed at toy bit j."""
    phi = {}
    for j, (pair, (u, v)) in enumerate(zip(readers, assignment)):
        phi[pair[0]], phi[pair[1]] = place(u, j), place(v, j)
    return phi


def closure_as_toy(knots, laws, readers, assignment):
    phi = map_r(readers, assignment)
    toy_laws = []
    for k, r in zip(knots, laws):
        u = 0
        for d in k:
            u ^= phi[d]
        toy_laws.append((u, r))
    info = is_toy_state(toy_laws, 3)
    sup = support(toy_laws, 3)
    words = sorted(sum(par(phi[d] & lam) << d for d in range(6)) for lam in sup)
    return info, words


def pairings(items):
    if not items:
        yield []
        return
    first = items[0]
    for k in range(1, len(items)):
        rest = items[1:k] + items[k + 1:]
        for p in pairings(rest):
            yield [(first, items[k])] + p


def p3(knots, readers):
    even = allowed_words(knots, [0, 0, 0, 0])
    assignments = list(itertools.product(list(itertools.permutations(QUESTIONS, 2)), repeat=3))
    per_assignment = []
    for a in assignments:
        info, words = closure_as_toy(knots, [0, 0, 0, 0], readers, a)
        per_assignment.append(info["pure"] and words == even)
    model_table = table_of_words(even, readers)
    # the toy theory's table for the same state, read through Map R under the first assignment
    a0 = assignments[0]
    phi = map_r(readers, a0)
    toy_laws = [(sum_masks([phi[d] for d in k], [1] * 3), 0) for k in knots]
    sup = support(toy_laws, 3)
    toy_table = {}
    for s, reads in contexts(readers).items():
        counts = [0] * 8
        for lam in sup:
            counts[BITS3.index(tuple(par(phi[d] & lam) for d in reads))] += 1
        toy_table[s] = [Fraction(c, len(sup)) for c in counts]
    equal_entries = sum(p == q for s in model_table for p, q in zip(model_table[s], toy_table[s]))
    # every pure toy state of three toy bits, scored on the record's target under every assignment
    spans, states = pure_toy_states(3)
    supports = [support(st, 3) for st in states]
    scored_ctx = [(reads, int(sum(s) == 3)) for s, reads in contexts(readers).items() if sum(s) in (1, 3)]
    best_by_assignment = []
    best_overall = Fraction(0)
    for a in assignments:
        phi = map_r(readers, a)
        best = Fraction(0)
        for sup in supports:
            hits = 0
            for lam in sup:
                vals = [par(phi[d] & lam) for d in range(6)]
                hits += sum((vals[r[0]] + vals[r[1]] + vals[r[2]]) % 2 == req for r, req in scored_ctx)
            best = max(best, Fraction(hits, 4 * len(sup)))
        best_by_assignment.append(best)
        best_overall = max(best_overall, best)
    closure_score, closure_matches = score(model_table)
    # pairings of the six distinctions into three readers
    opposite = {tuple(sorted(p)) for p in itertools.combinations(range(6), 2)
                if not any(set(p) <= set(k) for k in knots)}
    rows = []
    for pr in pairings(list(range(6))):
        verdicts, failing = set(), set()
        for a in assignments:
            info, _ = closure_as_toy(knots, [0, 0, 0, 0], pr, a)
            verdicts.add(info["pure"])
            phi = map_r(pr, a)
            vec = [sum_masks([phi[d] for d in k], [1] * 3) for k in knots]
            failing.add(tuple((i, j) for i, j in itertools.combinations(range(4), 2) if bracket(vec[i], vec[j], 3)))
        holders_of_a_pair = sorted(i for i, k in enumerate(knots) if any(set(p) <= set(k) for p in pr))
        fail = sorted(failing)[0] if len(failing) == 1 else None
        rows.append({"pairing": pr, "pairs no knot holds together": sum(tuple(sorted(p)) in opposite for p in pr),
                     "toy state under every assignment": verdicts == {True},
                     "same verdict under all 216 assignments": len(verdicts) == 1 and len(failing) == 1,
                     "knots holding both distinctions of a reader": holders_of_a_pair,
                     "knot pairs that fail to commute": fail,
                     "failing pairs are exactly those among the holding knots":
                         fail is not None and sorted(fail) == sorted(itertools.combinations(holders_of_a_pair, 2))})
    toy_count = sum(r["toy state under every assignment"] for r in rows)
    classes = {n: sorted({r["toy state under every assignment"] for r in rows if r["pairs no knot holds together"] == n})
               for n in (0, 1, 3)}
    eight = [r for r in rows if r["pairs no knot holds together"] == 0]
    eight_ok = (len(eight) == 8 and all(len(r["knots holding both distinctions of a reader"]) == 3 and
                                        r["failing pairs are exactly those among the holding knots"] for r in eight)
                and all(r["knot pairs that fail to commute"] == () for r in rows if r["pairs no knot holds together"]))
    # (b) the same closure under qubits: each reader's two distinctions to two distinct Paulis
    pauli = {(1, 0): Z, (0, 1): X, (1, 1): Y}   # q, p, q + p  ->  Z, X, Y
    stab_rows = []
    for a in assignments:
        ops = {}
        for (pair, (u, v)) in zip(readers, a):
            j = readers.index(pair)
            ops[pair[0]], ops[pair[1]] = on(pauli[u], j, 3), on(pauli[v], j, 3)
        kops = []
        for k in knots:
            m = np.eye(8, dtype=complex)
            for d in k:
                m = m @ ops[d]
            kops.append(m)
        commute = all(close(x @ y, y @ x) for x, y in itertools.combinations(kops, 2))
        prod = kops[0] @ kops[1] @ kops[2] @ kops[3]
        sign = 1 if close(prod, np.eye(8)) else -1 if close(prod, -np.eye(8)) else None

        def projector(laws):
            m = np.eye(8, dtype=complex)
            for kop, r in zip(kops, laws):
                m = m @ (np.eye(8) + (-1) ** r * kop) / 2
            return m

        even_rank = round(float(np.trace(projector([0, 0, 0, 0])).real))
        odd_proj = projector([0, 0, 0, 1])
        odd_rank = round(float(np.trace(odd_proj).real))
        matches = None
        if odd_rank == 1:
            w, vecs = np.linalg.eigh(odd_proj)
            psi = vecs[:, np.argmax(w)]
            table = {}
            for s, reads in contexts(readers).items():
                row = []
                for ans in BITS3:
                    proj = np.eye(8, dtype=complex)
                    for i, d in enumerate(reads):
                        proj = proj @ (np.eye(8) + (-1) ** ans[i] * ops[d]) / 2
                    row.append(frac(float(np.real(np.vdot(psi, proj @ psi)))))
                table[s] = row
            matches = score(table)
        stab_rows.append({"commute": commute, "product": sign, "even closure states": even_rank,
                          "odd closure states": odd_rank, "odd state's score and matches": matches})
    stab_ok = all(r["commute"] and r["product"] == -1 and r["even closure states"] == 0 and r["odd closure states"] == 1
                  and r["odd state's score and matches"] == (Fraction(1), 64) for r in stab_rows)
    holds = (all(per_assignment) and equal_entries == 64 and len(states) == 1080 and best_overall == Fraction(3, 4)
             and closure_score == Fraction(3, 4) and toy_count == 7 and classes == {0: [False], 1: [True], 3: [True]}
             and all(r["same verdict under all 216 assignments"] for r in rows) and eight_ok and stab_ok
             and len(allowed_words(knots, [0, 0, 0, 1])) == 0)
    return holds, {"assignments": len(assignments), "(a) pure toy state under every assignment": all(per_assignment),
                   "allowed states of the even closure": len(even),
                   "allowed states of the odd closure": len(allowed_words(knots, [0, 0, 0, 1])),
                   "model and toy tables agree (of 64)": equal_entries,
                   "(b) stabilizer: knot operators commute, product -1, even closure has no state, odd has one "
                   "reproducing the target, under every assignment": stab_ok,
                   "(b) products seen": sorted({str(r["product"]) for r in stab_rows}),
                   "(b) even-closure state counts seen": sorted({r["even closure states"] for r in stab_rows}),
                   "(c) pure toy states": len(states), "isotropic spans": len(spans), "best toy score": str(best_overall),
                   "best toy score equal for every assignment": len(set(best_by_assignment)) == 1,
                   "closure's own score": str(closure_score), "closure's matches of 64": closure_matches,
                   "(d) pairings": len(rows), "pairings giving a toy state": toy_count,
                   "by number of pairs no knot holds together": {str(k): v for k, v in classes.items()},
                   "the eight: three holding knots fail pairwise, the fourth commutes with all": eight_ok,
                   "pairing rows": rows}


def stabilizer_target(readers):
    """(|000> + i|111>)/sqrt 2 with s-read X and l-read Y: the record's target, 64 of 64?"""
    psi = np.zeros(8, dtype=complex)
    psi[0], psi[7] = 1 / np.sqrt(2), 1j / np.sqrt(2)
    reads = [(X, Y)] * 3
    table = {}
    for s in BITS3:
        row = []
        for ans in BITS3:
            proj = kron(*[(I2 + (-1) ** ans[i] * reads[i][s[i]]) / 2 for i in range(3)])
            row.append(frac(float(np.real(psi.conj() @ proj @ psi))))
        table[s] = row
    return table


# ---------------------------------------------------------------- P4: two forms on the closure

TOY_PHASES = {"a": lambda q, p: (q, p ^ (1 - q)),   # swap inside the q = 0 class
             "b": lambda q, p: (q, p ^ q)}         # swap inside the q = 1 class


def toy_apply(phase, lam, j):
    q, p = (lam >> (2 * j)) & 1, (lam >> (2 * j + 1)) & 1
    q2, p2 = TOY_PHASES[phase](q, p)
    lam &= ~(3 << (2 * j))
    return lam | (q2 << (2 * j)) | (p2 << (2 * j + 1))


def p4():
    base = [lam for lam in range(64)
            if par(lam & (place((1, 0), 0) | place((1, 0), 1))) == 0 and par(lam & (place((1, 0), 1) | place((1, 0), 2))) == 0
            and par(lam & (place((0, 1), 0) | place((0, 1), 1) | place((0, 1), 2))) == 0]
    assert len(base) == 8 and is_toy_state([(place((1, 0), 0) | place((1, 0), 1), 0), (place((1, 0), 1) | place((1, 0), 2), 0),
                                            (place((0, 1), 0) | place((0, 1), 1) | place((0, 1), 2), 0)], 3)["pure"]
    scored = [s for s in BITS3 if sum(s) in (1, 3)]

    def toy_parities(phases, g):
        state = [toy_apply(g, lam, 0) for lam in base] if g else base
        out = []
        for s in scored:
            seen = set()
            for lam in state:
                total = 0
                for j in range(3):
                    if s[j]:   # second read: the first read p_j taken after the reader's phase
                        total += (toy_apply(phases[j], lam, j) >> (2 * j + 1)) & 1
                    else:
                        total += (lam >> (2 * j + 1)) & 1
                seen.add(total % 2)
            out.append(seen.pop() if len(seen) == 1 else None)
        return out

    toy_rows = []
    for s0, s1, s2, g in itertools.product("ab", repeat=4):
        parities = toy_parities((s0, s1, s2), g)
        certain = all(x is not None for x in parities)
        toy_rows.append({"phases": s0 + s1 + s2, "state phase": g, "certain": certain,
                         "closing": (sum(parities) % 2) if certain else None})
    toy_unphased = [toy_parities(ph, None) for ph in itertools.product("ab", repeat=3)]
    ghz = np.zeros(8, dtype=complex)
    ghz[0] = ghz[7] = 1 / np.sqrt(2)

    def qubit_values(ks, phi):
        state = on(np.linalg.matrix_power(S, phi), 0, 3) @ ghz
        seconds = [np.linalg.matrix_power(S, k) @ X @ np.linalg.matrix_power(S, k).conj().T for k in ks]
        return [float(np.real(state.conj() @ kron(*[seconds[j] if s[j] else X for j in range(3)]) @ state)) for s in scored]

    qubit_rows = []
    for k0, k1, k2, phi in itertools.product((1, 3), repeat=4):
        values = qubit_values((k0, k1, k2), phi)
        certain = all(abs(abs(v) - 1) < TOL for v in values)
        closing = int(np.prod(np.sign(values)) < 0) if certain else None
        qubit_rows.append({"phases": [k0, k1, k2], "state phase": phi, "certain": certain, "closing": closing})
    qubit_unphased = [qubit_values(ks, 0) for ks in itertools.product((1, 3), repeat=3)]
    no_phase_uncertain = (all(all(x is None for x in row) for row in toy_unphased)
                          and all(all(abs(v) < TOL for v in row) for row in qubit_unphased))
    # the closing phase from the groups: twice the sum of the three phases
    z2z2 = {"a": (1, 0), "b": (0, 1)}
    formula_toy = {(2 * (sum(z2z2[t][0] for t in r["phases"])) % 2, 2 * (sum(z2z2[t][1] for t in r["phases"])) % 2)
                   for r in toy_rows}
    formula_qubit = {(2 * sum(r["phases"])) % 4 for r in qubit_rows}
    mutant = {(2 * sum({"a": 1, "b": 3}[t] for t in r["phases"])) % 4 for r in toy_rows}   # Z4 where Z2xZ2 is meant
    holds = (all(r["certain"] and r["closing"] == 0 for r in toy_rows) and len(toy_rows) == 16
             and all(r["certain"] and r["closing"] == 1 for r in qubit_rows) and len(qubit_rows) == 16
             and formula_toy == {(0, 0)} and formula_qubit == {2} and no_phase_uncertain)
    return holds, {"toy": toy_rows, "qubit": qubit_rows,
                   "without the state phase no scored context is certain (toy and qubit, 8 choices each)": no_phase_uncertain,
                   "closing phase, toy (Z2xZ2)": sorted(formula_toy), "closing phase, qubit (Z4)": sorted(formula_qubit),
                   "mutant (Z4 composition on the toy phases)": sorted(mutant)}


# ---------------------------------------------------------------- P5: the record's coherent constructions

def op64(change, value):
    """The record's question (change, value): multiply by the sign of the value, then apply the change."""
    m = np.zeros((64, 64))
    for w in range(64):
        m[w ^ change, w] = (-1) ** par(w & value)
    return m


def p5(knots, readers):
    words = allowed_words(knots, [0, 0, 0, 0])
    parents = [(0, 1, 2), (1, 3, 4), (3, 0, 5)]
    mask = lambda ds: sum(1 << d for d in ds)
    shared = mask(d for d in range(6) if sum(d in r for r in parents) == 2)
    changes = []
    for r in parents:
        row = mask(r)
        cands = [w for w in words if w & row == 0 and w & shared == shared & ~row]
        assert len(cands) == 1
        changes.append(cands[0])
    # the transport phase f(w ^ T_i) = (-1)^{l_i(w)} f(w), solved on the single orbit of the allowed words
    f = {words[0]: 1}
    queue = [words[0]]
    while queue:
        w = queue.pop()
        for (s, l), t in zip(readers, changes):
            nxt, want = w ^ t, (-1) ** ((w >> l) & 1) * f[w]
            if nxt in f:
                assert f[nxt] == want
            else:
                f[nxt] = want
                queue.append(nxt)
    assert len(f) == 8
    signed = np.zeros(64)
    flat = np.zeros(64)
    for w in words:
        signed[w], flat[w] = f[w], 1
    signed, flat = signed / np.sqrt(8), flat / np.sqrt(8)
    constructions = {
        "signed state, reads Z_s and T_i": (signed, [((0, 1 << s), (t, 0)) for (s, l), t in zip(readers, changes)]),
        "equal-positive state, rephased reads": (flat, [((0, 1 << s), (t, 1 << l)) for (s, l), t in zip(readers, changes)]),
        "signed state, reads confined to the pair": (signed, [((1 << l, 1 << s), (1 << s, 0)) for s, l in readers]),
        "signed state, value reads": (signed, [((0, 1 << s), (0, 1 << l)) for s, l in readers]),
        "control: confined reads with the sign dropped": (signed, [((1 << l, 0), (1 << s, 0)) for s, l in readers]),
    }
    out = {}
    for name, (psi, alts) in constructions.items():
        ops = [[op64(*q) for q in pair] for pair in alts]
        anticommute = [bool(close(a @ b, -b @ a)) for a, b in ops]
        commute = [bool(close(a @ b, b @ a)) for a, b in ops]
        square = [1 if close(a @ b @ a @ b, np.eye(64)) else -1 if close(a @ b @ a @ b, -np.eye(64)) else None
                  for a, b in ops]
        table = {}
        for s in BITS3:
            row = []
            for ans in BITS3:
                proj = np.eye(64)
                for i in range(3):
                    proj = proj @ (np.eye(64) + (-1) ** ans[i] * ops[i][s[i]]) / 2
                row.append(frac(float(psi @ proj @ psi)))
            table[s] = row
        win, matches = score(table)
        scored = [s for s in BITS3 if sum(s) in (1, 3)]
        ctx = [ops[0][s[0]] @ ops[1][s[1]] @ ops[2][s[2]] for s in scored]
        product = ctx[0] @ ctx[1] @ ctx[2] @ ctx[3]
        on_state = float(psi @ product @ psi)
        outside_pair = [bin(q[0] & ~((1 << s) | (1 << l))).count("1") > 0
                        for (s, l), pair in zip(readers, alts) for q in pair]
        allowed = set(words)
        leaves = [all((w ^ q[0]) not in allowed for w in words) for pair in alts for q in pair if q[0]]
        out[name] = {"score": str(win), "matches of 64": matches, "reads of each reader anticommute": anticommute,
                     "reads of each reader commute": commute, "(product of a reader's two reads) squared": square,
                     "product of the four scored context operators on the state": round(on_state, 12),
                     "product is -1 on the whole space": bool(close(product, -np.eye(64))),
                     "a read flips a distinction outside its reader's pair": any(outside_pair),
                     "every changing read takes every allowed word outside the eight": bool(leaves) and all(leaves)}
    coherent = [k for k in out if "value" not in k and not k.startswith("control")]
    ctrl = out["control: confined reads with the sign dropped"]
    gate = (out["signed state, reads Z_s and T_i"]["score"] == "1" and out["signed state, reads Z_s and T_i"]["matches of 64"] == 64
            and out["signed state, reads confined to the pair"]["score"] == "1"
            and out["signed state, reads confined to the pair"]["matches of 64"] == 64
            and out["equal-positive state, rephased reads"]["matches of 64"] == 64
            and out["signed state, value reads"]["score"] == "3/4" and out["signed state, value reads"]["matches of 64"] == 56)
    holds = (all(all(out[k]["reads of each reader anticommute"]) and out[k]["(product of a reader's two reads) squared"] == [-1] * 3
                 and abs(out[k]["product of the four scored context operators on the state"] + 1) < TOL for k in coherent)
             and all(out["signed state, value reads"]["reads of each reader commute"])
             and out["signed state, value reads"]["(product of a reader's two reads) squared"] == [1] * 3
             and abs(out["signed state, value reads"]["product of the four scored context operators on the state"] - 1) < TOL
             and all(ctrl["reads of each reader commute"]) and ctrl["score"] == "5/8")
    return gate, holds, {"changes T_i": [[d for d in range(6) if t >> d & 1] for t in changes],
                         "transport phase": {format(w, "06b")[::-1]: f[w] for w in words}, "constructions": out}


# ---------------------------------------------------------------- P6: two readers

def two_qubit_stabilizer_states():
    paulis = [I2, X, Y, Z]
    signed = [(sg, a, b) for sg in (1, -1) for a in range(4) for b in range(4) if (a, b) != (0, 0)]
    mats = {g: g[0] * kron(paulis[g[1]], paulis[g[2]]) for g in signed}
    states = []
    for g1, g2 in itertools.combinations(signed, 2):
        m1, m2 = mats[g1], mats[g2]
        if not close(m1 @ m2, m2 @ m1):
            continue
        proj = (np.eye(4) + m1) @ (np.eye(4) + m2) / 4
        if abs(np.trace(proj).real - 1) > TOL:
            continue
        w, v = np.linalg.eigh(proj)
        psi = v[:, np.argmax(w)]
        if not any(abs(abs(np.vdot(psi, other)) - 1) < 1e-9 for other in states):
            states.append(psi)
    return states


def chsh(psi, a0, a1, b0, b1):
    op = np.kron(a0, b0) + np.kron(a0, b1) + np.kron(a1, b0) - np.kron(a1, b1)
    return float(np.real(np.vdot(psi, op @ psi)))


def norm_of(x0, x1, y0, y1):
    m = np.kron(x0, y0) + np.kron(x0, y1) + np.kron(x1, y0) - np.kron(x1, y1)
    return float(max(abs(np.linalg.eigvalsh(m))))


def p6():
    states = two_qubit_stabilizer_states()
    reads = [sg * m for sg in (1, -1) for m in (X, Y, Z)]
    best = max(chsh(psi, *c) for psi in states for c in itertools.product(reads, repeat=4))

    def is_stabilizer(v):
        return max(abs(np.vdot(s, v)) for s in states) > 1 - 1e-9

    # (b) the sibling study's preparation on the class pair (E = 11, M = (01 + 10)/sqrt 2) per reader, Z = +1 on E
    psi = np.array([np.sqrt(1 / 3), np.sqrt(1 / 6), np.sqrt(1 / 6), np.sqrt(1 / 3)], dtype=complex)
    pauli_best = max(chsh(psi, *c) for c in itertools.product(reads, repeat=4))
    R = (2 * np.sqrt(2) * X - Z) / 3
    a0, a1, b0, b1 = X, Z, -Z @ R @ Z, R
    value = chsh(psi, a0, a1, b0, b1)
    corr = np.array([[float(np.real(np.vdot(psi, np.kron(p, q) @ psi))) for q in (X, Y, Z)] for p in (X, Y, Z)])
    top2 = sorted(np.linalg.eigvalsh(corr.T @ corr))[-2:]
    horodecki = 2 * np.sqrt(sum(top2))
    op = np.kron(a0, b0) + np.kron(a0, b1) + np.kron(a1, b0) - np.kron(a1, b1)
    comm_a, comm_b = a0 @ a1 - a1 @ a0, b0 @ b1 - b1 @ b0
    landau_b = bool(close(op @ op, 4 * np.eye(4) - np.kron(comm_a, comm_b)))
    is_pauli = any(close(R, r) for r in reads)
    # (c) reads X and Z on both sides: the square of the operator and its best state
    c_op = np.kron(X, X) + np.kron(X, Z) + np.kron(Z, X) - np.kron(Z, Z)
    landau_c = bool(close(c_op @ c_op, 4 * np.eye(4) + 4 * np.kron(Y, Y)))
    w, v = np.linalg.eigh(c_op)
    top = v[:, np.argmax(w)]
    # (d) either reader's two reads made to commute (equal, opposite, or the identity)
    commuting = (max(norm_of(a0, a1c, b0, b1) for a1c in (a0, -a0, I2)),
                 max(norm_of(a0, a1, b0, b1c) for b1c in (b0, -b0, I2)),
                 max(norm_of(X, a1c, X, Z) for a1c in (X, -X, I2)))
    holds = (len(states) == 60 and abs(best - 2) < TOL
             and not is_stabilizer(psi) and pauli_best <= 2 + TOL and abs(value - (2 + 12 * np.sqrt(2)) / 9) < TOL
             and abs(horodecki - 2 * np.sqrt(10) / 3) < 1e-9 and landau_b and not is_pauli
             and landau_c and abs(max(w) - 2 * np.sqrt(2)) < 1e-9 and not is_stabilizer(top)
             and max(commuting) <= 2 + TOL)
    return holds, {"(a) two-qubit stabilizer states": len(states), "(a) best score with signed Pauli reads": round(best, 12),
                   "(b) sibling preparation is a stabilizer state": is_stabilizer(psi),
                   "(b) its best score with signed Pauli reads": round(pauli_best, 12),
                   "(b) its correlations XX, YY, ZZ": [round(corr[i][i], 12) for i in range(3)],
                   "(b) sibling score": value, "(2 + 12 sqrt 2)/9": (2 + 12 * np.sqrt(2)) / 9,
                   "(b) best over all two-valued reads (Horodecki)": horodecki, "2 sqrt 10 / 3": 2 * np.sqrt(10) / 3,
                   "(b) Landau identity on the sibling reads": landau_b, "(b) R is a signed Pauli": is_pauli,
                   "(c) square of XX + XZ + ZX - ZZ is 4 + 4 YY": landau_c, "(c) its largest eigenvalue": float(max(w)),
                   "(c) its best state is a stabilizer state": is_stabilizer(top),
                   "(d) operator norm with one reader's two reads commuting": list(commuting)}


def main():
    knots, readers, gate_closure = the_closure()
    even = allowed_words(knots, [0, 0, 0, 0])
    odd = allowed_words(knots, [0, 0, 0, 1])
    stab = stabilizer_target(readers)
    stab_matches = sum(p == q for s in stab for p, q in zip(stab[s], target(s)))
    # gate: the toy-state test accepts the toy GHZ state and rejects knowing both questions of one toy bit
    ghz_laws = [(place((1, 0), 0) | place((1, 0), 1), 0), (place((1, 0), 1) | place((1, 0), 2), 0),
                (place((0, 1), 0) | place((0, 1), 1) | place((0, 1), 2), 0)]
    both_known = [(place((1, 0), 0), 0), (place((0, 1), 0), 0)]
    ok1, r1 = p1()
    ok2, r2 = p2()
    ok3, r3 = p3(knots, readers)
    ok4, r4 = p4()
    gate5, ok5, r5 = p5(knots, readers)
    ok6, r6 = p6()
    gate = {
        "closure": gate_closure,
        "closure as the fixture": (gate_closure["every two knots share one distinction"] and gate_closure["readers are those pairs"]
                                   and gate_closure["every distinction held twice"] and len(knots) == 4
                                   and sorted(knots[-1]) == [2, 4, 5] and len(even) == 8 and len(odd) == 0),
        "toy GHZ accepted": is_toy_state(ghz_laws, 3)["pure"],
        "both questions of one toy bit rejected": not is_toy_state(both_known, 1)["commuting"],
        "stabilizer state matches the target (of 64)": stab_matches,
        "birth-sign constructions reproduced": gate5,
        "mutant flips the closing sign": r4["mutant (Z4 composition on the toy phases)"] == [2],
    }
    gate_ok = (gate["closure as the fixture"] and gate["toy GHZ accepted"] and gate["both questions of one toy bit rejected"]
               and stab_matches == 64 and gate5 and gate["mutant flips the closing sign"])
    stab_score, _ = score(stab)
    r3["stabilizer state's score"] = str(stab_score)
    verdicts = {"G": gate_ok, "P1": ok1, "P2": ok2, "P3": ok3 and stab_score == 1, "P4": ok4, "P5": ok5, "P6": ok6}
    result = {"verdicts": verdicts, "gate": gate, "P1": r1, "P2": r2, "P3": r3, "P4": r4, "P5": r5, "P6": r6}
    (HERE / "results.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    for k, v in verdicts.items():
        print(k, "holds" if v else "FAILS")


if __name__ == "__main__":
    main()
