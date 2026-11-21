"""Exact phase, composition and recorded-outcome replay for study B287.

Numbers lie in Q[ζ] with ζ=exp(iπ/4) and ζ^4=-1. Matrices act on columns;
rightmost operations happen first in formulas and program lists run left to right.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W = "abcd"
CHOICES = {"P": (0, 1), "Q": (0, 2), "R": (1, 2), "L": (2, 3)}
CONNECTIONS = ((1, 1), (1, 0), (0, 1), (0, 0))
ZERO = (Q(0),) * 4
ONE = (Q(1), Q(0), Q(0), Q(0))


@lru_cache(None)
def zeta(n):
    n = n % 8
    out = list(ZERO)
    out[n % 4] = Q(1 if n < 4 else -1)
    return tuple(out)


@lru_cache(10000)
def add(a, b):
    return tuple(u + v for u, v in zip(a, b))


@lru_cache(10000)
def mult(a, b):
    if a == ZERO or b == ZERO:
        return ZERO
    if a == ONE:
        return b
    if b == ONE:
        return a
    out = list(ZERO)
    for i, x in enumerate(a):
        if not x:
            continue
        for j, y in enumerate(b):
            if y:
                out[(i + j) % 4] += x * y * (1 if i + j < 4 else -1)
    return tuple(out)


@lru_cache(10000)
def conjugate(a):
    return (a[0], -a[3], -a[2], -a[1])


def total(items):
    a = ZERO
    for v in items:
        a = add(a, v)
    return a


def scaled(x, v):
    return tuple(x * y for y in v)


HALF = scaled(Q(1, 2), add(zeta(1), zeta(-1)))  # 1/sqrt(2)


def printable(a):
    if a[2] == 0 and a[1] == -a[3]:
        return str(a[0]) if not a[1] else f"{a[0]}+({a[1]})sqrt(2)"
    return [str(x) for x in a]


def realpart(a):
    return scaled(Q(1, 2), add(a, conjugate(a)))


def identity(n=4):
    return tuple(tuple(ONE if x == y else ZERO for y in range(n)) for x in range(n))


def diagonal(angles):
    return tuple(
        tuple(zeta(a) if i == j else ZERO for j in range(len(angles)))
        for i, a in enumerate(angles)
    )


def adjoint(m):
    return tuple(tuple(conjugate(v) for v in row) for row in zip(*m))


@lru_cache(10000)
def mm(a, b):
    return tuple(
        tuple(total(mult(x, y) for x, y in zip(row, column)) for column in zip(*b))
        for row in a
    )


def program(*gates):
    result = identity(len(gates[0]))
    for g in gates:
        result = mm(g, result)
    return result


def scalar_times(a, m):
    return tuple(tuple(mult(a, x) for x in row) for row in m)


def apply(m, v):
    return tuple(total(mult(x, y) for x, y in zip(row, v)) for row in m)


def basis(i, n=4):
    return tuple(ONE if i == j else ZERO for j in range(n))


def coherent(i, j, angle, n=4):
    return tuple(
        HALF if k == i else mult(HALF, zeta(angle)) if k == j else ZERO
        for k in range(n)
    )


def matrix_out(m):
    return [[printable(x) for x in row] for row in m]


def same_ray_matrix(a, b):
    for left, right in zip((x for r in a for x in r), (x for r in b for x in r)):
        if right != ZERO:
            # Unitarity assures the common ratio has unit modulus.
            return all(
                mult(x, right) == mult(y, left)
                for l, r in zip(a, b)
                for x, y in zip(l, r)
            )
    return a == b


def rim(which, z=0, frame=0, full=False, alpha=0, beta=0, n=4):
    """Half pulse on named pair, or complete decorated permutation with α,β angles."""
    left, right = CHOICES.get(which, which)
    m = [list(row) for row in identity(n)]
    for w in range(n):
        if w != left and w != right:
            m[w][w] = zeta(beta if full else z)
    m[left][left] = m[right][right] = ZERO if full else HALF
    centre = zeta(alpha) if full else mult(zeta(2), HALF)
    m[right][left] = mult(centre, zeta(frame))
    m[left][right] = mult(centre, zeta(-frame))
    return tuple(tuple(row) for row in m)


def born(v):
    return tuple(mult(a, conjugate(a)) for a in v)


def split_on(vector, selector):
    result = {}
    for i, amp in enumerate(vector):
        if amp != ZERO:
            key = selector(i)
            r = result.setdefault(key, [ZERO] * len(vector))
            r[i] = amp
    return [tuple(x) for x in result.values()]


def run(initial, steps):
    branches = list(initial)
    for step in steps:
        if callable(step):
            branches = [x for v in branches for x in split_on(v, step)]
        else:
            branches = [apply(step, v) for v in branches]
    probs = tuple(total(born(v)[j] for v in branches) for j in range(len(branches[0])))
    assert total(probs) == ONE
    return branches, probs


def port(w, connection, copy_s=False):
    q, s = ((1, 0), (1, 1), (0, 0), (0, 1))[w]
    if copy_s:
        q ^= s
    first, second = connection
    if q and first:
        return "011", 1, q
    if second:
        return "101", 0, q
    return "110", 1, q


def complete_read(branches, probs, copy_s=False):
    physical = {}
    for conn in CONNECTIONS:
        kdist = defaultdict(lambda: ZERO)
        om = {}
        for j, p in enumerate(probs):
            k, z, q = port(j, conn, copy_s)
            kdist[k] = add(kdist[k], p)
            om[f"{W[j]},q_after_copy={q},K={k},slack={z}"] = printable(p)
        physical["".join(map(str, conn))] = {
            "K": {k: printable(kdist[k]) for k in ("110", "101", "011")},
            "full_readable_words": om,
        }
    return {
        "direct_word": [printable(p) for p in probs],
        "connected_controller": physical,
        "unnormalized_post_vectors_before_final_ordinary_read": [
            [printable(c) for c in b] for b in branches
        ],
        "conditioning": "For a declared word or q/K outcome retain its listed components in that sector and divide its density by the stated chance. Distinct stored environment sectors sum as probabilities. A zero-chance conditioned state is undefined.",
    }


def choices_of_input():
    starts = {x: [basis(j)] for j, x in enumerate(W)}
    starts.update(
        {
            x: [coherent(0, 2, k)]
            for x, k in (
                ("real_plus", 0),
                ("real_minus", 4),
                ("quadrature_plus", 2),
                ("quadrature_minus", 6),
            )
        }
    )
    starts["dephased_ac"] = [tuple(mult(HALF, a) for a in basis(j)) for j in (0, 2)]
    return starts


def term_arm(
    sources,
    z,
    variant,
    frame=(0, 0, 0),
    undo=(0, 0, 0),
    gauge=None,
    inverse=False,
    after_split=False,
    quadrature=0,
    tag="absent",
    sector_copy=False,
    modify_direct_d=False,
):
    """A fresh carrier for every input. Tag recording and true return are different instruments."""
    p, q, r = frame
    Z = lambda x: rim(x, z, {"P": p, "Q": q, "R": r, "L": 0}[x])
    bp, bq, br, bl = map(Z, ("P", "Q", "R", "L"))
    undo_a, undo_b, undo_frame = undo
    compensator = adjoint(
        rim("P", full=True, frame=undo_frame, alpha=undo_a, beta=undo_b)
    )
    project = lambda x: x if gauge is None else program(adjoint(gauge), x, gauge)
    if inverse:
        bp, bq, br, bl = map(adjoint, (bp, bq, br, bl))
        compensator = adjoint(compensator)
    split = bq
    unmix = adjoint(bq)
    if variant == "single":
        middle = [bp]
    elif variant == "compensated":
        middle = [bp, bp, compensator]
    elif variant == "without_undo":
        middle = [bp, bp]
        unmix = adjoint(br)
    elif variant == "substitution_cd":
        P, Qg, R = (mm(x, x) for x in (bp, bq, br))
        middle = [P, Qg, P, adjoint(R)]
        if modify_direct_d:
            middle.append(diagonal((0, 0, 0, 4)))
        split = bl
        unmix = adjoint(bl)
    else:
        raise ValueError(variant)
    steps = [] if after_split else [split]
    # Physical tag of active-vs-idle cut. Projecting here describes an orthogonal
    # unread copy; a coherently uncomputed copy has identity effect. We separately
    # execute the actual tagged isometry and inverse in tagged_circuit_controls().
    if tag in ("retained", "ignored", "elsewhere"):
        steps.append(lambda j: j in (0, 1))
    steps += middle
    if quadrature:
        steps.append(diagonal((0, 0, quadrature, 0)))
    steps.append(unmix)
    if gauge:
        sources = [apply(gauge, x) for x in sources]
    steps = [x if callable(x) else project(x) for x in steps]
    return complete_read(*run(sources, steps), copy_s=sector_copy)


def encoded_r(z, delta):
    # J maps b→d, d→b; a,c retain q since s=0. The guard receiving the
    # middle pulse sees c,d. A true adjoint restores the borrowed coordinates.
    j = program(diagonal((0, delta, 0, delta)), rim((1, 3), full=True))
    return program(j, rim("L", z), adjoint(j))


def symbolic_return_tables():
    # A signed permutation uses a root exponent for each incoming column.
    # Each component is (new index, Laurent monomial) with sparse exponent tuple.
    symbols = ("p", "q", "r", "eta")

    def ex(*values):
        return tuple(values)

    z = (0, 0, 0, 0)

    def signed(i, j, idle, edge=z, n=4):
        return tuple(
            (j, edge)
            if k == i
            else (i, tuple(-x for x in edge))
            if k == j
            else (k, idle)
            for k in range(n)
        )

    def adj(m):
        o = [None] * len(m)
        for i, (j, w) in enumerate(m):
            o[j] = (i, tuple(-x for x in w))
        return tuple(o)

    def seq(*oper):
        ret = tuple((i, z) for i in range(len(oper[0])))
        for op in oper:
            ret = tuple(
                (op[i][0], tuple(a + b for a, b in zip(w, op[i][1]))) for i, w in ret
            )
        return ret

    P = signed(0, 1, ex(1, 0, 0, 0))
    Qm = signed(0, 2, ex(0, 1, 0, 0))
    R = signed(1, 2, ex(0, 0, 1, 0), ex(0, 0, 0, 1))
    outputs = {
        "P2": seq(P, P),
        "Q2": seq(Qm, Qm),
        "R2": seq(R, R),
        "PQP": seq(P, Qm, P),
        "QPQ": seq(Qm, P, Qm),
        "R": R,
        "R_inverse_after_PQP": seq(P, Qm, P, adj(R)),
    }
    # Independent finite check of the heterogeneous class after the three T² relations.
    sols = {}
    for n in (3, 4):
        ok = []
        for p, q, r in product((0, 4), repeat=3):
            operators = {}
            for letter, arg in zip("PQR", (p, q, r)):
                operators[letter] = rim(letter, full=True, beta=arg, n=n)
            if all(
                same_ray_matrix(
                    operators[y], program(operators[i], operators[j], operators[i])
                )
                for i, j, y in permutations("PQR")
            ):
                ok.append((p, q, r))
        sols[n] = ok
    return {
        "variables": symbols,
        "columns": outputs,
        "heterogeneous_idle_sign_exponents_eighths": sols,
        "meaning": "p,q,r are normalized idle/active phases of the three complete double pulses; eta is the independent active transfer phase b→c of R. Products compare up to a common scalar on the declared sector.",
    }


def completed(x):
    return scalar_times(zeta(-2), mm(x, x))


def numerical_relations():
    result = {}
    for n, k in product((3, 4), range(8)):
        gates = {i: rim(i, k, n=n) for i in "PQR"}
        full = {i: completed(u) for i, u in gates.items()}
        i0 = identity(n)
        p, q, r = (full[i] for i in "PQR")
        obj = {}
        for name, u in gates.items():
            assert program(u, adjoint(u)) == i0
            t = full[name]
            # This checks all columns against a complete independently coded decorated permutation.
            assert t == rim(name, full=True, beta=(2 * k - 2), n=n)
            obj[name] = {
                "half": matrix_out(u),
                "normalized_double": matrix_out(t),
                "true_inverse": matrix_out(adjoint(u)),
                "P_squared_scalar": same_ray_matrix(mm(t, t), i0),
            }
        transported = {
            "".join((i, j, y)): same_ray_matrix(
                program(full[i], full[j], full[i]), full[y]
            )
            for i, j, y in permutations("PQR")
        }
        direct = same_ray_matrix(program(p, q, p), r)
        braid = same_ray_matrix(program(p, q, p), program(q, p, q))
        twice = same_ray_matrix(program(p, p), i0)
        assert set(transported.values()) == {direct}
        assert direct == (k in (1, 5)) and twice == (k % 2 == 1) and braid
        obj.update(
            {
                "direct": direct,
                "all_six_addressings": transported,
                "braid": braid,
                "squared_full_involution": twice,
                "closed_return": matrix_out(program(p, q, p, adjoint(r))),
            }
        )
        if n == 4:
            obj["physical_recoder"] = {}
            for delta in range(8):
                rc = encoded_r(k, delta)
                assert rc == rim("R", k, delta)
                closed = program(p, q, p, adjoint(completed(rc)))
                w = 2 * k - 2
                assert closed == diagonal((0, w - delta, w + delta, 2 * w))
                obj["physical_recoder"][str(delta)] = {
                    "transfer": matrix_out(rc),
                    "closed": matrix_out(closed),
                    "same_complete_at_all_four": same_ray_matrix(closed, i0),
                }
            # Equal-length coherent direct/indirect programs. An auxiliary receipt
            # for the type of each offer distinguishes the alternatives.
            padded = program(
                gates["R"],
                gates["R"],
                gates["Q"],
                adjoint(gates["Q"]),
                gates["Q"],
                adjoint(gates["Q"]),
            )
            indirect = program(
                gates["P"], gates["P"], gates["Q"], gates["Q"], gates["P"], gates["P"]
            )
            assert same_ray_matrix(padded, indirect) == direct
            obj["padded"] = {
                "direct": "R R Q Q^-1 Q Q^-1",
                "indirect": "P P Q Q P P",
                "matched_six_slots": True,
                "same_offer_types": False,
                "same_unitary_up_to_scalar": direct,
            }
        result[f"width{n}/z{k}"] = obj
    # A fixed D applied ONLY to full gates. All 6 x 6 ordinary products and
    # inverse laws still hold, but a separately calibrated half-pulse can see D.
    d = diagonal((4, 0, 0, 0))
    perms = {
        a: tuple(
            tuple(ONE if (a + (3,))[j] == i else ZERO for j in range(4))
            for i in range(4)
        )
        for a in permutations(range(3))
    }
    lifted = {a: program(adjoint(d), g, d) for a, g in perms.items()}
    for a, b in product(perms, repeat=2):
        ab = tuple(a[b[j]] for j in range(3))
        assert mm(lifted[a], lifted[b]) == lifted[ab]
    assert lifted[(1, 0, 2)] == rim("P", full=True, alpha=4) and lifted[
        (0, 2, 1)
    ] == rim("R", full=True)
    result["full_group"] = {
        "representation": "DgD^dagger with D=diag(-1,1,1,1) on full gates only",
        "all_products_checked": 36,
        "all_permutations": {
            "".join(map(str, k)): matrix_out(v) for k, v in lifted.items()
        },
    }
    return result


def real_chance(w):
    return scaled(Q(1, 2), add(ONE, realpart(w)))


def table_value(trial, where):
    return trial["direct_word"][W.index(where)]


def interference_tables():
    prep = choices_of_input()
    ports = {}
    source_checks = {}
    for k in range(8):
        w = 2 * k - 2
        kz = {}
        for name in ("compensated", "without_undo", "single", "substitution_cd"):
            cd = name == "substitution_cd"
            rows = {}
            for label, src in prep.items():
                # The four reference phases and incoherent pair are supplied at
                # the comparison cut. Basis sources enter before the splitter.
                rows[label] = term_arm(
                    src, k, name, after_split=label not in W, sector_copy=cd
                )
            addr = "c" if cd else "a"
            place = "b" if name == "without_undo" else addr
            if name in ("compensated", "without_undo", "substitution_cd"):
                assert table_value(rows[addr], place) == printable(real_chance(zeta(w)))
            if name == "single":
                x = scaled(Q(1, 2), mult(realpart(zeta(k)), HALF))
                assert table_value(rows["a"], "a") == printable(
                    add(scaled(Q(3, 8), ONE), x)
                )
                assert table_value(rows["a"], "b") == "1/4"
            rows["inverse_all"] = term_arm(
                prep[addr], k, name, inverse=True, sector_copy=cd
            )
            rows["quarter_turn_on_c"] = term_arm(
                prep[addr], k, name, quadrature=2, sector_copy=cd
            )
            rows["whole_reference_rephased"] = term_arm(
                prep[addr], k, name, gauge=diagonal((1, 3, 5, 2)), sector_copy=cd
            )
            assert (
                rows["whole_reference_rephased"]["direct_word"]
                == rows[addr]["direct_word"]
            )
            assert rows["inverse_all"]["direct_word"] == rows[addr]["direct_word"]
            if name != "single":
                # c-d receives the extra phase on c (the FIRST output of its
                # splitter), whereas the other comparison arms place it on c second.
                phase = w - 2 if cd else w + 2
                assert table_value(rows["quarter_turn_on_c"], place) == printable(
                    real_chance(zeta(phase))
                )
            if cd:
                rows["extra_pi_on_d"] = term_arm(
                    prep["c"], k, name, modify_direct_d=True, sector_copy=True
                )
                assert table_value(rows["extra_pi_on_d"], "c") == printable(
                    real_chance(zeta(w + 4))
                )
            kz[name] = rows
        ports[str(k)] = kz
        variations = {}
        for alpha, beta, uf, p, q, r in (
            (0, 4, 0, 0, 0, 0),
            (4, 0, 0, 0, 0, 0),
            (0, 0, 2, 0, 0, 0),
            (0, 0, 0, 0, 0, 4),
            (0, 0, 0, 1, 3, 2),
            (2, 3, 1, 5, 2, 6),
        ):
            details = {}
            for source in W:
                details[source] = {
                    name: term_arm(
                        prep[source],
                        k,
                        name,
                        frame=(p, q, r),
                        undo=(alpha, beta, uf),
                        sector_copy=name == "substitution_cd",
                    )
                    for name in ("compensated", "without_undo", "substitution_cd")
                }
            # Undo contribution for a -> b with phase u_P, M^dagger b -> a with -u_M.
            cphase = w + alpha - beta + uf - p
            rphase = w + q - p - r
            assert table_value(details["a"]["compensated"], "a") == printable(
                real_chance(zeta(cphase))
            )
            assert table_value(details["a"]["without_undo"], "b") == printable(
                real_chance(zeta(rphase))
            )
            variations[f"undo({alpha},{beta},{uf})/active({p},{q},{r})"] = details
        for delta in range(8):
            cfg = (0, 0, delta)
            scratch = term_arm(
                prep["c"], k, "substitution_cd", frame=cfg, sector_copy=True
            )
            independent = term_arm(prep["a"], k, "without_undo", frame=cfg)
            port_rate = printable(real_chance(zeta(w - delta)))
            assert scratch["connected_controller"]["11"]["K"]["101"] == port_rate
            assert independent["connected_controller"]["11"]["K"]["011"] == port_rate
            variations[f"connected_phased_R_{delta}"] = {
                "scratch_reference": scratch,
                "without_full_undo": independent,
            }
        source_checks[str(k)] = variations
    return {
        "format": "z exponent of exp(iπ/4). Four direct-word chances include zeros. Each controller record names the committed full physical-word decoding in physical/encoded and its exact chance.",
        "standard": ports,
        "changed_complete_undo_and_independent_pair_frames": source_checks,
    }


def tagged_circuit_controls():
    def word_gate(state, g):
        out = defaultdict(lambda: ZERO)
        for (j, t, l), amp in state.items():
            for i in range(4):
                if g[i][j] != ZERO:
                    out[i, t, l] = add(out[i, t, l], mult(g[i][j], amp))
        return {k: v for k, v in out.items() if v != ZERO}

    def xor_tag(state, gate):
        def transform(j, t, l):
            if gate == "t_from_route":
                return (j, t ^ int(j in (0, 1)), l)
            if gate == "l_from_t":
                return (j, t, l ^ t)
            raise ValueError(gate)

        return {transform(*k): v for k, v in state.items()}

    record = {}
    modes = {
        "absent": ([], []),
        "present_disconnected": ([], []),
        "retained": (["t_from_route"], []),
        "ignored": (["t_from_route"], []),
        "physically_returned": (["t_from_route"], ["t_from_route"]),
        "copied_elsewhere_and_t_returned": (
            ["t_from_route", "l_from_t"],
            ["t_from_route"],
        ),
        "both_physically_returned": (
            ["t_from_route", "l_from_t"],
            ["l_from_t", "t_from_route"],
        ),
    }
    for k, variant in product(
        range(8), ("compensated", "without_undo", "single", "substitution_cd")
    ):
        bp, bq, br, bl = (rim(x, k) for x in "PQRL")
        if variant == "substitution_cd":
            start = 2
            split = bl
            unsplit = adjoint(bl)
            mid = [completed(bp), completed(bq), completed(bp), adjoint(completed(br))]
        else:
            start = 0
            split = bq
            unsplit = adjoint(br if variant == "without_undo" else bq)
            mid = [bp] if variant == "single" else [bp, bp]
            if variant == "compensated":
                mid.append(rim("P", full=True))
        block = {}
        for mode, (before, after) in modes.items():
            state = word_gate({(start, 0, 0): ONE}, split)

            def change_tag(st, op):
                if variant != "substitution_cd" or op != "t_from_route":
                    return xor_tag(st, op)
                # A separate reference marks s=1 on the c,d comparison.
                return {(j, t ^ (j in (1, 3)), l): v for (j, t, l), v in st.items()}

            for op in before:
                state = change_tag(state, op)
            initial_tagged = {
                f"{W[i]}/{t}/{l}": printable(v) for (i, t, l), v in state.items()
            }
            for g in mid:
                state = word_gate(state, g)
            for op in after:
                state = change_tag(state, op)
            state = word_gate(state, unsplit)
            readable = {
                f"{W[i]}/{t}/{l}": printable(
                    mult(
                        state.get((i, t, l), ZERO),
                        conjugate(state.get((i, t, l), ZERO)),
                    )
                )
                for i, t, l in product(range(4), range(2), range(2))
            }
            raw = tuple(
                total(mult(v, conjugate(v)) for (j, _, _), v in state.items() if j == i)
                for i in range(4)
            )
            assert total(raw) == ONE
            block[mode] = {
                "joint_final_word_t_l": readable,
                "word_chance": list(map(printable, raw)),
                "tagged_after_split": initial_tagged,
                "final_amplitudes": {
                    f"{W[i]}/{t}/{l}": printable(v) for (i, t, l), v in state.items()
                },
            }
        assert (
            block["absent"]["word_chance"]
            == block["physically_returned"]["word_chance"]
            == block["both_physically_returned"]["word_chance"]
        )
        assert (
            block["retained"]["word_chance"]
            == block["ignored"]["word_chance"]
            == block["copied_elsewhere_and_t_returned"]["word_chance"]
        )
        if variant in ("compensated", "without_undo", "substitution_cd"):
            assert block["retained"]["word_chance"].count("1/2") == 2
        record[f"{variant}/z{k}"] = block
    return record


def lift_permutation(perm, k, complete=False):
    n = len(perm)
    assert all(perm[perm[j]] == j for j in range(n))

    def entry(i, j):
        if perm[j] == j:
            return zeta(2 * k - 2 if complete else k) if i == j else ZERO
        if complete:
            return ONE if i == perm[j] else ZERO
        if i == j:
            return HALF
        if i == perm[j]:
            return mult(zeta(2), HALF)
        return ZERO

    return tuple(tuple(entry(i, j) for j in range(n)) for i in range(n))


def support_controls(physical):
    # On disjoint physical threshold components, reduce by the local orbit
    # types (fixed singleton or two-word orbit). Each class has a real witness.
    arms = {}
    for law, row in physical["ordinary_thresholds"]["physical_disjoint_union"][
        "laws"
    ].items():
        witnesses = {}
        for trial in row["records"]:
            key = tuple(
                int(trial["programs"][g]["endpoint"] != trial["word"])
                for g in ("4", "5")
            )
            if key in witnesses:
                continue
            witnesses[key] = {
                "input": trial["word"],
                "4": trial["programs"]["4"]["endpoint"],
                "5": trial["programs"]["5"]["endpoint"],
                "45": trial["programs"]["union"]["endpoint"],
            }
        assert len(witnesses) == 4
        arms[law] = {}
        for key, d in sorted(witnesses.items()):
            l, r = key
            ordered = [d["input"]]
            for endpoint in (d["4"], d["5"], d["45"]):
                if endpoint not in ordered:
                    ordered.append(endpoint)
            n = len(ordered)
            p = tuple(i ^ l for i in range(n))
            q = tuple(i ^ (2 if l and r else r) for i in range(n))
            together = tuple(p[q[i]] for i in range(n))
            variants = {}
            for k in range(8):
                a, b, both = (lift_permutation(g, k) for g in (p, q, together))
                assert mm(a, b) == mm(b, a)
                pa = born(apply(mm(a, b), basis(0, n)))
                pb = born(apply(both, basis(0, n)))
                if l and r:
                    assert [printable(u) for u in pa] == ["1/4"] * 4
                    assert [printable(u) for u in pb] == ["1/2", "0", "0", "1/2"]
                double_indirect = mm(completed(a), completed(b))
                double_joint = completed(both)
                variants[k] = {
                    "two_separate_chances": list(map(printable, pa)),
                    "one_compound_chances": list(map(printable, pb)),
                    "normalized_double_separate": matrix_out(double_indirect),
                    "normalized_double_compound": matrix_out(double_joint),
                }
            arms[law]["".join(str(j) for j in key)] = {
                "actual_basis": ordered,
                "signatures": d,
                "all_z": variants,
            }
    # Partition a single ordinary map's MOVING support into disjoint alternatives,
    # with a remaining idle cell. All sectors and both whole-program phases matter.
    parts = {}
    for k in range(8):
        p = (1, 0, 2, 3, 4)
        q = (0, 1, 3, 2, 4)
        u = tuple(p[q[j]] for j in range(5))
        sep = mm(lift_permutation(p, k), lift_permutation(q, k))
        joined = lift_permutation(u, k)
        assert sep == scalar_times(zeta(k), joined)
        parts[k] = {
            "separate": matrix_out(sep),
            "joined": matrix_out(joined),
            "phase_of_separate_over_joined": printable(zeta(k)),
        }
    m = tuple(tuple(mult(x, conjugate(x)) for x in row) for row in rim("P", 0))
    assert mm(m, m) == m
    coherent_sqr = mm(rim("P", 0), rim("P", 0))
    assert born(apply(coherent_sqr, basis(0))) == basis(1)
    return {
        "independent_threshold_pools": arms,
        "mutually_exclusive_guard_partition": parts,
        "basis_kernel_with_intermediate_word_record": matrix_out(m),
        "two_measured_pulses": matrix_out(mm(m, m)),
        "two_unmeasured_pulses_input_a": list(
            map(printable, born(apply(coherent_sqr, basis(0))))
        ),
        "scope": "Ordinary compound threshold firing is a physical update. One coherent half of a compound permutation is a separate supplied operation.",
    }


def ternary_references(physical):
    evidence = {}
    for law, r in physical["ternary"]["laws"].items():
        rows = r["valid_rows"]
        words = [w["initial"] for w in rows]
        n = len(words)
        perm = {
            i: tuple(words.index(w["programs"][i]["last_word"]) for w in rows)
            for i in "PQR"
        }
        weights = {
            v: tuple(i for i, w in enumerate(words) if w.count("1") == v)
            for v in sorted({w.count("1") for w in words})
        }
        by_phase = {}
        for k in range(8):
            u = {j: lift_permutation(perm[j], k) for j in "PQR"}
            full_ordinary = lift_permutation(perm["P"], 1, complete=True)
            if k == 1:
                assert full_ordinary == completed(u["P"])
            comp = program(u["Q"], u["P"], u["P"], full_ordinary, adjoint(u["Q"]))
            other = program(u["Q"], u["P"], u["P"], adjoint(u["R"]))
            cd = program(
                completed(u["P"]),
                completed(u["Q"]),
                completed(u["P"]),
                adjoint(completed(u["R"])),
            )
            rows_by_class = {}
            for weight, idx in weights.items():
                rec = {}
                for j in idx:
                    for h in idx:
                        if j > h:
                            continue
                        for angle in (0,) if j == h else (0, 2, 4, 6):
                            vin = basis(j, n) if j == h else coherent(j, h, angle, n)
                            terminal = {}
                            for label, prog in (
                                ("compensated", comp),
                                ("without_undo", other),
                                ("substitution_return", cd),
                            ):
                                v = apply(prog, vin)
                                rates = born(v)
                                assert total(rates) == ONE
                                assert all(
                                    x == ZERO for z, x in enumerate(v) if z not in idx
                                )
                                terminal[label] = {
                                    "final_vector": list(map(printable, v)),
                                    "ordinary_word_chances": list(
                                        map(printable, rates)
                                    ),
                                }
                            rec[f"{words[j]},{words[h]}/{angle}"] = terminal
                rows_by_class[weight] = rec
            by_phase[k] = rows_by_class
        evidence[law] = {
            "word_order": words,
            "ordinary_name_permutations": perm,
            "native_occupancy_classes": weights,
            "all_within_class_references": by_phase,
        }
    return evidence


def physical_writer_check(physical):
    from physical_composition import basis_words, readout_word

    truth = {}
    for reverse, copy_s, conn in product((False, True), (False, True), CONNECTIONS):
        words = basis_words(reverse)
        for j, name in enumerate(W):
            kernel = readout_word(
                words[name], stages=conn, scratch_to_q=copy_s, reverse=reverse
            )
            fields = kernel["readout"]
            assert kernel["status"] == "admitted" and (
                fields["keeper"],
                fields["z"],
                fields["q"],
            ) == port(j, conn, copy_s)
            truth[f"{int(reverse)}/{int(copy_s)}/{''.join(map(str, conn))}/{name}"] = {
                "initial": words[name],
                "terminal": kernel["terminal"],
                "keeper": fields["keeper"],
                "q": fields["q"],
                "s": fields["s"],
                "slack": fields["z"],
            }
    return truth


def physical_tag_words():
    """Real old registers backing the logical branch and remote-copy controls."""
    from physical_composition import _routes

    routes = _routes()
    rows = {}
    for reverse, j, t, latch in product((False, True), range(4), range(2), range(2)):
        q, scratch = ((1, 0), (1, 1), (0, 0), (0, 1))[j]
        initial = routes.encode(245, q=q, s=scratch, t=t, l=latch, reverse=reverse)
        entry = {}
        for guard, target, control, address in (
            ("q_to_t", routes.T, routes.Q, q),
            ("s_to_t", routes.T, routes.S, scratch),
            ("t_to_l", routes.L, routes.T, t),
        ):
            trace = routes._register_exchange(
                initial, target, guard, controls=(control,), reverse=reverse
            )
            final = trace["after"]
            decoded = routes.decode(final, reverse=reverse)
            assert (decoded["t"], decoded["l"]) == (
                t ^ (address if target == routes.T else 0),
                latch ^ (address if target == routes.L else 0),
            )
            inverse = routes._register_exchange(
                final, target, guard, controls=(control,), reverse=reverse
            )
            assert inverse["after"] == initial
            assert all(not bad for bad in trace["physical_law_failures"].values())
            entry[guard] = {"trace": trace, "inverse": inverse, "final_read": decoded}
        rows[f"{int(reverse)}/{W[j]}/{t}/{latch}"] = entry
    return rows


def measured_record_control():
    """Classical intermediate word readings versus a chronological coherent offer."""
    out = {}
    for k in range(8):
        u = rim("P", k)
        corrected = rim("P", full=True)
        for input_index in range(4):
            initial = [basis(input_index)]
            for label, stages in {
                "one_offer": [u],
                "two_forward_no_read": [u, u],
                "two_forward_full_word_read_between": [u, lambda j: j, u],
                "two_and_undo_no_read": [u, u, corrected],
                "two_and_undo_full_word_read_between": [u, lambda j: j, u, corrected],
                "true_inverse": [u, adjoint(u)],
                "true_inverse_full_read_between": [u, lambda j: j, adjoint(u)],
            }.items():
                branches, chances = run(initial, stages)
                out[f"{k}/{W[input_index]}/{label}"] = {
                    "complete_word": list(map(printable, chances)),
                    "orthogonal_record_conditioned_vectors": [
                        [printable(x) for x in b] for b in branches
                    ],
                }
    return out


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_bindings():
    paths = [
        HERE / f
        for f in (
            "composition.py",
            "physical_composition.py",
            "preregistration.md",
            "design_reviews.md",
        )
    ]
    paths += [
        ROOT / p
        for p in (
            "research/ERASURE-AND-CLOSING-SIGNS-20261121-001/independent_checks.py",
            "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py",
            "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/keeper.py",
            "research/MOTION-LAW-20261119-001/selection.md",
            "research/MOTION-LAW-20261119-001/what_is_forced.md",
            "experiments/MOTION-LAW-20261119-001/MOTION-LAW-20261119-001-E001_rules/permutation_controls.py",
            "experiments/MOTION-LAW-20261119-001/MOTION-LAW-20261119-001-E001_rules/sources.py",
            "experiments/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A-E001_sign_records/physical_histories.py",
        )
    ]
    return {str(p.relative_to(ROOT)): hash_file(p) for p in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--write", action="store_true")
    output.add_argument("--check", action="store_true")
    args = parser.parse_args()
    from physical_composition import physical_checks

    physical = physical_checks()
    e = {
        "ticket": HERE.name,
        "ring": "[1,ζ,ζ²,ζ³], ζ=exp(iπ/4). All amplitudes and probabilities are exact.",
        "source_bindings": source_bindings(),
        "physical": physical,
        "ordinary_word_to_keeper": physical_writer_check(physical),
        "symbolic_relations": symbolic_return_tables(),
        "checked_coherent_relations": numerical_relations(),
        "all_readouts": interference_tables(),
        "physical_tag_controls": tagged_circuit_controls(),
        "actual_ordinary_tag_words": physical_tag_words(),
        "intermediate_full_word_readings": measured_record_control(),
        "ordinary_and_compound_controls": support_controls(physical),
        "ternary_reference_restrictions": ternary_references(physical),
    }
    canonical = (
        json.dumps(
            e, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        + b"\n"
    )
    # mtime 0 and empty gzip name keep the published receipt byte-reproducible.
    import io

    out = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", fileobj=out, compresslevel=9, mtime=0
    ) as f:
        f.write(canonical)
    receipt = out.getvalue()
    path = HERE / "observations.json.gz"
    if args.write:
        path.write_bytes(receipt)
    else:
        assert path.read_bytes() == receipt, f"replay differs from {path}"
    print(
        f"PASS {len(canonical)} exact-JSON bytes; {len(receipt)} compressed; sha256={hashlib.sha256(receipt).hexdigest()}"
    )


if __name__ == "__main__":
    main()
