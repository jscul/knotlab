"""The smallest lawful start on which a choice of allocation changes the distribution of the old
distinctions under uniform present words, and its full tables.

Added for R3 (see deviations.md): the three structures named in the freeze are larger than a table that
can be printed in full.  Candidates are connected starts of k knots (k = 3, then 4 if needed): between
each pair of knots 0, 1 or 2 shared distinctions, 0 to 3 loose distinctions per knot, every knot with at
least three distinctions.  A start is lawful under a law when the projection of its allowed words onto
each knot's own distinctions is the knot's full relation (the gate used by the generators study).
Ordering: fewest knots, then fewest distinctions.

Run (from the repository root):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""

from fractions import Fraction
from itertools import combinations, product
import json

import numpy as np

import allocations as A
import engine as E

ARTIFACTS = E.ROOT / "artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes"


def build(k, multiplicities, loose):
    pairs = list(combinations(range(k), 2))
    rows = [[] for _ in range(k)]
    d = 0
    for (a, b), m in zip(pairs, multiplicities, strict=True):
        for _ in range(m):
            rows[a].append(d)
            rows[b].append(d)
            d += 1
    for i, n in enumerate(loose):
        rows[i].extend(range(d, d + n))
        d += n
    return tuple(map(tuple, rows))


def connected(k, multiplicities):
    pairs = list(combinations(range(k), 2))
    seen, todo = {0}, [0]
    while todo:
        v = todo.pop()
        for (a, b), m in zip(pairs, multiplicities, strict=True):
            if m and v in (a, b):
                w = b if v == a else a
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
    return len(seen) == k


def lawful(stars, law):
    words, names = A.full_allowed_words(stars, law)
    pos = {d: i for i, d in enumerate(names)}
    for row in stars:
        mask = np.uint64(sum(1 << pos[d] for d in row))
        seen = len(np.unique(words & mask))
        expected = 2 ** (len(row) - 1) if law == "parity" else 2 ** len(row) - 2
        if seen != expected:
            return False
    return True


def candidates(k):
    pairs = list(combinations(range(k), 2))
    out = []
    for mult in product((0, 1, 2), repeat=len(pairs)):
        if not connected(k, mult):
            continue
        for loose in product(range(4), repeat=k):
            stars = build(k, mult, loose)
            if min(len(r) for r in stars) < 3:
                continue
            out.append((len({d for r in stars for d in r}), mult, loose, stars))
    out.sort(key=lambda t: (t[0], t[1], t[2]))
    return out


def max_uniform_tv(stars, law):
    plan = E.plan_round(stars, law)
    if plan.status != "extend" or A.class_count(plan) < 2:
        return None
    names, loose = A.structure_columns(stars)
    marginal = A.loose_marginal_counts(stars, law)
    classes = list(A.all_classes(plan))
    sigma0 = classes[0]
    W0 = marginal * A.weights_on_loose(plan, sigma0, law, loose)
    top = Fraction(0)
    for sigma in classes[1:]:
        W = marginal * A.weights_on_loose(plan, sigma, law, loose)
        num, den = A.tv_from_weights(W0, W)
        top = max(top, Fraction(num, den))
    return top


def search():
    report = {"k": None, "scanned": 0, "lawful_funded_with_choice": {"parity": 0, "nae": 0},
              "minimal": {}}
    for k in (3, 4):
        found = {"parity": [], "nae": []}
        for n_d, mult, loose, stars in candidates(k):
            if n_d > 14 and k == 4:
                continue
            report["scanned"] += 1
            for law in E.LAWS:
                if found[law] and n_d > found[law][0][0]:
                    continue
                if not lawful(stars, law):
                    continue
                tv = max_uniform_tv(stars, law)
                if tv is None:
                    continue
                report["lawful_funded_with_choice"][law] += 1
                if tv > 0:
                    found[law].append((n_d, mult, loose, stars, tv))
        report["k"] = k
        report["minimal"] = {law: [{"distinctions": n, "pair_multiplicities": m, "loose": l, "supports": [list(r) for r in s],
                                    "max_tv_uniform_present": f"{tv.numerator}/{tv.denominator}"}
                                   for n, m, l, s, tv in found[law]] for law in E.LAWS}
        if found["nae"]:
            break
    return report


def full_tables(stars, law):
    """Every allowed old word with the weight of each allocation, under both weightings."""
    plan = E.plan_round(stars, law)
    words, names = A.full_allowed_words(stars, law)
    classes = list(A.all_classes(plan))
    table = {"law": law, "distinctions": names, "knots": [list(r) for r in stars],
             "births": [{"parents": list(p), "fresh": f} for p, f in zip(plan.parents, plan.fresh_counts, strict=True)],
             "allocations": [], "old_words": [format(int(w), f"0{len(names)}b")[::-1] for w in words]}
    sigma0 = classes[0]
    for sigma in classes:
        ext = A.weights_on_words(plan, sigma, law, words, names)
        uni = ext / ext.sum()
        old = (ext >= 1) / (ext >= 1).sum()
        tv = Fraction(*A.tv_from_weights(A.weights_on_words(plan, sigma0, law, words, names), ext))
        table["allocations"].append({
            "pays": {str(k): list(v) for k, v in sigma.items()},
            "children_inputs": [list(i) for i in A.children_inputs(plan, sigma)],
            "uniform_present_weights_per_word": [int(x) for x in ext],
            "uniform_present_total": int(ext.sum()),
            "old_word_weights_per_word": [int(x >= 1) for x in ext],
            "tv_uniform_present_vs_first": f"{tv.numerator}/{tv.denominator}"})
        del uni, old
    return table


def main():
    report = search()
    print(json.dumps(report, sort_keys=True))
    chosen = report["minimal"]["nae"][0] if report["minimal"]["nae"] else None
    out = {"search": report}
    if chosen:
        stars = tuple(map(tuple, chosen["supports"]))
        out["example"] = {law: full_tables(stars, law) for law in E.LAWS}
        # the lawful gate of the generators study, as an independent check of the example
        import sys
        sys.path.insert(0, str(E.ROOT / "tools"))
        sys.path.insert(0, str(E.ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"))
        fixtures = E.load_module(E.ROOT / ("experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/"
                                           "fixtures.py"), "generators_fixtures")
        gate = {}
        for law in E.LAWS:
            try:
                fixtures.certify_source(stars, law)
                gate[law] = "passes certify_source (full local relation and canonical K1-K3 per arity)"
            except AssertionError as error:
                gate[law] = f"fails certify_source: {error!r}"
        out["example_gate"] = gate
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "r3_minimal.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
