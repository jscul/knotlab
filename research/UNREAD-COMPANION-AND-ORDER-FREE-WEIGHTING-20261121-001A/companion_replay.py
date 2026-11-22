"""Exact five-place source branches and the returned signed measurement."""

import argparse
from collections import defaultdict
from dataclasses import astuple, dataclass, replace
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001A"
sys.path.insert(0, str(PRIOR))
from meter_replay import (
    ALLOWED, Catalogue, IDEAL, IDENTITY_CHANNEL, IX, Mat, S, apply_channel,
    classical_hardware, compose, effect, input_library, local_hardware, zero,
)


BITS = (0, 1)
FIVE_WORDS = tuple("".join(map(str, b)) for b in product(BITS, repeat=5))
LAWS = ("parity", "nae")
SHARED = {"b": 2, "a": 0}


@dataclass(frozen=True)
class Exact:
    """An element of Q(sqrt(5))."""

    rational: F = F(0)
    root: F = F(0)

    @staticmethod
    def get(value):
        return value if isinstance(value, Exact) else Exact(F(value))

    def __bool__(self):
        return bool(self.rational or self.root)

    def __add__(self, other):
        other = self.get(other)
        return Exact(self.rational + other.rational, self.root + other.root)

    __radd__ = __add__

    def __neg__(self):
        return Exact(-self.rational, -self.root)

    def __sub__(self, other):
        return self + -self.get(other)

    def __rsub__(self, other):
        return self.get(other) - self

    def __mul__(self, other):
        other = self.get(other)
        a, b = self.rational, self.root
        c, d = other.rational, other.root
        return Exact(a*c + 5*b*d, a*d + b*c)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.get(other)
        a, b = other.rational, other.root
        n = a*a - 5*b*b
        return self * Exact(a/n, -b/n)

    def pack(self):
        return [str(self.rational), str(self.root)]

    def nonnegative(self):
        a, b = self.rational, self.root
        if a >= 0 and b >= 0:
            return True
        if a <= 0 and b <= 0:
            return False
        return a*a >= 5*b*b if a > 0 else a*a <= 5*b*b


ONE = Exact(F(1))
ETA = Exact(F(3, 2), F(-1, 2))
HERALD_RATE = ETA * F(2, 3)
DIAGONAL_HERALD_RATE = ETA * F(4, 3)


@dataclass(frozen=True)
class Matrix:
    rational: Mat
    root: Mat

    @classmethod
    def from_rational(cls, x):
        return cls(x, zero(len(x.a)))

    def __add__(self, other):
        return Matrix(self.rational + other.rational, self.root + other.root)

    def scale(self, value):
        q = Exact.get(value)
        return Matrix(self.rational.scale(q.rational) + self.root.scale(5*q.root),
                      self.rational.scale(q.root) + self.root.scale(q.rational))

    def trace(self):
        return Exact(self.rational.tr(), self.root.tr())

    def apply(self, state):
        return Matrix(apply_channel(self.rational, state), apply_channel(self.root, state))

    def effect(self):
        return Matrix(effect(self.rational), effect(self.root))

    def after(self, earlier):
        return Matrix(compose(self.rational, earlier.rational) + compose(self.root, earlier.root).scale(5),
                      compose(self.rational, earlier.root) + compose(self.root, earlier.rational))


@cache
def null(n):
    return Matrix.from_rational(zero(n))


IDENTITY = Matrix.from_rational(IDENTITY_CHANNEL)
SIGNED = {t: Matrix.from_rational(mapped) for t, mapped in IDEAL.items()}
TARGET_IDENTITY = Matrix.from_rational(IX)


def law_status(word, shared, laws):
    triples = (word[:3], word[SHARED[shared]] + word[3:])
    return tuple(tri in ALLOWED[law] for tri, law in zip(triples, laws, strict=True))


def source_table(shared, laws):
    checking = {word: law_status(word, shared, laws) for word in FIVE_WORDS}
    allowed = tuple(word for word, checks in checking.items() if all(checks))
    first = tuple(sorted({word[:3] for word in allowed}))
    second = tuple(sorted({word[SHARED[shared]]+word[3:] for word in allowed}))
    assert first == ALLOWED[laws[0]] and second == ALLOWED[laws[1]]
    unread = {d+e: tuple(w[:3] for w in allowed if w[3:] == d+e) for d, e in product("01", repeat=2)}
    conditional = {s: tuple(sorted({w[3:] for w in allowed if w[SHARED[shared]] == s})) for s in "01"}
    count = len(allowed)
    assert count == len(first)*len(conditional["0"]) and len(conditional["0"]) == len(conditional["1"])
    cross = sorted(set(conditional["0"]) & set(conditional["1"]))
    if laws[1] == "parity":
        assert not cross
    else:
        assert cross == ["01", "10"]
    base = sorted({w[:3] for w in FIVE_WORDS})
    matrices = {}
    for coherent in (True, False):
        reduced = [[sum(w in unread[env] and v in unread[env] for env in unread)
                    if coherent or w == v else 0 for v in base] for w in base]
        matrices["coherent" if coherent else "diagonal"] = Mat(reduced, count).dump()
    return {
        "lawfulness_in_order_acb_and_companion": checking, "allowed_acbde": allowed, "normalization": count,
        "first_triple": first, "companion_triple": second, "acb_order": base,
        "unread_decomposition_only": {env: {"acb_support": words, "mass": str(F(len(words), count))}
                                      for env, words in unread.items()},
        "conditional_companion_support_by_shared_value": conditional,
        "common_unread_words": cross,
        "exclusive_unread_words_by_shared_value": {s: [q for q in conditional[s] if q not in cross] for s in "01"},
        "positive_conditional_companion_overlap": str(F(len(cross), len(conditional["0"]))),
        "reduced_acb": matrices,
    }


@dataclass(frozen=True, order=True)
class Held:
    acbde: str
    u: int = 0
    v: int = 0
    tag_a: str = ""
    tag_b: str = ""

    def local(self, side):
        if side == "A":
            return self.acbde[:2], self.u, self.tag_a
        return self.acbde[2], self.v, self.tag_b


def density_terms(density):
    return [[astuple(left), astuple(right), value.pack()] for (left, right), value in sorted(density.items()) if value]


def aggregate_words(density, norm):
    weights = defaultdict(Exact)
    for (left, right), value in density.items():
        if left == right:
            weights[left.acbde] += value
    return {"unconditional": {w: p.pack() for w, p in sorted(weights.items()) if p},
            "conditional": {w: (p/norm).pack() for w, p in sorted(weights.items()) if p} if norm else None}


class Source:
    def __init__(self, shared, laws, coherent, words):
        self.shared, self.laws = shared, laws
        self.coherent = coherent
        self.words = words
        self.paths = {w: {Held(w): ONE} for w in words}
        self.den = ONE
        self.rho = {(Held(w), Held(v)): Exact(F(1, len(words))) for w, v in product(words, repeat=2)
                    if coherent or w == v}
        self.steps = [self.snapshot("supplied full preparation", "preparation")]

    def fork(self):
        copy = object.__new__(Source)
        copy.shared, copy.laws, copy.coherent, copy.words = self.shared, self.laws, self.coherent, self.words
        copy.paths, copy.den, copy.rho = self.paths, self.den, self.rho
        copy.steps = self.steps.copy()
        return copy

    def snapshot(self, name, site):
        total = self.weight()
        assert total.nonnegative()
        assert all(all(law_status(held.acbde, self.shared, self.laws)) for pair in self.rho for held in pair)
        assert all(self.rho.get((right, left)) == q for (left, right), q in self.rho.items())
        return {"primitive": name, "reader": site, "weight": total.pack(),
                "word_weights": aggregate_words(self.rho, total), "full_held_density": density_terms(self.rho)}

    def weight(self):
        return sum((v for (x, y), v in self.rho.items() if x == y), Exact())

    def update(self, name, side, op, squared_denominator=ONE):
        columns = {x: tuple((y, Exact.get(v)) for y, v in op(x) if v)
                   for x in sorted(set().union(*(p.keys() for p in self.paths.values())))}
        remote = "B" if side == "A" else "A"
        for x, responses in columns.items():
            for y, _ in responses:
                assert y.local(remote) == x.local(remote)
                assert y.acbde[3:] == x.acbde[3:]
                assert all(law_status(y.acbde, self.shared, self.laws)), (name, x, y)
        new = defaultdict(Exact)
        for (x, y), old in self.rho.items():
            for (a, u), (b, v) in product(columns[x], columns[y]):
                new[a, b] += old*u*v/squared_denominator
        self.rho = {pair: p for pair, p in new.items() if p}
        all_paths = {}
        for orig, path in self.paths.items():
            next_path = defaultdict(Exact)
            for x, a in path.items():
                for y, b in columns[x]:
                    next_path[y] += a*b
            all_paths[orig] = {x: y for x, y in next_path.items() if y}
        self.paths = all_paths
        self.den *= squared_denominator
        written = self.snapshot(name, side)
        written["nonzero_columns_numerators"] = [[astuple(x), [[astuple(y), a.pack()] for y, a in targets]]
                                                for x, targets in columns.items()]
        written["column_squared_denominator"] = squared_denominator.pack()
        self.steps.append(written)
        return self

    def move(self, name, side, image):
        return self.update(name, side, lambda x: ((image(x), 1),))

    def measure(self, name, side, predicate):
        return self.update(name, side, lambda x: ((x, 1),) if predicate(x) else ())

    def public_value(self, bit):
        index = SHARED[self.shared]
        return self.measure(f"measure the actual accessible {self.shared} place with reported value {bit}",
                            "A" if index == 0 else "B", lambda x: x.acbde[index] == str(bit))

    def accessible_density(self):
        visible = defaultdict(Exact)
        for (x, y), q in self.rho.items():
            if x.acbde[3:] == y.acbde[3:]:
                visible[replace(x, acbde=x.acbde[:3]), replace(y, acbde=y.acbde[:3])] += q
        return visible

    def check_named_preparation(self):
        replayed = defaultdict(Exact)
        for (w, p), (v, q) in product(self.paths.items(), repeat=2):
            if self.coherent or w == v:
                for (x, u), (y, t) in product(p.items(), q.items()):
                    replayed[x,y] += u*t/self.den/len(self.words)
        assert self.rho == {pair: q for pair, q in replayed.items() if q}
        return {w: [[astuple(x), c.pack()] for x, c in sorted(paths.items())] for w, paths in self.paths.items()}


def overwrite(x, pos, b):
    w = x.acbde
    return replace(x, acbde=w[:pos] + str(b) + w[pos+1:])


def c_transfer(x):
    # On arbitrary ancillas this is an invertible local map. On ready u=0
    # it leaves c=1-a and stores the exact old c in u.
    a, c = map(int, x.acbde[:2])
    return replace(overwrite(x, 1, x.u ^ (1-a)), u=c)


def b_transfer(x):
    return replace(overwrite(x, 2, x.v), v=int(x.acbde[2]))


def copy_a_coordinate(x):
    return replace(x, u=x.u ^ int(x.acbde[0] != x.acbde[1]))


def copy_b(x):
    return replace(x, v=x.v ^ int(x.acbde[2]))


def isolated_attempt(shared, laws, words):
    result = {}
    for word in words:
        equal = word[0] == word[1]
        altered = "01" + word[2:] if equal else word
        both = altered[:2] + "0" + altered[3:] if equal else word
        result[word] = {
            "equal_report": equal, "after_hypothetical_A_move": altered,
            "A_move_lawfulness": law_status(altered, shared, laws), "after_hypothetical_B_swap": both,
            "B_swap_lawfulness_if_A_move_had_been_legal": law_status(both, shared, laws),
        }
    assert any(x["equal_report"] and not all(x["A_move_lawfulness"] + x["B_swap_lawfulness_if_A_move_had_been_legal"])
               for x in result.values())
    return result


@cache
def filter_columns():
    """Return C, C inverse, and the numerator of the one failed Kraus."""
    table = {}
    for s in BITS:
        c = tuple(tuple(int((u,v) != (s,s)) for v in BITS) for u in BITS)
        a, b, f, d = c[0][0], c[0][1], c[1][0], c[1][1]
        assert a*d - b*f == -1
        inverse = ((-d, b), (f, -a))
        assert Mat(inverse) @ Mat(c) == Mat([[1, 0], [0, 1]])
        gram = [[sum(inverse[k][i]*inverse[k][j] for k in BITS) for j in BITS] for i in BITS]
        r = tuple(tuple(Exact.get(i == j) - ETA*gram[i][j] for j in BITS) for i in BITS)
        tau = r[0][0] + r[1][1]
        assert tau and tau.nonnegative()
        assert all(sum((r[k][i]*r[k][j] for k in BITS), Exact())/tau + ETA*gram[i][j] == Exact.get(i == j)
                   for i,j in product(BITS, repeat=2))
        table[s] = {"coefficient_matrix": c, "inverse": inverse, "refusal_matrix": r, "refusal_den": tau}
    return table


def copies(trace):
    trace.move("copy local A parity into private work", "A", copy_a_coordinate)
    trace.move("copy B's old bit into private work and keep physical b", "B", copy_b)


def isolate_prefix(trace, attempt):
    records = []
    for status in ("equal", "unequal"):
        branch = trace.fork().measure("report A's " + status + " row test", "A",
                                      lambda x: (x.acbde[0] == x.acbde[1]) == (status == "equal"))
        if status == "equal":
            branch.move("copy a into the private A meter", "A", lambda x: replace(x, u=int(x.acbde[0])))
            safely_move_a = all(all(x["A_move_lawfulness"]) for x in attempt.values() if x["equal_report"])
            if safely_move_a:
                branch.move("accepted first half of the old isolation, move A to 01", "A",
                            lambda x: replace(x, acbde="01" + x.acbde[2:]))
            branch.steps.append(branch.snapshot("refuse the next old extraction step before making an unlawful change", "none"))
        records.append((status, branch, False))
    return records


def retained_equality(trace):
    records = []
    for status in ("equal", "unequal"):
        branch = trace.fork().measure("report A's " + status + " row test", "A",
                                      lambda x: (x.acbde[0] == x.acbde[1]) == (status == "equal"))
        if status == "equal":
            branch.move("save A's original a in a private bit", "A", lambda x: replace(x, u=int(x.acbde[0])))
            if trace.laws[0] == "nae":
                branch.move("move c to a different bit from a and leave a in place", "A",
                            lambda x: overwrite(x, 1, 1-int(x.acbde[0])))
                if trace.shared == "a":
                    branch.move("swap b privately after A's row has become unequal", "B", b_transfer)
                else:
                    branch.move("copy b without disturbing the shared place", "B", copy_b)
                branch.move("complement B's private copy", "B", lambda x: replace(x, v=1-x.v))
            else:
                branch.move("copy the parity-compatible b without changing it", "B", copy_b)
        records.append((status, branch, status == "equal"))
    return records


def balanced(trace, public, tag):
    assert trace.shared == "a" and trace.laws[0] == "nae"
    result = []
    choices = tuple((f"a={s}/", trace.fork().public_value(s)) for s in BITS) if public else (("", trace.fork()),)
    for label, branch in choices:
        if tag in ("word", "shared"):
            branch.move("store an actual local source value in a separate tag", "A",
                        lambda x: replace(x, tag_a=x.acbde[:2] if tag == "word" else x.acbde[0]))
        if tag == "word":
            branch.move("store B's actual old bit in a separate tag", "B", lambda x: replace(x, tag_b=x.acbde[2]))
        branch.move("transfer old c privately and leave c=1-a in a single A gate", "A", c_transfer)
        branch.move("after A reports its readiness, transfer old b privately and leave physical b=0", "B", b_transfer)
        tables = filter_columns()
        denomin = tables[0]["refusal_den"]
        assert denomin == tables[1]["refusal_den"]

        def private_columns(x, success):
            table = tables[int(x.acbde[0])]
            matrix = table["inverse"] if success else table["refusal_matrix"]
            return tuple((replace(x, u=i), matrix[i][x.u]) for i in BITS)

        success = branch.fork().update("A's real balancing filter, success", "A",
                                       lambda x: private_columns(x, True), ONE/ETA)
        denied = branch.fork().update("A's complementary real filter, refusal", "A",
                                      lambda x: private_columns(x, False), denomin)
        result.extend(((label+"success", success, True), (label+"refusal", denied, False)))
    return result


def source_branches(shared, laws, coherent, words, attempt, method, tag):
    init = Source(shared, laws, coherent, words)
    if method == "old_equal_offer":
        return isolate_prefix(init, attempt)
    if method == "preserve_shared_equal":
        return retained_equality(init)
    if method == "private_copy":
        copies(init)
        return [("attempted", init, True)]
    if method == "public_shared_copy":
        out = []
        for s in BITS:
            chosen = init.fork().public_value(s)
            copies(chosen)
            out.append((f"{shared}={s}", chosen, True))
        return out
    assert method in ("balanced_coherent_a", "balanced_public_a")
    return balanced(init, method == "balanced_public_a", tag)


def sum_matrices(items, n):
    return sum(items, null(n))


def signed_permutation(meter_bits, drives):
    columns = []
    for a, b in product(BITS, repeat=2):
        active_a, active_b = (int(flag and bit) for bit, flag in zip(meter_bits, drives, strict=True))
        sign = ((-1) ** a if active_a else 1) * ((-1) ** (1-b) if active_b else 1)
        columns.append((2*(a ^ active_a) + (b ^ active_b), sign))
    return columns


@cache
def target_units(left, right, drives):
    left_cols, right_cols = signed_permutation(left, drives), signed_permutation(right, drives)
    choi = [[0] * 16 for _ in range(16)]
    for i, (a, p) in enumerate(left_cols):
        for j, (b, q) in enumerate(right_cols):
            choi[4*i+a][4*j+b] = p*q
    return Matrix.from_rational(Mat(choi))


def from_coefficients(terms, drives):
    return sum_matrices((target_units(a, b, drives).scale(v) for (a, b), v in terms.items() if v), 16)


def logical_meter(trace):
    state = [[Exact() for _ in range(4)] for _ in range(4)]
    for (x, y), q in trace.rho.items():
        if (x.acbde, x.tag_a, x.tag_b) == (y.acbde, y.tag_a, y.tag_b):
            state[2*x.u+x.v][2*y.u+y.v] += q
    return state


def record_address(address):
    return "".join("-" if side is None else str(side) for side in address)


def meter_terms(trace, received, drives):
    """Contract the analyser amplitudes against the named density terms."""
    denom = 2 ** sum(i is not None for i in received)
    target, words = defaultdict(Exact), defaultdict(lambda: defaultdict(Exact))
    for (x, y), value in trace.rho.items():
        # The original five places survive. Tracing a returned physical
        # register is a summation over matching bras and kets only.
        if (x.acbde, x.tag_a, x.tag_b) != (y.acbde, y.tag_a, y.tag_b):
            continue
        a, b = (x.u, x.v), (y.u, y.v)
        if any(r is None and i != j for r, i, j in zip(received, a, b, strict=True)):
            continue
        exponent = sum(r*(i+j) for r, i, j in zip(received, a, b, strict=True) if r is not None)
        coefficient = value*F((-1) ** exponent, denom)
        words[x.acbde][a, b] += coefficient
        target[a, b] += coefficient
    return from_coefficients(target, drives), {w: from_coefficients(terms, drives) for w, terms in sorted(words.items())}


def adjusted_probability(p, denominator):
    return (p/denominator).pack() if denominator else None


class Evidence:
    def __init__(self):
        self.cat = Catalogue()
        self.maps = {}
        self.inputs = input_library() | {f"mixed_sign_{t}": p.scale(F(1, 2)) for t, p in S.items()}

    def store(self, matrix):
        return [self.cat.put(matrix.rational), self.cat.put(matrix.root)]

    def channel(self, channel):
        ids = self.store(channel)
        key = "/".join(map(str, ids))
        if key not in self.maps:
            r, s = (part.a.reshape(4,4,4,4) for part in (channel.rational, channel.root))
            self.maps[key] = {"choi": ids,
                              "matrix_unit_output_ids_in_row_major_input_order": [
                                  self.store(Matrix(Mat(r[i,:,j,:], channel.rational.d),
                                                    Mat(s[i,:,j,:], channel.root.d)))
                                  for i,j in product(range(4), repeat=2)],
                              "two_local_target_spectator_probe": self.store(channel.scale(F(1,4))),
                              "effect": self.store(channel.effect())}
        return key

    def probe(self, channel, word_channels, weight):
        rows = {}
        for name, state in self.inputs.items():
            data = channel.apply(state)
            p = data.trace()
            assert p.nonnegative()
            raw_word_masses = {w: a.apply(state).trace() for w, a in word_channels.items()}
            assert sum(raw_word_masses.values(), Exact()) == p
            conditional = data.scale(ONE/p) if p else None
            overlaps = {}
            if p:
                for sign, ideal in IDEAL.items():
                    desired = apply_channel(ideal, state)
                    norm = desired.tr()
                    if norm and desired @ desired == desired.scale(norm):
                        value = Exact((conditional.rational @ desired).tr(), (conditional.root @ desired).tr())/norm
                        overlaps[str(sign)] = value.pack()
            rows[name] = {"launch_weight": p.pack(),
                          "weight_given_source_record": adjusted_probability(p, weight),
                          "target_subnormalized": self.store(data),
                          "target_conditional": self.store(conditional) if p else None,
                          "overlap_with_pure_ideal_conditionals": overlaps,
                          "named_five_place_word_weights": {w: m.pack() for w,m in raw_word_masses.items() if m},
                          "named_five_place_conditional_word_weights":
                              {w: (m/p).pack() for w,m in raw_word_masses.items() if m} if p else None}
        return rows

    def run(self, shared, laws, coherent, words, attempt, method, tag="none", fault="intact"):
        records = source_branches(shared, laws, coherent, words, attempt, method, tag)
        # Complete on the entire ready allowed input subspace, not merely
        # trace preserving on the two supplied preparations.
        for w,v in product(words,repeat=2):
            g = sum((n*branch.paths[v].get(out, Exact())/branch.den
                     for _, branch, _ in records for out,n in branch.paths[w].items()), Exact())
            assert g == Exact.get(w == v)

        source, fine, maps = {}, {}, {}
        for herald, trace, offer in records:
            w = trace.weight()
            basis = trace.check_named_preparation()
            a = fault != "A_idle" and offer
            b = offer
            analyzer = a,b
            drive = a,b and fault != "B_control_disconnected"
            addresses = product(*(BITS if active else (None,) for active in analyzer))
            no_copy_access = trace.accessible_density()
            meter = logical_meter(trace)
            source[herald] = {
                "launch_weight": w.pack(), "target_offer": offer, "steps": trace.steps,
                "final_source_and_work_after_tracing_de": density_terms(no_copy_access),
                "remaining_meter_word_order": ["00","01","10","11"],
                "remaining_meter": [[v.pack() for v in row] for row in meter],
                "paths_from_each_named_original_word": basis, "path_squared_denominator": trace.den.pack(),
            }
            branch_effects = []
            for flag in addresses:
                channel, word_maps = meter_terms(trace, flag, drive)
                if not offer:
                    assert channel == IDENTITY.scale(w)
                branch_effects.append(channel.effect())
                sign = (-1) ** sum(flag) if None not in flag else None
                key = herald + ":" + record_address(flag)
                maps[key] = channel
                fine[key] = {"source_record": herald, "local_analyzer_flags": flag, "local_control_offered": drive,
                             "joined_sign_if_both_messages_arrive": sign,
                             "forced_ready_bank_after_refusal": ("blank", "blank") if not offer else None,
                             "writer_lookup_addresses": tuple("ab"[v] if v is not None else "idle_a_or_b" for v in flag)
                                 if offer else ("blank", "blank"),
                             "channel": self.channel(channel),
                             "channel_at_each_surviving_five_place_word": {w: self.channel(x) for w,x in word_maps.items()},
                             "probe_results": self.probe(channel, word_maps, w)}
                if not offer:
                    assert flag == (None, None)
            assert sum_matrices(branch_effects, 4) == TARGET_IDENTITY.scale(w)
        effect_total = sum_matrices((channel.effect() for channel in maps.values()), 4)
        assert effect_total == TARGET_IDENTITY
        coarse = {s: sum_matrices((maps[k] for k, row in fine.items() if row["joined_sign_if_both_messages_arrive"] == s),16)
                  for s in (1,-1)}
        paid = sum((trace.weight() for _,trace,offer in records if offer), Exact())
        early_refusal = sum_matrices((maps[k] for k,r in fine.items() if not source[r["source_record"]]["target_offer"]),16)
        assert early_refusal == IDENTITY.scale(ONE-paid)

        is_balanced = method.startswith("balanced")
        expected_clean = is_balanced and coherent and tag != "word" and fault == "intact"
        if is_balanced:
            assert paid == (HERALD_RATE if coherent and tag != "word" else DIAGONAL_HERALD_RATE)
        if expected_clean:
            assert all(coarse[t] == SIGNED[t].scale(paid) for t in (1,-1))
            for name, row in fine.items():
                if row["joined_sign_if_both_messages_arrive"] is not None:
                    p = sum((branch.weight() for record,branch,_ in records if record == row["source_record"]), Exact())
                    assert maps[name] == SIGNED[row["joined_sign_if_both_messages_arrive"]].scale(p/2)
        else:
            assert not paid or any(coarse[t] != SIGNED[t].scale(paid) for t in (1,-1))
        matching_effects = all(coarse[t].effect() == SIGNED[t].effect().scale(paid) for t in (1, -1))
        return {
            "shared": shared, "ordered_laws": laws, "preparation": "coherent" if coherent else "diagonal",
            "method": method, "tag": tag, "separate_fault_setting": fault,
            "effect_total": self.store(effect_total), "source_records": source,
            "before_coupling_herald_gram_identity": True, "offered_analyzer_weight": paid.pack(),
            "successful_exact_meter": bool(expected_clean), "all_fine_records": fine,
            "sign_frequencies_match_all_inputs_when_both_records_arrive": matching_effects if paid else None,
            "refused_before_target_coupling": self.channel(early_refusal),
            "joined_maps_per_full_launch": {str(t): self.channel(ch) for t,ch in coarse.items()},
            "joined_maps_given_target_offer": {str(t): self.channel(ch.scale(ONE/paid)) if paid else None
                                               for t,ch in coarse.items()},
        }, maps


def word_replay(evidence):
    configurations, controls, maps, examples = {}, {}, {}, {}
    base = ("old_equal_offer", "preserve_shared_equal", "private_copy", "public_shared_copy")
    for shared, first, companion in product(SHARED, LAWS, LAWS):
        laws = first, companion
        key = f"s={shared}/{first}-{companion}"
        conf = source_table(shared, laws)
        allowed = conf["allowed_acbde"]
        attempt = isolated_attempt(shared, laws, allowed)
        conf["old_equal_knot_offer_each_basis_input"] = attempt
        configurations[key] = conf
        for coherent in (True,False):
            weighting = "coherent" if coherent else "diagonal"
            methods = [(m, "none", "intact") for m in base]
            if shared == "a" and first == "nae":
                methods.extend((m, "none", "intact") for m in ("balanced_public_a", "balanced_coherent_a"))
                if coherent:
                    methods.extend((m,tag,"intact") for m,tag in
                                   (("balanced_public_a","word"),("balanced_coherent_a","word"),("balanced_coherent_a","shared")))
                    methods.extend(("balanced_public_a","none",fault) for fault in ("A_idle","B_control_disconnected"))
            for method, tag, fault in methods:
                case = "/".join((key,weighting,method,tag,fault))
                controls[case], maps[case] = evidence.run(shared,laws,coherent,allowed,attempt,method,tag,fault)
            # Complete lawful failed attempt in every cell. The 00 result
            # shows why the meter output is distinct from either ideal sign.
            pick = "private_copy" if first == "parity" else "preserve_shared_equal"
            case = f"{key}/{weighting}/{pick}/none/intact"
            records = controls[case]["all_fine_records"]
            good = next(r for r in records.values() if r["local_analyzer_flags"] == (0,0))
            probe = good["probe_results"]["00"]
            half = Mat([[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,1]],2)
            assert probe["target_conditional"] == evidence.store(Matrix.from_rational(half))
            assert probe["overlap_with_pure_ideal_conditionals"]["1"] == ["1/2","0"]
            examples[f"{key}/{weighting}"] = {"case": case, "readout_record": good["source_record"],
                                               "local_analyzer_flags": [0,0], "00": probe}
    return configurations, controls, maps, examples


def fresh_repeats(evidence, cases, exact):
    result = {}
    for name, case in cases.items():
        if not case["successful_exact_meter"]:
            continue
        channels = exact[name]
        weights = case["offered_analyzer_weight"]
        p = Exact(F(weights[0]),F(weights[1]))
        registry = case["all_fine_records"]
        collected = {}
        effect_sum = null(4)
        signed_pairs = defaultdict(lambda: null(16))
        for (name_a, first),(name_b, second) in product(channels.items(), repeat=2):
            composed = second.after(first)
            effect_sum += composed.effect()
            sign_a = registry[name_a]["joined_sign_if_both_messages_arrive"]
            sign_b = registry[name_b]["joined_sign_if_both_messages_arrive"]
            if sign_a is not None and sign_b is not None:
                signed_pairs[sign_a,sign_b] += composed
            collected[name_a+" | "+name_b] = {
                "channel": evidence.channel(composed),
                "probe_weights": {probe: composed.apply(state).trace().pack()
                                  for probe,state in evidence.inputs.items()
                                  if probe in ("00","1/u+v","1/u-v","-1/u+v","-1/u-v")},
            }
        assert effect_sum == TARGET_IDENTITY
        for s,t in product((1,-1),repeat=2):
            expected = SIGNED[s].scale(p*p) if s == t else null(16)
            assert signed_pairs[s,t] == expected
        result[name] = {"distinct_source_and_writer_banks_each_launch": True,
                        "both_launches_full_records": collected,
                        "both_accepted_sign_maps": {f"{s}/{t}": evidence.channel(x) for (s,t),x in signed_pairs.items()},
                        "effect_total": evidence.store(effect_sum)}
    return result


def check_reduced(configurations, cases):
    # Independent equality of the traced basis enumeration and state sum
    # at the prepared full source, for every original population.
    for case in cases.values():
        key = f"s={case['shared']}/{'-'.join(case['ordered_laws'])}"
        table = configurations[key]
        state = next(iter(case["source_records"].values()))["steps"][0]["full_held_density"]
        raw = defaultdict(F)
        for x,y,q in state:
            if x[0][3:] == y[0][3:]:
                assert q[1] == "0"
                raw[x[0][:3],y[0][:3]] += F(q[0])
        computed = [[raw[x,y] for y in table["acb_order"]] for x in table["acb_order"]]
        m = table["reduced_acb"][case["preparation"]]
        assert computed == [[F(q,m["den"]) for q in row] for row in m["rows"]]
        if case["successful_exact_meter"]:
            for branch in case["source_records"].values():
                if branch["target_offer"]:
                    trace = branch["remaining_meter"]
                    w = Exact(*(F(x) for x in branch["launch_weight"]))/2
                    assert trace == [[(w if a in (0,3) and b in (0,3) else Exact()).pack()
                                      for b in range(4)] for a in range(4)]


def build():
    evidence = Evidence()
    configurations, cases, exact, examples = word_replay(evidence)
    check_reduced(configurations, cases)
    repeats = fresh_repeats(evidence,cases,exact)
    gates, analyzers, writers, fresh_transfers, refusals = local_hardware()
    joined = classical_hardware(writers)
    ranges = joined["combined_keeper_branches"]
    assert ranges["a/00/b/11/11/0"]["local_keepers"] == ("110","011")
    assert ranges["a/00/b/11/11/0"]["joined_keeper"] == "011"
    assert ranges["a/11/b/11/01/0"]["joined_keeper"] == "110"
    older_meter = HERE.parent/"TWO-READERS-ONE-SURVIVING-SIGN-20261121-001A"
    older_pointer = HERE.parent/"TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001B"
    lineage = (Path(__file__).resolve(), HERE/"preregistration.md", PRIOR/"meter_replay.py",
               older_meter/"instrument_hardware.py", older_meter/"instrument_math.py",
               older_pointer/"pointer_hardware.py", older_pointer/"real_algebra.py")
    filt = {str(s): {"C": table["coefficient_matrix"], "inverse": table["inverse"],
                     "success_squared_amplitude_multiplier": ETA.pack(),
                     "refusal_numerator": [[a.pack() for a in r] for r in table["refusal_matrix"]],
                     "refusal_squared_denominator": table["refusal_den"].pack()}
            for s,table in filter_columns().items()}
    return {
        "scope": "Bounded exact replay under the frozen serial access. Unread decompositions are mathematical and never used for a protocol control.",
        "coefficient_encoding": "For field values [r,s] means r+s sqrt(5). A pair of matrix identifiers denotes the rational and sqrt(5) parts.",
        "lawful_word_order": "acbde", "readers": {"A": "ac", "B": "b", "unread": "de"},
        "held_register_order": ["acbde","first_private_meter_bit","second_private_meter_bit","first_held_tag","second_held_tag"],
        "source_populations_in_testing_order": list(configurations),
        "source_populations": configurations,
        "private_balance_filter": filt,
        "inputs": {k:evidence.cat.put(v) for k,v in evidence.inputs.items()},
        "instrument_settings": cases,
        "explicit_00_nonselected_or_disturbed_control_for_every_population": examples,
        "fresh_independent_meter_repeat": repeats,
        "ordinary_hardware": {
            "calibration": "Actual inherited law-checked B294 controlled gate paths, binary analyzers, and ordinary keeper writers.",
            "target_gates": gates, "analyzers": analyzers, "writers": writers,
            "fresh_transfers": fresh_transfers, "source_refusal_leaves_target_and_both_keepers_untouched": refusals,
            "collector_and_disconnection_controls": joined,
            "full_join_index_recipe": "Use the two fine analyzer addresses and each actual writer connection independently. A missing message changes only the joined keeper. An idle bank retains the actual meter input address or ready blank at source refusal.",
        },
        "exact_post_analyzer_full_state_recipe": "Take the final full_held_density for that source record. For each named pair of held bytes apply the local signed data permutation selected by its private meter bits on its own side. The measured bit i in port k contributes (-1)^(ik)/sqrt(2) to that side of the block. Replace only the measured meter coordinate with its physical port. Optional writers act only on the two separate ordinary keeper states. This specifies also the off-diagonal blocks before tracing the returned apparatus.",
        "maps_by_reference": evidence.maps, "matrix_catalogue": evidence.cat.matrices,
        "summary": {"source_populations": len(configurations), "allowed_word_candidates": len(configurations)*len(FIVE_WORDS),
                    "instrument_settings":len(cases), "source_records": sum(len(x["source_records"]) for x in cases.values()),
                    "fine_single_records": sum(len(x["all_fine_records"]) for x in cases.values()),
                    "fresh_two_launch_records":sum(len(x["both_launches_full_records"]) for x in repeats.values()),
                    "ordinary_writer_and_message_settings":len(ranges)},
        "source_sha256": {str(p.relative_to(HERE.parents[1])): sha256(p.read_bytes()).hexdigest() for p in lineage},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="check a byte-identical regenerated archive")
    args = parser.parse_args()
    result = build()
    payload = (json.dumps(result,sort_keys=True,separators=(",",":"))+"\n").encode()
    compressed = gzip.compress(payload,mtime=0)
    path = HERE/"companion_evidence.json.gz"
    if args.verify:
        assert compressed == path.read_bytes()
    else:
        path.write_bytes(compressed)
    assert gzip.decompress(path.read_bytes()) == payload
    print(json.dumps(result["summary"],sort_keys=True))
    print("sha256",sha256(compressed).hexdigest(),"bytes",len(compressed))


if __name__ == "__main__":
    main()
