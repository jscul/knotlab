"""Independent small truth tables, exhaustive clause-pattern controls and two physical witnesses."""
import argparse
import contextlib
import io
import json
import resource
import sys
from collections import Counter
from itertools import combinations, product
from time import perf_counter

import closed_forms as scan


def tuple_reader(lib, row):
    knots = row["supports"]
    names = sorted({v for knot in knots for v in knot})
    local = {v: i for i, v in enumerate(names)}
    knots = [tuple(local[v] for v in knot) for knot in knots]
    n = len(names)
    states = [s for s in product((0, 1), repeat=n)
              if all(len({s[v] for v in knot}) > 1 for knot in knots)]
    readings = {}
    for size in (2, 3):
        for carrier in combinations(range(n), size):
            values = [int(len({s[v] for v in carrier}) == 1) for s in states]
            for knot in knots:
                fixes = {}
                for s, val in zip(states, values):
                    fixes.setdefault(tuple(s[k] for k in knot), set()).add(val)
                if all(len(opts) == 1 for opts in fixes.values()):
                    break
            else:
                readings[scan.support_mask(carrier)] = values
    signed = set()
    hist = Counter()
    for a, b, c in combinations(readings, 3):
        if a & b or a & c or b & c:
            continue
        words = set(zip(readings[a], readings[b], readings[c]))
        if len(words) == 8 or any(len({(w[i], w[j]) for w in words}) != 4
                                 for i, j in ((0, 1), (0, 2), (1, 2))):
            continue
        missing = set(product(range(2), repeat=3)) - words
        hist[len(missing)] += 1
        if len(missing) == 1:
            signed.add(tuple(sorted(2 * m + bit for m, bit in zip((a, b, c), missing.pop()))))
    count, unread, total, numbers, actual = scan.lower_bonds(lib, knots, n, None)
    assert count == len(states) and set(unread) == set(readings)
    assert total == sum(hist.values()) and numbers == hist and actual == signed
    return dict(census_id=row["census_id"], distinctions=n, allowed=count,
                unread=len(unread), bonds=total, exact_signed_clauses_agree=True)


def matchings(reads):
    if not reads:
        yield ()
        return
    first, *others = reads
    for i, partner in enumerate(others):
        for rest in matchings(others[:i] + others[i + 1:]):
            yield ((first, partner),) + rest


def reference_templates(names, clauses):
    """Check each four-clause subset on all 64 normalized six-reading words."""
    templates = []
    npos = {s: i for i, s in enumerate(names)}
    words = list(product((0, 1), repeat=6))
    for chosen in combinations(clauses, 4):
        if set().union(*(set(c) for c in chosen)) != set(names):
            continue
        indices = [[npos[s] for s in c] for c in chosen]
        allowed = [w for w in words if all(not all(w[i] for i in c) for c in indices)]
        for g in matchings(names):
            if any(any(len(set(c) & set(pair)) != 1 for pair in g) for c in chosen):
                continue
            for central in range(3):
                def upper(w):
                    return tuple(int((all if i == central else any)(w[npos[s]] for s in pair))
                                 for i, pair in enumerate(g))
                missing = set(product((0, 1), repeat=3)) - {upper(w) for w in allowed}
                if missing != {(1, 1, 1)}:
                    continue
                for drop in range(4):
                    if not any(upper(w) == (1, 1, 1) and
                               all(i == drop or not all(w[j] for j in c) for i, c in enumerate(indices))
                               for w in words):
                        break
                else:
                    counts = [sum(s in c for c in chosen) for s in g[central]]
                    if sorted(counts) == [1, 3]:
                        kind = "one_and_three"
                    elif all(len(set(x) & set(y)) == 1 for x, y in combinations(chosen, 2)):
                        kind = "alternating"
                    else:
                        kind = "paired"
                    templates.append((frozenset(chosen), g, central, kind))
    return templates


def synthetic(signs, pilot):
    names = tuple(2 * ((1 << (2*i)) | (1 << (2*i + 1))) + sign for i, sign in enumerate(signs))
    planted = tuple(tuple(names[j] for j in p) for p in product((0, 1), (2, 3), (4, 5)))
    templates = reference_templates(names, planted)
    needs = lambda room: any((room & (s >> 1)) == s >> 1 for s in names)
    subsets = (255,) if pilot else range(256)
    passes = 0
    for mask in subsets:
        chosen = {c for i, c in enumerate(planted) if mask & (1 << i)}
        groups, *_ = scan.arrangements(chosen, 12, needs)
        result = {(frozenset(cs), g, index, kind) for g in groups
                  for kind, index, cs in scan.possibilities(g, chosen)}
        assert result == {t for t in templates if t[0] <= chosen}
        box = any(all(c in chosen for c in scan.lower_choices(g).values()) for g in groups)
        assert box == (mask == 255)
        passes += 1
    inconsistent = set(planted[1:])
    a, b, c = planted[0]
    inconsistent.add(tuple(sorted((a ^ 1, b, c))))
    groups, *_ = scan.arrangements(inconsistent, 12, needs)
    assert not any(all(c in inconsistent for c in scan.lower_choices(g).values()) for g in groups)
    return dict(selected_signs=signs, lower_clause_subsets_checked=passes,
                full_template_comparisons=dict(Counter(t[-1] for t in templates)),
                changing_one_occurrence_of_one_sign_loses_box=True)


def canonical(words, positive):
    sys.path.insert(0, str(scan.RESEARCH.parent / "tools"))
    from knotlab.cli import main
    absent = set(product(range(2), repeat=3)) - set(words)
    cnf = "; ".join(" ".join(("~" if b else "") + name for name, b in zip("PQR", w))
                    for w in sorted(absent)) if absent else "P ~P"
    for contact in "PQR":
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(["check", "--cnf", cnf, "--loops", *(v for v in "PQR" if v != contact),
                         "--contact", contact, "--json"])
        assert code == 0 and json.loads(out.getvalue())["is_knot"] == positive
    return 3


def actual_witness(lib, knots, carriers, clauses, central, kind):
    # Literal source assignments, independent of the block search. Keep each
    # failure of exactly one law for the source-deletion controls.
    n = 1 + max(x for knot in knots for x in knot)
    supports = [scan.support_mask(k) for k in knots]
    carried = [scan.support_mask(c) for c in carriers]
    lower_counts = Counter()
    restored = Counter()
    upper_counts = Counter()
    def upper(w):
        if kind == "box":
            return tuple(w[i] ^ w[i+1] for i in (0, 2, 4))
        return tuple((min if i == central else max)(w[2*i:2*i+2]) for i in range(3))
    for state in range(1 << n):
        failures = [j for j, mask in enumerate(supports) if (state & mask) in (0, mask)]
        if len(failures) > 1:
            continue
        w = tuple(int((state & mask) in (0, mask)) for mask in carried)
        u = upper(w)
        if not failures:
            lower_counts[w] += 1
            upper_counts[u] += 1
        elif u == (1, 1, 1):
            restored[failures[0]] += 1
    assert set(upper_counts) == set(product((0, 1), repeat=3)) - {(1, 1, 1)}
    roles = canonical(upper_counts, True)
    for c in clauses:
        projection = {tuple(w[i] for i in c) for w in lower_counts}
        assert projection == set(product((0,1), repeat=3)) - {(1,1,1)}
        roles += canonical(projection, True)
    abstract = [w for w in product(range(2), repeat=6) if all(not all(w[i] for i in c) for c in clauses)]
    assert {upper(w) for w in abstract} == set(upper_counts)
    roles += canonical({upper(w) for w in abstract}, True)
    for omitted in range(len(clauses)):
        assert any(upper(w) == (1,1,1) and all(j == omitted or not all(w[i] for i in c)
                                                for j,c in enumerate(clauses))
                   for w in product(range(2), repeat=6))
    positive, examples = scan.search(lib, knots, len(knots), [], chosen=carriers)
    assert positive["allowed"] == sum(lower_counts.values())
    if kind == "box":
        assert positive["boxes"] == 1
    else:
        assert positive["four_clause_upper_steps"][kind] > 0
    assert kind in examples
    drop = min(restored)
    cut_knots = [k for i, k in enumerate(knots) if i != drop]
    negative, _ = scan.search(lib, cut_knots, len(cut_knots), [], chosen=carriers)
    if kind == "box":
        assert negative["boxes"] == 0
    roles += canonical(set(upper_counts) | {(1,1,1)}, False)
    return dict(kind=kind, knots=len(knots), distinctions=n, chosen_agreement_carriers=carriers,
                allowed_source_states=sum(lower_counts.values()), actual_six_reading_words=len(lower_counts),
                lower_conjunction_words=len(abstract), recovered_boxes=positive["boxes"],
                recovered_four_clause_upper_steps=positive["four_clause_upper_steps"],
                source_upper_word_counts={"".join(map(str, w)): c for w,c in sorted(upper_counts.items())},
                restored_upper_111_after_removing_each_source_law=[restored[i] for i in range(len(knots))],
                rerun_with_law_removed=drop, boxes_after_removal=negative["boxes"],
                four_clause_upper_steps_after_removal=negative["four_clause_upper_steps"],
                canonical_role_checks=roles, all_single_lower_clause_deletions_restore_111=True)


def run(pilot):
    start = perf_counter()
    lib = scan.kernel()
    stages = json.loads((scan.HERE / "growth_stages.json").read_text())
    ids = (17,) if pilot else (17, 24, 43, 560, 2912)
    small = [tuple_reader(lib, s) for s in stages if s["law"] == "one_fewer" and s["census_id"] in ids]
    signed = [synthetic(signs, pilot) for signs in ((1,1,1,1,1,1),(0,1,0,1,1,0))[:1 if pilot else 2]]
    ring = scan.RESEARCH / "RING-BOND-20261127-001" / "referee-R1"
    upper = scan.RESEARCH / "UPPER-GROWN-20261127-001" / "referee-R1"
    four = next(item["witness"] for item in json.loads((upper / "upper_four_closed.json").read_text())
                if "witness" in item)
    physical = [actual_witness(lib, four["knots"], four["carriers"], four["lower_clauses_missing_111"],
                               four["and_pair"], "alternating")]
    assert physical[0]["restored_upper_111_after_removing_each_source_law"] == four["restorations_by_dropped_source_law"]
    if not pilot:
        eight = json.loads((ring / "layer_witness.json").read_text())
        physical.append(actual_witness(lib, eight["source_knots_not_all_equal"],
                                       eight["lower_carriers_in_A0_A1_B0_B1_C0_C1_order"],
                                       list(product((0,1),(2,3),(4,5))), None, "box"))
        assert physical[1]["allowed_source_states"] == eight["allowed_source_states"]
    return dict(small_census_truth_tables=small, lower_clause_subsets=signed, physical=physical,
                elapsed_seconds=round(perf_counter()-start, 4),
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    result = run(args.pilot)
    filename = "closed_control_pilot.json" if args.pilot else "closed_controls.json"
    scan.write_json(scan.HERE / filename, result)
    print(filename, "seconds", result["elapsed_seconds"], "peak KiB", result["peak_rss_kib"])
