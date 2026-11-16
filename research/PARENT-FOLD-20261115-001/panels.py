"""Matched single-pin updates of public multi-level NAND circuits.

build returns (public, private_grades). Raw inputs are 0..n-1, false and true are
n and n+1, and gate i produces wire n+2+i. Frontier indices refer to its public
list order. No table, anchor index, edit role, or retained-bit label is public.
"""

import hashlib
import importlib.util
import json
import random
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOLD = "FOLD-TWO-OUTPUT-20261115-001"
ORDER = "TRIPLE-ORDER-20261115-001"
PROBE = "PROBE-WITNESS-20261115-001"
OLD = f"research/{ORDER}/panels.py"
ARCHIVES = {
    f"artifacts/{FOLD}/{FOLD}-E001_joint_tables/primary.json":
        "9a221c8946269dc6196bfa80ee480554b1df2d886fd7566872e30a5a97dcc314",
    f"artifacts/{FOLD}/{FOLD}-E001_joint_tables/sensitivity.json":
        "878e9768b5876166f39f222e818899cee3038997d7f9ac97d570881bdf9769d3",
    f"artifacts/{ORDER}/{ORDER}-E001_rank_triples/train.json":
        "89fc723710a37802747116db0cbb70cc40f0274e5e03d2b3ddce596969b1500a",
    f"artifacts/{ORDER}/{ORDER}-E001_rank_triples/held.json":
        "de634a3c58a262d483d168ddd4889bf23590c729fe6a3633b0a942cb5f63490a",
    f"artifacts/{PROBE}/{PROBE}-E001_fixed_probes/calibration.json":
        "3c077a7aef70acdff2d5061753904a3665f026bd2a90e8a99913652c65cbf10c",
    f"artifacts/{PROBE}/{PROBE}-E001_fixed_probes/held.json":
        "6a0600bda230ff25d68c6caa9e15a971e07302270761d3ebe13bd7774d9c3acc",
}
SOURCE_DEPENDENCIES = (OLD, f"research/{FOLD}/tasks.py", *ARCHIVES)
for _path, _sha in (
        (OLD, "fa8c8650151185f94e9eb9bc4020eb7b7f936234a4b4f681d1e168ee7f1f5638"),
        (f"research/{FOLD}/tasks.py", "80a658e8b791bcb93fc56b5d09aed1364f1309cc05f3f6005d78e16749598a9f")):
    if hashlib.sha256((ROOT / _path).read_bytes()).hexdigest() != _sha:
        raise ValueError(f"Archived fixture source changed at {_path}")
_spec = importlib.util.spec_from_file_location("_parent_fold_table_families", ROOT / OLD)
_old = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_old)
_bool = _old._base

# Fixed before constructing any circuit. Each seed supplies four parents per
# width, one for each (fold/mux, direct/conditionally masked replacement).
PLAN = {
    "oracle": ((7, 8, 9), (219841, 219857, 219871), 0),
    "train": ((8, 9, 10), (245261, 245269, 245279), 1),
    "blind": ((8, 9, 10), (281219, 281227, 281233), 2),
}
MASKS = (1, 2, 4, 6, 7, 8, 9, 11, 13, 14)  # All functions essential in both auxiliary bits.


class _Nand:
    def __init__(self, n):
        self.n = n
        self.gates = []

    def nand(self, a, b):
        wire = self.n + 2 + len(self.gates)
        self.gates.append([a, b])
        return wire

    def inv(self, a):
        return self.nand(a, a)

    def both(self, a, b):
        return self.inv(self.nand(a, b))

    def either(self, a, b):
        return self.nand(self.inv(a), self.inv(b))

    def xor(self, a, b):
        common = self.nand(a, b)
        return self.nand(self.nand(a, common), self.nand(b, common))

    def mux(self, selector, yes, no):
        return self.nand(self.nand(selector, yes), self.nand(self.inv(selector), no))

    def core(self, operation, args, alternate=False, recoded=False):
        a, b, c = args
        if operation == "fold":
            if alternate:
                b, c = c, b
            if recoded:
                return self.xor(self.nand(a, b), self.inv(c))
            return self.xor(self.both(a, b), c)
        if alternate:
            a, b = b, a
        return self.mux(self.inv(a), c, b) if recoded else self.mux(a, b, c)

    def tree(self, leaves, rng):
        forest = list(leaves)
        while len(forest) > 1:
            a = forest.pop(rng.randrange(len(forest)))
            b = forest.pop(rng.randrange(len(forest)))
            forest.append(rng.choice((self.both, self.either, self.xor))(a, b))
        return forest[0]

    def mask(self, a, b, code):
        if code in (6, 9):
            value = self.xor(a, b)
            return value if code == 6 else self.inv(value)
        negated = code.bit_count() == 3
        unique = (code ^ 15) if negated else code
        x = unique.bit_length() - 1
        value = self.both(a if x & 1 else self.inv(a), b if x & 2 else self.inv(b))
        return self.inv(value) if negated else value


def _known_piece(c, group, bit, rng):
    alias = c.inv(bit)
    records, positive = [], []
    for root, sign in ((bit, 1), (alias, 0)):
        complement = c.inv(root)
        same = c.inv(complement)
        ports = [same, complement]
        rng.shuffle(ports)
        records.append({"inputs": sorted(group), "bit": root, "ports": ports})
        positive.append(same if sign else complement)
    return records, positive


@lru_cache(maxsize=None)
def _first_in_presentation(split, m, direct, purpose):
    """Counterbalance wire age and displayed edit order separately within size and stratum."""
    seeds = PLAN[split][1]
    slots = (0, 1) if direct else (2, 3)
    cells = [(seed, slot) for seed in seeds for slot in slots]
    rng = random.Random(_old._digest(("parent presentation v1", split, m, direct, purpose)))
    return frozenset(rng.sample(cells, len(cells) // 2))


def _candidate(split, m, seed, slot, trial):
    rng = random.Random(_old._digest(("parent NAND circuit v1", split, m, seed, slot, trial)))
    n = m + 2
    c = _Nand(n)
    raw = rng.sample(range(n), n)
    codes = rng.sample(MASKS, m)
    frontier = [None] * m
    for i in rng.sample(range(m), m):
        frontier[i] = c.xor(raw[i], c.mask(raw[-2], raw[-1], codes[i]))
    boundary = len(c.gates)
    roles = rng.sample(range(m), m)
    local, outside = roles[:3], roles[3:]
    anchor_group = sorted(local)
    other_groups = rng.sample(list(combinations(outside, 3)), 2)
    operation = ("fold", "mux")[slot % 2]
    direct = slot < 2
    groups = [local, *other_groups]
    group_ops = [operation, "fold", "mux"]
    roots, positive, pieces = {}, {}, []
    for i in rng.sample(range(3), 3):
        args = [frontier[x] for x in groups[i]]
        roots[i] = c.core(group_ops[i], args, recoded=bool(rng.randrange(2)))
        rows, positive[i] = _known_piece(c, groups[i], roots[i], rng)
        pieces.extend(rows)
    rng.shuffle(pieces)
    anchor = roots[0]
    old = positive[0][rng.randrange(2)]
    args = [frontier[i] for i in local]
    e, w = (frontier[i] for i in outside[:2])
    if rng.randrange(2):
        e = c.inv(e)
    if rng.randrange(2):
        w = c.inv(w)
    original = c.xor(old, w)
    # Two alternatives are pre-existing physical wires. Neither directly feeds
    # the base gate. In the masked stratum both have exactly the same parents
    # (recomputed h, a distinct j, selector); they exchange the two MUX data pins.
    hs = old if direct else c.core(operation, args, recoded=True)
    j = c.core(operation, args, alternate=True, recoded=not direct)
    selector_flip = rng.randrange(2)
    selector = c.inv(e) if selector_flip else e
    replacements = [None, None]
    good_earlier = (seed, slot) in _first_in_presentation(split, m, direct, "physical wire age")
    for side in ((0, 1) if good_earlier else (1, 0)):
        good, bad = (hs, j) if side == 0 else (j, hs)
        if direct:
            replacement = c.inv(good)
        else:
            yes, no = (bad, good) if selector_flip else (good, bad)
            replacement = c.mux(selector, yes, no)
        # The two edits terminate at identically-shaped, private identity copies.
        replacements[side] = c.inv(c.inv(replacement))
    pin = (slot + PLAN[split][1].index(seed)) % 2
    target = c.nand(e, original) if pin else c.nand(original, e)
    outside_wires = [frontier[i] for i in outside]
    left = c.tree([*outside_wires, positive[1][0]], rng)
    right = c.tree([*outside_wires, positive[2][0]], rng)
    mixed = c.tree([positive[1][1], positive[2][1], rng.choice(outside_wires)], rng)
    common = c.xor(target, mixed)
    first = c.xor(common, left)
    context = c.tree([positive[0][1], rng.choice(outside_wires)], rng)
    mode = (slot + PLAN[split][1].index(seed) + m) % 3
    if mode == 0:
        second = c.xor(right, c.xor(common, context))
    elif mode == 1:
        second = c.xor(right, c.both(common, context))
    else:
        second = c.xor(right, c.either(common, context))
    outputs = [first, second]
    rng.shuffle(outputs)
    def opaque():
        return f"{rng.getrandbits(128):032x}"

    edit_rows = [{"id": opaque(), "gate": target, "pin": pin, "to": to} for to in replacements]
    good_first = (seed, slot) in _first_in_presentation(split, m, direct, "public edit order")
    public_edits = list(edit_rows if good_first else reversed(edit_rows))
    public = {
        "id": opaque(), "n": n, "gates": c.gates, "upstream_count": boundary,
        "frontier": frontier, "outputs": outputs, "pieces": pieces, "edits": public_edits,
    }
    private = {
        "seed": seed, "m": m, "operation": operation, "stratum": "direct" if direct else "masked",
        "mode": mode, "anchor": anchor_group, "anchor_bit": anchor, "outside": outside,
        "gate": target, "original_pin_wire": original, "gate_enable": e,
        "replacement_sources": {"surviving": hs, "alternate": j},
        "edit_ids": [r["id"] for r in edit_rows], "trial": trial,
        "anchor_piece": next(i for i, p in enumerate(pieces) if p["bit"] == anchor),
    }
    return public, private


def _stage(public, edit=None, external=None, overrides=None):
    n = public["n"]
    m = len(public["frontier"])
    dims, columns = (m, _bool._columns(m)) if external is None else external
    full = _bool._full(dims)
    first = n + 2 + public["upstream_count"]
    wires = [0] * first
    wires[n + 1] = full
    for wire, col in zip(public["frontier"], columns):
        wires[wire] = col
    for wire, inputs in enumerate(public["gates"][public["upstream_count"]:], first):
        a, b = inputs
        if edit is not None and edit["gate"] == wire:
            a, b = (edit["to"], b) if edit["pin"] == 0 else (a, edit["to"])
        value = full ^ (wires[a] & wires[b])
        wires.append(overrides.get(wire, value) if overrides is not None else value)
    return wires


def _prior_raw():
    keys = set()
    for name, expected in ARCHIVES.items():
        data = (ROOT / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Archived public fixtures changed at {name}")
        for r in json.loads(data):
            keys.add(_old._raw_family(r["n"], r["outputs"]))
    return keys


def _context_family(public, spec):
    # Treat the old bit and output of the edited NAND as two independent inputs.
    # All remaining active context sources are the m-3 stage signals outside the
    # anchor. This classifies the consumers independent of the inner operation.
    m = spec["m"]
    dims = m - 1
    independent = _bool._columns(dims)
    columns = [0] * m
    for axis, col in zip(spec["outside"], independent[2:]):
        columns[axis] = col
    values = _stage(public, external=(dims, columns), overrides={
        spec["anchor_bit"]: independent[0], spec["gate"]: independent[1],
    })
    return _old._digest(("parent outside v1", m, _old._raw_family(dims, [values[i] for i in public["outputs"]])))


def _lift(v, axes):
    return sum(((v >> j) & 1) << axis for j, axis in enumerate(axes))


def _retention(m, outputs, triple, bit_values):
    outside = [i for i in range(m) if i not in triple]
    residues = list(zip(*(_bool._residuals(m, t, triple) for t in outputs)))
    by_value = [{residues[x] for x in range(8) if bit_values[x] == b} for b in (0, 1)]
    sizes = [len(part) for part in by_value]
    result = {"old_bit_sufficient": max(sizes) == 1, "old_bit_residual_counts": sizes,
              "minimum_width_with_old_bit": 1 + (max(sizes) - 1).bit_length(),
              "old_bit_counterexample": None}
    for x, y in combinations(range(8), 2):
        if bit_values[x] != bit_values[y] or residues[x] == residues[y]:
            continue
        port = next(i for i in range(len(outputs)) if residues[x][i] != residues[y][i])
        change = residues[x][port] ^ residues[y][port]
        ext = (change & -change).bit_length() - 1
        result["old_bit_counterexample"] = {
            "inputs": [_lift(a, triple) | _lift(ext, outside) for a in (x, y)],
            "port": port, "old_bit": bit_values[x],
        }
        break
    return result


def _snapshot(m, outputs, triple, bit_values):
    groups = list(combinations(range(m), 3))
    ranks = [len(set(zip(*(_bool._residuals(m, t, group) for t in outputs)))) for group in groups]
    widths = [(rank - 1).bit_length() for rank in ranks]
    best = min(widths)
    return {"outputs": outputs, "width": best, "min_classes": min(ranks),
            "minimizers": [g for g, w in zip(groups, widths) if w == best], "candidate_classes": ranks,
            **_retention(m, outputs, triple, bit_values)}


def _grade(public, spec, domain, occupied, seen_contexts):
    m, group = spec["m"], spec["anchor"]
    context = _context_family(public, spec)
    if int(context[:8], 16) % 3 != domain or context in seen_contexts:
        return None
    by_id = {e["id"]: e for e in public["edits"]}
    edits = [by_id[key] for key in spec["edit_ids"]]
    states = [_stage(public, e) for e in (None, *edits)]
    outputs = [[w[i] for i in public["outputs"]] for w in states]
    keys = [_old._raw_family(m, pair) for pair in outputs]
    if (any(int(k[:8], 16) % 3 != domain or k in occupied for k in keys)
            or len(set(keys)) != 3):
        return None
    if any(len(_bool._support(m, t)) != m for pair in outputs for t in pair):
        return None
    if any(p[0] == p[1] or (p[0] ^ p[1]) == _bool._full(m) for p in outputs):
        return None
    if any(a == b for pair in outputs[1:] for a, b in zip(outputs[0], pair)):
        return None
    old = states[0][spec["anchor_bit"]]
    code = [(old >> _lift(x, group)) & 1 for x in range(8)]
    details = [_snapshot(m, pair, group, code) for pair in outputs]
    expected = (2, 2, 4)
    if any(d["min_classes"] != count or tuple(group) not in d["minimizers"]
           for d, count in zip(details, expected)):
        return None
    if any(d["minimizers"] != [tuple(group)] for d in details[:2]):
        return None
    if [d["old_bit_sufficient"] for d in details] != [True, True, False]:
        raise AssertionError("Matched pin change broke the specified semantic construction")
    by_role = {}
    for e, role, d, current in zip(edits, ("surviving", "broken"), details[1:], states[1:]):
        delta = (states[0][spec["gate"]] ^ current[spec["gate"]]).bit_count()
        if delta != 1 << (m - 2):
            raise AssertionError("The two edits must change the NAND on a quarter of the rows")
        by_role[e["id"]] = {
            **d, "kind": role, "changed_outputs": [0, 1],
            "output_change_counts": [(a ^ b).bit_count() for a, b in zip(outputs[0], d["outputs"])],
            "target_change_count": delta,
            "replacement_alone_old_bit_sufficient": _retention(m, [states[0][e["to"]]], group, code)["old_bit_sufficient"],
        }
    seen_contexts.add(context)
    occupied.update(keys)
    return {**spec, "structure": context, "truth_families": keys,
            "base": {**details[0], "anchor": group, "anchor_bit": spec["anchor_bit"],
                     "anchor_piece": spec["anchor_piece"], "old_bit_local_values": code},
            "edits": by_role}


def build(split="oracle"):
    """Build only the requested split. train and blind are conditional reserve names."""
    arities, seeds, domain = PLAN[split]
    _bool._split.cache_clear()
    occupied = _prior_raw()
    contexts, entries = set(), []
    for seed in seeds:
        for m in arities:
            for slot in range(4):
                for trial in range(1, 8193):
                    public, spec = _candidate(split, m, seed, slot, trial)
                    grade = _grade(public, spec, domain, occupied, contexts)
                    if grade is not None:
                        entries.append((public, grade))
                        break
                else:
                    raise RuntimeError(f"No eligible parent for {split}, {m}, {seed}, {slot}")
    random.Random(_old._digest(("parent public order", split))).shuffle(entries)
    return [p for p, _ in entries], {p["id"]: g for p, g in entries}


def _raw_replay(p, edit=None):
    """Evaluate every raw assignment from wire zero, without replacing the prefix."""
    n = p["n"]
    mask = (1 << (1 << n)) - 1
    words = [*_bool._columns(n), 0, mask]
    for wire, row in enumerate(p["gates"], n + 2):
        pins = list(row)
        if edit is not None and wire == edit["gate"]:
            pins[edit["pin"]] = edit["to"]
        if any(pin < 0 or pin >= wire for pin in pins):
            raise AssertionError("Wire does not precede its consumer")
        words.append(mask ^ (words[pins[0]] & words[pins[1]]))
    return words


def _frontier_replay(p, words):
    n = p["n"]
    frontier = p["frontier"]
    m = len(frontier)
    boundary = n + 2 + p["upstream_count"]
    if any(not n + 2 <= w < boundary for w in frontier) or len(set(frontier)) != m:
        raise AssertionError("An asserted frontier signal is not a distinct upstream gate")
    active = {n, n + 1, *frontier}
    for wire in range(boundary, n + 2 + len(p["gates"])):
        if not set(p["gates"][wire - n - 2]) <= active:
            raise AssertionError("Downstream circuit bypasses the frontier")
        active.add(wire)
    supports = [set(_bool._support(n, words[w])) for w in frontier]
    aux = set.intersection(*supports)
    if len(aux) != 2 or any(len(s) != 3 for s in supports) or len(set.union(*supports)) != n:
        raise AssertionError("Each frontier signal must use its own raw signal and the two common auxiliaries")
    aux_assignments = _bool._assignments(tuple(sorted(aux)))
    masks = {tuple((words[w] >> raw) & 1 for raw in aux_assignments) for w in frontier}
    if len(masks) != m:
        raise AssertionError("Repeated auxiliary mask")
    lifts = [[] for _ in range(1 << m)]
    for raw in range(1 << n):
        code = sum(((words[w] >> raw) & 1) << j for j, w in enumerate(frontier))
        lifts[code].append(raw)
    if any(len(x) != 4 for x in lifts):
        raise AssertionError("The frontier does not have four raw preimages at every assignment")
    return lifts


def _project(word, lifts):
    value = 0
    for x, raw_states in enumerate(lifts):
        bits = {(word >> r) & 1 for r in raw_states}
        if len(bits) != 1:
            raise AssertionError("The physical wire varies at fixed frontier assignment")
        value |= bits.pop() << x
    return value


def _check_snapshot(m, outputs, old, g, group):
    counts = _bool._independent_ranks(m, outputs)
    triples = tuple(combinations(range(m), 3))
    if set(counts) != set(triples):
        raise AssertionError("Both outputs must depend essentially on every frontier signal")
    ranks = [counts[t] for t in triples]
    best = (min(ranks) - 1).bit_length()
    winners = [t for t in triples if (counts[t] - 1).bit_length() == best]
    if (g["outputs"] != outputs or g["candidate_classes"] != ranks or g["min_classes"] != min(ranks)
            or g["width"] != best or winners != g["minimizers"]):
        raise AssertionError("Direct scalar global grouping differs from the saved grade")
    inners = _bool._assignments(tuple(group))
    outside = _bool._assignments(tuple(i for i in range(m) if i not in group))
    partitions = [set(), set()]
    for inner in inners:
        bit = (old >> inner) & 1
        if any(((old >> (inner | outer)) & 1) != bit for outer in outside):
            raise AssertionError("The old physical bit varies at fixed triple")
        signature = tuple(sum(((t >> (inner | outer)) & 1) << i for i, t in enumerate(outputs))
                          for outer in outside)
        partitions[bit].add(signature)
    per_bit = [len(s) for s in partitions]
    if (g["old_bit_residual_counts"] != per_bit or g["old_bit_sufficient"] != (max(per_bit) == 1)
            or g["minimum_width_with_old_bit"] != 1 + (max(per_bit) - 1).bit_length()):
        raise AssertionError("The physical old bit and the saved sufficiency grade disagree")
    witness = g["old_bit_counterexample"]
    if witness:
        x, y = witness["inputs"]
        o = outputs[witness["port"]]
        group_mask = sum(1 << i for i in group)
        if ((x ^ y) & ~group_mask or ((old >> x) & 1) != ((old >> y) & 1)
                or ((old >> x) & 1) != witness["old_bit"] or ((o >> x) & 1) == ((o >> y) & 1)):
            raise AssertionError("Invalid old-bit counterexample")
    if bool(witness) == g["old_bit_sufficient"]:
        raise AssertionError("Unexpected witness presence")


def _audit_parent(p, grade):
    required = {"id", "n", "gates", "upstream_count", "frontier", "outputs", "pieces", "edits"}
    m, n = grade["m"], p["n"]
    if set(p) != required or n != m + 2 or len(p["outputs"]) != 2:
        raise AssertionError("Wrong public schema")
    baseline = _raw_replay(p)
    lifts = _frontier_replay(p, baseline)
    group = grade["base"]["anchor"]
    old = _project(baseline[grade["base"]["anchor_bit"]], lifts)
    offered = Counter()
    for piece in p["pieces"]:
        t = _project(baseline[piece["bit"]], lifts)
        if (set(piece) != {"inputs", "bit", "ports"} or tuple(piece["inputs"]) != _bool._support(m, t)
                or len(piece["inputs"]) != 3 or len(set(piece["ports"])) != 2):
            raise AssertionError("Invalid local piece or public fields")
        readings = [_project(baseline[i], lifts) for i in piece["ports"]]
        if set(readings) != {t, _bool._full(m) ^ t}:
            raise AssertionError("Local readings are not nonconstant unary functions of this bit")
        offered[tuple(piece["inputs"])] += 1
    if len(offered) < 3 or len(set(offered.values())) != 1:
        raise AssertionError("Wrong number of local groups or uneven aliasing")
    base_outputs = [_project(baseline[w], lifts) for w in p["outputs"]]
    _check_snapshot(m, base_outputs, old, grade["base"], group)
    target, pin = p["edits"][0]["gate"], p["edits"][0]["pin"]
    first_downstream = n + 2 + p["upstream_count"]
    if (target < first_downstream or target in p["outputs"] or len(p["edits"]) != 2
            or p["edits"][0]["to"] == p["edits"][1]["to"]):
        raise AssertionError("Expected two real changes to one downstream internal gate")
    # Minimum topological depth from the edited gate to each public reading.
    paths = {target: 0}
    for wire in range(target + 1, len(baseline)):
        reached = [paths[t] for t in p["gates"][wire - n - 2] if t in paths]
        if reached:
            paths[wire] = min(reached) + 1
    if min(paths.get(w, -1) for w in p["outputs"]) < 2:
        raise AssertionError("Both outputs must have actual consumers above the changed gate")
    for edit in p["edits"]:
        if (set(edit) != {"id", "gate", "pin", "to"} or edit["gate"] != target or edit["pin"] != pin
                or edit["to"] >= target or edit["to"] == p["gates"][target - n - 2][pin]):
            raise AssertionError("Edits do not share one legal original pin")
        d = grade["edits"][edit["id"]]
        after = _raw_replay(p, edit)
        outputs = [_project(after[w], lifts) for w in p["outputs"]]
        _check_snapshot(m, outputs, old, d, group)
        diff = [(x ^ y).bit_count() for x, y in zip(base_outputs, outputs)]
        expected = 1 if d["kind"] == "surviving" else 2
        if (d["width"] != expected or d["old_bit_sufficient"] != (expected == 1)
                or d["minimum_width_with_old_bit"] != expected or d["changed_outputs"] != [0, 1]
                or min(diff) <= 0 or diff != d["output_change_counts"] or min(diff) > (1 << (m - 2))
                or (baseline[target] ^ after[target]).bit_count() != 1 << (n - 2)):
            raise AssertionError("Retained/broken truth or output change is not the specified one")
        feeder = _project(baseline[edit["to"]], lifts)
        feeder_ranks = set()
        for bit_value in (0, 1):
            outsides = _bool._assignments(tuple(i for i in range(m) if i not in group))
            feeder_ranks.add(len({tuple((feeder >> (outside | inner)) & 1 for outside in outsides)
                                  for inner in _bool._assignments(tuple(group)) if (old >> inner) & 1 == bit_value}))
        observed = max(feeder_ranks) == 1
        if (d["replacement_alone_old_bit_sufficient"] != observed
                or observed != (grade["stratum"] == "direct" and d["kind"] == "surviving")):
            raise AssertionError("Replacement-wire aliasing control failed")
    return min(paths[w] for w in p["outputs"])


def audit(split="oracle"):
    """Independent physical and scalar grading of just the requested split."""
    public, grades = build(split)
    arities, seeds, domain = PLAN[split]
    cells = Counter()
    positions = Counter()
    previous, seen_contexts = _prior_raw(), set()
    summary = Counter()
    depths = []
    for p in public:
        g = grades[p["id"]]
        depths.append(_audit_parent(p, g))
        cells[g["m"], g["seed"], g["operation"], g["stratum"]] += 1
        if (any(k in previous or int(k[:8], 16) % 3 != domain for k in g["truth_families"])
                or g["structure"] in seen_contexts or int(g["structure"][:8], 16) % 3 != domain):
            raise AssertionError("Structural or output family collision")
        previous.update(g["truth_families"])
        seen_contexts.add(g["structure"])
        d, e = (g["edits"][x["id"]] for x in p["edits"])
        positions[g["m"], g["stratum"], "first", d["kind"] == "surviving"] += 1
        first_earlier = p["edits"][0]["to"] < p["edits"][1]["to"]
        positions[g["m"], g["stratum"], "earlier", first_earlier == (d["kind"] == "surviving")] += 1
        summary["pairs_matching_both_output_change_counts"] += d["output_change_counts"] == e["output_change_counts"]
        summary["masked_parents"] += g["stratum"] == "masked"
        summary["broken_edits_with_tied_minima"] += any(x["kind"] == "broken" and len(x["minimizers"]) > 1
                                                        for x in (d, e))
    if (len(public) != 4 * len(arities) * len(seeds) or len(cells) != len(public)
            or set(cells.values()) != {1} or len(grades) != len(public)
            or len(positions) != 8 * len(arities) or set(positions.values()) != {len(seeds)}):
        raise AssertionError("Unbalanced panel cells")
    return {
        **summary, "parents": len(public), "edits": 2 * len(public),
        "gate_count_range": [min(len(p["gates"]) for p in public), max(len(p["gates"]) for p in public)],
        "minimum_downstream_depth": min(depths),
        "global_candidate_labels": sum(len(d["candidate_classes"]) for g in grades.values()
                                       for d in (g["base"], *g["edits"].values())),
        "old_truth_families_excluded": len(_prior_raw()),
        "public_sha256": _old._digest(public), "grades_sha256": _old._digest(grades),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
