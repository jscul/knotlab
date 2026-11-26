"""Check the retained side tables without importing the census or scoring code."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from itertools import combinations, product
import json
import math
from pathlib import Path
import re
import resource
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words"
SEED = 2026112603
MASKS = tuple(range(1, 16))


def old_bits(value):
    return tuple((value >> offset) & 1 for offset in (2, 1, 0))


def fresh_values(old, setting):
    x1, x2, x3 = old_bits(old)
    parent = (x2, x3)[setting]
    return tuple(fresh for fresh in (0, 1) if len({x1, parent, fresh}) > 1)


BIRTHS = [[fresh_values(x, setting) for x in range(8)] for setting in (0, 1)]
W = np.array([[len(v) for v in rows] for rows in BIRTHS], dtype=np.int64)
RESPONSE = np.array([
    [[sum((-1) ** ((mask & (2 * x + z)).bit_count()) for z in old)
      for x, old in enumerate(rows)] for mask in MASKS]
    for rows in BIRTHS
], dtype=np.int64)
SWAP = tuple(4 * a + 2 * c + b for a, b, c in map(old_bits, range(8)))
ROW_MAPS = np.array([
    tuple((SWAP[x] if swap else x) ^ (7 if flip else 0) for x in range(8))
    for swap, flip in product((False, True), repeat=2)
])
MAX_INT = np.iinfo(np.int64).max


def primitive(row):
    factor = math.gcd(*row)
    if factor:
        if next(x for x in row if x) < 0:
            factor = -factor
        return tuple(x // factor for x in row)
    return tuple(row)


@cache
def row_basis(rows):
    """Primitive integral form of the unique reduced row basis over the rationals."""
    basis = {}
    for row in rows:
        for pivot, existing in basis.items():
            if row[pivot]:
                row = primitive([a * existing[pivot] - b * row[pivot]
                                 for a, b in zip(row, existing)])
        if any(row):
            pivot = next(i for i, v in enumerate(row) if v)
            for old_pivot, existing in basis.items():
                if existing[pivot]:
                    basis[old_pivot] = primitive([
                        b * row[pivot] - a * existing[pivot] for a, b in zip(row, existing)
                    ])
            basis[pivot] = row
    return tuple(basis[pivot] for pivot in sorted(basis))


def wedge(u, v):
    return tuple(u[i] * v[j] - u[j] * v[i] for i, j in combinations(range(len(u)), 2))


def codes(items):
    ids = {}
    indices = []
    for item in items:
        indices.append(ids.setdefault(item, len(ids)))
    return np.array(indices), list(ids)


def support(tables):
    return tables.any(axis=1) @ (1 << np.arange(tables.shape[-1]))


def compatibility(tables):
    """The projected far-setting vectors have rank at most one iff these minors vanish."""
    size = tables.shape[-1]
    width = math.comb(size, 2)
    setting_totals = W @ tables
    rows = (tuple(sorted({primitive(row) for row in table.tolist() if any(row)}))
            for table in tables)
    span_codes, spans = codes(map(row_basis, rows))
    weight_codes, weights = codes(
        primitive(wedge(*v)) for v in setting_totals.tolist()
    )
    span_wedges = np.zeros((len(spans), width, width), dtype=np.int64)
    for i, basis in enumerate(spans):
        for j, (u, v) in enumerate(combinations(basis, 2)):
            span_wedges[i, j] = wedge(u, v)
    weights = np.array(weights, dtype=np.int64).T
    assert int(np.abs(span_wedges).max()) * int(np.abs(weights).max()) * width <= MAX_INT
    compatible = np.empty((len(spans), weights.shape[1]), dtype=bool)
    for i in range(0, len(spans), 128):
        compatible[i:i + 128] = (span_wedges[i:i + 128] @ weights == 0).all(axis=1)
    row_basis.cache_clear()
    return span_codes, weight_codes, compatible


def archive_counts(tables, flags, blocks, unordered, row_limit=None):
    spans, weights, hide = compatibility(tables)
    supports = support(tables)
    n = len(tables)
    j = np.arange(n)
    totals = Counter()
    matches = []
    for summary in blocks:
        start, end = summary["rows"]
        if row_limit is not None:
            end = min(end, start + row_limit)
        count = Counter()
        for lo in range(start, end, 128):
            i = np.arange(lo, min(lo + 128, end))
            selected = j >= i[:, None] if unordered else np.ones((len(i), n), dtype=bool)
            has_words = (supports[i, None] & supports[j]) != 0
            hidden = hide[spans[i, None], weights[j]] & hide[spans[j], weights[i, None]]
            both_alloc = flags[i, None] & flags[j]
            present = selected & has_words
            count.update(
                pairs_with_no_word=int((selected & ~has_words).sum()),
                pairs_evaluated=int(present.sum()),
                pairs_hidden=int((present & hidden).sum()),
                alloc_pairs=int((present & both_alloc).sum()),
                pairs_hidden_alloc=int((present & hidden & both_alloc).sum()),
            )
        totals.update(count)
        match = {key: [count[key], summary[key]] for key in count if count[key] != summary[key]}
        matches.append(dict(rows=[start, end], mismatches=match if row_limit is None else None))
    return dict(totals=dict(totals), blocks=matches, row_span_kinds=hide.shape[0],
                setting_span_kinds=hide.shape[1])


def archive_side_tables(tag):
    path = ART / f"sides_{tag}.npz"
    with np.load(path) as archive:
        tables = archive["T"].astype(np.int64)
        flags = archive["alloc"]
        nonempty = archive["nonempty"]
    assert (tables >= 0).all()
    assert np.array_equal(nonempty, tables.any(axis=(1, 2)))
    assert len(tables) == len(np.unique(tables, axis=0))
    named = ART / f"sides_{tag}.json"
    opener = open if named.exists() else gzip.open
    path = named if named.exists() else named.with_suffix(".json.gz")
    with opener(path, "rt") as infile:
        provenance = json.load(infile)
    assert len(provenance["structures"]) == len(tables)
    assert np.array_equal(flags, [x["alloc_struct"] is not None for x in provenance["structures"]])
    return tables, flags, nonempty, provenance


def side_views(tables, flags, nonempty):
    exact = tables[nonempty]
    flagged = flags[nonempty]
    factor = np.gcd.reduce(exact.reshape(len(exact), -1), axis=1)
    normal = exact // factor[:, None, None]
    projective, index = np.unique(normal, axis=0, return_inverse=True)
    projective_flags = np.zeros(len(projective), dtype=bool)
    np.logical_or.at(projective_flags, index.reshape(-1), flagged)
    keys = [
        min(tuple(table[p].ravel()) for p in ROW_MAPS)
        for table in projective
    ]
    orbit_ids, _ = codes(keys)
    representatives = np.full(max(orbit_ids) + 1, len(projective), dtype=np.int64)
    np.minimum.at(representatives, orbit_ids, np.arange(len(projective)))
    orbit_flags = np.zeros(len(representatives), dtype=bool)
    np.logical_or.at(orbit_flags, orbit_ids, projective_flags)
    return (projective, projective_flags), (projective[representatives], orbit_flags), orbit_ids


def empty_ordered_pairs(tables):
    signatures = Counter(support(tables).tolist())
    return sum(a * b for x, a in signatures.items() for y, b in signatures.items() if not x & y)


def archive_blocks(tag, tables):
    paths = ART.glob(f"pairs_{tag}_*_summary.json")
    blocks = sorted([json.loads(path.read_text()) for path in paths], key=lambda d: d["rows"])
    assert blocks[0]["rows"][0] == 0
    assert blocks[-1]["rows"][1] == tables
    assert [x["rows"][1] for x in blocks[:-1]] == [x["rows"][0] for x in blocks[1:]]
    for block in blocks:
        lo, hi = block["rows"]
        expected = sum(tables - i for i in range(lo, hi)) if block["sym"] else tables * (hi - lo)
        assert block["tables_combined"] == tables
        assert block["pairs_evaluated"] + block["pairs_with_no_word"] == expected
    return blocks


def old_matrices(tables, left, right):
    return tables[left] @ tables[right].transpose(0, 2, 1)


def hiding(matrices):
    both_hidden = np.ones(len(matrices), dtype=bool)
    for old in (matrices, matrices.transpose(0, 2, 1)):
        marginal = old @ W.T
        both_hidden &= (marginal[:, :, 0] * marginal[:, :, 1].sum(1)[:, None]
                        == marginal[:, :, 1] * marginal[:, :, 0].sum(1)[:, None]).all(1)
    return both_hidden & matrices.any(axis=(1, 2))


def denominators(matrices):
    den = (W @ matrices @ W.T).reshape(-1, 4)
    common = np.ones(len(den), dtype=np.int64)
    for cell in den.T:
        multiply = cell // np.gcd(common, cell)
        if np.any(common > (MAX_INT // 4) // multiply):
            den = den.astype(object)
            common = np.array([math.lcm(*row) for row in den.tolist()], dtype=object)
            break
        common *= multiply
    return common, common[:, None] // den


def parity(matrices):
    common, scale = denominators(matrices)
    c = [(RESPONSE[a] @ matrices @ RESPONSE[b].T) * scale[:, i, None, None]
         for i, (a, b) in enumerate(product(range(2), repeat=2))]
    best = np.zeros(len(matrices), dtype=common.dtype)
    # Flipping the second Alice parity and both Bob output signs accounts for
    # every one-minus sign choice and the absolute value.
    for sign in (1, -1):
        v0 = np.abs(c[0][:, :, None, :] + sign * c[2][:, None, :, :]).max(axis=3)
        v1 = np.abs(c[1][:, :, None, :] - sign * c[3][:, None, :, :]).max(axis=3)
        best = np.maximum(best, (v0 + v1).max(axis=(1, 2)))
    return best, common


def scores(matrices, flags=None):
    maximum = {k: Fraction(-1) for k in ("all", "hidden", "allocation")}
    counts = Counter({k: 0 for k in ("tables", "hidden", "allocation", "all_gt2",
                                     "hidden_eq2", "hidden_gt2", "hidden_alloc_eq2")})
    for i in range(0, len(matrices), 256):
        batch = matrices[i:i + 256]
        factor = np.gcd.reduce(batch.reshape(-1, 64), axis=1)
        batch = batch // factor[:, None, None]
        hidden = hiding(batch)
        alloc = np.zeros(len(batch), dtype=bool) if flags is None else flags[i:i + 256]
        num, den = parity(batch)
        counts.update(tables=len(batch), hidden=int(hidden.sum()), allocation=int(alloc.sum()),
                      all_gt2=int((num > 2 * den).sum()),
                      hidden_eq2=int((hidden & (num == 2 * den)).sum()),
                      hidden_gt2=int((hidden & (num > 2 * den)).sum()),
                      hidden_alloc_eq2=int((hidden & alloc & (num == 2 * den)).sum()))
        for name, selected in (("all", slice(None)), ("hidden", hidden), ("allocation", alloc)):
            v = np.stack([num[selected], den[selected]], axis=1)
            values = (Fraction(int(a), int(b)) for a, b in set(map(tuple, v.tolist())))
            maximum[name] = max(maximum[name], max(values, default=Fraction(-1)))
    return dict(counts=counts, maximum={k: str(n) if n >= 0 else None for k, n in maximum.items()})


def canon_matrices(matrices):
    factor = np.gcd.reduce(matrices.reshape(-1, 64), axis=1)
    narrowed = matrices // factor[:, None, None]
    # Old tables in the small census fit in one byte per entry. Pack each
    # row for lexicographic comparison, keeping full keys instead of hashes.
    assert narrowed.max() < 256
    narrowed = narrowed.astype(np.uint8)
    best = narrowed.view(">u8").reshape(-1, 8).copy()
    rows = np.arange(len(best))
    for a, b, transpose in product(ROW_MAPS, ROW_MAPS, range(2)):
        image = narrowed[:, a[:, None], b]
        if transpose:
            image = image.transpose(0, 2, 1)
        image = np.ascontiguousarray(image).view(">u8").reshape(-1, 8)
        first = (image != best).argmax(axis=1)
        less = image[rows, first] < best[rows, first]
        best[less] = image[less]
    return best.view("V64").ravel()


def score_small(tables, flags, row_limit):
    old = {}
    n = len(tables)
    stop = n if row_limit is None else min(row_limit, n)
    for lo in range(0, stop, 32):
        i, j = np.nonzero(np.arange(lo, min(lo + 32, stop))[:, None] <= np.arange(n))
        i += lo
        matrices = old_matrices(tables, i, j)
        alive = matrices.any(axis=(1, 2))
        keys = canon_matrices(matrices[alive])
        alloc = (flags[i] & flags[j])[alive]
        for key in keys.tolist():
            old.setdefault(key, False)
        for key in keys[alloc].tolist():
            old[key] = True
    matrix = np.frombuffer(b"".join(old), dtype=np.uint8).reshape(-1, 8, 8).astype(np.int64)
    return scores(matrix, np.array(list(old.values()), dtype=bool))


def sample_larger(tables, flags, sample, rng):
    n = len(tables)
    count = n * (n + 1) // 2
    chosen = rng.choice(count, size=min(sample, count), replace=False)
    offsets = np.r_[0, np.arange(n, 0, -1).cumsum()]
    i = np.searchsorted(offsets, chosen, side="right") - 1
    j = i + chosen - offsets[i]
    matrices = old_matrices(tables, i, j)
    nonzero = matrices.any(axis=(1, 2))
    return dict(attempted=len(chosen), no_word=int((~nonzero).sum()),
                **scores(matrices[nonzero], (flags[i] & flags[j])[nonzero]))


def check_max_witnesses(blocks):
    old = []
    result = []
    for block in blocks:
        for item in (block.get("top_hidden"), block.get("top_nonhidden")):
            if item is not None:
                matrix = np.array(item["M"], dtype=np.int64)
                check = np.array(item["T_A"], dtype=np.int64) @ np.array(item["T_B"], dtype=np.int64).T
                assert np.array_equal(matrix, check // math.gcd(*check.ravel()))
                old.append(matrix)
                result.append((item["exact"], item["hidden"]))
    old = np.array(old, dtype=np.int64)
    num, den = parity(old)
    rebuilt = [(str(Fraction(int(a), int(b))), bool(h)) for a, b, h in zip(num, den, hiding(old))]
    assert rebuilt == result
    return len(rebuilt)


@cache
def signs(n, fix_first=False):
    code = np.arange(2 ** (n - fix_first))
    return 1 - 2 * (((code[:, None] << fix_first) >> np.arange(n)) & 1)


def unrestricted(matrix):
    """Exact maximum after averaging fresh inputs locally and optimizing Bob's signs."""
    if matrix.any(axis=1).sum() > matrix.any(axis=0).sum():
        matrix = matrix.T
    common, scale = denominators(matrix[None])
    seen = matrix.any(axis=1)
    other = matrix.any(axis=0)
    matrix = matrix[np.ix_(seen, other)]
    n = matrix.shape[0]
    a0, a1 = signs(n, True), signs(n)
    score = np.zeros((len(a0), len(a1)), dtype=common.dtype)
    for b in range(2):
        left = a0 @ (matrix * W[0, seen][:, None] * W[b, other][None, :] * scale[0, b])
        right = a1 @ (matrix * W[1, seen][:, None] * W[b, other][None, :] * scale[0, 2 + b])
        for y in range(matrix.shape[1]):
            score += np.abs(left[:, y, None] + (-1) ** b * right[None, :, y])
    return Fraction(int(score.max()), int(common[0]))


def check_unrestricted(cut, larger_n, rng, pilot):
    start = time.monotonic()
    with np.load(ART / f"extras_c{cut}_tables.npz") as files:
        matrices = files["M"].astype(np.int64)
        census = files["in_census"]
    small = np.flatnonzero(census)
    other = np.flatnonzero(~census)
    selected_small = rng.choice(small, 16, replace=False) if pilot else small
    selected_big = rng.choice(other, min(larger_n, len(other)), replace=False)
    maximum = {}
    for label, indices in (("small_census", selected_small), ("extended_only", selected_big)):
        selected = matrices[indices]
        score = scores(selected)["counts"]
        assert score["hidden_eq2"] == len(selected) == score["hidden"]
        seen = Counter(str(unrestricted(m)) for m in selected)
        maximum[label] = dict(histogram=dict(seen), tested=len(indices),
                              hidden_parity_exact_two=score["hidden_eq2"])
    return dict(groups=maximum, retained_small=len(small), retained_extended_only=len(other),
                wall_seconds=round(time.monotonic() - start, 3))


def validate_complete_records():
    # Direct finished-word enumeration on an exactly hidden table above 2
    # establishes that the score and hiding checks do not enforce a bound.
    witness = json.loads((ART / "reference_final.json").read_text())
    matrix = np.array(witness["M"], dtype=np.int64)
    complete = np.zeros((2, 2, 16, 16), dtype=np.int64)
    for a, b, x, y, z, zz in product(range(2), range(2), range(8), range(8), range(2), range(2)):
        oldx, oldy = old_bits(x), old_bits(y)
        if len({oldx[0], oldx[a + 1], z}) > 1 and len({oldy[0], oldy[b + 1], zz}) > 1:
            complete[a, b, 2 * x + z, 2 * y + zz] += matrix[x, y]
    for j in range(2):
        for u, v in ((complete[j, 0].sum(1), complete[j, 1].sum(1)),
                     (complete[0, j].sum(0), complete[1, j].sum(0))):
            assert np.array_equal(u * v.sum(), v * u.sum())
    num, den = parity(matrix[None])
    assert Fraction(int(num[0]), int(den[0])) == unrestricted(matrix) == Fraction(20, 9)
    return dict(hidden=True, parity="20/9", unrestricted="20/9")


def structured_word_table(structure, cut):
    names = ["x1", "x2", "x3"] + [f"s{i + 1}" for i in range(cut)]
    names += [f"h{i + 1}" for i in range(structure["internal"])]
    holders = Counter()
    shape = np.arange(2 ** len(names))
    columns = (shape[None, :] >> np.arange(len(names) - 1, -1, -1)[:, None]) & 1
    allowed = np.ones(len(shape), dtype=bool)
    allocation = False
    constraints = set()
    for knot in structure["knots"]:
        members, law = knot["members"], knot["law"]
        assert len(set(members)) == len(members) and len(members) in (3, 4)
        holders.update(members)
        constraints.add((tuple(sorted(members)), law))
        has_law = columns[[names.index(member) for member in members]].sum(axis=0)
        if law == "nae":
            allowed &= (has_law > 0) & (has_law < len(members))
        else:
            assert law in ("odd", "even")
            allowed &= has_law % 2 == (law == "odd")
        allocation |= "x2" in members and "x3" in members and "x1" not in members
    assert all(holders[name] == 1 for name in names[:3 + cut])
    assert all(1 <= holders[name] <= 2 for name in names[3 + cut:])
    table = allowed.reshape(8, 2 ** cut, -1).sum(axis=2)
    return table, allocation, len(constraints) != len(structure["knots"])


def witness_sample(tables, provenance, n, rng):
    count = Counter(witness_rows=0, allocation_witnesses=0,
                    sample_primary_witness_has_allocation=0, sample_repeated_constraint=0)
    for i in rng.choice(len(tables), size=min(len(tables), n), replace=False):
        item = provenance["structures"][i]
        for k in ("struct", "alloc_struct"):
            if item[k] is None:
                continue
            table, allocation, repeated = structured_word_table(item[k], provenance["cut"])
            assert np.array_equal(table, tables[i])
            if k == "alloc_struct":
                assert allocation
                count["allocation_witnesses"] += 1
            else:
                count["sample_primary_witness_has_allocation"] += allocation
                count["sample_repeated_constraint"] += repeated
            count["witness_rows"] += 1
    return dict(count)


def one_pool(tag, samples, rng, pilot):
    start = time.monotonic()
    tables, flags, nonempty, provenance = archive_side_tables(tag)
    (projective, pflag), (representatives, rflag), orbit_ids = side_views(tables, flags, nonempty)
    small = tag.endswith("_k3_i3")
    unordered = not small
    used, used_flags = (representatives, rflag) if unordered else (projective, pflag)
    blocks = archive_blocks(tag, len(used))
    assert all(block["sym"] == unordered for block in blocks)
    span_check = time.monotonic()
    counts = archive_counts(used, used_flags, blocks, unordered, row_limit=16 if pilot else None)
    count_time = time.monotonic() - span_check
    scoring_start = time.monotonic()
    replay = (score_small(representatives, rflag, row_limit=8 if pilot else None) if small
              else sample_larger(representatives, rflag, samples, rng))
    scoring_time = time.monotonic() - scoring_start
    orbit_sizes = np.unique(np.bincount(orbit_ids), return_counts=True)
    out = dict(
        exact_tables=len(tables), exact_nonempty=int(nonempty.sum()), exact_allocation=int(flags.sum()),
        exact_ordered_attempted=len(tables) ** 2,
        exact_ordered_no_word=empty_ordered_pairs(tables),
        projective_tables=len(projective), projective_allocation=int(pflag.sum()),
        projective_ordered_attempted=len(projective) ** 2,
        projective_ordered_no_word=empty_ordered_pairs(projective),
        row_classes=len(representatives), row_classes_allocation=int(rflag.sum()),
        row_class_sizes=dict(zip(orbit_sizes[0].tolist(), orbit_sizes[1].tolist())),
        archived_scoring="unordered row-class pairs" if unordered else "ordered projective pairs",
        counts=counts, witness_sample=witness_sample(tables, provenance, 8 if pilot else 128, rng),
        witness_maxima_checked=check_max_witnesses(blocks), exact_parity_replay=replay,
        count_seconds=round(count_time, 3), score_seconds=round(scoring_time, 3),
        wall_seconds=round(time.monotonic() - start, 3),
    )
    if "valid" in provenance:
        out["draw_archive"] = {k: provenance[k] for k in ("mode", "seed", "tried", "valid")}
    else:
        out["structure_count_from_archive"] = sum(d["structures"] for d in provenance["stats"])
    return out


def overlap(tags, row_limit=None):
    """Count repeated side-class pairings across the five catalogues of each cut."""
    results = {}
    for cut in (1, 2):
        catalogues = {}
        supports = {}
        for tag in tags:
            if not tag.startswith(f"c{cut}_") or tag.endswith("_k3_i3"):
                continue
            with np.load(ART / f"sides_{tag}.npz") as archive:
                exact = archive["T"][archive["nonempty"]][:row_limit].astype(np.int64)
            (_, _), (reps, _), _ = side_views(
                exact, np.zeros(len(exact), dtype=bool), np.ones(len(exact), dtype=bool))
            table_keys = [
                min(table[p].astype("<i2").tobytes() for p in ROW_MAPS)
                for table in reps
            ]
            catalogues[tag] = set(table_keys)
            supports.update(zip(table_keys, support(reps).tolist()))
        union_totals = Counter()
        sum_of_catalogues = Counter()
        for size in range(1, len(catalogues) + 1):
            for keys in combinations(catalogues.values(), size):
                shared = set.intersection(*keys)
                n = len(shared)
                masks = Counter(supports[key] for key in shared)
                empty = sum(a * b for p, a in masks.items() for q, b in masks.items() if not p & q) // 2
                attempted = n * (n + 1) // 2
                sign = (-1) ** (size + 1)
                union_totals.update(attempted=sign * attempted, empty=sign * empty,
                                    nonempty=sign * (attempted - empty))
                if size == 1:
                    sum_of_catalogues.update(attempted=attempted, empty=empty, nonempty=attempted - empty)
        results[cut] = dict(row_classes={k: len(v) for k, v in catalogues.items()},
                            union_classes=len(set.union(*catalogues.values())),
                            within_pool_pairs=sum_of_catalogues, distinct_pairs=union_totals,
                            repeated_across_pools=sum_of_catalogues - union_totals)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--samples", type=int, default=6000)
    parser.add_argument("--larger-functions", type=int, default=15000)
    parser.add_argument("--overlap-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    rng = np.random.default_rng(SEED)
    tags = sorted(re.match(r"sides_(.*)\.npz", p.name)[1] for p in ART.glob("sides_*.npz"))
    provenance = dict(seed=SEED, pilot=args.pilot, larger_pair_sample_per_pool=args.samples,
                      larger_function_sample_limit_per_cut=args.larger_functions)
    if args.overlap_only:
        limit = 256 if args.pilot else None
        output = dict(row_limit=limit, overlap=overlap(tags, limit))
    else:
        output = dict(settings=provenance, complete_record_control=validate_complete_records(), pools={})
        for tag in tags:
            output["pools"][tag] = one_pool(tag, args.samples, rng, args.pilot)
            print(tag, output["pools"][tag]["wall_seconds"], flush=True)
        for cut in (1, 2):
            output[f"unrestricted_cut_{cut}"] = check_unrestricted(cut, args.larger_functions, rng, args.pilot)
            print("unrestricted outputs", cut, output[f"unrestricted_cut_{cut}"]["wall_seconds"], flush=True)
    output["wall_seconds"] = round(time.monotonic() - start, 3)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    output["cpu_seconds"] = round(usage.ru_utime + usage.ru_stime, 3)
    output["max_rss_kib"] = usage.ru_maxrss
    args.output.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
