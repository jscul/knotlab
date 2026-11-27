"""Rebuild the selected ring clusters and the joint images on their readings."""

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from layer_readings import agreement, bonds, candidates, fibers, occurring, source_table, truth_columns


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY.parent / "NAE-LAYER-20261127-001" / "referee-R1"))
from growth_rule import advance


def id_for_cluster(laws):
    return tuple(sorted(tuple(sorted(tuple(c) for c in law)) for law in laws))


def archive_id(entry):
    return id_for_cluster([[carrier for carrier, sign in law] for law in entry["cluster"]])


def disjoint_except_identity(first, second):
    return all(a == b or set(a).isdisjoint(b) for a in first for b in second)


def selected_clusters(laws, allow_overlap):
    """A pair must meet. A connected triple has at least two meeting pairs."""
    can_mix = {i: set() for i in range(len(laws))}
    meet = {i: set() for i in range(len(laws))}
    for i, j in combinations(range(len(laws)), 2):
        if allow_overlap or disjoint_except_identity(laws[i], laws[j]):
            can_mix[i].add(j)
            can_mix[j].add(i)
            if not set(laws[i]).isdisjoint(laws[j]):
                meet[i].add(j)
                meet[j].add(i)
    for i in meet:
        for j in sorted(meet[i]):
            if i < j:
                yield (i, j)
    triples = set()
    for i, neighbours in meet.items():
        for j, k in combinations(neighbours, 2):
            if k in can_mix[j]:
                triples.add(tuple(sorted((i, j, k))))
    yield from sorted(triples)


def modeled_rows(readings, lower_bonds, inside):
    universe, columns = truth_columns(len(readings))
    labels = {r: i for i, r in enumerate(readings)}
    allowed = universe
    restrictions = []
    supports = []
    for law in inside:
        places = tuple(labels[r] for r in law)
        supports.append(places)
        groups = fibers(universe, [columns[i] for i in places])
        rule = universe
        for missing in lower_bonds[law]:
            rule &= ~groups[missing]
        allowed &= rule
        restrictions.append(rule)
    return allowed, universe, columns, supports, restrictions


def examine_upper(rows, universe, columns, supports, restrictions=None):
    values = candidates(rows, columns, supports)
    syntax = unread = free_pairs = constrained = all_essential = 0
    carriers = [s for size in (2, 3) for s in combinations(range(len(columns)), size)]
    for left, middle in combinations(carriers, 2):
        if not set(left).isdisjoint(middle):
            continue
        occupied = set(left) | set(middle)
        for right in carriers:
            # Use the same ordering as combinations(carriers, 3).
            if (len(right), right) <= (len(middle), middle) or not occupied.isdisjoint(right):
                continue
            syntax += 1
            triple = left, middle, right
            if not all(c in values for c in triple):
                continue
            unread += 1
            chosen = [values[c] for c in triple]
            if any(len(occurring(rows, pair)) < 4 for pair in combinations(chosen, 2)):
                continue
            free_pairs += 1
            image = occurring(rows, chosen)
            if len(image) == 8:
                continue
            constrained += 1
            if restrictions is None:
                continue
            # Recompute the read columns on the full universe when a law is omitted.
            views = [agreement(universe, [columns[p] for p in c]) for c in triple]
            every_essential = True
            for i in range(len(restrictions)):
                allowed = universe
                for j, law in enumerate(restrictions):
                    if i != j:
                        allowed &= law
                if not occurring(allowed, views) - image:
                    every_essential = False
                    break
            all_essential += every_essential
    result = {"three_disjoint_upper_carriers": syntax, "also_unread_by_each_lower_bond": unread,
              "also_all_pairs_free": free_pairs, "also_whole_constrained": constrained}
    if restrictions is not None:
        result["also_every_lower_law_essential"] = all_essential
    return result


def cluster_rows(base, low_values, all_bonds, laws, clusters):
    rows = []
    for ids in clusters:
        chosen = tuple(laws[i] for i in ids)
        readings = sorted(set().union(*map(set, chosen)))
        inside = [l for l in combinations(readings, 3) if l in all_bonds]
        allowed, universe, columns, supports, restrictions = modeled_rows(readings, all_bonds, chosen)
        all_allowed = modeled_rows(readings, all_bonds, inside)[0]
        # Column order codes states in reverse bit order to the printed words.
        raw_image = occurring(base, [low_values[r] for r in reversed(readings)])
        joint = sum(1 << n for n in raw_image)
        assert joint & ~all_allowed == 0 and all_allowed & ~allowed == 0
        row = {
            "cluster": chosen, "number_of_unique_readings": len(readings), "inside": len(inside),
            "joint": joint.bit_count(), "conjunction": allowed.bit_count(),
            "conjunction_of_all_bonds_on_these_readings": all_allowed.bit_count(),
            "upper_on_cluster_laws": examine_upper(allowed, universe, columns, supports, restrictions),
            "upper_on_actual_joint_image_without_a_law_deletion_test": examine_upper(joint, universe, columns, supports),
        }
        rows.append(row)
    return rows


def frequencies(items):
    return dict(sorted(Counter(items).items()))


def summarize(rows):
    result = {
        "clusters": len(rows), "clusters_by_number_of_bonds": frequencies(len(x["cluster"]) for x in rows),
        "clusters_by_number_of_distinct_lower_readings": frequencies(x["number_of_unique_readings"] for x in rows),
        "clusters_with_at_least_six_lower_readings": sum(x["number_of_unique_readings"] >= 6 for x in rows),
        "joint_smaller_than_cluster_conjunction": sum(x["joint"] < x["conjunction"] for x in rows),
        "joint_smaller_than_conjunction_of_all_bonds_on_these_readings": sum(
            x["joint"] < x["conjunction_of_all_bonds_on_these_readings"] for x in rows),
        "joint_cluster_conjunction_all_bonds_sizes": frequencies(
            f"{x['joint']}/{x['conjunction']}/{x['conjunction_of_all_bonds_on_these_readings']}" for x in rows),
    }
    for key in ("upper_on_cluster_laws", "upper_on_actual_joint_image_without_a_law_deletion_test"):
        tests = ["three_disjoint_upper_carriers", "also_unread_by_each_lower_bond", "also_all_pairs_free",
                 "also_whole_constrained"]
        if key == "upper_on_cluster_laws":
            tests.append("also_every_lower_law_essential")
        result[key] = {test: sum(row[key][test] for row in rows) for test in tests}
        result[key + "_clusters_with_whole_constrained"] = sum(row[key]["also_whole_constrained"] > 0 for row in rows)
    return result


def match_archive(data):
    strict = json.loads((STUDY / "out" / "layer2_strict.json").read_text())
    post = json.loads((STUDY / "post" / "l2_extra.json").read_text())
    rechecked_examples = 0
    for t in (1, 2):
        current = data[f"round_{t}_disjoint"]
        saved = strict[f"round {t}"]
        counts = current["summary"]
        assert (len(current["rows"]), current["first_bonds"]) == (saved["clusters"], saved["bonds"])
        assert counts["joint_smaller_than_cluster_conjunction"] == saved["tally"].get("L2 J smaller than conj", 0)
        assert len(current["rows"]) - counts["joint_smaller_than_cluster_conjunction"] == saved["tally"].get("L2 J equals conj", 0)
        for size in (2, 3):
            assert counts["clusters_by_number_of_bonds"].get(size, 0) == saved["tally"].get(f"clusters {size} bonds", 0)
        assert counts["upper_on_cluster_laws"].get("also_every_lower_law_essential", 0) == saved["tally"].get(
            "L1 bonds of the layer above", 0)
        assert counts["upper_on_cluster_laws_clusters_with_whole_constrained"] == saved["tally"].get(
            "L1 clusters with a bond of the layer above", 0)
        indexed = {id_for_cluster(row["cluster"]): row for row in current["rows"]}
        for example in saved["examples"]:
            row = indexed[archive_id(example)]
            assert [row["joint"], row["conjunction"], row["upper_on_cluster_laws"]["also_every_lower_law_essential"]] == [
                example["J"], example["conj"], len(example["layer-above bonds"])]
            rechecked_examples += 1
    pairs = {id_for_cluster(row["cluster"]): row for row in data["round_2_disjoint"]["rows"] if len(row["cluster"]) == 2}
    assert len(post) == len(pairs) and {archive_id(x) for x in post} == set(pairs)
    for archived in post:
        row = pairs[archive_id(archived)]
        assert [row["number_of_unique_readings"], row["joint"], row["conjunction"], row["inside"],
                row["conjunction_of_all_bonds_on_these_readings"]] == [
            archived[k] for k in ("readings", "J", "conj", "bonds inside its readings", "conj of all of them")]
    return {"archived_strict_summaries_rebuilt": 2, "archived_strict_examples_rebuilt": rechecked_examples,
            "archived_post_hoc_cluster_records_rebuilt": len(post),
            "round_one_overlap_saved_separate_json": (STUDY / "out" / "layer2_overlap.json").exists()}


def run(pilot=False):
    stage = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
    results = {}
    for turn in (1, 2):
        stage = advance(stage).supports
        _, columns, _, state_rows = source_table(stage)
        first, first_values = bonds(state_rows, columns, stage)
        assert all(len(m) == 1 for m in first.values())
        law_keys = sorted(first)
        for overlap in ([False, True] if turn == 1 else [False]):
            clusters = list(selected_clusters(law_keys, overlap))
            if pilot:
                clusters = clusters[:2]
            records = cluster_rows(state_rows, first_values, first, law_keys, clusters)
            key = f"round_{turn}_" + ("overlap" if overlap else "disjoint")
            results[key] = {"supports": stage, "allowed_source_states": state_rows.bit_count(),
                            "first_bonds": len(first), "summary": summarize(records), "rows": records}
        if pilot:
            break
    if not pilot:
        results["raw_comparisons"] = match_archive(results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    results = run(args.pilot)
    if not args.pilot:
        (HERE / "layer_recount.json").write_text(json.dumps(results, indent=1) + "\n")
    print(json.dumps({case: result["summary"] for case, result in results.items() if "summary" in result}))


if __name__ == "__main__":
    main()
