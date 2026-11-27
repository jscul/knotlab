"""Compare exact pair means to the normalized expansion retaining only pair terms per knot."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter

resource.setrlimit(resource.RLIMIT_AS, (1400 * 1024**2,) * 2)
import os
for setting in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[setting] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
ROSTER = HERE.parents[2] / "research/FORBID-EDITS-20261126-001/starts.json"


def holdings(record):
    count, shared, loose = record
    knots = [[] for _ in range(count)]
    label = 0
    for a, b, multiplicity in shared:
        for _ in range(multiplicity):
            knots[a].append(label)
            knots[b].append(label)
            label += 1
    for knot, number in zip(knots, loose):
        knot.extend(range(label, label + number))
        label += number
    return knots, label


@lru_cache(maxsize=16)
def bit_counts(width):
    return np.fromiter((i.bit_count() for i in range(1 << width)), dtype=np.int64)


@lru_cache(maxsize=512)
def local_weights(width, mask):
    # The sum of the pair signs is ((sum of the individual signs)^2 - places)/2.
    places = mask.bit_count()
    ones = bit_counts(width)[np.arange(1 << width) & mask]
    value_sum = places - 2 * ones
    pair_sum = (value_sum**2 - places) // 2
    return (ones > 0) & (ones < places), 2**(places - 1) - 1 - pair_sum


def sign_sums(weights):
    # At index T this yields the sum of weights times the sign product on T.
    values = weights.astype(np.int64, copy=True)
    span = 1
    while span < len(values):
        groups = values.reshape((-1, 2 * span))
        left, right = groups[:, :span], groups[:, span:]
        old_left = left.copy()
        left += right
        right[:] = old_left - right
        span *= 2
    return values


def compare(records):
    groups = defaultdict(Counter)
    example = None
    for record_index, record in records:
        knots, n = holdings(record)
        places = [len(k) for k in knots]
        shared_count = sum(m for _, _, m in record[1])
        rings = shared_count - len(knots) + 1
        group = groups[(rings, max(places) == 3)]
        allowed = np.ones(1 << n, dtype=bool)
        truncated = np.ones(1 << n, dtype=np.int64)
        # Product and its sign sums fit exactly in int64: max local value <= 2^a,
        # sum of arities <= 2n by the two-holder limit, and n <= 12 here.
        assert sum(places) <= 2*n and n <= 12
        for knot in knots:
            legal, pair_only = local_weights(n, sum(1 << x for x in knot))
            allowed &= legal
            truncated *= pair_only
        exact, short = sign_sums(allowed), sign_sums(truncated)
        total, short_total = int(exact[0]), int(short[0])
        assert min(total, short_total) > 0
        first_miss = True
        together = {pair for k in knots for pair in combinations(k, 2)}
        group["starts"] += 1
        for x, y in combinations(range(n), 2):
            label = "same knot" if (x, y) in together else "no common knot"
            group[label + " pairs"] += 1
            mask = (1 << x) + (1 << y)
            a, b = int(exact[mask]), int(short[mask])
            if a * short_total != b * total:
                group[label + " failures"] += 1
                if first_miss:
                    group["starts with a failure"] += 1
                    first_miss = False
                if example is None and label == "no common knot":
                    example = dict(knots=knots, pair=[x,y], roster_index=record_index,
                                   states=total, sign_sum=a, exact=str(Fraction(a,total)),
                                   pair_terms_only=str(Fraction(b,short_total)))
    rows = [dict(independent_rings=r, all_three_place=t, **dict(counts))
            for (r,t),counts in sorted(groups.items())]
    return rows, example


def other_weighting():
    knots = ((0,1,2), (0,3,4), (1,5,6))
    allowed = [s for s in range(128)
               if all(len({(s >> x) & 1 for x in k}) == 2 for k in knots)]
    def sign(s, selected):
        return (-1)**sum((s >> x) & 1 for x in selected)
    def delta(s):
        if s & 1:
            s ^= 127
        fixed = tuple((s >> x) & 1 for x in (0,1,3,5))
        return sign(s, (2,4,6)) if fixed == (0,1,1,0) else 0
    weights = {s: 2 + delta(s) for s in allowed}
    assert all(weights[s] == weights[s ^ 127] for s in allowed)
    def means(selected):
        return (Fraction(sum(sign(s,selected) for s in allowed),len(allowed)),
                Fraction(sum(w*sign(s,selected) for s,w in weights.items()),sum(weights.values())))
    pair_agreements = sum(len(set(means(pair))) == 1 for pair in combinations(range(7),2))
    separated = list(combinations(knots[1],2))
    products = [a+b for a in separated for b in combinations(knots[2],2)]
    joint_agreements = sum(len(set(means(p))) == 1 for p in products)
    def joint(k):
        return [means(select) for size in range(len(k)+1) for select in combinations(k,size)]
    local_agreements = sum(all(a==b for a,b in joint(k)) for k in knots)
    end_law_equal = all(a==b for a,b in joint(knots[1]+knots[2]))
    selected = (0,2,4,6)
    assert (pair_agreements, joint_agreements, local_agreements, end_law_equal) == (21,9,3,True)
    return dict(knots=knots, states=len(allowed), weights=dict(sorted(Counter(weights.values()).items())),
                construction="Start with weight 2. Where distinctions (0,1,3,5) read (0,1,1,0), add the product of signs at (2,4,6). Give each flipped state the same weight as its partner. Leave all other weights at 2.",
                mass=sum(weights.values()), unchanged_pair_means=pair_agreements,
                unchanged_two_by_two_joint_means=joint_agreements, unchanged_single_knot_tables=local_agreements,
                complete_joint_table_on_two_outer_knots_unchanged=end_law_equal,
                chosen_even_support=selected, means_equal_then_changed=list(map(str,means(selected))))



def four_distinctions(limit):
    """Sum over subsets of violated rules, imposing equality within each selected rule."""
    left = [[] for _ in range(7)]
    right = [[] for _ in range(7)]
    for i in range(7):
        for offset, shift in enumerate((0, 1, 3)):
            label = 3*i + offset
            left[i].append(label)
            right[(i+shift) % 7].append(label)
    knots = left + right
    readings = [(0, 6, 3, 9), (0, 6, 3, 13)]
    assert all(len(set(k) & set(reading)) <= 1 for k in knots for reading in readings)
    sums = [[0]*16 for _ in readings]
    for selected in range(limit):
        parent = list(range(21))
        def root(i):
            while parent[i] != i:
                i = parent[i]
            return i
        for k, (a,b,c) in enumerate(knots):
            if selected & (1 << k):
                first = root(a)
                parent[root(b)] = first
                parent[root(c)] = first
        components = [root(i) for i in range(21)]
        # A free equality class contributes zero if its sign occurs an odd number of times.
        term = (-1 if selected.bit_count() % 2 else 1) * (1 << len(set(components)))
        for reading, values in zip(readings, sums):
            odd = [0]
            for name in reading:
                mark = 1 << components[name]
                odd.extend([parity ^ mark for parity in odd])
            for mask, parity in enumerate(odd):
                if parity == 0:
                    values[mask] += term
    if limit == (1 << len(knots)):
        assert sums[0][:15] == sums[1][:15]
        assert sums[0][0] == 38982 and [x[-1] for x in sums] == [1270,1398]
    return dict(knots=knots, ordered_readings=readings, signed_sums_indexed_by_subset=sums,
                even_counts=[(v[0]+v[-1])//2 for v in sums])



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    roster = json.loads(ROSTER.read_text())
    sample = list(enumerate(roster))[::149]   # spread pilot across the fixed order
    start = perf_counter()
    compare(sample)
    seconds = perf_counter() - start
    print(f"{len(sample)}-start pilot {seconds:.3f}s; extrapolated full run {seconds*len(roster)/len(sample):.2f}s", flush=True)
    timed = perf_counter()
    four_distinctions(256)
    print(f"Four-distinction inclusion-exclusion pilot (256 of 16,384): {perf_counter()-timed:.4f}s", flush=True)
    if args.pilot:
        return
    rows, example = compare(enumerate(roster))
    totals = Counter()
    for row in rows:
        totals.update({k:v for k,v in row.items() if k not in ("independent_rings","all_three_place")})
    data = dict(totals=dict(totals), roster="research/FORBID-EDITS-20261126-001/starts.json", roster_size=len(roster),
                description="Each knot retains the constant and every two-place sign term, before multiplying and normalizing. Exact means use the literal not-all-equal truth tables. A failure means the two means differ, with exact integer arithmetic.",
                strata=rows, first_distant_difference=example, weighting_control=other_weighting())
    data["separate_four_distinction_readings"] = four_distinctions(1 << 14)
    (HERE / "pair_factors.json").write_text(json.dumps(data,indent=2)+"\n")


if __name__ == "__main__":
    main()
