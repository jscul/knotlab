"""Rebuild named ordinary growth from founders and compare the funded histories."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations, product
import json
from math import prod
from pathlib import Path
import random
from resource import RUSAGE_SELF, getrlimit, getrusage, RLIMIT_AS
from time import perf_counter


SCOPE = "ERASURE-AND-CLOSING-SIGNS-20261121-001B"
HERE = Path(__file__).resolve().parent
ARCHIVE = (
    HERE.parents[2] / "artifacts" / SCOPE / f"{SCOPE}-E001_closures"
    / "panels_histories.json.gz"
)
SEED = 20261126
SAMPLE_SIZES = {"T": 32, "E": 16, "M": 16, "S": 8}
NAMED_POSITIVES = {("S", 2), ("T", 201), ("M", 1)}
NAMED_CONTROLS = {("T", 2), ("T", 57)}
LAWS = ("parity", "nae")
HORIZON = 4
HOLDER_LIMIT = 512
NAME_LIMIT = 4096
BIRTH_FIELDS = (
    "holder", "parents", "inputs", "fresh", "new_names", "support", "old_span_rows"
)
CLOSURE_FIELDS = BIRTH_FIELDS + (
    "closing_arity", "component_holders", "component_names",
    "old_component_holders", "old_component_loose", "old_component_names",
    "shared_names", "simple_meetings"
)
CUT_FIELDS = (
    "age", "before_holder_count", "before_name_count", "after_rows", "components",
    "new_held_twice", "positive_grants", "preceding_closed_pieces", "whole_closed"
)


def occurrences(rows):
    names = defaultdict(list)
    for holder, row in enumerate(rows):
        assert row == sorted(set(row))
        for name in row:
            names[name].append(holder)
    assert all(len(holders) <= 2 for holders in names.values())
    return names


def incidence_neighbors(names, size):
    neighbors = [set() for _ in range(size)]
    for holders in names.values():
        if len(holders) == 2:
            left, right = holders
            neighbors[left].add(right)
            neighbors[right].add(left)
    return neighbors


def components(rows, names, neighbors):
    waiting = set(range(len(rows)))
    found = []
    while waiting:
        todo = [min(waiting)]
        waiting.remove(todo[0])
        members = []
        while todo:
            holder = todo.pop()
            members.append(holder)
            newly_found = neighbors[holder] & waiting
            waiting.difference_update(newly_found)
            todo.extend(newly_found)
        used = sorted({name for h in members for name in rows[h]})
        found.append({
            "holders": sorted(members),
            "names": used,
            "loose": [name for name in used if len(names[name]) == 1],
        })
    return found


def local_accepts(word, law):
    ones = sum(word)
    if law == "parity":
        return ones % 2 == 0
    return 0 < ones < len(word)


def founder_check(rows, names, parts, law):
    """Condition on shared values, then count and project the independent loose values."""
    projections = [set() for _ in rows]
    essential = set()
    part_counts = []
    for part in parts:
        holders = part["holders"]
        shared = [name for name in part["names"] if len(names[name]) == 2]
        count = 0
        for shared_values in product((0, 1), repeat=len(shared)):
            shared_word = dict(zip(shared, shared_values))
            allowed = []
            has_forbidden = []
            for h in holders:
                row = rows[h]
                allowed_here = set()
                local_options = tuple(
                    (shared_word[name],) if name in shared_word else (0, 1) for name in row
                )
                for word in product(*local_options):
                    if local_accepts(word, law):
                        allowed_here.add(word)
                allowed.append(allowed_here)
                has_forbidden.append(len(allowed_here) < prod(map(len, local_options)))
            completions = prod(map(len, allowed))
            count += completions
            if completions:
                for h, words in zip(holders, allowed):
                    projections[h].update(words)
            for i, h in enumerate(holders):
                if has_forbidden[i] and all(words for j, words in enumerate(allowed) if j != i):
                    essential.add(h)
        part_counts.append(count)
    expected = [
        {word for word in product((0, 1), repeat=len(row)) if local_accepts(word, law)}
        for row in rows
    ]
    total = prod(part_counts)
    return {
        "founder_words": total,
        "projection_sizes": [len(words) for words in projections],
        "lawful": bool(total) and all(len(row) >= 3 for row in rows) and projections == expected,
        "essential": len(essential) == len(rows),
    }


def proposal_groups(witnessed):
    """Every unheld set stays unheld in any larger pairwise witnessed set."""
    witnessed = [set(group) for group in witnessed if len(group) > 1]
    pairs = {pair for group in witnessed for pair in combinations(sorted(group), 2)}
    neighbors = defaultdict(set)
    for u, v in pairs:
        neighbors[u].add(v)
        neighbors[v].add(u)
    larger = []

    def visit(chosen, available, excluded):
        if not available and not excluded:
            if len(chosen) >= 3 and not any(chosen <= group for group in witnessed):
                larger.append(tuple(sorted(chosen)))
            return
        pivot = max(available | excluded, key=lambda h: (len(available & neighbors[h]), -h))
        for h in sorted(available - neighbors[pivot]):
            visit(chosen | {h}, available & neighbors[h], excluded & neighbors[h])
            available.remove(h)
            excluded.add(h)

    if neighbors:
        visit(set(), set(neighbors), set())
    covered = {pair for group in larger for pair in combinations(group, 2)}
    return sorted(larger) + sorted(pairs - covered)


def as_mask(names):
    return sum(1 << name for name in names)


def span_basis(rows, odd=(), sign_bit=0):
    """Reduce named rows over the two-element field, keeping each row combination."""
    basis = {}
    odd = set(odd)
    for holder, support in enumerate(rows):
        pending = as_mask(support)
        if holder in odd:
            pending |= sign_bit
        certificate = 1 << holder
        while pending:
            pivot = pending.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (pending, certificate)
                break
            existing, used = basis[pivot]
            pending ^= existing
            certificate ^= used
    return basis


def span_certificate(basis, support, number_of_rows):
    pending = as_mask(support)
    certificate = 0
    while pending:
        pivot = pending.bit_length() - 1
        if pivot not in basis:
            return None
        existing, used = basis[pivot]
        pending ^= existing
        certificate ^= used
    return [index for index in range(number_of_rows) if certificate >> index & 1]


def parity_words(rows, odd=()):
    names = {name for row in rows for name in row}
    rank = len(span_basis(rows))
    augmented_rank = len(span_basis(rows, odd, 1 << (max(names) + 1)))
    return 0 if augmented_rank > rank else 1 << (len(names) - rank)


def nae_counterword(rows, inputs, names):
    """Find a literal older word which gives every selected input zero."""
    def extend(word):
        while True:
            choice = None
            for row in rows:
                values = {word[name] for name in row if name in word}
                if len(values) == 2:
                    continue
                remaining = [name for name in row if name not in word]
                if not remaining:
                    return None
                if len(values) == 1 and len(remaining) == 1:
                    word[remaining[0]] = 1 - next(iter(values))
                    break
                if choice is None or len(remaining) < choice[0]:
                    choice = (len(remaining), remaining[0], 1 - min(values, default=1))
            else:
                if choice is None:
                    return word
                _, name, preferred = choice
                for bit in (preferred, 1 - preferred):
                    result = extend(word | {name: bit})
                    if result is not None:
                        return result
                return None

    word = extend(dict.fromkeys(inputs, 0))
    assert word is not None
    full_word = {name: word.get(name, 0) for name in names}
    assert all(full_word[name] == 0 for name in inputs)
    assert all(local_accepts(tuple(full_word[name] for name in row), "nae") for row in rows)
    return sorted(name for name, bit in full_word.items() if bit)


def trace_law(source_rows, law):
    rows = source_rows.copy()
    names = occurrences(rows)
    neighbors = incidence_neighbors(names, len(rows))
    parts = components(rows, names, neighbors)
    founder = founder_check(rows, names, parts, law)
    result = {
        "founder": founder,
        "initial_components": parts,
        "cuts": [],
        "signed_parity_applicable": law == "parity",
        "censored": None,
        "termination": "still_open",
    }
    if not founder["lawful"] or not founder["essential"]:
        raise ValueError("Archived founder fails the stated admissibility conditions")
    if not any(part["loose"] for part in parts):
        result["termination"] = "initial_no_loose"
    for age in range(1, HORIZON + 1):
        available = defaultdict(list)
        for name, holders in sorted(names.items()):
            if len(holders) == 1:
                available[holders[0]].append(name)
        if not available:
            break

        groups = proposal_groups([members & available.keys() for members in neighbors])
        owed = Counter(h for group in groups for h in group)
        short = [
            {"holder": h, "loose": available[h], "owed": owed[h]}
            for h in sorted(available) if owed[h] > len(available[h])
        ]
        if short:
            result["termination"] = "stall"
            result["refused_roster"] = [list(group) for group in groups]
            result["shortages"] = short
            break
        parents = groups + [
            (h,) for h in sorted(available) for _ in range(len(available[h]) - owed[h])
        ]
        if len(rows) + len(parents) > HOLDER_LIMIT:
            result["termination"] = "resource_censored"
            result["censored"] = "holder_limit"
            break
        chosen_by_parent = defaultdict(set)
        for i, group in enumerate(parents):
            for h in group:
                chosen_by_parent[h].add(i)
        next_demand = Counter(
            i for group in proposal_groups(list(chosen_by_parent.values())) for i in group
        )
        slots = {h: iter(distinctions) for h, distinctions in available.items()}
        old_basis = span_basis(rows) if law == "parity" else None
        part_by_holder = {h: part for part in parts for h in part["holders"]}
        next_name = max(names) + 1
        births = []
        for i, group in enumerate(parents):
            in_names = sorted(next(slots[h]) for h in group)
            demand = next_demand[i]
            old_part = part_by_holder[group[0]]
            assert all(part_by_holder[h] is old_part for h in group)
            if law == "parity":
                certificate = span_certificate(old_basis, in_names, len(rows))
                assert (certificate is not None) == (in_names == old_part["loose"])
                if certificate is not None:
                    combined = set()
                    for h in certificate:
                        combined.symmetric_difference_update(rows[h])
                    assert combined == set(in_names) and demand == 0
                    assert certificate == old_part["holders"]
            else:
                certificate = None
            fresh = max(demand, 3 - len(group), 1) if certificate is None else 0
            new_names = list(range(next_name, next_name + fresh))
            birth = {
                "holder": len(rows) + i,
                "parents": list(group),
                "inputs": in_names,
                "fresh": fresh,
                "new_names": new_names,
                "support": in_names + new_names,
                "old_span_rows": certificate,
                "next_demand": demand,
            }
            if law == "nae":
                birth["older_word_one_names"] = nae_counterword(rows, in_names, names)
            births.append(birth)
            next_name += fresh
        if len(names) + sum(b["fresh"] for b in births) > NAME_LIMIT:
            result["termination"] = "resource_censored"
            result["censored"] = "name_limit"
            break
        after_rows = rows + [birth["support"] for birth in births]
        after_names = occurrences(after_rows)
        after_neighbors = incidence_neighbors(after_names, len(after_rows))
        after_parts = components(after_rows, after_names, after_neighbors)
        closed_before = {tuple(part["holders"]) for part in parts if not part["loose"]}
        new_closures = []
        for part in after_parts:
            if part["loose"] or tuple(part["holders"]) in closed_before:
                continue
            (birth,) = [b for b in births if b["holder"] in part["holders"]]
            assert birth["fresh"] == 0
            old_part = part_by_holder[birth["parents"][0]]
            assert part["holders"] == old_part["holders"] + [birth["holder"]]
            assert part["names"] == old_part["names"]
            new_closures.append({
                **birth,
                "closing_arity": len(birth["support"]),
                "component_holders": part["holders"],
                "component_names": part["names"],
                "old_component_holders": old_part["holders"],
                "old_component_loose": old_part["loose"],
                "old_component_names": old_part["names"],
                "shared_names": len(part["names"]),
                "simple_meetings": len({tuple(after_names[name]) for name in part["names"]}),
            })
        new_closures.sort(key=lambda closure: closure["holder"])
        assert len(new_closures) == sum(b["fresh"] == 0 for b in births)
        twice_now = {
            name for name in names if len(names[name]) == 1 and len(after_names[name]) == 2
        }
        assert twice_now == {name for b in births for name in b["inputs"]}
        assert len(twice_now) == sum(len(b["inputs"]) for b in births)
        whole_closed = not any(part["loose"] for part in after_parts)
        result["cuts"].append({
            "age": age,
            "before_holder_count": len(rows),
            "before_name_count": len(names),
            "after_rows": after_rows,
            "births": births,
            "components": after_parts,
            "new_closing_components": new_closures,
            "new_held_twice": len(twice_now),
            "positive_grants": sum(b["fresh"] > 0 for b in births),
            "preceding_closed_pieces": len(closed_before),
            "whole_closed": whole_closed,
        })
        rows, names, neighbors, parts = after_rows, after_names, after_neighbors, after_parts
        if whole_closed:
            result["termination"] = "closed"
            break
    result["last_complete_age"] = len(result["cuts"])
    return result


def comparable(history):
    """Drop comparison-external receipts while retaining named physical history."""
    selected = {
        k: history[k] for k in (
            "founder", "initial_components", "termination", "last_complete_age",
            "censored", "signed_parity_applicable"
        )
    }
    selected["cuts"] = []
    for cut in history["cuts"]:
        selected["cuts"].append({k: cut[k] for k in CUT_FIELDS} | {
            "births": [{k: birth[k] for k in BIRTH_FIELDS} for birth in cut["births"]],
            "new_closing_components": sorted(
                [{k: c[k] for k in CLOSURE_FIELDS} for c in cut["new_closing_components"]],
                key=lambda closure: closure["holder"],
            ),
        })
    return selected


def differences(present, recorded, location=()):
    if isinstance(present, dict) and isinstance(recorded, dict) and present.keys() == recorded.keys():
        for key in present:
            yield from differences(present[key], recorded[key], location + (key,))
    elif isinstance(present, list) and isinstance(recorded, list) and len(present) == len(recorded):
        for i, (left, right) in enumerate(zip(present, recorded)):
            yield from differences(left, right, location + (i,))
    elif present != recorded:
        yield {"field": location, "rebuilt": present, "archive": recorded}


def select_founders(archive):
    rng = random.Random(SEED)
    selected = {}
    for panel, size in SAMPLE_SIZES.items():
        draw_indices = sorted(row["draw"] for row in archive if row["panel"] == panel)
        selected[panel] = sorted(rng.sample(draw_indices, size))
    return selected


def add_to_summary(summary, item):
    for law, history in item["laws"].items():
        key = f'{item["stratum"]}/{item["panel"]}/{law}'
        record = summary[key]
        record["draws"] += 1
        record["lawful_founders"] += history["founder"]["lawful"]
        record["termination_" + history["termination"]] += 1
        record["funded_cuts"] += len(history["cuts"])
        record["births"] += sum(len(cut["births"]) for cut in history["cuts"])
        record["new_held_twice"] += sum(cut["new_held_twice"] for cut in history["cuts"])
        record["positive_grants"] += sum(cut["positive_grants"] for cut in history["cuts"])
        closings = [c for cut in history["cuts"] for c in cut["new_closing_components"]]
        record["new_closing_components"] += len(closings)
        record["draws_with_closing_component"] += bool(closings)
        record["simultaneous_closing_cuts"] += sum(
            len(cut["new_closing_components"]) > 1 for cut in history["cuts"]
        )
        for closing in closings:
            record[f'zero_grant_arity_{closing["closing_arity"]}'] += 1
        if law == "nae":
            record["older_counterwords"] += sum(len(cut["births"]) for cut in history["cuts"])


def named_trials(histories):
    by_id = {(h["panel"], h["draw"]): h for h in histories}
    minimum = by_id["S", 2]
    even_cut = minimum["laws"]["parity"]["cuts"][0]["after_rows"]
    unsigned_cut = minimum["laws"]["nae"]["cuts"][0]["after_rows"]

    def unsigned_words(rows):
        names = occurrences(rows)
        neighbors = incidence_neighbors(names, len(rows))
        return founder_check(rows, names, components(rows, names, neighbors), "nae")["founder_words"]

    fresh_cut = by_id["T", 2]["laws"]["parity"]["cuts"][0]
    fresh_birth = next(b for b in fresh_cut["births"] if b["holder"] == 7)
    fresh_name = fresh_birth["new_names"][0]
    assert sum(fresh_name in row for row in fresh_cut["after_rows"]) == 1
    return {
        "five_knot_whole_S2": {
            "older_parity_words": parity_words(minimum["source_rows"]),
            "funded_even_parity_words": parity_words(even_cut),
            "reversed_closing_parity_words": parity_words(even_cut, [4]),
            "actual_unsigned_words": unsigned_words(unsigned_cut),
            "unsigned_words_on_parity_names": unsigned_words(even_cut),
            "actual_unsigned_new_names": minimum["laws"]["nae"]["cuts"][0]["births"][0]["new_names"],
        },
        "positive_grant_control_T2": {
            "holder": 7,
            "toggled_fresh_name": fresh_name,
            "funded_even_parity_words": parity_words(fresh_cut["after_rows"]),
            "reversed_holder_parity_words": parity_words(fresh_cut["after_rows"], [7]),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--all", action="store_true", help="retain only summaries for the full archive")
    args = parser.parse_args()
    started = perf_counter()
    with gzip.open(ARCHIVE, "rt") as file:
        archive = json.load(file)
    selected = select_founders(archive)
    selected_ids = {
        (panel, draw) for panel, draws in selected.items()
        for draw in (draws[:1] if args.pilot else draws)
    }
    indexed = {(row["panel"], row["draw"]): row for row in archive}
    assert len(indexed) == len(archive)
    included = indexed.keys() if args.all else selected_ids | NAMED_POSITIVES | NAMED_CONTROLS
    histories = []
    summary = defaultdict(Counter)
    mismatches = []
    mismatch_count = 0
    for panel, draw in sorted(included, key=lambda pair: ("TEMS".index(pair[0]), pair[1])):
        case_started = perf_counter()
        archive_row = indexed[panel, draw]
        source_rows = archive_row["source_rows"]
        if args.all:
            stratum = "population"
        elif draw in selected[panel]:
            stratum = "seeded"
        elif (panel, draw) in NAMED_POSITIVES:
            stratum = "named_positive"
        else:
            stratum = "named_control"
        laws = {law: trace_law(source_rows, law) for law in LAWS}
        for law in LAWS:
            for mismatch in differences(comparable(laws[law]), comparable(archive_row["laws"][law])):
                mismatch_count += 1
                if not args.all or not mismatches:
                    mismatches.append({"panel": panel, "draw": draw, "law": law, **mismatch})
        history = {
            "panel": panel,
            "draw": draw,
            "stratum": stratum,
            "source_rows": source_rows,
            "laws": laws,
            "elapsed_seconds": perf_counter() - case_started,
        }
        add_to_summary(summary, history)
        if not args.all:
            histories.append(history)
    result = {
        "archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        "summary": summary,
        "mismatches": mismatches,
        "address_space_limit_bytes": getrlimit(RLIMIT_AS)[0],
        "peak_rss_kib": getrusage(RUSAGE_SELF).ru_maxrss,
        "elapsed_seconds_before_writing": perf_counter() - started,
    }
    if args.all:
        output = HERE / "growth_all_summary.json"
        result.update({
            "mode": "all_archived_founders",
            "founder_pairs_rebuilt": len(included),
            "mismatch_count": mismatch_count,
        })
    else:
        output = HERE / ("growth_pilot.json" if args.pilot else "growth_replay.json")
        result.update({
            "mode": "pilot" if args.pilot else "complete_selected_set",
            "sample_seed": SEED,
            "seeded_draws": selected,
            "named_positive_targets": sorted(NAMED_POSITIVES),
            "named_control_targets": sorted(NAMED_CONTROLS),
            "histories": histories,
            "named_trials": named_trials(histories),
        })
    with output.open("w") as file:
        json.dump(result, file, separators=(",", ":"), sort_keys=True)
        file.write("\n")
    print(f"{len(included)} paired histories, {mismatch_count} mismatches, "
          f"{perf_counter() - started:.3f} seconds through output")
    if mismatches:
        print(json.dumps(mismatches[0]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
