"""Exact reserved-source assessment for the round-two loose-count prediction."""

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from math import comb, factorial
from time import perf_counter_ns, process_time_ns

import networkx as nx

from growth import collision_read, compact_growth, replay
from search import LAWS, NAMESPACE
from source import Start, certify, founder_code, partition


def weighted_reserve(excluded):
    """Sum labeled proposal weights over exact unlabeled decorated starts."""
    universe = defaultdict(Fraction)
    reserve = {}
    counts = Counter()
    for graph in nx.graph_atlas_g():
        n, e = len(graph), graph.number_of_edges()
        if n not in (4, 5, 6) or e not in (n - 1, n) or not nx.is_connected(graph):
            continue
        counts[n, e - n + 1] += 1
        automorphisms = sum(1 for _ in nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
        labelings = factorial(n) // automorphisms
        base = Fraction(labelings, 6 * 2**n * n**(n-2))
        if e == n:
            (cycle,) = nx.cycle_basis(graph)
            base *= Fraction(len(cycle), comb(n, 2) - n + 1)
        meetings = tuple(sorted(tuple(sorted(pair)) for pair in graph.edges))
        floor = tuple(max(0, 3 - graph.degree[k]) for k in range(n))
        for bits in product((0, 1), repeat=n):
            start = Start(meetings, tuple(a + b for a, b in zip(floor, bits, strict=True)))
            code = founder_code(start)
            universe[code] += base
            if partition(code) == "validation":
                reserve.setdefault(code, start)
    if counts != {(4, 0): 2, (4, 1): 2, (5, 0): 3, (5, 1): 5, (6, 0): 6, (6, 1): 13}:
        raise ValueError(f"unexpected atlas skeleton counts: {counts}")
    if len(universe) != 864 or sum(universe.values()) != 1:
        raise ValueError("the exact proposal-weight census failed its size or normalization check")
    region_totals = defaultdict(Fraction)
    for code, weight in universe.items():
        region_totals[partition(code)] += weight
    omitted = {code: universe[code] for code in sorted(reserve.keys() & excluded)}
    return [(code, reserve[code], universe[code]) for code in sorted(reserve.keys() - excluded)], dict(region_totals), omitted


def fraction_json(x):
    return [x.numerator, x.denominator]


def prediction(left, right):
    _, h_left, b_left = left["read"]
    _, h_right, b_right = right["read"]
    actual, predictor = b_left - b_right, h_left - h_right
    if not actual:
        return "both_tied" if not predictor else "birth_tied"
    if not predictor:
        return "loose_tied"
    return "concordant" if actual * predictor > 0 else "reverse"


def assess(rows):
    by_stratum = defaultdict(list)
    for row in rows:
        if row["read"] is not None:
            by_stratum[row["read"][0]].append(row)
    counts = Counter()
    weights = defaultdict(Fraction)
    pairs = {}
    reverse_example = None
    for key, group in sorted(by_stratum.items()):
        by_bucket = Counter()
        for left, right in combinations(group, 2):
            verdict = prediction(left, right)
            by_bucket[verdict] += 1
            counts[verdict] += 1
            weights[verdict] += Fraction(*left["weight"]) * Fraction(*right["weight"])
            if verdict == "reverse" and reverse_example is None:
                reverse_example = [{"founder": row["founder"], "read": row["read"],
                                    "third_round_join_savings": row["third_round_join_savings"]}
                                   for row in (left, right)]
        pairs["/".join(map(str, key))] = dict(by_bucket)
    total = sum(counts.values())
    weight_total = sum(weights.values())
    opportunity_count = comb(len(rows), 2)
    w = [Fraction(*r["weight"]) for r in rows]
    opportunity_mass = (sum(w)**2 - sum(x*x for x in w)) / 2
    decisive = counts["concordant"] + counts["reverse"]
    correct = weights["concordant"]
    decisive_mass = correct + weights["reverse"]
    nontie = decisive + counts["loose_tied"]
    nontie_mass = decisive_mass + weights["loose_tied"]
    categories = ("concordant", "reverse", "loose_tied", "birth_tied", "both_tied")
    disjoint = []
    for seed in range(4):
        ordered = {}
        for key, group in by_stratum.items():
            def sort_key(row):
                return sha256(f"{NAMESPACE}/reserve-disjoint/{seed}/{row['founder']}".encode()).digest()
            ordered[key] = sorted(group, key=sort_key)
        disjoint.append(dict(Counter(prediction(a, b) for g in ordered.values()
                                     for a, b in zip(g[::2], g[1::2]))))
    return {"opportunity_count": opportunity_count, "opportunity_mass": fraction_json(opportunity_mass),
            "lawful_sources": sum(not r["lawfulness"]["failures"] for r in rows),
            "completed_rounds_at_least": {r: sum(row["growth"] is not None and
                                                len(row["growth"]["rounds"]) >= r for row in rows)
                                          for r in (1, 2, 3)},
            "matched_count": total, "matched_mass": fraction_json(weight_total),
            "matched_share": (None if opportunity_count == 0 else fraction_json(Fraction(total, opportunity_count))),
            "matched_weighted_share": (None if not opportunity_mass else fraction_json(weight_total / opportunity_mass)),
            "matched_by_stratum": pairs, "count": {k: counts[k] for k in categories},
            "weight": {k: fraction_json(weights[k]) for k in categories},
            "weighted_fraction": {k: None if not weight_total else fraction_json(weights[k] / weight_total)
                                  for k in categories},
            "accuracy_given_distinct_and_called": None if not decisive else fraction_json(Fraction(counts["concordant"], decisive)),
            "weighted_accuracy_given_distinct_and_called": None if not decisive_mass else fraction_json(correct / decisive_mass),
            "coverage_given_distinct": None if not nontie else fraction_json(Fraction(decisive, nontie)),
            "weighted_coverage_given_distinct": None if not nontie_mass else fraction_json(decisive_mass / nontie_mass),
            "accuracy_half_credit_abstentions": (None if not nontie else
                                                  fraction_json(Fraction(2*counts["concordant"] + counts["loose_tied"], 2*nontie))),
            "weighted_accuracy_half_credit_abstentions": (None if not nontie_mass else
                                                           fraction_json((correct + weights["loose_tied"]/2) / nontie_mass)),
            "reference_accuracy_fair_ordering": [1, 2],
            "first_reversed_pair": reverse_example,
            "disjoint_hash_pair_counts": disjoint}


def census(excluded):
    began, wall = process_time_ns(), perf_counter_ns()
    reserve, totals, omitted = weighted_reserve(excluded)
    enumeration = {"cpu_ns": process_time_ns() - began, "wall_ns": perf_counter_ns() - wall}
    by_law = {law: [] for law in LAWS}
    for code, start, weight in reserve:
        cpu, w = process_time_ns(), perf_counter_ns()
        stars = start.stars
        projection = certify(stars)
        common = {"founder": code, "meetings": start.meetings, "loose": start.loose,
                  "lawfulness": projection, "weight": fraction_json(weight),
                  "source_cpu_ns": process_time_ns() - cpu, "source_wall_ns": perf_counter_ns() - w}
        for law in LAWS:
            cpu, w = process_time_ns(), perf_counter_ns()
            growth = None if projection["failures"] else compact_growth(stars, law, horizon=3)
            read = None if growth is None else collision_read(growth, len(stars))
            certificate = None if read is None else replay(start, law, 3)
            if certificate is not None and certificate["rounds"] != growth["rounds"]:
                raise ValueError("fresh reserve readout differs under independent literal replay")
            savings = None
            if read is not None:
                savings = sum((p - 1) * k for p, _, k in growth["rounds"][2]["arity_and_fresh"])
                if read[1] - savings != read[2]:
                    raise ValueError("third-round births do not account for all loose supply")
            by_law[law].append({**common, "growth": growth, "read": read,
                                "third_round_join_savings": savings,
                                "literal_replay": certificate,
                                "growth_cpu_ns": process_time_ns() - cpu,
                                "growth_wall_ns": perf_counter_ns() - w})
    return {"universe_count": 864, "reserve_count": len(reserve),
            "partition_masses": {k: fraction_json(t) for k, t in totals.items()},
            "public_reference_exclusions": {k: fraction_json(t) for k, t in omitted.items()},
            "enumeration": enumeration, "by_law": by_law,
            "summary": {law: assess(rows) for law, rows in by_law.items()},
            "total_cpu_ns": process_time_ns() - began, "total_wall_ns": perf_counter_ns() - wall}
