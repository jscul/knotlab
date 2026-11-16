"""Public four-port wirings and grading-only characterizations of their answer sets."""

import hashlib
import importlib.util
import json
import random
from collections import Counter
from functools import lru_cache
from itertools import permutations
from pathlib import Path


A, B, C, D, E, F, G, H, I = range(1, 10)
RAW = range(512)
ALL = (1 << 512) - 1
COLUMNS = tuple(sum(1 << raw for raw in RAW if raw & (1 << i)) for i in range(9))
ORDERS = tuple(permutations(range(4)))
ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = "GROUP-SENDER-20261115-001"
# IDs from the accepted preceding joint checkpoint's four closed/open pairs.
ARCHIVED_PAIRS = (
    ("e222e4c6f70ebd38", "5becdc37b516b478"),
    ("3a072e9eb4c9ff46", "b511178208ab2c81"),
    ("148d2df296a6bc85", "4b4bf998127df26c"),
    ("d9a601d3e6ebdf8b", "27388477186a5ba0"),
)


def _cnf(*clauses, pad):
    """Embed the given conjunction into one ternary and three binary clauses."""
    result = []
    for index, clause in enumerate(clauses):
        width = 3 if index == 0 else 2
        if not 1 <= len(clause) <= width or index >= 4:
            raise ValueError(f"Clause outside the fixed format: {clauses}")
        result.append(clause + (clause[-1],) * (width - len(clause)))
    result.extend([(pad, -pad)] * (4 - len(result)))
    return tuple(result)


def _unit(value):
    return _cnf((value,), pad=value)


def _conjunction(*values):
    return _cnf(*((v,) for v in values), pad=values[0])


def _disjunction(*values):
    return _cnf(values, pad=values[-1])


def _xor(x, y):
    return _cnf((x, y), (-x, -y), pad=y)


def _or_and(x, y, z):
    return _cnf((x, y), (x, z), pad=z)


def _multiplexer(s, yes, no):
    return _cnf((-s, yes), (s, no), pad=no)


def _training_templates():
    left_or, right_or = _disjunction(A, B), _disjunction(C, D)
    left_and, right_and = _conjunction(A, B), _conjunction(C, D)
    independent = _xor(E, F)
    triangle = (_xor(A, B), _xor(B, C), _xor(D, E))
    return {
        "and_disjoint": (left_or, right_or, independent, _cnf((A, B), (C, D), pad=C)),
        "and_overlap": (left_and, _conjunction(B, C), _disjunction(D, E), _conjunction(A, B, C)),
        "or_disjoint": (left_and, right_and, independent,
                        _cnf((A, C), (A, D), (B, C), (B, D), pad=C)),
        "or_overlap": (left_or, _disjunction(B, C), _conjunction(D, E), _disjunction(A, B, C)),
        "xor_triangle": triangle + (_xor(A, C),),
        "xor_separate": (_unit(-A), _unit(B), _conjunction(C, E), _xor(-A, B)),
        "open_four_compounds": triangle + (_xor(A, F),),
        "open_correlated": (left_or, right_or, independent, _cnf((A, B), (C, G), pad=C)),
    }


def _held_templates():
    p, q = _or_and(A, B, C), _or_and(A, B, -C)
    split_q = _or_and(A, -B, H)
    base = (p, q, _unit(D))
    split_base = (p, split_q, _unit(D))
    mux_base = (_unit(A), _conjunction(B, D), _conjunction(C, E))
    rare_base = (_conjunction(A, B), _conjunction(C, D), _conjunction(E, F))

    def mux_compounds(selector):
        return _cnf((-selector, B), (-selector, D), (selector, C), (selector, E), pad=B)

    return {
        "primary": (base + (_xor(A, D),), base + (_xor(E, D),)),
        "split_source": (split_base + (_xor(A, D),), split_base + (_xor(E, D),)),
        "and_or": (base + (_disjunction(A, D),), base + (_disjunction(E, D),)),
        "mux": (mux_base + (mux_compounds(A),), mux_base + (mux_compounds(F),)),
        "rare": (rare_base + (_conjunction(A, B, C, D),), rare_base + (_conjunction(A, B, C, H),)),
    }


def _collision():
    return (
        _multiplexer(B, A, C),
        _cnf((-A, C), (A, -C), (A, B), (-A, -B), pad=A),
        _cnf((B,), (A, C), (-A, -C), pad=B),
        _cnf((A,), (-B, C), (B, -C), pad=A),
    )


def _recode(template, family, split, layout, seed, port_order):
    rng = random.Random(seed)
    sources = rng.sample(range(1, 10), 9)
    phase = [rng.getrandbits(1) for _ in sources]
    physical = []
    for question in template:
        clauses = []
        for clause in question:
            pins = []
            for literal in clause:
                index = abs(literal) - 1
                negative = (literal < 0) ^ bool(phase[index])
                pins.append(-sources[index] if negative else sources[index])
            rng.shuffle(pins)
            clauses.append(tuple(pins))
        rng.shuffle(clauses)
        physical.append(tuple(clauses))
    wiring = tuple(physical[i] for i in port_order)
    key = hashlib.sha256(json.dumps(wiring, separators=(",", ":")).encode()).hexdigest()[:16]
    metadata = {"family": family, "split": split, "layout": layout,
                "port_order": list(port_order), "cell_order": [x - 1 for x in sources],
                "cell_phase": phase}
    return key, wiring, metadata


def training_panel():
    """Each port visits every position. Only the raw wiring is an agent input."""
    out = []
    for index, (family, template) in enumerate(_training_templates().items()):
        order = ORDERS[(5 * index + 1) % 24]
        for layout in range(4):
            rotated = order[layout:] + order[:layout]
            out.append(_recode(template, family, "train", f"{family}-{layout}",
                               70127 + 241 * index + 19 * layout, rotated))
    return tuple(out)


@lru_cache(maxsize=1)
def _archived():
    spec = importlib.util.spec_from_file_location("answer_compose_group_panels",
                                                 ROOT / "research" / PREVIOUS / "panels.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {key: (w, m) for key, w, m in module.held_panel()
            if m["family"] in ("xor_closed", "xor_open")}


def held_panel():
    """Every freshly matched pair uses one identical physical recoding."""
    out = []
    for index, (group, templates) in enumerate(_held_templates().items()):
        orders = ORDERS if group == "primary" else tuple(ORDERS[(2 + index + 5*i) % 24] for i in range(4))
        for layout, order in enumerate(orders):
            name = f"{group}-{layout}"
            seed = 91387 + 1493 * index + 23 * layout
            pair = [_recode(template, f"{group}_{side}", "held", name, seed, order)
                    for side, template in zip(("closed", "open"), templates)]
            pair[0][2]["partner"] = pair[1][0]
            pair[1][2]["partner"] = pair[0][0]
            out.extend(pair)
    prior = _archived()
    for layout, keys in enumerate(ARCHIVED_PAIRS):
        for key, other in (keys, keys[::-1]):
            wiring, old = prior[key]
            if old["partner"] != other:
                raise ValueError(f"Archived pair mismatch at {key}")
            meta = dict(old, split="held", layout=f"archived-{layout}", original_id=key,
                        cell_phase=[0] * 9, source_ticket=PREVIOUS)
            out.append((key, wiring, meta))
    out.append(_recode(_collision(), "projection_collision", "held", "collision-0", 129293, ORDERS[17]))
    return tuple(out)


@lru_cache(maxsize=None)
def _column(question):
    result = ALL
    for clause in question:
        disjunction = 0
        for literal in clause:
            values = COLUMNS[abs(literal) - 1]
            disjunction |= values if literal > 0 else ALL ^ values
        result &= disjunction
    return result


def truth(wiring, raw):
    """Four bits in physical port order. Raw bit i is selected by literal ±(i+1)."""
    if not 0 <= raw < 512:
        raise ValueError("Expected a nine-bit raw assignment")
    return tuple((_column(question) >> raw) & 1 for question in wiring)


@lru_cache(maxsize=None)
def _orbit(answer_mask):
    """Canonical allowed answer set under all port permutations and output complements."""
    seen = [v for v in range(16) if answer_mask & (1 << v)]
    images = []
    for order in ORDERS:
        moved = [sum(((v >> old) & 1) << i for i, old in enumerate(order)) for v in seen]
        for flip in range(16):
            images.append(sum(1 << (v ^ flip) for v in moved))
    return min(images)


def characterize(wiring):
    """Finite bounds, projection witnesses and physical examples. These are evaluator-only."""
    answer_rows = [sum(bit << i for i, bit in enumerate(truth(wiring, raw))) for raw in RAW]
    counts = Counter(answer_rows)
    examples = {v: answer_rows.index(v) for v in counts}
    collisions = {}
    possible = []
    for omitted in range(4):
        other = 15 ^ (1 << omitted)
        for value in sorted(counts):
            opposite = value ^ (1 << omitted)
            if opposite in counts:
                collisions[omitted] = [examples[value], examples[opposite]]
                break
        else:
            possible.append(other)
    mask = sum(1 << v for v in counts)
    return {"answer_patterns": len(counts), "answer_mask": mask,
            "answer_counts": [counts[v] for v in range(16)],
            "minimum_bits": (len(counts) - 1).bit_length(), "three_answer_masks": possible,
            "orbit": _orbit(mask), "first_raw_by_answer": examples,
            "collision_raws_by_omitted_port": collisions,
            "ones_by_port": [_column(q).bit_count() for q in wiring]}


def audit():
    """Check the fixture contract without fitting or executing a policy."""
    train, held = training_panel(), held_panel()
    all_rows = train + held
    if (len(train), len(held), len({k for k, _, _ in all_rows}), len({w for _, w, _ in all_rows})) != (32, 89, 121, 121):
        raise AssertionError("Split sizes or physical wiring identities changed")
    results = {}
    references = {}
    observations = {}
    for key, wiring, meta in all_rows:
        for question in wiring:
            if sorted(map(len, question)) != [2, 2, 2, 3] or any(not 1 <= abs(p) <= 9 for c in question for p in c):
                raise AssertionError(f"Wiring format changed at {key}")
        row = characterize(wiring)
        results[key] = row
        references.setdefault(meta["family"], {"id": key, **row})
        observations.setdefault(meta["family"], []).append((row["answer_patterns"], len(row["three_answer_masks"])))
    expected = {"and_disjoint": (8, 1), "and_overlap": (8, 1), "or_disjoint": (8, 1), "or_overlap": (8, 1),
                "xor_triangle": (8, 3), "xor_separate": (8, 3), "open_four_compounds": (16, 0),
                "open_correlated": (12, 0), "primary_closed": (8, 2), "primary_open": (16, 0),
                "split_source_closed": (8, 2), "split_source_open": (16, 0),
                "and_or_closed": (8, 1), "and_or_open": (12, 0), "mux_closed": (8, 1), "mux_open": (12, 0),
                "rare_closed": (8, 1), "rare_open": (12, 0), "xor_closed": (8, 4), "xor_open": (16, 0),
                "projection_collision": (8, 0)}
    if set(observations) != set(expected) or any(set(v) != {expected[k]} for k, v in observations.items()):
        raise AssertionError(f"Unexpected signatures or projection sizes: {observations}")
    train_orbits = {results[k]["orbit"] for k, _, _ in train}
    novel = [references[f]["orbit"] for f in ("primary_closed", "and_or_closed", "mux_closed", "xor_closed",
                                                "projection_collision")]
    if len(set(novel)) != len(novel) or train_orbits.intersection(novel):
        raise AssertionError("A claimed held relation duplicates training or another held relation up to symmetry")
    if references["split_source_closed"]["orbit"] != references["primary_closed"]["orbit"]:
        raise AssertionError("Second primary wiring did not realize the same answer relation")
    index = {k: (w, m) for k, w, m in held}
    changes = {"primary_closed": 256, "split_source_closed": 256, "and_or_closed": 128,
               "mux_closed": 96, "rare_closed": 32, "xor_closed": 256}
    for key, wiring, meta in held:
        if meta["family"] not in changes:
            continue
        partner, other = index[meta["partner"]]
        changed = [i for i in range(4) if wiring[i] != partner[i]]
        if other["partner"] != key or changed != [meta["port_order"].index(3)]:
            raise AssertionError(f"Wrong matched port at {key}")
        port = changed[0]
        edits = {(abs(p), abs(q)) for c1, c2 in zip(wiring[port], partner[port])
                 for p, q in zip(c1, c2) if p != q}
        if len(edits) != 1 or any(x == y for x, y in edits):
            raise AssertionError(f"Expected one consistent source rewire at {key}")
        if (_column(wiring[port]) ^ _column(partner[port])).bit_count() != changes[meta["family"]]:
            raise AssertionError(f"Matched raw differences changed at {key}")
    primary_orders = {tuple(m["port_order"]) for _, _, m in held if m["family"] == "primary_closed"}
    if primary_orders != set(ORDERS):
        raise AssertionError("Missing a primary port permutation")
    return {"training": len(train), "held": len(held), "counts_by_family": {k: len(v) for k, v in observations.items()},
            "raw_answer_changes_by_closed_family": changes, "training_orbits": sorted(train_orbits),
            "representative_by_family": references}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
