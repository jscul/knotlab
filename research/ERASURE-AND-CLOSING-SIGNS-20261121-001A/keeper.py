"""Exact pulse, return and physical-port replay for the registered B286 study.

A compact word holds (data,q,t,l,s,K,z,environment). The decoder in ordinary_routes.py
expands its ordinary fields to the 44 physically named marks. One term is an element
of Z[sqrt(2),i]. Each pulse doubles a common amplitude denominator.
"""

import argparse
from collections import defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = "TWO-KNOTS-ONE-DECISION-20261121-001"
PROOF = ROOT / "proofs" / HERE.name / (HERE.name + "-P001_keeper")
ROWS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8))
CHANGES = (1, 2, 7, 8)
F = sum(1 << i for i in CHANGES)
U = 511 ^ ((1 << 1) | (1 << 3) | (1 << 8))
V = U ^ F
ZERO = (0, 0, 0, 0)
ONE = (1, 0, 0, 0)
MODES = (
    "clean",
    "held",
    "held_read",
    "uncomputed",
    "export_reset",
    "two_return_one",
    "two_return_both",
    "old_held",
    "old_return",
    "logged_and_returned",
    "lost",
    "missing_pre",
)
CONNECTIONS = ((1, 1), (1, 0), (0, 1), (0, 0))


@dataclass(frozen=True, order=True)
class Word:
    data: int
    q: int = 0
    t: int = 0
    l: int = 0
    s: int = 0
    keeper: int = 6
    z: int = 1
    env: int = 0


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, n):
    return tuple(n * x for x in a)


def root2(a):
    r, s, i, j = a
    return 2 * s, r, 2 * j, i


def imag(a, sign):
    r, s, i, j = a
    return -sign * i, -sign * j, sign * r, sign * s


def norm(a):
    r, s, i, j = a
    return r * r + 2 * s * s + i * i + 2 * j * j, 2 * (r * s + i * j)


def sum_norm(items):
    p = q = 0
    for a in items:
        x, y = norm(a)
        p += x
        q += y
    return p, q


def accumulate(out, k, a):
    out[k] = add(out.get(k, ZERO), a)


def squash(out):
    return {k: a for k, a in out.items() if a != ZERO}


def perm(state, action):
    out = {}
    for k, a in state.items():
        dst = action(k)
        assert dst not in out, "the stipulated pulse word must be an injective exchange"
        out[dst] = a
    return out


def pulse(state, action, sense=1, idle="unit"):
    out = {}
    for k, a in state.items():
        dst = action(k)
        if dst == k and idle == "unit":
            accumulate(out, k, scale(a, 2))
        else:
            r = root2(a)
            accumulate(out, k, r)
            accumulate(out, dst, imag(r, sense))
    out = squash(out)
    assert sum_norm(out.values()) == tuple(4 * x for x in sum_norm(state.values()))
    return out


def visible_prob(a, b, total):
    assert total > 0
    if b:
        return f"{Fraction(a, total)}+({Fraction(b, total)})sqrt(2)"
    return str(Fraction(a, total))


def record_key(w):
    return (w.data, w.q, w.t, w.l, w.s, format(w.keeper, "03b"), w.z, w.env)


def prob_table(state, key=record_key):
    total, irr = sum_norm(state.values())
    assert not irr
    out = defaultdict(lambda: [0, 0])
    for w, a in state.items():
        x, y = norm(a)
        g = out[key(w)]
        g[0] += x
        g[1] += y
    return {str(k): visible_prob(x, y, total) for k, (x, y) in sorted(out.items())}


def vector(state):
    d, irr = sum_norm(state.values())
    assert not irr
    from math import gcd
    from functools import reduce

    div = reduce(gcd, (abs(i) for a in state.values() for i in a), 0) or 1
    return {
        "basis_keys": "(data,q,t,l,s,K,z,environment)",
        "amplitude_coordinates": "(a,b,c,d) = a+b sqrt(2)+i(c+d sqrt(2))",
        "squared_norm": d // (div * div),
        "amplitudes": {str(record_key(w)): [i // div for i in a] for w, a in sorted(state.items())},
    }


def snap(trace, label, state):
    if trace is not None:
        trace.append({"after": label, "ordinary_distribution": prob_table(state)})


def flip_field(name, guard=lambda k: True):
    def action(k):
        return replace(k, **{name: getattr(k, name) ^ 1}) if guard(k) else k

    return action


def flip_data(i, guard=lambda k: True):
    return lambda k: replace(k, data=k.data ^ (1 << i)) if guard(k) else k


def transport(state, acts, trace=None):
    for name, op in acts:
        state = perm(state, op)
        snap(trace, name, state)
    return state


def sleeve(state, guard, sense, idle, trace=None, label="phase"):
    a = flip_field("s", guard)
    for j in range(2):
        state = pulse(state, a, sense, idle)
        snap(trace, f"{label} pulse {j + 1}", state)
    state = perm(state, a)
    snap(trace, label + " return scratch", state)
    return state


def mixer(state, idle, sense=1, trace=None):
    g = lambda k: k.q
    state = sleeve(state, g, -sense, idle, trace, "q inverse phase before")
    state = pulse(state, flip_field("q"), sense, idle)
    snap(trace, "q elementary half exchange", state)
    return sleeve(state, g, -sense, idle, trace, "q inverse phase after")


def packed(state, sense, idle, trace=None):
    g = lambda k: (k.data >> 1) & 1
    ops = [(f"conditional data {j}", flip_data(j, g)) for j in (2, 7, 8)]
    state = transport(state, ops, trace)
    state = pulse(state, flip_data(1), sense, idle)
    snap(trace, "elementary half exchange on data 1", state)
    return transport(state, reversed(ops), trace)


def source(u, v, arm, idle="unit", sense=1, trace=None):
    w = Word(u)
    state = {w: ONE}
    snap(trace, "ready", state)
    state = packed(state, sense, idle, trace)
    base = (u >> 1) & 1
    state = sleeve(
        state,
        lambda k: ((k.data >> 1) & 1) ^ base,
        (-1 if arm == "plus" else 1) * sense,
        idle,
        trace,
        "private source phase",
    )
    return state


def start(u, v, kind):
    if kind == "u":
        return {Word(u): ONE}
    if kind == "v":
        return {Word(v): ONE}
    return {Word(u): ONE, Word(v): scale(ONE, 1 if kind == "plus" else -1)}


def first_stage(w):
    if not w.q:
        return w
    a, b, c = (w.keeper >> 2) & 1, (w.keeper >> 1) & 1, w.keeper & 1
    return replace(w, keeper=(c << 2) | (b << 1) | a)


def second_stage(w):
    b, c = (w.keeper >> 1) & 1, w.keeper & 1
    if b == w.z and b != c:
        return replace(w, keeper=w.keeper ^ 3, z=w.z ^ 1)
    return w


def write(state, connection, trace=None):
    for j, action in enumerate((first_stage, second_stage)):
        if connection[j]:
            state = perm(state, action)
        snap(trace, f"write {j + 1}, {'connected' if connection[j] else 'disconnected'}", state)
    return state


def residual(state, guard, overlap):
    # (Re, Im, orthogonal component, common denominator), for a fresh E bit.
    a, b, c, den = {
        "zero": (0, 0, 1, 1),
        "unit": (1, 0, 0, 1),
        "three_fifths": (3, 0, 4, 5),
        "imaginary": (0, 1, 0, 1),
    }[overlap]
    out = {}
    for k, v in state.items():
        assert not k.env & 2
        if guard(k):
            accumulate(out, k, add(scale(v, a), imag(v, b)))
            accumulate(out, replace(k, env=k.env | 2), scale(v, c))
        else:
            accumulate(out, k, scale(v, den))
    return squash(out)


def detector(state, mode="clean", idle="unit", sense=1, trace=None, overlap=None):
    if mode == "missing_pre":
        return state
    old = lambda k: (k.data >> 1) & 1
    if mode in ("old_held", "old_return"):
        state = transport(state, [("write old data into l", flip_field("l", old))], trace)
    state = mixer(state, idle, sense, trace)
    if mode not in ("old_held", "old_return"):
        if mode != "clean":
            state = transport(state, [("mark true q route in t", flip_field("t", lambda k: k.q))], trace)
    state = transport(
        state, [(f"q-controlled full exchange {i}", flip_data(i, lambda k: k.q)) for i in CHANGES], trace
    )
    for _ in range(2):
        state = sleeve(
            state, lambda k: k.q and (k.data >> 3) & 1, sense, idle, trace, "compiled q times mark3"
        )
    if mode in ("held_read", "export_reset", "logged_and_returned", "lost"):
        state = transport(state, [("route copied/exported", flip_field("env", lambda k: k.t))], trace)
    if mode in ("two_return_one", "two_return_both"):
        state = transport(state, [("duplicate route t into l", flip_field("l", lambda k: k.t))], trace)
    if mode == "two_return_both":
        state = transport(state, [("return l via t", flip_field("l", lambda k: k.t))], trace)
    if mode in ("uncomputed", "two_return_one", "two_return_both", "logged_and_returned"):
        state = transport(state, [("return t via q", flip_field("t", lambda k: k.q))], trace)
    if mode in ("export_reset", "lost"):
        state = transport(
            state, [("return visible t; old copy elsewhere", flip_field("t", lambda k: k.env))], trace
        )
    if mode == "old_return":
        state = transport(
            state, [("return old l via new x XOR q", flip_field("l", lambda k: old(k) ^ k.q))], trace
        )
    if overlap is not None:
        state = residual(state, lambda k: k.q, overlap)
        snap(trace, "residual route state", state)
    return mixer(state, idle, sense, trace)


def physical_readout(state, mode, connection):
    if mode == "missing_pre":
        return state
    return write(state, connection)


def headers():
    return {
        "ordinary_fields": ["data", "q", "t", "l", "s", "keeper", "z", "environment"],
        "constants": "h=1, all thirteen private ternary marks=1; the complete leaf names and physical-bit decoder are in ordinary_routes.py.",
        "mode_lost": "The environment label indexes a mathematical mixture for genuine ordinary loss. The numerical instrument is the trace over this index; only its reduced tables are physical in the no-environment arm.",
        "source_settings": "A private source receipt is fixed by each arm, never passed to the detector. Every case reports conditional on its named setting. Sign selection, where averaged, is independently fair.",
        "guards": "The ordinary output stages are A,C if q=1, followed by the joint B,C,z offer if B=z differs from C.",
        "targets": {"mark": 3, "changed": CHANGES, "selected_words": [U, V]},
    }


def legal(data, law):
    weights = [sum((data >> j) & 1 for j in row) for row in ROWS]
    return all(n % 2 == 0 for n in weights) if law == "parity" else all(0 < n < 3 for n in weights)


def mixture(tables):
    keys = set().union(*(t.keys() for t in tables))
    return {k: str(sum(Fraction(t.get(k, "0")) for t in tables) / len(tables)) for k in sorted(keys)}


def output(state, mode, conn):
    s = physical_readout(state, mode, conn)
    sections = {}
    # The source tag t is read only in held_read. A genuinely lost environment indexes
    # Kraus sectors and is absent from its physical output. The q port is actually read.
    groups = defaultdict(dict)
    for w, a in s.items():
        port = () if mode == "missing_pre" else (w.q,)
        if mode == "held_read":
            port += (w.t,)
        if mode == "lost":
            port += (w.env,)
        groups[port][w] = a
    for port, component in groups.items():
        if mode == "lost":
            component = {replace(w, env=0): a for w, a in component.items()}
        sections[str(port)] = vector(component)
    fields = (lambda w: record_key(replace(w, env=0))) if mode == "lost" else record_key
    return {
        "K": prob_table(s, lambda w: format(w.keeper, "03b")),
        "complete": prob_table(s, fields),
        "post_read_components": sections,
        "component_weights": prob_table(
            s,
            lambda w: (
                (() if mode == "missing_pre" else (w.q,))
                + ((w.t,) if mode == "held_read" else ())
                + ((w.env,) if mode == "lost" else ())
            ),
        ),
    }


def source_plan(u, arm, sense=1):
    g = lambda k: (k.data >> 1) & 1
    controls = [("ordinary", flip_data(j, g), 1) for j in (2, 7, 8)]
    h = flip_field("s", lambda k: ((k.data >> 1) & 1) ^ ((u >> 1) & 1))
    direction = (-1 if arm == "plus" else 1) * sense
    return (
        controls
        + [("pulse", flip_data(1), sense)]
        + controls[::-1]
        + [("pulse", h, direction)] * 2
        + [("ordinary", h, 1)]
    )


def monitored_source(u, arm, idle, read_steps, summary_only=False):
    branches = {(): {Word(u): ONE}}
    for index, (kind, action, sense) in enumerate(source_plan(u, arm)):
        next_branches = {}
        for history, state in branches.items():
            state = pulse(state, action, sense, idle) if kind == "pulse" else perm(state, action)
            if index in read_steps:
                for w, a in state.items():
                    next_branches[history + (record_key(w),)] = {w: a}
            else:
                next_branches[history] = state
        branches = next_branches
    norms = {str(h): sum_norm(s.values())[0] for h, s in branches.items()}
    total = sum(norms.values())
    if summary_only:
        return {h: str(Fraction(v, total)) for h, v in norms.items()}
    return {
        "physical_read_steps": sorted(read_steps),
        "history": {k: str(Fraction(v, total)) for k, v in norms.items()},
        "source_and_output_given_history": {
            str(h): {"source": vector(s), "keeper": output(detector(s), "clean", (1, 1))["K"]}
            for h, s in branches.items()
        },
    }


def normalized_pair(state, u, v):
    """Relative v/u for this controlled source, up to a global amplitude."""
    a = state[Word(u)]
    b = state[Word(v)]
    for text, expected in (("+1", a), ("-1", scale(a, -1)), ("+i", imag(a, 1)), ("-i", imag(a, -1))):
        if b == expected:
            return text
    raise AssertionError((a, b))


def primary():
    rows = {}
    traces = {}
    preparations = {}
    singleton = {}
    partial = {}
    for idle in ("unit", "common"):
        preparations[idle] = {}
        for arm in ("plus", "minus"):
            t = []
            made = source(U, V, arm, idle, trace=t)
            preparations[idle][arm] = dict(
                relative_v_over_u=normalized_pair(made, U, V), final=vector(made), physical_snapshots=t
            )
        assert [a["ordinary_distribution"] for a in preparations[idle]["plus"]["physical_snapshots"]] == [
            a["ordinary_distribution"] for a in preparations[idle]["minus"]["physical_snapshots"]
        ]
        for mode in MODES:
            for kind in ("u", "v", "plus", "minus", "prepared_plus", "prepared_minus"):
                state = (
                    source(U, V, kind.removeprefix("prepared_"), idle)
                    if kind.startswith("prepared")
                    else start(U, V, kind)
                )
                t = (
                    []
                    if mode in ("clean", "uncomputed", "two_return_one", "two_return_both")
                    and kind in ("prepared_plus", "prepared_minus")
                    else None
                )
                middle = detector(state, mode, idle, trace=t)
                if t is not None:
                    traces[f"{idle}/{mode}/{kind}"] = t
                for conn in CONNECTIONS:
                    tag = f"{idle}/{mode}/{kind}/{conn[0]}{conn[1]}"
                    rows[tag] = output(middle, mode, conn)
            for conn in CONNECTIONS:
                end = f"/{conn[0]}{conn[1]}"
                prefix = f"{idle}/{mode}/"
                parts = [rows[prefix + k + end] for k in ("u", "v")]
                rows[prefix + "dephased" + end] = {
                    "K": mixture([x["K"] for x in parts]),
                    "complete": mixture([x["complete"] for x in parts]),
                    "post_read_components": "equal classical mixture of the two named singleton instruments",
                }
        singleton[idle] = {}
        for word in (U, V):
            singleton[idle][word] = {
                f"{choice}/{conn}": output({replace(Word(word), q=choice): ONE}, "clean", conn)
                for choice in (0, 1)
                for conn in CONNECTIONS
            }
    overlaps = {
        "zero": Fraction(),
        "three_fifths": Fraction(3, 5),
        "unit": Fraction(1),
        "imaginary": Fraction(),
    }
    for where in ("q_route", "old_data"):
        for name, gamma_real in overlaps.items():
            for kind in ("u", "v", "plus", "minus"):
                s = start(U, V, kind)
                if where == "q_route":
                    d = detector(s, overlap=name)
                else:
                    d = detector(residual(s, lambda k: ((k.data ^ U) >> 1) & 1, name))
                o = output(d, "clean", (1, 1))
                k = Fraction(o["K"].get("101", "0"))
                sign = 1 if kind == "plus" else -1 if kind == "minus" else 0
                assert k == (1 + sign * gamma_real) / 2
                partial[f"{where}/{name}/{kind}"] = o
    for mode in MODES:
        for idle in ("unit", "common"):
            for conn in CONNECTIONS:
                m = rows[f"{idle}/{mode}/u/{conn[0]}{conn[1]}"]
                n = rows[f"{idle}/{mode}/v/{conn[0]}{conn[1]}"]
                assert m["K"] == n["K"]
    assert rows["unit/clean/prepared_plus/11"]["K"] == {"101": "1"}
    assert rows["unit/clean/prepared_minus/11"]["K"] == {"011": "1"}
    assert (
        rows["common/clean/prepared_plus/11"]["K"]
        == rows["common/clean/prepared_minus/11"]["K"]
        == {"011": "1/2", "101": "1/2"}
    )
    for kind in ("u", "v"):
        assert rows[f"unit/clean/{kind}/11"]["complete"] == rows[f"common/clean/{kind}/11"]["complete"]
    fixed = {a: rows[f"unit/clean/{a}/11"]["K"] for a in ("u", "v", "plus", "minus")}
    monitor = {}
    all_histories = {}
    for idle in ("unit", "common"):
        for label, schedule in (("all", set(range(10))), *((f"cut{i}", {i}) for i in range(10))):
            results = {a: monitored_source(U, a, idle, schedule) for a in ("plus", "minus")}
            assert results["plus"]["history"] == results["minus"]["history"]
            monitor[f"{idle}/{label}"] = results
        digest = hashlib.sha256()
        count = 0
        for mask in range(1 << 10):
            cuts = {j for j in range(10) if (mask >> j) & 1}
            p = monitored_source(U, "plus", idle, cuts, True)
            m = monitored_source(U, "minus", idle, cuts, True)
            assert p == m
            digest.update(json.dumps([mask, p], sort_keys=True).encode())
            count += len(p)
        all_histories[idle] = {
            "ordinary_read_subsets": 1 << 10,
            "nonempty_histories_across_subsets": count,
            "comparison_digest": digest.hexdigest(),
            "unequal_history_distributions": 0,
        }
    return {
        "preparation": preparations,
        "full_selected_rows": rows,
        "all_physical_detector_snapshots_at_selected_controls": traces,
        "fixed_full_selector_and_singleton": singleton,
        "residual_cases": partial,
        "actually_observed_source_histories": monitor,
        "all_source_read_subsets": all_histories,
        "canonical_four_outcomes": fixed,
    }


def catalogue():
    counts = {}
    raw = {}
    for law in ("parity", "nae"):
        words = []
        controls = {}
        patterns = defaultdict(int)
        for w in range(512):
            v = w ^ F
            prior = legal(w, law)
            other = legal(v, law)
            status = (
                "admitted"
                if prior and other
                else "valid_to_invalid"
                if prior
                else "invalid_to_valid"
                if other
                else "both_invalid"
            )
            row = {"old": w, "other": v, "admission": status}
            if status == "admitted":
                for sense in (1, -1):
                    for arm in ("plus", "minus"):
                        made = source(w, v, arm, sense=sense)
                        level = (w >> 3) & 1
                        expected = "011" if (arm == "minus") ^ level else "101"
                        fresh = output(detector(made, sense=sense), "clean", (1, 1))
                        assert fresh["K"] == {expected: "1"}
                        controls[f"{w}/{sense}/{arm}"] = {
                            "data_input": [w, v],
                            "bit3": level,
                            "port": expected,
                            "complete": fresh["complete"],
                        }
                trace = []
                packed({Word(w): ONE}, 1, "unit", trace)
                bad = next(
                    (
                        i + 1
                        for i, s in enumerate(trace)
                        if any(not legal(z, law) for z in dist_data(s["ordinary_distribution"]))
                    ),
                    None,
                )
                row["first_decoded_departure_step_in_packed_half"] = bad
                t = []
                made = source(w, v, "plus", trace=t)
                detector(made, trace=t)
                fail = next(
                    (
                        (i + 1, s["after"], s["ordinary_distribution"])
                        for i, s in enumerate(t)
                        if any(not legal(z, law) for z in dist_data(s["ordinary_distribution"]))
                    ),
                    None,
                )
                row["first_decoded_departure_in_source_and_detector"] = fail
                assert legal(v, law)
            else:
                row["physical_launch_result"] = "refused; K=110, q=t=l=s=0, z=h=1, original data kept"
            patterns[status] += 1
            words.append(row)
        counts[law] = {
            "states": dict(patterns),
            "closed_pairs": patterns["admitted"] // 2,
            "uniform_nine_bit_admission": str(Fraction(patterns["admitted"], 512)),
            "strict_decoded_packed_source_accepted": sum(
                r.get("first_decoded_departure_step_in_packed_half") is None
                for r in words
                if r["admission"] == "admitted"
            ),
            "strict_decoded_full_source_and_detector_accepted": sum(
                r.get("first_decoded_departure_in_source_and_detector") is None
                for r in words
                if r["admission"] == "admitted"
            ),
            "admitted_by_old_mark3_value": {
                b: sum((r["old"] >> 3) & 1 == b for r in words if r["admission"] == "admitted")
                for b in (0, 1)
            },
        }
        for arm in ("plus", "minus"):
            mass = defaultdict(Fraction)
            for row in words:
                if row["admission"] == "admitted":
                    event = controls[f"{row['old']}/1/{arm}"]["port"]
                else:
                    event = "110"
                mass[event] += Fraction(1, 512)
            assert sum(mass.values()) == 1
            counts[law][f"all_nine_bit_launches_{arm}"] = {k: str(v) for k, v in sorted(mass.items())}
        raw[law] = {"word_table": words, "direct_both_orientations_pulse_conjugates": controls}
    return counts, raw


def dist_data(entries):
    return [int(x[1:].split(",", 1)[0]) for x in entries]


def calibration_and_gauges():
    results = {}
    for orient in (1, -1):
        for idle in ("unit", "common"):
            checks = {}
            for q in (0, 1):
                for scratch in (0, 1):
                    w = Word(U, q=q, s=scratch)
                    s = {w: ONE}
                    op = flip_field("s", lambda k: k.q)
                    for direction in (-1, 1):
                        a = pulse(s, op, direction, idle)
                        checks[f"{q}/{scratch}/{direction}"] = prob_table(a)
                        assert prob_table(a) == prob_table(pulse(s, op, direction, "unit"))
            results[f"idle={idle},phase_orientation={orient}"] = checks
    # Independent orientation of all names; transport the whole operation, including source and return.
    g = tuple((2 * j + 1) % 9 for j in range(9))
    ren = lambda w: sum(((w >> j) & 1) << g[j] for j in range(9))
    moved = sum(1 << g[j] for j in CHANGES)
    assert len(set(g)) == 9
    for w in range(512):
        assert ren(w ^ F) == ren(w) ^ moved and ((w >> 3) & 1) == ((ren(w) >> g[3]) & 1)
        for j in (2, 7, 8):
            original = w ^ (1 << j) if w >> 1 & 1 else w
            transformed = (ren(w) ^ (1 << g[j])) if ren(w) >> g[1] & 1 else ren(w)
            assert ren(original) == transformed
    naive = {Word(U): ONE}
    for j in CHANGES:
        naive = pulse(naive, flip_data(j))
    combined = packed({Word(U): ONE}, 1, "unit")
    assert len(naive) == 16 and set(w.data for w in combined) == {U, V}
    unsupported = {}
    for law in ("parity", "nae"):
        dist = prob_table(
            naive,
            lambda k: "pair" if k.data in (U, V) else "legal_offpair" if legal(k.data, law) else "illegal",
        )
        unsupported[law] = dist
    return {
        "per_word_elementary_calibrations": results,
        "nine_name_transport": g,
        "transported_all_words": 512,
        "one_half_on_each_changed_bit": vector(naive),
        "one_half_total_category": unsupported,
        "conjugated_elementary_half": vector(combined),
    }


def projected_reference_and_rival():
    """Directly evaluate (I±U)/2, independently of all gate sequences."""
    checked = 0
    for law in ("parity", "nae"):
        for w in range(512):
            v = w ^ F
            if not legal(w, law) or not legal(v, law):
                continue
            chi = (-1) ** ((w >> 3) & 1)
            for label in ("u", "v", "plus", "minus"):
                inp = start(w, v, label)
                a0 = inp.get(Word(w), ZERO)[0]
                a1 = inp.get(Word(v), ZERO)[0]
                final = detector(inp)
                for a in (0, 1):
                    c = chi * (-1) ** a
                    expected = (a0 + c * a1, a1 + c * a0)
                    p = Fraction(sum(k * k for k in expected), 4 * (a0 * a0 + a1 * a1))
                    actual = prob_table(final, lambda word: word.q)
                    assert p == Fraction(actual.get(str(a), 0))
                    coords = [final.get(Word(x, q=a), ZERO) for x in (w, v)]
                    assert scale(coords[0], expected[1]) == scale(coords[1], expected[0])
                    checked += 1
    herald = {}
    for raw in ("u", "v"):
        s = detector(start(U, V, raw), idle="common")
        for q in (0, 1):
            sub = {Word(k.data): a for k, a in s.items() if k.q == q}
            herald[f"{raw}/port{q}"] = {
                "chance": prob_table(s, lambda k: k.q)[str(q)],
                "relative_v_over_u": normalized_pair(sub, U, V),
            }
    return {
        "analytic_projector_port_and_conditional_ray_checks": checked,
        "common_idle_rival_selective_singleton_preparations": herald,
    }


def controls():
    """Explicitly cross an independent proxy and stored input tags; remove the mixer."""
    out = {}
    for arm in ("plus", "minus"):
        made = source(U, V, arm)
        for proxy in (0, 1):
            d = detector(made)
            fixed = output(d, "clean", (1, 1))
            leak = output({replace(Word(U), q=proxy): ONE}, "clean", (1, 1))
            out[f"prepared_{arm}/physical_proxy_{proxy}"] = {
                "private_proxy": proxy,
                "reader_has_no_proxy": fixed,
                "explicit_wire_from_proxy": leak,
            }
        for q in (0, 1):
            moved = perm(made, lambda w: replace(w, data=w.data ^ (F if q else 0), q=q))
            out[f"ordinary_fixed_selector_{q}/signed_{arm}"] = output(moved, "clean", (1, 1))
        for mode in ("source_tag_copied", "source_tag_returned"):
            tagged = perm(made, flip_field("l", lambda w: (w.data >> 1) & 1))
            if mode.endswith("returned"):
                tagged = perm(tagged, flip_field("l", lambda w: (w.data >> 1) & 1))
            out[f"{mode}/{arm}"] = output(detector(tagged), "clean", (1, 1))
        # Measure q in its ordinary basis without the final mixer. Both routes keep their data states.
        qmixed = mixer(made, "unit")
        followed = transport(qmixed, [(str(j), flip_data(j, lambda w: w.q)) for j in CHANGES])
        out[f"no_final_mixer/{arm}"] = output(followed, "clean", (1, 1))
    for word in (U, V):
        for proxy in (0, 1):
            out[f"fixed_singleton_{word}/proxy_{proxy}"] = {
                "clean_reader": output(detector({Word(word): ONE}), "clean", (1, 1)),
                "proxy_reader": output({replace(Word(word), q=proxy): ONE}, "clean", (1, 1)),
            }
    out["primitive_equal_members"] = {
        "decoded_control": "invalid unequal-bit register; no signed data launch",
        "physical_equal_occupation": "a real full swap leaves the literal word unchanged; elementary unit-idle pulse leaves its amplitude unchanged, common-idle pulse gives exp(±iπ/4)",
    }
    out["scorer_relabel"] = (
        "swapping only the printed plus/minus labels exchanges their names and leaves all stored K words fixed"
    )
    return out


def build():
    sys.path.insert(0, str(ROOT / "research" / PREVIOUS))
    import measurement as old

    device = old.compile_device(ROWS, old.law(ROWS, "parity", odd=5))
    assert device.flips[3] == F and device.signs[3] == 0
    import ordinary_routes

    ordinary = ordinary_routes.ordinary_checks()
    selected = primary()
    counts, pairs = catalogue()
    gauges = calibration_and_gauges()
    physical_writer_examples = {}
    for w in (U, V):
        for q in (0, 1):
            for conn in CONNECTIONS:
                physical = ordinary_routes.encode(w, q=q)
                final, trace = ordinary_routes.write_keeper(physical, stages=conn)
                dec = ordinary_routes.decode(final)
                compact = next(iter(write({Word(w, q=q): ONE}, conn)))
                assert dec["keeper"] == format(compact.keeper, "03b") and dec["z"] == compact.z
                physical_writer_examples[str((w, q, conn))] = dict(before=physical, after=final, offers=trace)
    return {
        **headers(),
        "ordinary_physical_checks": ordinary,
        "signed_pulse_and_route": selected,
        "independent_physical_writer_comparison": physical_writer_examples,
        "all_512_admissions": counts,
        "complete_nine_bit_populations": pairs,
        "primitive_and_transport_controls": gauges,
        "source_proxy_and_read_failures": controls(),
        "independent_projector_and_herald_controls": projected_reference_and_rival(),
    }


def main():
    argv = argparse.ArgumentParser(description=__doc__)
    flag = argv.add_mutually_exclusive_group(required=True)
    flag.add_argument("--write", action="store_true")
    flag.add_argument("--check", action="store_true")
    args = argv.parse_args()
    result = build()
    raw = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    dest = HERE / "outcomes.json.gz"
    if args.write:
        dest.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    else:
        assert gzip.decompress(dest.read_bytes()) == raw, "changed physical, sign or launch evidence"
    print("Complete ordinary and coherent keeper replay verified.", hashlib.sha256(raw).hexdigest())
    print(json.dumps(result["all_512_admissions"], sort_keys=True))


if __name__ == "__main__":
    main()
