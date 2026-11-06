#!/usr/bin/env python3
"""Lane C of NEXT-DIRECTION-SCAN-20261026-001: the Borromean bridge.

K1-K3 verdicts (erasure as forgetting) for the relations behind the twisted
triple product, read two ways:

* vector reading: each slot vector (for the Borromean determinant, a leaf
  loop's vector of values under the three classes) is one many-valued
  distinction;
* bit reading: each coordinate bit is one distinction, knotlab's own reading.

Also computed: the identity tying the kernel count to the knot's allowed
states, the Potts edge gadget over F_2 and F_3, a type-III / D4 check on T^3,
the K1-K3 status of group multiplication relations (including UT3(F4) x| C3
with and without a hard pair), and the bounded-hub reduction of cubic phases to
quadratic Gauss sums.

Run from the repository root (standard library plus tools/knotlab):
    PYTHONPATH=tools python3 -B research/NEXT-DIRECTION-SCAN-20261026-001C/scan_c.py
It writes results.json, cli_log.txt and relations/*.cnf next to this file and
exits nonzero if a prediction recorded below fails.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from fractions import Fraction
from itertools import combinations, permutations, product
from math import log2
from pathlib import Path

from knotlab.knots import check_knot
from knotlab.relations import Relation
from knotlab.space import bonds

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
(HERE / "relations").mkdir(exist_ok=True)
RESULTS: dict[str, object] = {}
CLI_LOG: list[str] = []
FAILURES: list[str] = []


def expect(label: str, value: object, wanted: object) -> None:
    ok = value == wanted
    print(f"  [{'ok' if ok else 'MISMATCH'}] {label}: {value}" + ("" if ok else f" (expected {wanted})"))
    if not ok:
        FAILURES.append(label)


# --------------------------------------------------------------------------- fields

class Field:
    """F_q for q in {2, 3, 4, 5, 7}; F_4 = {0, 1, w, w+1} coded 0, 1, 2, 3."""

    def __init__(self, q: int):
        self.q = q
        if q == 4:
            add = [[a ^ b for b in range(4)] for a in range(4)]
            mul = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]
        elif q in (2, 3, 5, 7):
            add = [[(a + b) % q for b in range(q)] for a in range(q)]
            mul = [[(a * b) % q for b in range(q)] for a in range(q)]
        else:
            raise ValueError(q)
        self.add, self.mul = add, mul
        self.neg = [next(b for b in range(q) if add[a][b] == 0) for a in range(q)]
        self.sub = [[add[a][self.neg[b]] for b in range(q)] for a in range(q)]
        # absolute trace to F_2 (only used for q = 4): tr(x) = x + x^2
        self.trace = [0, 0, 1, 1] if q == 4 else None


def det3(F: Field, u, v, w) -> int:
    M, S, A = F.mul, F.sub, F.add
    c0 = S[M[v[1]][w[2]]][M[v[2]][w[1]]]
    c1 = S[M[v[0]][w[2]]][M[v[2]][w[0]]]
    c2 = S[M[v[0]][w[1]]][M[v[1]][w[0]]]
    return A[S[M[u[0]][c0]][M[u[1]][c1]]][M[u[2]][c2]]


# --------------------------------------------------------------------------- the test

def mv_check(allowed: set, sizes: list[int]) -> dict:
    """K1-K3 with erasure as forgetting, for variables with the given numbers of values.

    Same definition as knotlab.check_knot (and as is_many_valued_knot in
    KNOT-LOOPS-20261019-001C-E001): K1 the relation is not full; K2 the shadow
    on all but any one variable is full; K3 the relation is nonempty.
    """
    total = 1
    for size in sizes:
        total *= size
    k1 = len(allowed) < total
    k3 = len(allowed) > 0
    failing = []
    for i, size in enumerate(sizes):
        shadow = {state[:i] + state[i + 1:] for state in allowed}
        if len(shadow) != total // size:
            failing.append(i)
    return {"K1": k1, "K2": not failing, "K3": k3, "knot": k1 and not failing and k3,
            "allowed": len(allowed), "states": total, "K2_fails_when_forgetting": failing}


def short(verdict: dict) -> str:
    return (f"K1 {'yes' if verdict['K1'] else 'no'}, K2 {'yes' if verdict['K2'] else 'no'}, "
            f"K3 {'yes' if verdict['K3'] else 'no'} -> knot: {'YES' if verdict['knot'] else 'no'}"
            f"  ({verdict['allowed']}/{verdict['states']} states allowed)")


def cli_check(name: str, variables: list[str], rows: set, contact: str | None = None,
              timeout: int = 900) -> dict:
    """The canonical CLI on the CNF whose clauses exclude exactly the excluded states.

    K1-K3 under forgetting is symmetric in all variables, so which variable is
    named the contact does not change the verdict.
    """
    contact = contact or variables[-1]
    loops = [v for v in variables if v != contact]
    clauses = [" ".join(("~" + v) if x else v for v, x in zip(variables, state))
               for state in product((0, 1), repeat=len(variables)) if state not in rows]
    cnf = "; ".join(clauses)
    path = HERE / "relations" / f"{name}.cnf"
    path.write_text(cnf + "\n")
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
           "--loops", *loops, "--contact", contact, "--json"]
    start = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, env={**os.environ, "PYTHONPATH": "tools"},
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    out = json.loads(proc.stdout)
    record = {key: out[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot",
                                        "pairwise_definable", "minimum_width", "notes")}
    record["allowed_states"] = len(out["allowed"])
    record["seconds"] = round(time.time() - start, 1)
    CLI_LOG.append(
        f"$ PYTHONPATH=tools python3 -B -m knotlab check --cnf \"$(cat {path.relative_to(ROOT)})\" "
        f"--loops {' '.join(loops)} --contact {contact} --json\n"
        f"  {name}: {len(clauses)} clauses; allowed {record['allowed_states']}/{2 ** len(variables)}; "
        f"K1 {record['binding']}, K2 {record['loss_on_erasure']}, K3 {record['coexistence']}, "
        f"knot {record['is_knot']}; 2-CNF definable {record['pairwise_definable']}; "
        f"min width {record['minimum_width']}"
        + (f"\n  note: {record['notes'][0]}" if record["notes"] else "")
    )
    return record


def bond_summary(variables: list[str], rows: set) -> dict:
    relation = Relation(tuple(variables), frozenset(tuple(bool(x) for x in r) for r in rows))
    found = bonds(relation)
    kinds: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for bond in found:
        names = sorted(bond, key=variables.index)
        shadow = relation.project(names)
        excluded = 2 ** len(names) - len(shadow.rows)
        kind = (f"size {len(names)}, "
                + ("atom (1 excluded state)" if excluded == 1
                   else "parity (half excluded)" if excluded == 2 ** (len(names) - 1)
                   else f"{excluded} excluded states"))
        kinds[kind] = kinds.get(kind, 0) + 1
        examples.setdefault(kind, [])
        if len(examples[kind]) < 3:
            examples[kind].append("{" + ", ".join(names) + "}")
    return {"bonds": len(found), "kinds": kinds, "examples": examples}


def bits(value: int, width: int) -> tuple:
    return tuple((value >> i) & 1 for i in range(width))


# --------------------------------------------------------------------------- section 0

def validate() -> None:
    print("\n[0] the many-valued checker agrees with knotlab.check_knot")
    names = ("A", "B", "c")
    cube = list(product((False, True), repeat=3))
    agree = knots = 0
    for mask in range(256):
        rows = frozenset(row for i, row in enumerate(cube) if mask >> i & 1)
        rep = check_knot(Relation(names, rows), ["A", "B"], "c")
        mine = mv_check({tuple(int(x) for x in r) for r in rows}, [2, 2, 2])
        agree += (rep.binding, rep.loss_on_erasure, rep.coexistence) == (mine["K1"], mine["K2"], mine["K3"])
        knots += mine["knot"]
    expect("all 256 relations on three bits agree", agree, 256)
    expect("knots among them (the 34 of Fact 1)", knots, 34)
    rng = random.Random(20261026)
    names4 = ("A", "B", "C", "c")
    hyper = list(product((False, True), repeat=4))
    agree4 = 0
    for _ in range(3000):
        mask = rng.getrandbits(16)
        rows = frozenset(row for i, row in enumerate(hyper) if mask >> i & 1)
        rep = check_knot(Relation(names4, rows), ["A", "B", "C"], "c")
        mine = mv_check({tuple(int(x) for x in r) for r in rows}, [2, 2, 2, 2])
        agree4 += (rep.binding, rep.loss_on_erasure, rep.coexistence) == (mine["K1"], mine["K2"], mine["K3"])
    expect("3000 random relations on four bits agree", agree4, 3000)
    RESULTS["validation"] = {"three_bits_agree": agree, "three_bit_knots": knots, "four_bits_agree": agree4}


# --------------------------------------------------------------------------- section 1

def controls() -> None:
    print("\n[1] controls through the canonical CLI")
    even = {s for s in product((0, 1), repeat=3) if sum(s) % 2 == 0}
    r = cli_check("control_parity_even", ["x", "y", "z"], even)
    expect("parity x+y+z = 0 (positive control) is a knot", r["is_knot"], True)
    tie = {s for s in product((0, 1), repeat=3) if s[0] == s[1]}
    r2 = cli_check("control_tie_x_eq_y", ["x", "y", "z"], tie)
    expect("x = y with z free (negative control) is a knot", r2["is_knot"], False)
    fixed = {s for s in product((0, 1), repeat=3) if s[0] == 1 and s[2] == s[0] ^ s[1]}
    r3 = cli_check("control_xor_of_fixed_value", ["A", "B", "c"], fixed)
    expect("c = A xor B with A fixed true (classifier) is a knot", r3["is_knot"], False)
    atom = {s for s in product((0, 1), repeat=3) if not (s[0] and s[1] and s[2])}
    r4 = cli_check("control_atom_xyz_eq_0", ["x", "y", "z"], atom)
    expect("xyz = 0 over F_2 (the atom up to polarity) is a knot", r4["is_knot"], True)
    RESULTS["controls"] = {"parity": r, "tie": r2, "xor_of_fixed": r3, "atom_xyz": r4}


# --------------------------------------------------------------------------- section 2

def vectors(q: int, d: int) -> list[tuple]:
    return list(product(range(q), repeat=d))


def vector_relation(F: Field, dims, form) -> tuple[set, list[int]]:
    """Allowed states (indices) of {(a, b, c): form(a, b, c) == 0} on F^d1 x F^d2 x F^d3."""
    spaces = [vectors(F.q, d) for d in dims]
    allowed = set()
    for i, a in enumerate(spaces[0]):
        for j, b in enumerate(spaces[1]):
            for k, c in enumerate(spaces[2]):
                if form(a, b, c) == 0:
                    allowed.add((i, j, k))
    return allowed, [len(s) for s in spaces]


def vector_reading() -> None:
    print("\n[2] vector reading: each slot vector is one many-valued distinction")
    out = {}
    for q in (2, 3, 4):
        F = Field(q)
        allowed, sizes = vector_relation(F, (3, 3, 3), lambda a, b, c, F=F: det3(F, a, b, c))
        v = mv_check(allowed, sizes)
        print(f"  det(u, v, w) = 0 over F_{q}^3: {short(v)}")
        expect(f"det = 0 over F_{q}^3 is a vector-level knot", v["knot"], True)
        out[f"det_F{q}"] = v
    F4 = Field(4)
    allowed, sizes = vector_relation(F4, (3, 3, 3), lambda a, b, c: F4.trace[det3(F4, a, b, c)])
    v = mv_check(allowed, sizes)
    print(f"  tr det(u, v, w) = 0 over F_4^3 (the mod-2 phase of the counts): {short(v)}")
    expect("tr det = 0 over F_4^3 is a vector-level knot", v["knot"], True)
    out["trdet_F4"] = v

    F2 = Field(2)
    def alt(sub_triples):
        def form(a, b, c):
            total = 0
            for (i, j, k) in sub_triples:
                total ^= det3(F2, (a[i], a[j], a[k]), (b[i], b[j], b[k]), (c[i], c[j], c[k]))
            return total
        return form
    cases = [
        ("decomposable e1^e2^e3 on F_2^4", 4, [(0, 1, 2)]),
        ("e123 + e145 on F_2^5 (two Borromean triples sharing a leaf)", 5, [(0, 1, 2), (0, 3, 4)]),
        ("e123 + e456 on F_2^6 (two disjoint Borromean triples)", 6, [(0, 1, 2), (3, 4, 5)]),
    ]
    for label, d, triples in cases:
        allowed, sizes = vector_relation(F2, (d, d, d), alt(triples))
        v = mv_check(allowed, sizes)
        print(f"  {label}: {short(v)}")
        expect(f"{label} is a vector-level knot", v["knot"], True)
        out[label] = v

    sigma = lambda x: sum(x) % 2
    allowed, sizes = vector_relation(F2, (2, 2, 2), lambda a, b, c: sigma(a) * sigma(b) * sigma(c))
    v = mv_check(allowed, sizes)
    print(f"  atom of slot parities s(a)s(b)s(c) = 0 on F_2^2: {short(v)}")
    out["atom_of_parities"] = v

    # kernel relation of det over F_2 with a free third slot
    V3 = vectors(2, 3)
    kernel = {(i, j) for i, a in enumerate(V3) for j, b in enumerate(V3)
              if all(det3(F2, a, b, c) == 0 for c in V3)}
    with_free = {(i, j, k) for (i, j) in kernel for k in range(8)}
    v = mv_check(with_free, [8, 8, 8])
    print(f"  kernel relation {{(a,b): det(a,b,.) = 0}} on F_2^3 with a free contact: {short(v)}")
    expect("kernel relation with a free contact is a knot", v["knot"], False)
    expect("kernel count N(det) over F_2 (pairs a, b with a x b = 0)", len(kernel), 22)
    out["kernel_det_F2_free_contact"] = v
    out["N_det_F2"] = len(kernel)

    # bilinear controls on F_2^2: dot product and the 2x2 determinant (symplectic form)
    V2 = vectors(2, 2)
    forms2 = {"dot a.b": lambda a, b: (a[0] * b[0] + a[1] * b[1]) % 2,
              "det2 [a b] (symplectic)": lambda a, b: (a[0] * b[1] + a[1] * b[0]) % 2}
    for label, B in forms2.items():
        free_c = {(i, j, k) for i, a in enumerate(V2) for j, b in enumerate(V2) for k in range(2)
                  if B(a, b) == 0}
        v1 = mv_check(free_c, [4, 4, 2])
        times_c = {(i, j, k) for i, a in enumerate(V2) for j, b in enumerate(V2) for k in range(2)
                   if B(a, b) * k == 0}
        v2 = mv_check(times_c, [4, 4, 2])
        graph = {(i, j, k) for i, a in enumerate(V2) for j, b in enumerate(V2) for k in range(2)
                 if B(a, b) == k}
        v3 = mv_check(graph, [4, 4, 2])
        print(f"  bilinear {label}: B(a,b) = 0 with free c: {short(v1)}")
        print(f"  bilinear {label}: B(a,b) * c = 0, c in F_2 (bounded contact): {short(v2)}")
        print(f"  bilinear {label}: graph B(a,b) = c: {short(v3)}")
        expect(f"{label}: zero set with free contact is a knot", v1["knot"], False)
        expect(f"{label}: B(a,b)*c = 0 with a one-bit contact is a knot", v2["knot"], True)
        expect(f"{label}: graph B(a,b) = c is a knot", v3["knot"], False)
        out[f"bilinear {label}"] = {"free_contact": v1, "times_bounded_contact": v2, "graph": v3}

    graph_det = {(i, j, k, s) for i, a in enumerate(V3) for j, b in enumerate(V3)
                 for k, c in enumerate(V3) for s in range(2) if det3(F2, a, b, c) == s}
    v = mv_check(graph_det, [8, 8, 8, 2])
    print(f"  graph of det, {{(u, v, w, s): det = s}} over F_2: {short(v)}")
    expect("graph of det is a knot", v["knot"], False)
    out["graph_det_F2"] = v
    RESULTS["vector_reading"] = out


# --------------------------------------------------------------------------- section 3

def bit_reading() -> None:
    print("\n[3] bit reading: each coordinate bit is one distinction (canonical CLI where small)")
    out = {}
    F2 = Field(2)
    names9 = [f"{s}{i}" for s in "uvw" for i in (1, 2, 3)]
    det_rows = set()
    for state in product((0, 1), repeat=9):
        if det3(F2, state[0:3], state[3:6], state[6:9]) == 0:
            det_rows.add(state)
    r = cli_check("bits_det_F2", names9, det_rows)
    expect("det = 0 on 9 bits is a knot (canonical CLI)", r["is_knot"], False)
    r["bonds"] = bond_summary(names9, det_rows)
    print(f"  det on 9 bits: knot {r['is_knot']}; bonds: {r['bonds']['kinds']}")
    out["det_F2_9bits"] = r

    names6 = ["a1", "a2", "a3", "b1", "b2", "b3"]
    kernel_rows = {s for s in product((0, 1), repeat=6)
                   if all(det3(F2, s[0:3], s[3:6], c) == 0 for c in product((0, 1), repeat=3))}
    r = cli_check("bits_kernel_det_F2", names6, kernel_rows)
    expect("kernel relation a x b = 0 on 6 bits is a knot", r["is_knot"], False)
    r["bonds"] = bond_summary(names6, kernel_rows)
    print(f"  kernel a x b = 0 on 6 bits: knot {r['is_knot']}; bonds: {r['bonds']['kinds']}")
    out["kernel_det_F2_6bits"] = r

    names4 = ["x1", "x2", "y1", "y2"]
    minor = {s for s in product((0, 1), repeat=4) if (s[0] * s[3] + s[1] * s[2]) % 2 == 0}
    r = cli_check("bits_det2_minor", names4, minor)
    expect("2x2 minor x1 y2 = x2 y1 on 4 bits is a knot", r["is_knot"], False)
    r["bonds"] = bond_summary(names4, minor)
    print(f"  2x2 minor on 4 bits: knot {r['is_knot']}; bonds: {r['bonds']['kinds']}")
    out["det2_minor_4bits"] = r

    dot = {s for s in product((0, 1), repeat=4) if (s[0] * s[2] + s[1] * s[3]) % 2 == 0}
    r = cli_check("bits_dot_zero", ["a1", "a2", "b1", "b2"], dot)
    r["bonds"] = bond_summary(["a1", "a2", "b1", "b2"], dot)
    print(f"  dot product a.b = 0 on 4 bits: knot {r['is_knot']}; bonds: {r['bonds']['kinds']}")
    out["dot_zero_4bits"] = r

    times_c = {s for s in product((0, 1), repeat=5) if ((s[0] * s[2] + s[1] * s[3]) * s[4]) % 2 == 0}
    r = cli_check("bits_dot_times_c", ["a1", "a2", "b1", "b2", "c"], times_c)
    expect("(a.b) c = 0 on 5 bits is a knot", r["is_knot"], False)
    out["dot_times_c_5bits"] = r

    sig = {s for s in product((0, 1), repeat=6)
           if ((s[0] ^ s[1]) & (s[2] ^ s[3]) & (s[4] ^ s[5])) == 0}
    r = cli_check("bits_atom_of_parities", ["a1", "a2", "b1", "b2", "c1", "c2"], sig)
    expect("atom of slot parities on 6 bits is a knot", r["is_knot"], True)
    out["atom_of_parities_6bits"] = r

    graph = {s for s in product((0, 1), repeat=10) if det3(F2, s[0:3], s[3:6], s[6:9]) == s[9]}
    r = cli_check("bits_graph_det", names9 + ["s"], graph)
    expect("graph of det on 10 bits is a knot", r["is_knot"], False)
    out["graph_det_10bits"] = r

    signed_atom_graph = {s for s in product((0, 1), repeat=4) if s[3] == s[0] * s[1] * s[2]}
    r = cli_check("bits_signed_atom_graph", ["x", "y", "z", "s"], signed_atom_graph)
    expect("signed atom written as a relation, s = xyz, is a knot", r["is_knot"], False)
    out["signed_atom_graph_4bits"] = r

    # larger bit-level cases with the validated checker (same definition, too many states for the CLI)
    def bitwise(F, q_bits, dims, form):
        allowed = set()
        spaces = [vectors(F.q, d) for d in dims]
        for a in spaces[0]:
            for b in spaces[1]:
                for c in spaces[2]:
                    if form(a, b, c) == 0:
                        allowed.add(tuple(bit for x in (*a, *b, *c) for bit in bits(x, q_bits)))
        return mv_check(allowed, [2] * (q_bits * sum(dims)))
    e123_456 = lambda a, b, c: det3(F2, a[0:3], b[0:3], c[0:3]) ^ det3(F2, a[3:6], b[3:6], c[3:6])
    v = bitwise(F2, 1, (6, 6, 6), e123_456)
    print(f"  e123 + e456 on 18 bits: {short(v)}")
    expect("e123 + e456 on 18 bits is a knot", v["knot"], False)
    out["e123_e456_18bits"] = v
    F4 = Field(4)
    v = bitwise(F4, 2, (3, 3, 3), lambda a, b, c: det3(F4, a, b, c))
    print(f"  det over F_4 on 18 bits: {short(v)}")
    expect("det over F_4 on 18 bits is a knot", v["knot"], False)
    out["det_F4_18bits"] = v
    v = bitwise(F4, 2, (3, 3, 3), lambda a, b, c: F4.trace[det3(F4, a, b, c)])
    print(f"  tr det over F_4 on 18 bits: {short(v)}")
    expect("tr det over F_4 on 18 bits is a knot", v["knot"], False)
    out["trdet_F4_18bits"] = v
    F3 = Field(3)
    allowed = {(*a, *b, *c) for a in vectors(3, 3) for b in vectors(3, 3) for c in vectors(3, 3)
               if det3(F3, a, b, c) == 0}
    v = mv_check(allowed, [3] * 9)
    print(f"  det over F_3 read coordinate by coordinate (9 trits): {short(v)}")
    expect("det over F_3, coordinate reading, is a knot", v["knot"], False)
    out["det_F3_9trits"] = v
    RESULTS["bit_reading"] = out


# --------------------------------------------------------------------------- section 4

def all_trilinear_forms() -> None:
    print("\n[4] every trilinear form over F_2 in small dimensions, both readings")
    table = []
    for dims in ((1, 1, 1), (1, 1, 2), (1, 2, 2), (2, 2, 2), (1, 2, 3), (2, 2, 3)):
        d1, d2, d3 = dims
        cells = [(i, j, k) for i in range(d1) for j in range(d2) for k in range(d3)]
        spaces = [vectors(2, d) for d in dims]
        vec_knots = bit_knots = nonzero = 0
        bit_knot_is_all_ones = True
        for mask in range(1, 2 ** len(cells)):
            nonzero += 1
            support = [cells[n] for n in range(len(cells)) if mask >> n & 1]
            allowed_vec, allowed_bit = set(), set()
            for x, a in enumerate(spaces[0]):
                for y, b in enumerate(spaces[1]):
                    for z, c in enumerate(spaces[2]):
                        if sum(a[i] * b[j] * c[k] for i, j, k in support) % 2 == 0:
                            allowed_vec.add((x, y, z))
                            allowed_bit.add((*a, *b, *c))
            vk = mv_check(allowed_vec, [len(s) for s in spaces])["knot"]
            bk = mv_check(allowed_bit, [2] * sum(dims))["knot"]
            vec_knots += vk
            bit_knots += bk
            if bk and mask != 2 ** len(cells) - 1:
                bit_knot_is_all_ones = False
        row = {"dims": dims, "nonzero_forms": nonzero, "vector_knots": vec_knots,
               "bit_knots": bit_knots, "bit_knot_only_all_ones_tensor": bit_knot_is_all_ones}
        table.append(row)
        print(f"  dims {dims}: {nonzero} nonzero forms; vector-level knots {vec_knots}; "
              f"bit-level knots {bit_knots} (only the all-ones tensor: {bit_knot_is_all_ones})")
        expect(f"dims {dims}: every nonzero form is a vector-level knot", vec_knots, nonzero)
        expect(f"dims {dims}: exactly one bit-level knot, the all-ones tensor",
               (bit_knots, bit_knot_is_all_ones), (1, True))
    # every alternating form on F_2^4
    F2 = Field(2)
    triples = list(combinations(range(4), 3))
    V4 = vectors(2, 4)
    alt_rows = []
    for mask in range(1, 16):
        chosen = [t for n, t in enumerate(triples) if mask >> n & 1]
        allowed_vec, allowed_bit = set(), set()
        for x, a in enumerate(V4):
            for y, b in enumerate(V4):
                for z, c in enumerate(V4):
                    value = 0
                    for (i, j, k) in chosen:
                        value ^= det3(F2, (a[i], a[j], a[k]), (b[i], b[j], b[k]), (c[i], c[j], c[k]))
                    if value == 0:
                        allowed_vec.add((x, y, z))
                        allowed_bit.add((*a, *b, *c))
        alt_rows.append((mv_check(allowed_vec, [16] * 3)["knot"], mv_check(allowed_bit, [2] * 12)["knot"]))
    vec = sum(v for v, _ in alt_rows)
    bit = sum(b for _, b in alt_rows)
    print(f"  all 15 nonzero alternating forms on F_2^4: vector-level knots {vec}, bit-level knots {bit}")
    expect("alternating forms on F_2^4: vector-level knots", vec, 15)
    expect("alternating forms on F_2^4: bit-level knots", bit, 0)
    RESULTS["all_trilinear_forms_F2"] = {"table": table, "alternating_F2^4": {"vector_knots": vec, "bit_knots": bit}}


# --------------------------------------------------------------------------- section 5

def count_identity() -> None:
    print("\n[5] the kernel count is an affine function of the knot's allowed states")
    rng = random.Random(7)
    rows = []
    for q, dims, trials in ((2, (2, 2, 2), 6), (2, (3, 3, 3), 4), (2, (2, 3, 2), 4), (3, (2, 2, 2), 4), (4, (2, 2, 2), 3)):
        F = Field(q)
        d1, d2, d3 = dims
        spaces = [vectors(q, d) for d in dims]
        for _ in range(trials):
            t = {(i, j, k): rng.randrange(q) for i in range(d1) for j in range(d2) for k in range(d3)}

            def T(a, b, c, t=t, F=F):
                total = 0
                for (i, j, k), coeff in t.items():
                    if coeff:
                        total = F.add[total][F.mul[coeff][F.mul[F.mul[a[i]][b[j]]][c[k]]]]
                return total
            zeros = sum(1 for a in spaces[0] for b in spaces[1] for c in spaces[2] if T(a, b, c) == 0)
            N = sum(1 for a in spaces[0] for b in spaces[1] if all(T(a, b, c) == 0 for c in spaces[2]))
            predicted = q ** (d1 + d2 + d3 - 1) + (q - 1) * q ** (d3 - 1) * N
            rows.append({"q": q, "dims": dims, "zeros": zeros, "N": N, "identity_holds": zeros == predicted})
    holds = all(r["identity_holds"] for r in rows)
    expect(f"#Z(T) = q^(d1+d2+d3-1) + (q-1) q^(d3-1) N(T) on {len(rows)} random forms", holds, True)
    # det over F_2 as a worked example: how much the vector-level knot hides from its pairs
    hidden = 9 - log2(344)
    print(f"  det over F_2: #Z = 344 of 512, N = 22; the knot hides {hidden:.4f} bits from its pairs "
          f"= 1 - log2(1 + 22/64) = {1 - log2(1 + 22 / 64):.4f}")
    RESULTS["count_identity"] = {"cases": rows, "all_hold": holds, "det_F2_bits_hidden": hidden}


# --------------------------------------------------------------------------- section 6

def potts_gadget() -> None:
    print("\n[6] the Borromean edge gadget over F_2 and F_3 is a Potts weight")
    F2, F3 = Field(2), Field(3)
    V3 = vectors(2, 3)
    sums2 = {}
    for w in V3:
        sums2[w] = sum((-1) ** det3(F2, w, p, s) for p in V3 for s in V3)
    values2 = sorted(set(sums2[w] for w in V3 if any(w)))
    expect("F_2: sum over p, s of (-1)^det(w,p,s) at w = 0", sums2[(0, 0, 0)], 64)
    expect("F_2: the same sum at every w != 0", values2, [16])
    W3 = vectors(3, 3)
    dist = {}
    for w in W3:
        counts = [0, 0, 0]
        for p in W3:
            for s in W3:
                counts[det3(F3, w, p, s)] += 1
        dist[w] = counts
    zero_w = dist[(0, 0, 0)]
    nonzero_w = {tuple(dist[w]) for w in W3 if any(w)}
    # sum of omega^k with counts n_k equals n_0 - n_1 when n_1 = n_2
    expect("F_3: value counts of det(0, p, s)", zero_w, [729, 0, 0])
    expect("F_3: value counts (0, 1, 2) of det(w, p, s) for every w != 0",
           sorted(nonzero_w), [(297, 216, 216)])
    print("  F_3: sum over p, s of omega^det(w,p,s) = 729 at w = 0 and 297 - 216 = 81 = 3^4 otherwise")

    # end to end over F_2: T = sum over edges uv of (x_u + x_v) ^ p_e ^ s_e
    def kernel_count(n, edges):
        D = n + 2 * len(edges)
        lams = []
        for e, (u, v) in enumerate(edges):
            lams.append(((1 << u) | (1 << v), 1 << (n + 2 * e), 1 << (n + 2 * e + 1)))
        par = lambda x: bin(x).count("1") & 1
        count = 0
        for a in range(1 << D):
            la = [(par(l1 & a), par(l2 & a), par(l3 & a)) for l1, l2, l3 in lams]
            for b in range(1 << D):
                functional = 0
                for (l1, l2, l3), (a1, a2, a3) in zip(lams, la):
                    b1, b2, b3 = par(l1 & b), par(l2 & b), par(l3 & b)
                    if (a2 & b3) ^ (a3 & b2):
                        functional ^= l1
                    if (a1 & b3) ^ (a3 & b1):
                        functional ^= l2
                    if (a1 & b2) ^ (a2 & b1):
                        functional ^= l3
                if functional == 0:
                    count += 1
        return count

    def potts(n, edges, Q, v):
        total = Fraction(0)
        for subset in range(1 << len(edges)):
            parent = list(range(n))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            size = 0
            for e, (u, w) in enumerate(edges):
                if subset >> e & 1:
                    size += 1
                    parent[find(u)] = find(w)
            components = len({find(x) for x in range(n)})
            total += Fraction(Q) ** components * Fraction(v) ** size
        return total
    rows = []
    for label, n, edges in (("path of two edges", 3, [(0, 1), (1, 2)]), ("triangle", 3, [(0, 1), (1, 2), (0, 2)])):
        start = time.time()
        N = kernel_count(n, edges)
        predicted = Fraction(2) ** (2 * len(edges) - n) * potts(n, edges, 8, 3)
        rows.append({"graph": label, "N": N, "predicted": str(predicted), "seconds": round(time.time() - start, 1)})
        expect(f"F_2 {label}: N(T) = 2^(2m-n) Z_Potts(G; Q=8, v=3)", Fraction(N), predicted)
    RESULTS["potts_gadget"] = {"F2_sum_w0": sums2[(0, 0, 0)], "F2_sum_w_nonzero": values2,
                               "F3_counts_w0": zero_w, "F3_counts_w_nonzero": sorted(nonzero_w),
                               "end_to_end_F2": rows,
                               "tutte_point": "Q = 8, v = 3: (x, y) = (1 + Q/v, 1 + v) = (11/3, 4)"}


# --------------------------------------------------------------------------- section 7

def group(name: str):
    """Elements and multiplication of a few small groups."""
    if name == "Z2^3":
        els = list(range(8))
        return els, lambda x, y: x ^ y
    if name in ("D4 = UT3(F2)", "H(F3)"):
        p = 2 if name.startswith("D4") else 3
        els = list(product(range(p), repeat=3))
        return els, lambda g, h: ((g[0] + h[0]) % p, (g[1] + h[1]) % p, (g[2] + h[2] + g[0] * h[1]) % p)
    if name == "Q8":
        # (sign, unit) with unit 0..3 = 1, i, j, k
        table = {(0, 0): (0, 0), (0, 1): (0, 1), (0, 2): (0, 2), (0, 3): (0, 3),
                 (1, 0): (0, 1), (1, 1): (1, 0), (1, 2): (0, 3), (1, 3): (1, 2),
                 (2, 0): (0, 2), (2, 1): (1, 3), (2, 2): (1, 0), (2, 3): (0, 1),
                 (3, 0): (0, 3), (3, 1): (0, 2), (3, 2): (1, 1), (3, 3): (1, 0)}
        els = list(product(range(2), range(4)))

        def mul(g, h):
            sign, unit = table[(g[1], h[1])]
            return ((g[0] + h[0] + sign) % 2, unit)
        return els, mul
    if name == "S3":
        els = list(permutations(range(3)))
        return els, lambda g, h: tuple(g[h[i]] for i in range(3))
    if name.startswith("UT3(F4)"):
        F = Field(4)
        alpha, beta = (2, 2) if "hard" in name else (2, 3)  # w, w  or  w, w^2
        ab = F.mul[alpha][beta]

        def act(k, n):
            x, y, z = n
            for _ in range(k):
                x, y, z = F.mul[alpha][x], F.mul[beta][y], F.mul[ab][z]
            return (x, y, z)

        def ut(n, m):
            return (n[0] ^ m[0], n[1] ^ m[1], n[2] ^ m[2] ^ F.mul[n[0]][m[1]])
        els = [(n, k) for n in product(range(4), repeat=3) for k in range(3)]
        return els, lambda g, h: (ut(g[0], act(g[1], h[0])), (g[1] + h[1]) % 3)
    raise ValueError(name)


def group_laws() -> None:
    print("\n[7] group laws: the multiplication relation {(x, y, z): xy = z} and commuting pairs")
    out = {}
    names = ["Z2^3", "D4 = UT3(F2)", "Q8", "S3", "H(F3)",
             "UT3(F4) x| C3, action (w, w, w^2): hard pair",
             "UT3(F4) x| C3, action (w, w^2, 1): no hard pair"]
    for name in names:
        els, mul = group(name)
        index = {g: i for i, g in enumerate(els)}
        n = len(els)
        # check it is a group (associativity on a sample) before trusting the table
        rng = random.Random(1)
        sample = [(rng.choice(els), rng.choice(els), rng.choice(els)) for _ in range(500)]
        assert all(mul(mul(a, b), c) == mul(a, mul(b, c)) for a, b, c in sample), name
        allowed = {(index[a], index[b], index[mul(a, b)]) for a in els for b in els}
        v = mv_check(allowed, [n, n, n])
        commuting = sum(1 for a in els for b in els if mul(a, b) == mul(b, a))
        row = {"order": n, "multiplication": v, "commuting_pairs": commuting,
               "bits_hidden_by_multiplication": log2(n)}
        if n <= 27:
            tie = {(index[a], index[b], k) for a in els for b in els if mul(a, b) == mul(b, a)
                   for k in range(n)}
            row["commuting_with_free_contact"] = mv_check(tie, [n, n, n])
        out[name] = row
        print(f"  {name} (order {n}): multiplication {short(v)}; commuting pairs {commuting} of {n * n}")
        expect(f"{name}: multiplication relation is a knot", v["knot"], True)
        if "commuting_with_free_contact" in row:
            expect(f"{name}: commuting pairs with a free contact is a knot",
                   row["commuting_with_free_contact"]["knot"], False)
    # D4 and Q8 counts on T^3 and on #3 (S^1 x S^2)
    for name in ("D4 = UT3(F2)", "Q8"):
        els, mul = group(name)
        triples = sum(1 for a in els for b in els if mul(a, b) == mul(b, a)
                      for c in els if mul(a, c) == mul(c, a) and mul(b, c) == mul(c, b))
        out[name]["Hom(Z^3)"] = triples
        expect(f"|Hom(Z^3, {name})| (pairwise commuting triples)", triples, 176)
    F2 = Field(2)
    V3 = vectors(2, 3)
    type3_T3 = Fraction(sum((-1) ** det3(F2, a, b, c) for a in V3 for b in V3 for c in V3), 8)
    expect("type-III sum (1/8) sum (-1)^det over H^1(T^3; F_2)^3 = |Hom(Z^3, D4)| / 8", type3_T3, 22)
    out["type_III"] = {"T3": str(type3_T3), "connected_sum_three_S1xS2": "512/8 = 64 (T = 0)",
                       "type_I_II_on_both": "64: a cup a = 0 for classes that lift to Z"}
    RESULTS["group_laws"] = out


# --------------------------------------------------------------------------- section 8

def toggle(poly: set, mono: frozenset) -> None:
    if mono in poly:
        poly.remove(mono)
    else:
        poly.add(mono)


def gauss_quadratic(n: int, poly: set) -> int:
    """Sum over x in F_2^n of (-1)^P(x) for P of degree <= 2 (monomials as frozensets), in polynomial time."""
    poly = set(poly)
    remaining = set(range(n))
    factor = 1
    while remaining:
        x = min(remaining)
        remaining.discard(x)
        L, R = set(), set()
        for m in poly:
            if x in m:
                toggle(L, m - {x})
            else:
                toggle(R, m)
        if not L:
            factor *= 2
            poly = R
            continue
        if L == {frozenset()}:
            return 0
        y = next(next(iter(m)) for m in sorted(L, key=sorted) if len(m) == 1)
        A = set(L)
        toggle(A, frozenset({y}))  # on L = 0, y = A(others)
        new = set()
        for m in R:
            if y in m:
                rest = m - {y}
                for a in A:
                    toggle(new, a | rest)
            else:
                toggle(new, m)
        poly = new
        remaining.discard(y)
        factor *= 2
    return factor * (-1 if frozenset() in poly else 1)


def brute(n: int, poly: set) -> int:
    total = 0
    for x in range(1 << n):
        value = 0
        for m in poly:
            if all(x >> v & 1 for v in m):
                value ^= 1
        total += -1 if value else 1
    return total


def substitute(poly: set, values: dict) -> set:
    new = set()
    for m in poly:
        if any(v in values and values[v] == 0 for v in m):
            continue
        toggle(new, frozenset(v for v in m if v not in values))
    return new


def hubs_and_signs() -> None:
    print("\n[8] signed counting: pairwise phases are Gauss sums; a bounded hub reduces cubic phases to them")
    rng = random.Random(26)
    checks = {"quadratic": 0, "signed_2cnf": 0, "hub_cubic": 0}
    for _ in range(60):
        n = rng.randint(3, 13)
        poly = set()
        for _ in range(rng.randint(1, 3 * n)):
            toggle(poly, frozenset(rng.sample(range(n), rng.choice((0, 1, 2, 2, 2)))))
        checks["quadratic"] += gauss_quadratic(n, poly) == brute(n, poly)
    for _ in range(60):
        n = rng.randint(3, 13)
        poly = set()
        for _ in range(rng.randint(1, 3 * n)):
            (i, si), (j, sj) = [(v, rng.random() < 0.5) for v in rng.sample(range(n), 2)]
            # clause (l_i or l_j) is violated exactly when both literals are false
            fi = [frozenset(), frozenset({i})] if si else [frozenset({i})]
            fj = [frozenset(), frozenset({j})] if sj else [frozenset({j})]
            for a in fi:
                for b in fj:
                    toggle(poly, a | b)
        checks["signed_2cnf"] += gauss_quadratic(n, poly) == brute(n, poly)
    for _ in range(60):
        n = rng.randint(5, 14)
        hubs = list(range(rng.choice((1, 2))))
        poly = set()
        for _ in range(rng.randint(2, 3 * n)):
            degree = rng.choice((1, 2, 3, 3))
            if degree == 3:
                h = rng.choice(hubs)
                others = rng.sample([v for v in range(n) if v != h], 2)
                toggle(poly, frozenset([h, *others]))
            else:
                toggle(poly, frozenset(rng.sample(range(n), degree)))
        total = 0
        for values in product((0, 1), repeat=len(hubs)):
            reduced = substitute(poly, dict(zip(hubs, values)))
            rest = [v for v in range(n) if v not in hubs]
            relabel = {v: i for i, v in enumerate(rest)}
            total += gauss_quadratic(len(rest), {frozenset(relabel[v] for v in m) for m in reduced})
        checks["hub_cubic"] += total == brute(n, poly)
    expect("random quadratic phases: elimination = brute force (60 cases)", checks["quadratic"], 60)
    expect("random signed 2-CNF, sum of (-1)^(#violated clauses) (60 cases)", checks["signed_2cnf"], 60)
    expect("cubic phases whose cubic terms all touch a hub of 1-2 bits (60 cases)", checks["hub_cubic"], 60)
    # interference marginals of the signed atom, the signed pair and the signed determinant
    atom_marginal = {(x, y): sum((-1) ** (x * y * z) for z in (0, 1)) for x in (0, 1) for y in (0, 1)}
    pair_marginal = {x: sum((-1) ** (x * y) for y in (0, 1)) for x in (0, 1)}
    F2 = Field(2)
    V3 = vectors(2, 3)
    det_marginal = {}
    for a in V3:
        for b in V3:
            det_marginal[(a, b)] = sum((-1) ** det3(F2, a, b, c) for c in V3)
    support = sum(1 for value in det_marginal.values() if value)
    expect("sum over z of (-1)^xyz, at (x, y) = 00, 01, 10, 11",
           [atom_marginal[k] for k in sorted(atom_marginal)], [2, 2, 2, 0])
    expect("sum over y of (-1)^xy, at x = 0, 1", [pair_marginal[0], pair_marginal[1]], [2, 0])
    expect("sum over w of (-1)^det(u, v, w): pairs (u, v) with a nonzero value (= N(det))", support, 22)
    RESULTS["signed"] = {"checks": checks, "atom_marginal": {str(k): v for k, v in atom_marginal.items()},
                         "pair_marginal": pair_marginal, "det_marginal_support": support}


def main() -> int:
    start = time.time()
    validate()
    controls()
    vector_reading()
    bit_reading()
    all_trilinear_forms()
    count_identity()
    potts_gadget()
    group_laws()
    hubs_and_signs()
    RESULTS["failures"] = FAILURES
    RESULTS["seconds"] = round(time.time() - start, 1)
    (HERE / "results.json").write_text(json.dumps(RESULTS, indent=2, sort_keys=True, default=str) + "\n")
    (HERE / "cli_log.txt").write_text("\n\n".join(CLI_LOG) + "\n")
    print(f"\n{len(FAILURES)} mismatches; {RESULTS['seconds']} s")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
