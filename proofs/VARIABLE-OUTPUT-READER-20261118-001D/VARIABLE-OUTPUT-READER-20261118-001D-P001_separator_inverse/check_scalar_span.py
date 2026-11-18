"""Infer forced short parity equations from a scalar matrix without an incidence input."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PREV = HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001C" / "VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse"
NINETEEN = HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001B" / "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen"
assert sha256((PREV / "check_gluing.py").read_bytes()).hexdigest() == "6ce8aa70d9ec7ead98da8a4bfd0c891a935dc0cc2fb4effa3bad3e885f653335"
sys.path.insert(0, str(PREV))
import check_gluing as bridge


def names(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def as_mask(indices):
    return sum(1 << i for i in indices)


def span(generators):
    words = {0}
    for row in generators:
        if row not in words:
            words |= {old ^ row for old in words}
    return words


def short_cliques(table, width, size):
    """All sets of the required size whose every pair can share so short a bond."""
    links = []
    for i in range(width):
        links.append(as_mask(j for j in range(i + 1, width) if table[i, j] is not None
                             and table[i, j] < size))

    def extend(prefix, pool, left):
        if left == 0:
            yield prefix
            return
        while pool.bit_count() >= left:
            bit = pool & -pool
            pool ^= bit
            yield from extend(prefix | bit, pool & links[bit.bit_length() - 1], left - 1)

    return tuple(extend(0, (1 << width) - 1, size))


def infer(table, width):
    by_size = {k: short_cliques(table, width, k) for k in range(3, 7)}
    shapes = {w for group in by_size.values() for w in group}
    # Any nonzero dual word splits into disjoint minimal words. Up to size six
    # this allows one bond, or two disjoint ternary bonds.
    allowed_short = set(shapes)
    allowed_short.update(a | b for a, b in combinations(by_size[3], 2) if a & b == 0)
    obligations = defaultdict(list)
    for w in shapes:
        for pair in combinations(names(w), 2):
            if table[pair] == w.bit_count() - 1:
                obligations[pair].append(w)
    tight = {pair for pair, dist in table.items() if dist is not None and dist <= 5}
    if tight != obligations.keys():
        raise ValueError("a short minimum has no compatible support")
    known = {0}
    passes = []
    while True:
        known_short = [x for x in known if x and x.bit_count() < 6]
        viable = set()
        for w in shapes:
            if any(w & x == x and w != x for x in known_short):
                continue
            if w not in known and any(0 < (z := w ^ x).bit_count() <= 6 and z not in allowed_short
                                      for x in known):
                continue
            viable.add(w)
        forced = set()
        for pair, group in obligations.items():
            possible = [w for w in group if w in viable]
            if not possible:
                raise ValueError(f"no minimal parity support can attain the observed pair {pair}")
            if len(possible) == 1:
                forced.add(possible[0])
        passes.append({"rank_before": len(known).bit_length() - 1, "viable_supports": len(viable),
                       "uniquely_witnessed": len(forced)})
        new = sorted(forced - known)
        if not new:
            break
        for word in new:
            if word not in known:
                known |= {old ^ word for old in known}
    undecided = viable - known
    return known, undecided, passes


def read_json(path, expected):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == expected
    return json.loads(raw)


def fixtures():
    small = read_json(NINETEEN / "near_witness.json",
                      "960ec63a1a23da44e6c70a489fd8bd27f6ab6152efe8a7599c47a72b2adb42da")
    twenty = read_json(PREV / "parity.json",
                       "c70aa4d9f59a48c21ea0d9325e0249b09051322586ffd60888deb6706a4f335e")
    larger = read_json(PREV / "witness.json",
                       "7685dbb6636b3611a6e8a1f090bba446365feeaad00f22437594bfa3b6fd93ca")
    for n, case, key in [(19, small, "junction_supports"),
                         (20, twenty["results"]["to_other_distinctions"]["smallest_witness"], "junction_supports"),
                         (27, larger["padded_witness"], "checks"),
                         (28, larger["exact_count_witness"], "checks")]:
        for side in ("legal_side", "forbidden_side"):
            marked_key = "operands" if n == 20 else "marked"
            yield f"{n}_{side}", n, case[side][key], tuple(case[side][marked_key])


def compare_truth(name, width, checks, matrix):
    known, undecided, passes = infer(matrix, width)
    truth = span(as_mask(s) for s in checks)
    assert known <= truth and all(as_mask(s) in known | undecided for s in checks)
    if not undecided:
        assert known == truth
    return {"name": name, "width": width, "true_rank": len(truth).bit_length() - 1,
            "forced_rank": len(known).bit_length() - 1, "undecided_possible_stars": len(undecided),
            "proves_unique_dual_from_the_scalar_table": not undecided, "passes": passes}


def restrict(table, kept):
    return {(a, b): table[kept[a], kept[b]] for a, b in combinations(range(len(kept)), 2)}


def controls():
    assert sha256((PREV / "check_core.py").read_bytes()).hexdigest() == "2499b1bd43e3af655a599e3216ae42a138b1c1e0e501afb9ed70c4f9c7ed5750"
    import check_core as trim
    records = []
    for name, width, checks, marks in fixtures():
        matrix = bridge.scalar_table(bridge.minimal_dual(checks), width)
        original = compare_truth(name, width, checks, matrix)
        kept = trim.retained_part(trim.matrix_from_pairs(matrix, width), marks)
        assert kept is not None
        labels = {old: i for i, old in enumerate(kept)}
        local = [[labels[i] for i in star] for star in checks if set(star) <= labels.keys()]
        retained = compare_truth(name, len(kept), local, restrict(matrix, kept))
        records.append({"original": original, "retained": retained})
    return records


def run():
    # These instructions use only the matrix. False tables exercise the infeasible path.
    bad = {(0, 1): 2, (0, 2): 3, (1, 2): 2}
    try:
        infer(bad, 3)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("failed to detect an impossible distance table")
    return {"fixtures": controls(),
            "deliberately_wrong_table_rejected": message}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
