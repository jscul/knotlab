"""Fresh matched two-output fixtures. build(split) returns public rows and private grades.

The only public fields are id, n, outputs. Packed bit x is the answer at input x.
The grade arrays candidate_classes and candidate_widths follow combinations(range(n), 3).
Calibration, primary held, and the two optional reserves occupy four fixed disjoint
domains. Building a split only reads frozen earlier fixtures. No probe is run here.
"""

import hashlib
import importlib.util
import json
import random
from collections import Counter
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOLD = "FOLD-TWO-OUTPUT-20261115-001"
ORDER = "TRIPLE-ORDER-20261115-001"
FOLD_DATA = f"artifacts/{FOLD}/{FOLD}-E001_joint_tables"
ORDER_DATA = f"artifacts/{ORDER}/{ORDER}-E001_rank_triples"
FOLD_MODULE = f"research/{FOLD}/tasks.py"
ORDER_MODULE = f"research/{ORDER}/panels.py"
SOURCE_HASHES = {
    FOLD_MODULE: "80a658e8b791bcb93fc56b5d09aed1364f1309cc05f3f6005d78e16749598a9f",
    ORDER_MODULE: "fa8c8650151185f94e9eb9bc4020eb7b7f936234a4b4f681d1e168ee7f1f5638",
}
ORDER_HASHES = {
    "train.json": "89fc723710a37802747116db0cbb70cc40f0274e5e03d2b3ddce596969b1500a",
    "train-grades.json": "78a3e2ff35633160dd88f937d22490cb5abe044b14ee8fd67e3f766d67847e0d",
    "held.json": "de634a3c58a262d483d168ddd4889bf23590c729fe6a3633b0a942cb5f63490a",
    "held-grades.json": "fc750e6a1bfe8df16cf4959f3e5e4652b7fb7b7c6711ebb14c9c90e0b4a99ca1",
}
SOURCE_DEPENDENCIES = (
    FOLD_MODULE, ORDER_MODULE,
    *(f"{FOLD_DATA}/{name}.json" for name in ("primary", "sensitivity", "grades")),
    *(f"{ORDER_DATA}/{name}" for name in ORDER_HASHES),
)


def _verified(relative_path, expected):
    data = (ROOT / relative_path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Frozen dependency has changed: {relative_path}")
    return data


for _path, _expected in SOURCE_HASHES.items():
    _verified(_path, _expected)
_spec = importlib.util.spec_from_file_location("_probe_witness_fixture_history", ROOT / ORDER_MODULE)
_old = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_old)

# domain, seed, pairs per arity. The archive's one-bit predicate is the low bit
# of this same byte. A second bit partitions its two domains without mutating
# the imported construction or borrowing any new task from another split.
PLAN = {
    "calibration": (0, 1493809, 8),
    "held": (1, 1558901, 32),
    "reserve_train": (2, 1608313, 8),
    "reserve_held": (3, 1780471, 16),
}


def _prior_families():
    def read(name):
        return json.loads(_verified(f"{ORDER_DATA}/{name}", ORDER_HASHES[name]))

    raw, structures = _old._archive_keys()
    for phase in ("train", "held"):
        public, grades = read(f"{phase}.json"), read(f"{phase}-grades.json")
        for row in public:
            g = grades[row["id"]]
            raw_key = _old._raw_family(row["n"], row["outputs"])
            if raw_key != g["truth_family"]:
                raise AssertionError("Archived public fingerprint mismatch")
            raw.add(raw_key)
            if g["kind"] == "shared":
                structure = _old._consumer_family(row["n"], g["logical_consumers"])
                if structure != g["structure"]:
                    raise AssertionError("Archived downstream fingerprint mismatch")
                structures.add(structure)
    return raw, structures


def _domain(key):
    return int(key[:2], 16) % 4


class _Unavailable:
    """Set protocol used by the frozen sampler; excludes archives and all other domains."""

    def __init__(self, prior, domain):
        self.seen = prior.copy()
        self.domain = domain

    def __contains__(self, key):
        return _domain(key) != self.domain or key in self.seen

    def add(self, key):
        if key in self:
            raise AssertionError("Sampler admitted an unavailable family")
        self.seen.add(key)


def build(split):
    """Generate one named split in isolation. Reserve constructors run only on request."""
    if split not in PLAN:
        raise ValueError(f"Unknown panel {split!r}; expected one of {tuple(PLAN)}")
    domain, seed, size = PLAN[split]

    def rng(purpose, n=0):
        return random.Random(_old._digest(("probe-witness-fixture-v1", seed, purpose, n)))

    _old._base._split.cache_clear()
    prior_raw, prior_structures = _prior_families()
    raw = _Unavailable(prior_raw, domain)
    structures = _Unavailable(prior_structures, domain)
    archive_side = "test" if domain % 2 else "train"
    public_ids, pair_ids = rng("public identities"), rng("private pair identities")
    tagged = []
    for n in _old.ARITIES:
        forms, names = rng("logical consumer trees", n), rng("physical raw indices", n)
        for index in range(size):
            pair = _old._sample(archive_side, n, index, forms, names, raw, structures)
            pair_id = f"{pair_ids.getrandbits(96):024x}"
            ids = [f"{public_ids.getrandbits(128):032x}" for _ in pair]
            for side, (outputs, details) in enumerate(pair):
                row = {"id": ids[side], "n": n, "outputs": outputs}
                grade = {**details, "pair": pair_id, "partner": ids[1 - side]}
                tagged.append((row, grade))
    rng("public order").shuffle(tagged)
    public = [r for r, _ in tagged]
    grades = {r["id"]: grade for r, grade in tagged}
    if len(public) != len(grades):
        raise AssertionError("Public identity collision")
    return public, grades


def _check_split(split, public, grades):
    """Grade-only replay from scalar rows, independent of the bit-packed generator."""
    domain, _, size = PLAN[split]
    by_id = {row["id"]: row for row in public}
    if len(public) != 2 * len(_old.ARITIES) * size or set(by_id) != set(grades):
        raise AssertionError("Wrong panel size or task identity set")
    counts, shared_families, paired_tables = Counter(), set(), set()
    for row in public:
        key, n, outputs = row["id"], row["n"], row["outputs"]
        g = grades[key]
        if set(row) != {"id", "n", "outputs"} or (n, *outputs) in paired_tables:
            raise AssertionError("Public fields or truth-table uniqueness failed")
        paired_tables.add((n, *outputs))
        other = grades[g["partner"]]
        other_outputs = by_id[g["partner"]]["outputs"]
        changed = g["changed_output"]
        if (other["pair"] != g["pair"] or other["partner"] != key or other["kind"] == g["kind"]
                or other["structure"] != g["structure"] or other["triple"] != g["triple"]
                or other["truth_family"] != g["truth_family"] or other["source_order"] != g["source_order"]
                or other["operation"] != g["operation"] or other["changed_output"] != changed
                or other_outputs[1 - changed] != outputs[1 - changed] or other_outputs[changed] == outputs[changed]):
            raise AssertionError("Matched source, port, or shared/rewired conditions failed")
        # The scalar implementation derives shared essential support and enumerates
        # all outside assignments directly. It uses neither a planted triple nor a probe.
        ranks = _old._base._independent_ranks(n, outputs)
        triples = tuple(combinations(range(n), 3))
        if set(ranks) != set(triples):
            raise AssertionError("An output omits a raw input")
        classes = [ranks[t] for t in triples]
        widths = [(rank - 1).bit_length() for rank in classes]
        best = min(widths)
        winners = [t for t, w in zip(triples, widths) if w == best]
        single = [_old._base._independent_ranks(n, (table, table)) for table in outputs]
        decoys = [t for t, w in zip(triples, widths) if w > best and min(s[t] for s in single) == 2]
        target = 2 if g["kind"] == "shared" else 4
        if (classes != g["candidate_classes"] or widths != g["candidate_widths"]
                or min(classes) != target or g["min_classes"] != target or ranks[g["triple"]] != target
                or winners != g["minimizers"] or winners != g["class_minimizers"] or g["width"] != best
                or (g["kind"] == "shared" and winners != [g["triple"]])
                or not decoys or decoys != g["single_output_decoys"]):
            raise AssertionError("Independent residual labels disagree")
        for expr, table in zip(g["source"], outputs):
            if any(_old._base._scalar(expr, x) != ((table >> x) & 1) for x in range(1 << n)):
                raise AssertionError("Independent source evaluation disagrees")
        if (_old._raw_family(n, outputs) != g["truth_family"]
                or _old._consumer_family(n, g["logical_consumers"]) != g["structure"]
                or any(_domain(g[k]) != domain for k in ("truth_family", "structure"))):
            raise AssertionError("Wrong public or consumer domain")
        counts[n, g["operation"], g["kind"], changed] += 1
        if g["kind"] == "shared":
            shared_families.add((g["pair"], g["structure"], g["truth_family"]))
    if (len(counts) != 24 or set(counts.values()) != {size // 4}
            or any(len({f[i] for f in shared_families}) != 3 * size for i in range(3))):
        raise AssertionError("Arity, operation, changed port or family balance failed")
    return {
        "pairs": 3 * size, "public_rows": len(public),
        "eligible_labels": sum(len(g["candidate_classes"]) for g in grades.values()),
        "public_sha256": _old._digest(public), "grades_sha256": _old._digest(grades),
        "matched_output_histogram_pairs": sum(g["kind"] == "shared" and g["joint_histogram_matched"]
                                              for g in grades.values()),
        "rewired_tied_optima": sum(g["kind"] == "rewired" and len(g["minimizers"]) > 1 for g in grades.values()),
    }


def audit():
    """Verify calibration and primary held against each other and both previous studies."""
    raw, structures = _prior_families()
    ids = set()
    report = {"relevant_prior_truth_families": len(raw), "relevant_prior_downstream_families": len(structures)}
    for split in ("calibration", "held"):
        public, grades = build(split)
        report[split] = _check_split(split, public, grades)
        here_raw = {g["truth_family"] for g in grades.values()}
        here_structure = {g["structure"] for g in grades.values()}
        if set(grades) & ids or raw & here_raw or structures & here_structure:
            raise AssertionError("Overlapping identity or family across panels")
        ids.update(grades)
        raw.update(here_raw)
        structures.update(here_structure)
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
