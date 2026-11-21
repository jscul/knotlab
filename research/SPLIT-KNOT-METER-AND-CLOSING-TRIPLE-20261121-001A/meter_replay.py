"""Replay the named split source, exact target maps, and ordinary keepers."""

import argparse
from collections import defaultdict
from dataclasses import astuple, dataclass, replace
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from math import lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "TWO-READERS-ONE-SURVIVING-SIGN-20261121-001A"
sys.path.insert(0, str(PRIOR))
import instrument_hardware as hardware
from coherent_meter import branches, joint_controls, maps
from instrument_math import (
    BELL_PHASE, IDEAL, IDENTITY_CHANNEL, I, IX, J, M, MEASX, S, UNITS,
    Catalogue, Mat, add, apply_channel, choi, compose, effect, input_library,
    kraus_map, proportional, tensor, zero,
)


BITS = (0, 1)
WORDS = tuple("".join(map(str, word)) for word in product(BITS, repeat=3))
ALLOWED = {
    "parity": tuple(word for word in WORDS if word.count("1") % 2 == 0),
    "nae": tuple(word for word in WORDS if word not in ("000", "111")),
}
ROWS = ("00", "01", "10", "11")
SETTINGS = ("coherent", "diagonal", "dephase_between_b")
ADDRESSES = "ab"


@dataclass(frozen=True, order=True)
class Held:
    physical_acb: str
    meter_a: int = 0
    meter_b: int = 0
    saved_a: str = "00"
    tag_a: str = "00"
    tag_b: int = 0

    def local(self, side):
        if side == "A":
            return self.physical_acb[:2], self.meter_a, self.saved_a, self.tag_a
        return self.physical_acb[2], self.meter_b, self.tag_b


def unique(column, gain=1):
    return ((column, gain),)


def exclusive(left, right):
    return "".join(str(int(a != b)) for a, b in zip(left, right, strict=True))


def diagonal_summary(density, group, total=None):
    counts = defaultdict(F)
    for (x, y), value in density.items():
        if x == y:
            counts[group(x)] += value
    if total is None:
        total = sum(counts.values(), F(0))
    return {
        "unconditional": {k: str(v) for k, v in sorted(counts.items()) if v},
        "conditional": {k: str(v / total) for k, v in sorted(counts.items()) if v} if total else None,
    }


class SourceTrace:
    """Integer Kraus columns on reachable full words and exact squared denominators."""

    def __init__(self, law, weighting):
        self.law = law
        self.weighting = weighting
        self.paths = {word: {Held(word): 1} for word in ALLOWED[law]}
        self.squared_denominator = F(1)
        self.steps = [self.snapshot("supplied preparation", "source")]

    def fork(self):
        other = object.__new__(SourceTrace)
        other.law, other.weighting = self.law, self.weighting
        other.paths = self.paths
        other.squared_denominator = self.squared_denominator
        other.steps = self.steps.copy()
        return other

    def has_cross_word_coherence(self, left, right):
        if self.weighting == "coherent":
            return True
        if self.weighting == "diagonal":
            return left == right
        assert self.weighting == "dephase_between_b"
        return left[2] == right[2]

    def density(self):
        n = len(self.paths) * self.squared_denominator
        terms = defaultdict(F)
        for (left, a), (right, b) in product(self.paths.items(), repeat=2):
            if self.has_cross_word_coherence(left, right):
                for (x, u), (y, v) in product(a.items(), b.items()):
                    terms[x, y] += F(u * v) / n
        return {k: value for k, value in terms.items() if value}

    def density_given_basis_input(self, original):
        paths = self.paths[original]
        return {(x, y): F(u * v) / self.squared_denominator
                for (x, u), (y, v) in product(paths.items(), repeat=2)}

    def snapshot(self, name, site):
        rho = self.density()
        law = ALLOWED[self.law]
        assert all(x.physical_acb in law and y.physical_acb in law for x, y in rho)
        assert all(rho.get((y, x)) == value for (x, y), value in rho.items())
        weight = sum((value for (x, y), value in rho.items() if x == y), F(0))
        return {
            "primitive": name,
            "sites": site,
            "weight_per_launch": str(weight),
            "named_physical_words": diagonal_summary(rho, lambda k: k.physical_acb, weight),
            "basis_paths_by_original_acb": {
                word: [[astuple(state), coef] for state, coef in sorted(terms.items())]
                for word, terms in self.paths.items()
            },
            "common_squared_path_denominator": str(self.squared_denominator),
            "density_terms": [[astuple(x), astuple(y), str(v)] for (x, y), v in sorted(rho.items())],
        }

    def step(self, name, site, operation, squared_denominator=1):
        old = sorted(set().union(*(terms.keys() for terms in self.paths.values())))
        columns = {x: tuple((y, n) for y, n in operation(x) if n) for x in old}
        for x, outputs in columns.items():
            for y, _ in outputs:
                assert y.physical_acb in ALLOWED[self.law], (name, x, y)
                if site in ("A", "B"):
                    remote = "B" if site == "A" else "A"
                    assert x.local(remote) == y.local(remote), (name, x, y)
                else:
                    assert site == "A and B at one atomic event"
        paths = {}
        for original, source in self.paths.items():
            combined = defaultdict(int)
            for x, amplitude in source.items():
                for y, coefficient in columns[x]:
                    combined[y] += amplitude * coefficient
            paths[original] = {y: n for y, n in combined.items() if n}
        self.paths = paths
        self.squared_denominator *= squared_denominator
        row = self.snapshot(name, site)
        row["primitive_squared_denominator"] = str(squared_denominator)
        row["reachable_nonzero_word_columns"] = [
            [astuple(x), [[astuple(y), n] for y, n in targets]]
            for x, targets in columns.items()
        ]
        self.steps.append(row)
        return self

    def deterministic(self, name, site, image):
        return self.step(name, site, lambda x: unique(image(x)))

    def select(self, name, site, predicate):
        return self.step(name, site, lambda x: unique(x) if predicate(x) else ())


def a_parity(x):
    return int(x.physical_acb[0] != x.physical_acb[1])


def copy_a_parity(x):
    return replace(x, meter_a=x.meter_a ^ a_parity(x))


def copy_b(x):
    return replace(x, meter_b=x.meter_b ^ int(x.physical_acb[2]))


def clear_a(x):
    a, c, b = x.physical_acb
    return replace(x, physical_acb=a + str(int(c) ^ x.meter_a) + b)


def clear_b(x):
    a, c, b = x.physical_acb
    return replace(x, physical_acb=a + c + str(int(b) ^ x.meter_b))


def swap_b(x):
    return replace(x, meter_b=int(x.physical_acb[2]),
                   physical_acb=x.physical_acb[:2] + str(x.meter_b))


def copy_equal_row(x):
    return replace(x, meter_a=x.meter_a ^ int(x.physical_acb[:2] == "11"))


def clear_equal_row(x):
    return replace(x, physical_acb=exclusive(x.physical_acb[:2], str(x.meter_a) + str(1-x.meter_a))
                   + x.physical_acb[2])


def save_a_row(x):
    return replace(x, saved_a=exclusive(x.saved_a, x.physical_acb[:2]))


def clear_saved_a(x):
    swap_mask = exclusive(x.saved_a, "01")
    return replace(x, physical_acb=exclusive(x.physical_acb[:2], swap_mask) + x.physical_acb[2])


def copy_tag_a(x):
    return replace(x, tag_a=exclusive(x.tag_a, x.physical_acb[:2]))


def transfer_redundant_a(x):
    a, c, b = x.physical_acb
    ready_value = x.saved_a[0]
    next_c = exclusive(c, exclusive(a, ready_value))
    return replace(x, physical_acb=ready_value + next_c + b, saved_a=a + x.saved_a[1])


def local_permutation_audit(law, name, ancilla, forward, backward):
    full = tuple(replace(Held(word), **{name: value}) for word, value in product(WORDS, ancilla))
    assert {forward(x) for x in full} == set(full)
    assert all(backward(forward(x)) == x and forward(backward(x)) == x for x in full)
    conditions = {
        "every_clean_original_word": lambda x: getattr(x, name) == ancilla[0],
        "all_ancillary_inputs": lambda x: True,
    }
    return {
        scope: {
            direction: [[astuple(x), astuple(op(x)), op(x).physical_acb in ALLOWED[law]]
                        for x in full if x.physical_acb in ALLOWED[law] and condition(x)]
            for direction, op in (("forward", forward), ("inverse", backward))
        }
        for scope, condition in conditions.items()
    }


def legality_table():
    truths = {}
    for law, words in ALLOWED.items():
        rows = {}
        for word in words:
            both = copy_b(copy_a_parity(Held(word)))
            outputs = (clear_a(both), clear_b(both), clear_b(clear_a(both)))
            rows[word] = {
                "both_coherent_copies": astuple(both),
                "A_only_B_only_atomic_physical_outputs": [x.physical_acb for x in outputs],
                "lawful_A_only_B_only_atomic": [x.physical_acb in words for x in outputs],
            }
        permits_b = {a: [b for b in "01" if a + b in words] for a in ROWS}
        permits_a = {b: [a for a in ROWS if a + b in words] for b in "01"}
        truths[law] = {"parity_offer_on_each_initial_source_word": rows,
                       "remote_b_given_ac": permits_b, "remote_ac_given_b": permits_a}

    assert [sum(x["lawful_A_only_B_only_atomic"][i] for x in
                truths["parity"]["parity_offer_on_each_initial_source_word"].values())
            for i in range(3)] == [2, 2, 4]
    assert [sum(x["lawful_A_only_B_only_atomic"][i] for x in
                truths["nae"]["parity_offer_on_each_initial_source_word"].values())
            for i in range(3)] == [4, 5, 3]
    for law in ALLOWED:
        truths[law]["permutations_on_ready_and_arbitrary_ancilla"] = {
            "copy_A_parity_and_clear": local_permutation_audit(
                law, "meter_a", BITS, lambda x: clear_a(copy_a_parity(x)), lambda x: copy_a_parity(clear_a(x))),
            "copy_B_and_clear": local_permutation_audit(
                law, "meter_b", BITS, lambda x: clear_b(copy_b(x)), lambda x: copy_b(clear_b(x))),
            "B_swap_with_clean_or_dirty_meter": local_permutation_audit(law, "meter_b", BITS, swap_b, swap_b),
            "A_equal_row_copy_and_move": local_permutation_audit(
                law, "meter_a", BITS,
                lambda x: clear_equal_row(copy_equal_row(x)), lambda x: copy_equal_row(clear_equal_row(x))),
            "A_save_whole_row_and_clear": local_permutation_audit(
                law, "saved_a", ROWS,
                lambda x: clear_saved_a(save_a_row(x)), lambda x: save_a_row(clear_saved_a(x))),
            "A_transfer_redundant_bit_preserving_ac_parity": local_permutation_audit(
                law, "saved_a", ROWS, transfer_redundant_a, transfer_redundant_a),
        }
    serialized = {}
    for word in ALLOWED["nae"]:
        a, c, b = word
        serialized[word] = {"a_first": "0" + c + b, "c_first": a + "1" + b}
        serialized[word].update({k + "_lawful": v in ALLOWED["nae"] for k, v in tuple(serialized[word].items())})
    assert not serialized["100"]["a_first_lawful"] and not serialized["101"]["c_first_lawful"]
    truths["nae"]["hypothetical_serialized_clear_whole_A"] = serialized
    return truths


def preparation(family, weighting, *, tag="none", phases=()):
    law = "parity" if family.startswith("parity") else "nae"
    trace = SourceTrace(law, weighting)
    if family in ("parity_serial_refused", "parity_missing_A", "parity_missing_B", "nae_atomic_refused"):
        trace.steps.append(trace.snapshot("withhold the extraction, coupling and keeper offers", "none"))
        return [("source_refused", trace, False)]

    if tag != "none":
        if law == "parity":
            trace.deterministic("copy the actual source b to a retained tag", "B",
                                lambda x: replace(x, tag_b=x.tag_b ^ int(x.physical_acb[2])))
        else:
            trace.deterministic("copy the actual old A row to a retained tag", "A", copy_tag_a)

    if family in ("parity_atomic", "parity_copied", "parity_lawful_A_transfer"):
        trace.deterministic("copy ac parity into a clean private bit, preserving both physical places",
                            "A", copy_a_parity)
        trace.deterministic("copy b into a clean private bit, preserving physical b", "B", copy_b)
        if family == "parity_atomic":
            trace.deterministic("clear the two physical values together from the private copies",
                                "A and B at one atomic event", lambda x: clear_b(clear_a(x)))
        elif family == "parity_lawful_A_transfer":
            trace.deterministic("transfer A's redundant coordinate and preserve the A parity fiber", "A",
                                transfer_redundant_a)
        else:
            trace.steps.append(trace.snapshot("keep the old physical word after the local clear is refused", "none"))
        if tag == "uncomputed":
            trace.deterministic("return the tag by controlled reversal from the unchanged meter bit",
                                "B", lambda x: replace(x, tag_b=x.tag_b ^ x.meter_b))
        result = [("accepted", trace, True)]
    elif family == "parity_conditioned":
        result = []
        for bit in BITS:
            chosen = trace.fork().select(f"read the actual local parity fiber {bit}", "A",
                                         lambda x: a_parity(x) == bit)
            announced = "11" if bit == 0 else "00"
            chosen.deterministic("conditioned local change after A reports its measured fiber",
                                 "A", lambda x: replace(x, physical_acb=exclusive(x.physical_acb[:2], announced)
                                                       + x.physical_acb[2]))
            chosen.deterministic("copy the surviving A fiber", "A", copy_a_parity)
            chosen.deterministic("copy the surviving b", "B", copy_b)
            result.append((f"reported_fiber_{bit}", chosen, True))
    elif family in ("nae_equal", "nae_equal_merged"):
        equal = lambda x: not a_parity(x)
        failure = trace.fork().select("reported unequal row, retain the entire source", "A", lambda x: not equal(x))
        good = trace.fork()
        if family == "nae_equal_merged":
            good.step("one equal-row Kraus, no record of which equal row", "A",
                      lambda x: unique(clear_equal_row(copy_equal_row(x))) if equal(x) else ())
        else:
            good.select("one equal-row herald, no record of which equal row", "A", equal)
            good.deterministic("store the first A bit in the equal fiber", "A", copy_equal_row)
            good.deterministic("move the accepted physical A row to 01", "A", clear_equal_row)
        good.deterministic("B swaps its physical bit with the clean meter bit", "B", swap_b)
        good.deterministic("B complements its private copy of old b", "B",
                           lambda x: replace(x, meter_b=1 - x.meter_b))
        if tag == "uncomputed":
            good.deterministic("return the old A tag using its still-held equal-row bit", "A",
                               lambda x: replace(x, tag_a=exclusive(x.tag_a, "11" if x.meter_a else "00")))
        result = [("equal", good, True), ("unequal", failure, False)]
    elif family == "nae_whole_a":
        trace.deterministic("store the whole A row and clear the two A places to 01 in one local gate", "A",
                            lambda x: clear_saved_a(save_a_row(x)))
        result = []
        for name, matrix, denominator in whole_a_filter_rows():
            def operation(x):
                col = ROWS.index(x.saved_a)
                return tuple((replace(x, saved_a="00", meter_a=i), row[col]) for i, row in enumerate(matrix))

            chosen = trace.fork().step("private filter " + name, "A", operation, denominator)
            if name == "success":
                chosen.deterministic("B swaps into its clean meter after the herald", "B", swap_b)
            result.append((name, chosen, name == "success"))
    else:
        raise ValueError(family)

    if tag == "read":
        result = [(f"{name}/old_A_row={row}", branch.fork().select("read the actual old A tag", "A",
                                                                  lambda x: x.tag_a == row), accepted)
                  for name, branch, accepted in result for row in ROWS]
        assert law == "nae"
    for _, branch, accepted in result:
        if accepted:
            for site in phases:
                control = (lambda x: x.meter_a) if site == "A" else (lambda x: x.meter_b)
                branch.step("local calibrated meter phase", site, lambda x: unique(x, (-1) ** control(x)))
    return result


@cache
def whole_a_filter_rows():
    source = Mat([[int(a + b in ALLOWED["nae"]) for b in "01"] for a in ROWS])
    assert source.T @ source == Mat([[3, 2], [2, 3]])
    rows = (
        ("success", ((-2, 1, 1, 3), (3, 1, 1, -2)), F(25)),
        ("failure_plus", ((1, 2, 2, 1),), F(25, 2)),
        ("failure_perpendicular_1", ((0, 1, -1, 0),), F(2)),
        ("failure_perpendicular_2", ((2, -1, -1, 2),), F(10)),
    )
    assert Mat(rows[0][1], 5) @ source == I
    assert add([(Mat(m).T @ Mat(m)).scale(1 / q) for _, m, q in rows], 4) == IX
    return rows


def instrument_columns(drives, analyzers, rho):
    """Resolve the local X addresses and retain all remaining register blocks."""
    gate_a, gate_b = drives
    arms = {ij: tensor(J if gate_a and ij[0] else I, J.scale(-1) if gate_b and ij[1] else I)
            for ij in product(BITS, repeat=2)}
    pairs = {(r, s): choi([a @ unit @ b.T for unit in UNITS])
             for (r, a), (s, b) in product(arms.items(), repeat=2)}
    denomin = 2 ** sum(analyzers)
    for address in product(*(BITS if measured else (None,) for measured in analyzers)):
        phases = [lambda input_bit, outcome=outcome: 1 if outcome is None else (-1) ** (outcome * input_bit)
                  for outcome in address]

        def returned(row):
            return replace(row, meter_a=row.meter_a if address[0] is None else address[0],
                           meter_b=row.meter_b if address[1] is None else address[1])

        observed = {}
        for (x, y), coeff in rho.items():
            left, right = (x.meter_a, x.meter_b), (y.meter_a, y.meter_b)
            weight = coeff * phases[0](left[0]) * phases[0](right[0]) * phases[1](left[1]) * phases[1](right[1])
            key = returned(x), returned(y)
            observed[key] = observed.get(key, zero(16)) + pairs[left, right].scale(weight / denomin)
        observed = {key: ch for key, ch in observed.items() if ch != zero(16)}
        yield address, observed


def read_meter(rho, drives, analyzers, target_channels):
    matrix = np.full((4, 4), F(0), dtype=object)
    for (x, y), coeff in rho.items():
        residual = lambda s: (s.physical_acb, s.saved_a, s.tag_a, s.tag_b)
        if residual(x) == residual(y):
            matrix[2*x.meter_a + x.meter_b, 2*y.meter_a + y.meter_b] += coeff
    d = lcm(*(x.denominator for x in matrix.flat))
    meter = Mat(matrix * d, d)
    gate_a = J if drives[0] else I
    gate_b = J.scale(-1) if drives[1] else I
    tested = maps(branches(joint_controls(gate_a, gate_b),
                          MEASX if analyzers[0] else (I,), MEASX if analyzers[1] else (I,)), meter)
    for address, observed in target_channels.items():
        assert tested[tuple(a if a is not None else 0 for a in address)] == observed
    return meter


def masked_tag_blocks(joint, tag):
    masked = {}
    for (x, y), ch in joint.items():
        if getattr(x, tag) == getattr(y, tag):
            blank = "00" if tag == "tag_a" else 0
            key = replace(x, **{tag: blank}), replace(y, **{tag: blank})
            masked[key] = masked.get(key, zero(16)) + ch
    return {key: ch for key, ch in masked.items() if ch != zero(16)}


def port_key(address):
    return "".join("-" if a is None else str(a) for a in address)


def sign_of(address):
    return (-1) ** sum(address) if None not in address else None


def trace_registers(blocks):
    return add([part for (x, y), part in blocks.items() if x == y], 16)


def writer_address(state, address, accepted):
    if not accepted:
        return ("blank", "blank")
    raw = (state.meter_a, state.meter_b)
    return tuple(ADDRESSES[i] if a is not None else "idle_" + ADDRESSES[i]
                 for i, a in zip(raw, address, strict=True))


class Evidence:
    def __init__(self):
        self.cat = Catalogue()
        self.channels = {}
        self.probes = input_library() | {f"opposite_sign_mixture_{s}": S[s].scale(F(1, 2)) for s in (1, -1)}

    def channel(self, channel):
        pointer = self.cat.put(channel)
        if pointer not in self.channels:
            matrix = channel.a.reshape(4, 4, 4, 4)
            self.channels[pointer] = {
                "choi": pointer,
                "local_spectator_pair_at_each_reader": self.cat.put(channel.scale(F(1, 4))),
                "unit_outputs_00_01_02_03_10_11_12_13_20_21_22_23_30_31_32_33": [
                    self.cat.put(Mat(matrix[i, :, j, :], channel.d)) for i, j in product(range(4), repeat=2)
                ],
                "effect": self.cat.put(effect(channel)),
                "constant_times_sign_projection": {str(s): proportional(channel, t) for s, t in IDEAL.items()},
            }
        return pointer

    def block_table(self, joint, address, accepted):
        return [
            {"left": astuple(x), "right": astuple(y), "choi": self.cat.put(ch),
             "left_ordinary_record_addresses": writer_address(x, address, accepted),
             "right_ordinary_record_addresses": writer_address(y, address, accepted)}
            for (x, y), ch in sorted(joint.items())
        ]

    def probe_row(self, joint, channel):
        data = {}
        for name, input_state in self.probes.items():
            result = apply_channel(channel, input_state)
            p = result.tr()
            words = {(x, x): apply_channel(ch, input_state).tr() for (x, y), ch in joint.items() if x == y}
            conditional = result.scale(1 / p) if p else None
            assert sum(words.values(), F(0)) == p
            overlaps = {}
            for t, ideal in IDEAL.items():
                desired = apply_channel(ideal, input_state)
                norm = desired.tr()
                if p and norm and desired @ desired == desired.scale(norm):
                    overlaps[str(t)] = str((conditional @ desired).tr() / norm)
            data[name] = {
                "unconditional_weight": str(p), "target_unnormalized": self.cat.put(result),
                "target_conditional": self.cat.put(conditional) if p else None,
                "pure_ideal_overlaps": overlaps,
                "acb_words": diagonal_summary(words, lambda x: x.physical_acb, p),
            }
        return data

    def run(self, **plan):
        family = plan["family"]
        weighting = plan.get("weighting", "coherent")
        tags = plan.get("tag", "none")
        phases = plan.get("phases", ())
        schedule = preparation(family, weighting, tag=tags, phases=phases)
        original_words = tuple(schedule[0][1].paths)
        gram = []
        for i, j in product(original_words, repeat=2):
            coefficient = sum((F(n * trace.paths[j].get(x, 0)) / trace.squared_denominator
                               for _, trace, _ in schedule for x, n in trace.paths[i].items()), F(0))
            assert coefficient == (i == j)
            gram.append(str(coefficient))
        sources, output, ch = {}, {}, {}
        for herald, trace, accepted in schedule:
            rho = trace.density()
            measure = plan.get("analyzers", (True, True)) if accepted else (False, False)
            drives = plan.get("drives", (True, True)) if accepted else (False, False)
            assert all(not live or read for live, read in zip(drives, measure, strict=True))
            fine = {}
            for address, observed in instrument_columns(drives, measure, rho):
                data = trace_registers(observed)
                fine[address] = data
                key = herald + ":" + port_key(address)
                ch[key] = data
                row = {
                    "source_herald": herald, "target_coupling_offered": drives, "analyzer_flags": address,
                    "joined_sign_if_both_flags_delivered": sign_of(address), "channel": self.channel(data),
                    "joint_returned_blocks": self.block_table(observed, address, accepted),
                    "probes": self.probe_row(observed, data),
                }
                source_weight = F(trace.steps[-1]["weight_per_launch"])
                row["conditional_outcome_weights_given_source_record"] = {
                    name: str(F(record["unconditional_weight"]) / source_weight) if source_weight else None
                    for name, record in row["probes"].items()
                }
                if tags == "ignored":
                    hidden = masked_tag_blocks(observed, "tag_a" if family.startswith("nae") else "tag_b")
                    assert trace_registers(hidden) == data
                    row["after_tracing_the_unobserved_tag"] = self.block_table(hidden, address, accepted)
                if not accepted:
                    assert data == IDENTITY_CHANNEL.scale(source_weight)
                    assert len(fine) == 1
                output[key] = row
            meter = read_meter(rho, drives, measure, fine)
            assert add([effect(v) for v in fine.values()], 4) == IX.scale(meter.tr())
            sources[herald] = {
                "admitted_to_coupling": accepted, "weight_per_launch": str(meter.tr()),
                "word_and_workspace_trace": trace.steps, "reduced_binary_meter": self.cat.put(meter),
            }

        assert add([effect(v) for v in ch.values()], 4) == IX
        sign_maps = {s: add([ch[k] for k, v in output.items() if v["joined_sign_if_both_flags_delivered"] == s], 16)
                     for s in (1, -1)}
        weights = sum((F(z["weight_per_launch"]) for z in sources.values() if z["admitted_to_coupling"]), F(0))
        p = plan.get("clean_p")
        if p is not None:
            assert weights == p
            frame = (-1) ** len(phases)
            assert all(sign_maps[s] == IDEAL[frame*s].scale(p) for s in (1, -1))
            for key, r in output.items():
                s = r["joined_sign_if_both_flags_delivered"]
                if s:
                    assert ch[key] == IDEAL[frame*s].scale(p / 2)
                else:
                    assert r["analyzer_flags"] == (None, None)
        if plan.get("classical_controls"):
            baseline = (IDENTITY_CHANNEL + kraus_map(M))
            assert all(sign_maps[s] == baseline.scale(weights / 4) for s in (1, -1))
            for key, case in output.items():
                if case["joined_sign_if_both_flags_delivered"] is not None:
                    prior = F(sources[case["source_herald"]]["weight_per_launch"])
                    assert effect(ch[key]) == IX.scale(prior / 4)

        env_names = {
            "coherent": "one common environment state",
            "diagonal": "orthogonal environment labels indexed by the complete original acb word, traced in every coefficient",
            "dephase_between_b": "environment labels indexed by the original b bit, traced in every coefficient",
        }
        denied = zero(16)
        denied_density = defaultdict(F)
        for herald, trace, admitted in schedule:
            if not admitted:
                denied += ch[herald + ":--"]
                for word_pair, coeff in trace.density().items():
                    denied_density[word_pair] += coeff
        denied_trace = effect(denied).tr() / 4
        assert denied_trace == 1 - weights and denied == IDENTITY_CHANNEL.scale(denied_trace)
        frozen_plan = plan.copy()
        if p is not None:
            frozen_plan["clean_p"] = str(p)
        record = {
            "plan": frozen_plan, "preparation_environment": env_names[weighting], "source_records": sources,
            "full_herald_kraus_gram_original_acb_order": {"words": original_words, "entries_row_major": gram},
            "source_admission_weight": str(weights), "all_fine_records": output,
            "combined_source_refusal": {
                "weight_per_launch": str(denied_trace),
                "normalized_target_channel": self.channel(IDENTITY_CHANNEL) if denied_trace else None,
                "subnormalized_target_channel": self.channel(denied),
                "named_physical_words_after_tracing_fine_refusal_labels": diagonal_summary(
                    denied_density, lambda x: x.physical_acb, denied_trace),
                "conditional_held_density_after_tracing_fine_refusal_labels": [
                    [astuple(x), astuple(y), str(v / denied_trace)]
                    for (x, y), v in sorted(denied_density.items()) if v
                ],
            },
            "joined_maps_per_launch_with_both_flags": {str(s): self.channel(v) for s, v in sign_maps.items()},
            "joined_maps_if_conditioned_on_admission": {
                str(s): self.channel(v.scale(1 / weights)) if weights else None for s, v in sign_maps.items()
            },
            "total_effect": self.cat.put(add([effect(v) for v in ch.values()], 4)),
            "signed_map_checks": {
                "joined_sign_probabilities_match_throughout": all(effect(sign_maps[s]) == S[s].scale(weights) for s in (1, -1)) if weights else None,
                "complete_joined_signed_maps_match": all(sign_maps[s] == IDEAL[s].scale(weights) for s in (1, -1)) if weights else None,
                "corrected_phase_for_intentionally_reversed_controls": (-1) ** len(phases),
            },
        }
        return record, ch


def verify_ordinary(trace):
    prior = hardware._prior()
    for bank, rev in trace["coordinate_reversed"].items():
        points = (trace["initial"][bank], trace["final"][bank])
        assert all(not any(prior._failures(word, rev).values()) for word in points)
    for step in trace["offers"]:
        rev = trace["coordinate_reversed"][step["target_bank"]]
        assert all(not any(prior._failures(step[k], rev).values()) for k in ("before", "after"))


def local_hardware():
    prior = hardware._prior()
    gates, analysis, writers, repeat = {}, {}, {}, {}
    for site, drive, data, meter in product("AB", (False, True), ADDRESSES, ADDRESSES):
        gate = "CJ" if site == "A" else "C_minus_J"
        initial = {"A_data": prior._basis(data), "A_meter": prior._basis(meter)}
        results, trace = hardware._exact_gate(initial, {k: False for k in initial}, hardware.GATES[gate], drive=drive)
        active = drive and meter == "b"
        end = (ADDRESSES[1 - ADDRESSES.index(data)] if active else data)
        minus = active and (data == ("b" if site == "A" else "a"))
        assert results == {(prior._basis(end), initial["A_meter"]): (hardware.ONE if not minus else (F(-1), F(0)))}
        gates[f"{site}/{int(drive)}/{data}{meter}"] = {
            "hardware_receipt_uses_local_A_labels_for_either_reader": True,
            "gate": gate, "initial": initial, "terminal_data": end, "amplitude": -1 if minus else 1, "all_paths": trace,
        }

    for code in ADDRESSES:
        row = prior._basis_offer(prior._basis(code), "real_ab", inverse=True, reverse=False)
        values = {p["address"]: tuple(p["amplitude"]) for p in row["all_four_basis_rows"]}
        assert [values[c][0] for c in "abcd"] == [1, 1 if code == "a" else -1, 0, 0]
        assert all(values[c][1] == 2 for c in "ab")
        analysis[code] = row
        transfer = prior._pointer_transfer(prior._basis(code), "A_extracted_meter", "A_fresh_reader", False,
                                            separate=False)
        verify_ordinary(transfer)
        assert prior._address(transfer["final"]["A_extracted_meter"], False) == "c"
        assert prior._address(transfer["final"]["A_fresh_reader"], False) == code
        repeat[code] = transfer
        for stages in prior.STAGES:
            skey = "".join(str(int(x)) for x in stages)
            port = prior._port(prior._basis(code), "b", stages, False, complete=True)
            verify_ordinary(port)
            assert port["physical_completed_receipt"] == 0 and port["measured_flag"] == ADDRESSES.index(code)
            if all(stages):
                assert port["keeper"] == ("101" if code == "a" else "011")
            writers[f"{code}/{skey}"] = port

    for idle in ("idle_a", "idle_b", "blank"):
        underlying = idle[-1] if idle != "blank" else "c"
        untouched = prior.Trace({"meter": prior._basis(underlying)}, permitted_shared_guards=False)
        raw = untouched.output()
        assert raw["initial"] == raw["final"] and prior._routes().decode(raw["final"]["meter"])["keeper"] == "110"
        verify_ordinary(raw)
        writers[idle] = {"keeper": "110", "physical_completed_receipt": 1, "measured_flag": None,
                         "final": {"A_record": raw["final"]["meter"]}, "trace": raw}

    refuses = {}
    for left, right in product(ADDRESSES, repeat=2):
        ready = {f"{site}_{bank}": prior._basis(code) for site, data in zip("AB", (left, right), strict=True)
                 for bank, code in (("data", data), ("meter", "c"), ("keeper", "c"))}
        trace = prior.Trace(ready, permitted_shared_guards=False)
        for site in "AB":
            trace.exchange("leave target control idle before source admission", f"{site}_data", prior.S, offered=False)
            trace.exchange("leave analysis idle before source admission", f"{site}_meter", prior.MEASURED_RECEIPT, offered=False)
            trace.writes(f"{site}_keeper", (False, False))
        done = trace.output()
        verify_ordinary(done)
        assert done["initial"] == done["final"]
        refuses[left+right] = done
    return gates, analysis, writers, repeat, refuses


def classical_hardware(writers):
    prior = hardware._prior()
    rows, traces = {}, {}
    codes = ("a", "b", "idle_a", "idle_b", "blank")
    stages_for = {c: prior.STAGES if c in "ab" else (None,) for c in codes}
    for a, b in product(codes, repeat=2):
        for wc_a, wc_b, send_a, send_b, keeper_only in product(stages_for[a], stages_for[b], BITS, BITS, BITS):
            keys = tuple(code + "/" + "".join(str(int(x)) for x in stages) if stages is not None else code
                         for code, stages in zip((a, b), (wc_a, wc_b), strict=True))
            measured = tuple(writers[k] for k in keys)
            send = (send_a, send_b)
            delivered = tuple(bool(conn and p["measured_flag"] is not None and
                                   (not keeper_only or p["keeper_matches_flag"])) for conn, p in zip(send, measured, strict=True))
            both = all(delivered)
            sign_bit = measured[0]["measured_flag"] ^ measured[1]["measured_flag"] if both else None
            output = "110" if sign_bit is None else ("011" if sign_bit else "101")
            left, right = (p["final"]["A_record"] for p in measured)
            trace_id = f"{left}/{right}/{int(delivered[0])}{int(delivered[1])}"
            if trace_id not in traces:
                banks = {"A_meter": left, "B_meter": right, "message_A": prior._basis("c"),
                         "message_B": prior._basis("c"), "collector": prior._basis("c")}
                sim = prior.Trace(banks)
                for site, offered in zip("AB", delivered, strict=True):
                    sim.exchange("disclose already measured flag", f"message_{site}", prior.T,
                                 ((f"{site}_meter", prior.T, 1),), offered=offered)
                    sim.exchange("set physical message present", f"message_{site}", prior.L, offered=offered)
                for site in "AB":
                    sim.exchange("xor two received classical flags", "collector", prior.Q,
                                 (("message_A", prior.L, 1), ("message_B", prior.L, 1), (f"message_{site}", prior.T, 1)))
                sim.writes("collector", (both, both))
                assert prior._routes().decode(sim.words["collector"])["keeper"] == output
                assert all(sim.words[side] == banks[side] for side in ("A_meter", "B_meter"))
                traces[trace_id] = sim.output()
                verify_ordinary(traces[trace_id])
            rows["/".join((*keys, f"{send_a}{send_b}", str(keeper_only)))] = {
                "local_write_records": keys, "message_presence": delivered,
                "local_keepers": tuple(p["keeper"] for p in measured), "joined_keeper": output,
                "recorded_sign": None if sign_bit is None else (-1) ** sign_bit, "join_trace": trace_id,
            }
    assert any(x["local_keepers"] == ("110", "011") and x["joined_keeper"] == "011" for x in rows.values())
    return {"conditions": "Switches are separate fault settings; they add no event probability.",
            "index_order": "writer A key, writer B key, two attempted message bits, keeper-only read bit",
            "combined_keeper_branches": rows, "physical_join_traces": traces}


def scenarios():
    plans = {}
    clean = {"parity_atomic": F(1), "nae_equal": F(1, 3), "nae_whole_a": F(1, 3)}
    for family, probability in clean.items():
        for weighting in SETTINGS:
            plan = {"family": family, "weighting": weighting}
            if weighting == "coherent":
                plan["clean_p"] = probability
            elif family != "nae_whole_a" or weighting == "dephase_between_b":
                plan["classical_controls"] = True
            plans[f"{family}/{weighting}"] = plan
        for phase in ("A", "B", "AB"):
            plans[f"{family}/coherent/phase_{phase}"] = {"family": family, "phases": tuple(phase), "clean_p": probability}
        for tag in ("kept", "ignored"):
            plans[f"{family}/coherent/tag_{tag}"] = {"family": family, "tag": tag, "classical_controls": family != "nae_whole_a"}
        if family != "nae_whole_a":
            plans[f"{family}/coherent/tag_uncomputed"] = {"family": family, "tag": "uncomputed", "clean_p": probability}
            for side, drive in (("A", (False, True)), ("B", (True, False)), ("AB", (False, False))):
                plans[f"{family}/control_{side}_disconnected"] = {"family": family, "drives": drive}
                plans[f"{family}/reader_{side}_idle"] = {"family": family, "drives": drive, "analyzers": drive}
    for family, weighting in product(("parity_serial_refused", "parity_missing_A", "parity_missing_B", "nae_atomic_refused"), SETTINGS[:2]):
        plans[f"{family}/{weighting}"] = {"family": family, "weighting": weighting}
    for family, weighting in product(("parity_copied", "parity_lawful_A_transfer", "parity_conditioned"), SETTINGS):
        plans[f"{family}/{weighting}"] = {"family": family, "weighting": weighting, "classical_controls": True}
    for weighting in SETTINGS[:2]:
        plans[f"nae_equal/{weighting}/tag_read"] = {"family": "nae_equal", "weighting": weighting,
                                                   "tag": "read", "classical_controls": True}
        plans[f"nae_equal_merged/{weighting}"] = {"family": "nae_equal_merged", "weighting": weighting,
                                                 **({"clean_p": F(1, 3)} if weighting == "coherent" else {"classical_controls": True})}
    return plans


def repeat_checks(evidence, cases, exact_channels):
    result = {}
    for family, weighting in product(("parity_atomic", "nae_equal", "nae_whole_a"), SETTINGS):
        key = f"{family}/{weighting}"
        channels = exact_channels[key]
        first = cases[key]["all_fine_records"]
        both_success = defaultdict(lambda: zero(16))
        rows = {}
        for left, right in product(channels, repeat=2):
            out = compose(channels[right], channels[left])
            signs = first[left]["joined_sign_if_both_flags_delivered"], first[right]["joined_sign_if_both_flags_delivered"]
            if None not in signs:
                both_success[signs] += out
            rows[left + "/" + right] = {
                "first_record": left, "second_record": right, "channel": evidence.channel(out),
                "weight_on_product_00": str(apply_channel(out, evidence.probes["00"]).tr()),
                "weight_on_within_sign_sums_and_differences": {
                    probe: str(apply_channel(out, evidence.probes[probe]).tr())
                    for probe in ("1/u+v", "1/u-v", "-1/u+v", "-1/u-v")
                },
            }
        total = add([effect(compose(y, x)) for x, y in product(channels.values(), repeat=2)], 4)
        assert total == IX
        if weighting == "coherent":
            p = F(cases[key]["source_admission_weight"])
            for s, t in product((1, -1), repeat=2):
                assert both_success[s, t] == (IDEAL[s].scale(p * p) if s == t else zero(16))
        result[key] = {
            "independent_second_meter_with_its_own_source_and_both_writers": True,
            "full_two_launches": rows,
            "first_and_second_reported_sign_maps": {f"{s}/{t}": evidence.channel(v) for (s, t), v in both_success.items()},
            "total_effect": evidence.cat.put(total),
        }
    return result


def basis_checks(evidence):
    result = {}
    for family in ("parity_atomic", "parity_serial_refused", "parity_lawful_A_transfer",
                   "nae_equal", "nae_whole_a", "nae_atomic_refused"):
        branches = preparation(family, "coherent")
        raw = {}
        for original in branches[0][1].paths:
            outcomes = {}
            effect_sum = zero(4)
            for record, trace, accepted in branches:
                rho = trace.density_given_basis_input(original)
                for address, blocks in instrument_columns((accepted, accepted), (accepted, accepted), rho):
                    ch = trace_registers(blocks)
                    effect_sum += effect(ch)
                    key = record + ":" + port_key(address)
                    p = apply_channel(ch, evidence.probes["00"]).tr()
                    outcomes[key] = {
                        "source_flag": record, "local_analyzer_flags": address,
                        "target_channel_given_this_original_word": evidence.channel(ch),
                        "joint_probability_given_original_word_and_target_00": str(p),
                        "joint_probability_per_uniform_diagonal_launch_on_00": str(p / len(trace.paths)),
                        "source_words_at_end_before_coupling": diagonal_summary(rho, lambda x: x.physical_acb),
                    }
                    if not accepted:
                        assert ch == IDENTITY_CHANNEL.scale(p)
            assert effect_sum == IX
            if family == "nae_equal":
                assert outcomes["unequal:--"]["joint_probability_given_original_word_and_target_00"] == (
                    "0" if original in ("001", "110") else "1"
                )
                for port in ("00", "01", "10", "11"):
                    assert outcomes[f"equal:{port}"]["joint_probability_given_original_word_and_target_00"] == (
                        "1/4" if original in ("001", "110") else "0"
                    )
            raw[original] = outcomes
        result[family] = raw
    return result


def check_exact_cases(evidence, cases, channels, gates):
    parity = cases["parity_atomic/coherent"]["source_records"]["accepted"]
    equal = cases["nae_equal/coherent"]["source_records"]["equal"]
    unequal = cases["nae_equal/coherent"]["source_records"]["unequal"]
    all_a = cases["nae_whole_a/coherent"]["source_records"]
    assert parity["weight_per_launch"] == "1" and equal["weight_per_launch"] == "1/3"
    expected = {
        "001": [[("010", 0, 0, "00", "00", 0), 1]],
        "110": [[("010", 1, 1, "00", "00", 0), 1]],
    }
    paths = equal["word_and_workspace_trace"][-1]["basis_paths_by_original_acb"]
    assert {k: v for k, v in paths.items() if v} == expected
    retained = unequal["word_and_workspace_trace"][-1]["named_physical_words"]["conditional"]
    assert retained == {x: "1/4" for x in ("010", "011", "100", "101")}
    bell = evidence.cat.put(BELL_PHASE[1])
    assert parity["reduced_binary_meter"] == bell
    assert equal["reduced_binary_meter"] == evidence.cat.put(BELL_PHASE[1].scale(F(1, 3)))
    assert all_a["success"]["reduced_binary_meter"] == equal["reduced_binary_meter"]
    assert [all_a[key]["weight_per_launch"] for key in all_a] == ["1/3", "2/3", "0", "0"]
    for key in ("parity_atomic/diagonal", "nae_equal/diagonal", "nae_equal/coherent/tag_kept"):
        data = cases[key]
        assert not data["signed_map_checks"]["joined_sign_probabilities_match_throughout"]
        for name, row in data["all_fine_records"].items():
            s = row["joined_sign_if_both_flags_delivered"]
            if s is not None:
                assert row["probes"]["00"]["pure_ideal_overlaps"][str(s)] == "1/2"
                assert row["probes"]["opposite_sign_mixture_1"]["unconditional_weight"] == row["probes"]["opposite_sign_mixture_-1"]["unconditional_weight"]
    for family in ("parity_atomic", "nae_equal"):
        base = channels[f"{family}/coherent"]
        assert channels[f"{family}/coherent/phase_AB"] == base
        assert channels[f"{family}/coherent/tag_uncomputed"] == base
        assert channels[f"{family}/coherent/tag_kept"] == channels[f"{family}/coherent/tag_ignored"]
        for site in "AB":
            assert not cases[f"{family}/control_{site}_disconnected"]["signed_map_checks"]["complete_joined_signed_maps_match"]
            assert not cases[f"{family}/reader_{site}_idle"]["signed_map_checks"]["complete_joined_signed_maps_match"]
    for key in ("parity_serial_refused/coherent", "parity_missing_A/coherent", "parity_missing_B/coherent", "nae_atomic_refused/coherent"):
        assert list(channels[key].values()) == [IDENTITY_CHANNEL]
    assert len(gates) == 16


def build():
    evidence = Evidence()
    cases, channels = {}, {}
    legality = legality_table()
    for name, plan in scenarios().items():
        cases[name], channels[name] = evidence.run(**plan)
    gates, analyzers, writers, fresh, refusal = local_hardware()
    classical = classical_hardware(writers)
    twice = repeat_checks(evidence, cases, channels)
    basis = basis_checks(evidence)
    check_exact_cases(evidence, cases, channels, gates)
    root = HERE.parents[1]
    code_sources = (
        Path(__file__).resolve(), HERE / "preregistration.md", PRIOR / "coherent_meter.py",
        PRIOR / "instrument_hardware.py", PRIOR / "instrument_math.py", Path(hardware._prior().__file__).resolve(),
        HERE.parent / "TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001B" / "real_algebra.py",
    )
    src = {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest() for path in code_sources}
    return {
        "scope": "Exact replay of supplied positive-amplitude and diagonal preparations, with split-source physical places retained at every primitive.",
        "held_register_order": ("physical_acb", "private_meter_a", "private_meter_b", "saved_A_row",
                                "tag_on_original_A_row", "tag_on_original_b"),
        "physical_branch_convention": {
            "source_flag": "equal accepts the two original acb words 001 and 110 together. The herald does not reveal which.",
            "local_analyzer_flags": "0 is the X plus address a and 1 is the X minus address b. These flags do not report an original source word.",
            "final_meter_fields": "After an analyzer they hold its physical port bit. If idle they are still the unmeasured computational bit.",
            "zero_analyzer_addresses_c_d": "Both spare analyzer addresses are exact zero on all admitted binary meter paths. The calibration retains them.",
            "classical_comparison": "Received flags determine if and how the third keeper writes. A local failed keeper after an analyzer keeps its observed address and bit.",
            "readout_post_state_recipe": "For every joint returned register pair, the matching law-checked ordinary keeper traces are selected independently by its two address keys and fault settings. The data and three original source places stay unchanged by those writers.",
        },
        "legality": legality,
        "whole_A_filter": {"input_saved_A_row_order": ROWS,
                           "fine_operators_numerator_and_squared_denominator": [(n, m, str(q)) for n, m, q in whole_a_filter_rows()],
                           "same_readable_refusal_if_unresolved": ("failure_plus", "failure_perpendicular_1", "failure_perpendicular_2")},
        "probe_input_density_ids": {name: evidence.cat.put(state) for name, state in evidence.probes.items()},
        "one_launch": cases,
        "separate_basis_input_probes_on_each_original_named_word": basis,
        "ordinary_hardware": {
            "target_control_all_real_paths": gates, "single_local_analyzer_columns": analyzers,
            "local_writer_and_idle_words": writers, "joined_writer": classical,
            "refusal_no_target_coupling_all_ordinary_inputs": refusal, "fresh_encoded_local_meter_transfers": fresh,
        },
        "fresh_repeat": twice,
        "channels_by_choi_id": evidence.channels, "matrix_catalogue": evidence.cat.matrices,
        "summary": {"cases": len(cases), "source_records": sum(len(x["source_records"]) for x in cases.values()),
                    "one_launch_records": sum(len(x["all_fine_records"]) for x in cases.values()),
                    "basis_input_fine_records": sum(len(x) for family in basis.values() for x in family.values()),
                    "two_launch_records": sum(len(x["full_two_launches"]) for x in twice.values()),
                    "ordinary_writer_and_message_settings": len(classical["combined_keeper_branches"]),
                    "ordinary_join_traces": len(classical["physical_join_traces"])},
        "source_sha256": src,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="reproduce and compare with the saved exact evidence")
    args = parser.parse_args()
    result = build()
    raw = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    compressed = gzip.compress(raw, mtime=0)
    path = HERE / "meter_evidence.json.gz"
    if args.verify:
        assert compressed == path.read_bytes()
    else:
        path.write_bytes(compressed)
    assert gzip.decompress(path.read_bytes()) == raw
    print(json.dumps(result["summary"], sort_keys=True))
    print("sha256", sha256(compressed).hexdigest(), "bytes", len(compressed))


if __name__ == "__main__":
    main()
