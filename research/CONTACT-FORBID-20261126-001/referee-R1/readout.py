"""Two finite checks on the distinction between a full record and a chosen reading."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import prod
from time import process_time
import resource

from shared import HERE, PREVIOUS, WEIGHTS, allowed, births_for, holder_lists, mask, passes, satisfies


def prepared(start, readers, st):
    base = holder_lists(start)
    first = max(d for r in base for d in r) + 1
    edited = [r.copy() for r in base]
    for i, (h, bit) in enumerate(zip(readers, st, strict=True)):
        if bit:
            edited[h].append(first + i)
    states = list(allowed(edited, sorted({d for r in edited for d in r}), "nae"))
    status, births = births_for(edited, states, "nae")
    assert status == "funded"
    old_masks = list(map(mask, base))
    states = [word for word in states if all(satisfies(word, m, "nae") for m in old_masks)]
    return edited, births, states


def fresh_options(births):
    return [(mask(ds), [tuple(w for w in range(1 << fresh)
                         if passes(ones + w.bit_count(), len(ds) + fresh, "nae"))
                        for ones in range(len(ds) + 1)]) for _, ds, fresh in births]


def tables_for_alternative(start, st):
    readers = (3, 4)
    ed, births, states = prepared(start, readers, st)
    common, = [i for i, birth in enumerate(births) if set(readers) <= set(birth[0])]
    _, ds, fresh = births[common]
    assert ds == (9, 10, 11) and fresh == prod(st)
    uses = Counter(d for r in holder_lists(start) for d in r)
    marks = [next(d for d in ed[h] if uses[d] == 1) for h in readers]
    results = {name: {w: Counter() for w in WEIGHTS} for name in ("stored", "declared")}
    options = fresh_options(births)
    for old in states:
        choices = [opts[(old & m).bit_count()] for m, opts in options]
        completions = prod(len(x) for x in choices)
        if completions == 0:
            continue
        old_pair = tuple((old >> d) & 1 for d in marks)
        # The parity of three common old inputs is a fair bit by complementation.
        r = (old & mask(ds)).bit_count() % 2
        declared_pair = (r, r ^ fresh)
        conditional = Counter()
        for choice in product(*choices):
            pair = (choice[common], choice[common]) if fresh else old_pair
            conditional[pair] += 1
        for pair, count in conditional.items():
            results["stored"]["U"][pair] += count
            results["stored"]["S"][pair] += Fraction(count, completions)
        results["declared"]["U"][declared_pair] += completions
        results["declared"]["S"][declared_pair] += 1

    return {kind: {w: [str(results[kind][w][pair] / Fraction(results[kind][w].total()))
                           for pair in product((0, 1), repeat=2)] for w in WEIGHTS}
            for kind in results}


def three_records(start, st):
    readers = (2, 3, 4)
    ed, births, states = prepared(start, readers, st)
    local = [[birth for birth in births if h in birth[0]] for h in readers]
    # Keep all old distinctions of each reader's holders and births, including the other parents' inputs.
    visible = [mask(set(ed[h]).union(*(set(ds) for _, ds, _ in bs))) for h, bs in zip(readers, local, strict=True)]
    options = fresh_options(births)
    hist = [{w: Counter() for w in WEIGHTS} for h in readers]
    for old in states:
        count = prod(len(opts[(old & m).bit_count()]) for m, opts in options)
        if count:
            for i, m in enumerate(visible):
                hist[i]["U"][old & m] += count
                hist[i]["S"][old & m] += 1
    return local, hist


def summarize_three(tables):
    out = {}
    for reader in range(3):
        comparisons = {}
        for a, b in combinations(tables, 2):
            if a[reader] != b[reader]:
                continue
            name = "/".join("".join(map(str, st)) for st in (a, b))
            h, k = tables[a][1][reader], tables[b][1][reader]
            if tables[a][0][reader] != tables[b][0][reader]:
                comparisons[name] = {w: "1" for w in WEIGHTS}
                continue
            # Given the complete old inputs, the distribution of the local fresh tuple
            # is uniform over its allowed values under either weighting. Appending this
            # same conditional distribution to visible old values preserves their TV.
            comparisons[name] = {}
            for w in WEIGHTS:
                p, q = h[w], k[w]
                ptotal, qtotal = p.total(), q.total()
                tv = sum(abs(Fraction(p[v], ptotal) - Fraction(q[v], qtotal)) for v in p.keys() | q.keys()) / 2
                comparisons[name][w] = str(tv)
        out[str(reader)] = comparisons
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    started = process_time()
    source = json.loads((PREVIOUS / "starts.json").read_text())
    # Two holders at the five-knot start with a three-parent common birth.
    twos = [(1, 1)] if args.pilot else product(range(2), repeat=2)
    alternatives = {"".join(map(str, st)): tables_for_alternative(source[5280], st) for st in twos}
    scores = {}
    if not args.pilot:
        for kind in ("stored", "declared"):
            scores[kind] = {}
            for w in WEIGHTS:
                means = []
                for t in alternatives.values():
                    p00, p01, p10, p11 = map(Fraction, t[kind][w])
                    assert p00 + p01 == p00 + p10 == Fraction(1, 2)
                    means.append(p00 + p11 - p01 - p10)
                scores[kind][w] = str(abs(sum(means[:3]) - means[3]))
    # Three holders at the five-knot start with one five-parent birth.
    threes = [(1, 0, 1), (1, 1, 0)] if args.pilot else product(range(2), repeat=3)
    records = summarize_three({st: three_records(source[4821], st) for st in threes})
    evidence = {"two-reader probabilities 00 01 10 11": alternatives, "scores": scores,
                "three-reader complete-record total variations": records,
                "cpu seconds": round(process_time() - started, 3),
                "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if not args.pilot:
        (HERE / "readout.json").write_text(json.dumps(evidence, indent=1) + "\n")
    print(scores, evidence["cpu seconds"], evidence["peak KiB"])


if __name__ == "__main__":
    main()
