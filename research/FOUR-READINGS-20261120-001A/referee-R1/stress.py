"""Compare literal three-step growth and companion panels with a fresh enumeration."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import resource
import sys
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
STUDY = "FOUR-READINGS-20261120-001A"
EVIDENCE = ROOT / "artifacts" / STUDY / f"{STUDY}-E001_signed_rules"
ARCHIVE = (
    ROOT / "artifacts/HEAVY-GROWTH-20261119-001"
    / "HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json"
)
SINGLETON = "start-03"


def holdings(sizes, meetings):
    supports = [[] for _ in sizes]
    for distinction, (a, b) in enumerate(meetings):
        supports[a].append(distinction)
        supports[b].append(distinction)
    next_distinction = len(meetings)
    for support, size in zip(supports, sizes, strict=True):
        need = size - len(support)
        assert need >= 0
        support.extend(range(next_distinction, next_distinction + need))
        next_distinction += need
    return supports


def word_to_meetings(word):
    available = set(range(len(word) + 2))
    degrees = Counter(word)
    meetings = []
    for name in word:
        leaf = min(holder for holder in available if degrees[holder] == 0)
        meetings.append(tuple(sorted((leaf, name))))
        available.remove(leaf)
        degrees[name] -= 1
    meetings.append(tuple(sorted(available)))
    return sorted(meetings)


def check_sources(supports, counts):
    masks = [sum(1 << distinction for distinction in support) for support in supports]
    span = {0}
    for row in masks:
        span |= {row ^ previous for previous in span}
    # A row survives forgetting exactly when its support lies in the retained set.
    parity = [len(support) >= 3 and {x for x in span if not x & ~row} == {0, row}
              for support, row in zip(supports, masks, strict=True)]

    nae = []
    for target, support in enumerate(supports):
        # Each other knot with a loose distinction can satisfy its constraint
        # independently once its shared distinctions have been assigned.
        restricted = [row for pos, row in enumerate(supports) if pos != target
                      and all(counts[distinction] == 2 for distinction in row)]
        unset = sorted(set().union(*map(set, restricted)) - set(support))
        allowed = 0
        for word in product((0, 1), repeat=len(support)):
            if len(set(word)) < 2:
                continue
            fixed = dict(zip(support, word, strict=True))
            for remaining in product((0, 1), repeat=len(unset)):
                values = fixed | dict(zip(unset, remaining, strict=True))
                if all(len({values[d] for d in row}) == 2 for row in restricted):
                    allowed += 1
                    break
        nae.append(len(support) >= 3 and allowed == (1 << len(support)) - 2)
    return {"parity": parity, "nae": nae}


def groups(live, witnesses):
    """Enumerate maximal unheld compatible sets and their uncovered pairs."""
    neighbours = {name: set() for name in live}
    for witness in witnesses:
        for a, b in combinations(witness, 2):
            neighbours[a].add(b)
            neighbours[b].add(a)

    maximal_unheld = []

    def visit(clique, extension, candidates, containing):
        if any(extension.issubset(witness) for witness in containing):
            return
        if len(clique) >= 3 and not containing and not candidates:
            maximal_unheld.append(clique)
            return
        for name in sorted(extension):
            visit(clique + (name,),
                  {other for other in extension & neighbours[name] if other > name},
                  candidates & neighbours[name],
                  [witness for witness in containing if name in witness])

    for name in sorted(live):
        visit((name,), {other for other in neighbours[name] if other > name},
              neighbours[name], [witness for witness in witnesses if name in witness])
    covered = {pair for group in maximal_unheld for pair in combinations(group, 2)}
    return maximal_unheld + [(a, b) for a in sorted(live) for b in sorted(neighbours[a])
                             if a < b and (a, b) not in covered]


def physical_index(supports):
    by_distinction = {}
    for holder, row in enumerate(supports):
        assert len(set(row)) == len(row)
        for distinction in row:
            by_distinction.setdefault(distinction, []).append(holder)
    return by_distinction


def next_demands(proposed):
    witnessed = {}
    for index, parents in enumerate(proposed):
        for holder in parents:
            witnessed.setdefault(holder, set()).add(index)
    lookahead = groups(range(len(proposed)), witnessed.values())
    return Counter(index for group in lookahead for index in group)


def create_births(proposed, closed, loose, holder_count, distinction_count):
    demands = next_demands(proposed)
    by_holder = {}
    for distinction, holder in sorted(loose.items(), reverse=True):
        by_holder.setdefault(holder, []).append(distinction)
    births = []
    for index, parents in enumerate(proposed):
        fresh = 0 if closed else max(demands[index], 3 - len(parents), 1)
        places = [by_holder[parent].pop() for parent in parents]
        places.extend(range(distinction_count, distinction_count + fresh))
        distinction_count += fresh
        births.append({"holder": holder_count + index, "parents": len(parents),
                       "places": sorted(places), "demand": demands[index], "fresh": fresh})
    return births


def next_stage(supports, law, record):
    by_distinction = physical_index(supports)
    loose = {d: holders[0] for d, holders in by_distinction.items() if len(holders) == 1}
    supplies = Counter(loose.values())
    meetings = [set() for _ in supports]
    for holders in by_distinction.values():
        assert len(holders) in {1, 2}
        if len(holders) == 2:
            first, second = holders
            if second in supplies:
                meetings[first].add(second)
            if first in supplies:
                meetings[second].add(first)
    proposed = groups(supplies, meetings)
    costs = Counter(holder for group in proposed for holder in group)
    shortage = {holder for holder, cost in costs.items() if cost > supplies[holder]}
    if shortage:
        if record is not None:
            assert record["status"] == "stall", record
        return {"status": "stall", "shortage_count": len(shortage)}
    for holder, count in (supplies - costs).items():
        proposed.extend([(holder,)] * count)

    # Derive the groups before reading recorded births. Use the record's names
    # only to align indistinguishable loose distinctions and repeated singletons.
    old_count = len(supports)
    closed = law == "parity" and len(proposed) == 1
    births = (create_births(proposed, closed, loose, old_count, len(by_distinction))
              if record is None else record["new"])
    mapped = []
    used_loose, fresh = set(), set()
    for index, birth in enumerate(births):
        assert birth["holder"] == old_count + index
        places = set(birth["places"])
        assert len(places) == len(birth["places"])
        paid = places & by_distinction.keys()
        assert paid <= loose.keys() and paid.isdisjoint(used_loose)
        used_loose.update(paid)
        parents = tuple(sorted(loose[d] for d in paid))
        assert len(parents) == len(set(parents)) == birth["parents"]
        created = places - paid
        assert created.isdisjoint(fresh)
        fresh.update(created)
        mapped.append((parents, len(created)))
    assert used_loose == loose.keys()
    assert Counter(parents for parents, _ in mapped) == Counter(proposed)
    assert fresh == set(range(len(by_distinction), len(by_distinction) + len(fresh)))

    demands = next_demands([parents for parents, _ in mapped])
    for index, ((parents, created), birth) in enumerate(zip(mapped, births, strict=True)):
        assert demands[index] == birth["demand"]
        expected = 0 if closed else max(demands[index], 3 - len(parents), 1)
        assert created == expected == birth["fresh"]
    reconstructed = {
        "status": "closed" if closed else "grown",
        "births": len(proposed),
        "holders": old_count + len(proposed),
        "distinctions": len(by_distinction) + len(fresh),
        "loose": len(fresh),
    }
    if record is None:
        reconstructed["new"] = births
    else:
        assert reconstructed == {key: record[key] for key in reconstructed}
    assert reconstructed["holders"] <= 400 and reconstructed["distinctions"] <= 2000
    supports.extend(birth["places"] for birth in births)
    return reconstructed


def check_case(case, supports, steps, *, complete_to=0):
    assert case["stars"] == supports
    counts = Counter(d for row in supports for d in row)
    projected = check_sources(supports, counts)
    results = {}
    for law, full in projected.items():
        assert all(full)
        assert case["laws"][law]["source_full_knots"] == full
        shown = case["laws"][law]["stages"]
        assert steps <= len(shown) or shown[-1]["status"] in {"closed", "stall"}
        current = supports.copy()
        trace = []
        for stage in shown[:steps]:
            trace.append(next_stage(current, law, stage))
        recorded_steps = len(trace)
        while len(trace) < complete_to and trace[-1]["status"] == "grown":
            trace.append(next_stage(current, law, None))
        results[law] = {"source_full_knots": len(full), "stages": trace,
                        "recorded_steps_checked": recorded_steps,
                        "newly_computed_steps": list(range(recorded_steps + 1, len(trace) + 1))}
        if trace[-1]["status"] == "closed":
            results[law]["closed_supports"] = current
    return results


def check_archive(case, source, steps):
    reconstructed = holdings(source["sizes"], source["meetings"])
    assert reconstructed == source["gate"]["literal_supports"]
    results = check_case(case, reconstructed, steps)
    for law in results.values():
        assert [stage["births"] for stage in law["stages"]] == source["round_junction_counts"][1:steps + 1]
    return {"archive_id": source["identifier"], "laws": results}


def shared_meetings(supports):
    index = physical_index(supports)
    assert all(len(pair) == 2 for pair in index.values())
    meetings = {tuple(pair) for pair in index.values()}
    assert len(meetings) == len(index)
    return meetings


def check_subset_meetings(supports, labels):
    meetings = shared_meetings(supports)
    neighbours = [set() for _ in supports]
    for a, b in meetings:
        neighbours[a].add(b)
        neighbours[b].add(a)
    names = {0: frozenset()}
    assert len(neighbours[0]) == labels
    names.update((holder, frozenset({label})) for label, holder in enumerate(sorted(neighbours[0])))
    level = set(neighbours[0])
    for width in range(2, labels + 1):
        next_level = set().union(*(neighbours[parent] for parent in level)) - names.keys()
        names.update((holder, frozenset().union(*(names[parent] for parent in neighbours[holder] & level)))
                     for holder in next_level)
        assert all(len(names[holder]) == width for holder in next_level)
        level = next_level
    assert len(names) == len(set(names.values())) == len(supports) == 2 ** labels
    expected = {(a, b) for a, b in combinations(range(len(supports)), 2)
                if len(names[a] ^ names[b]) == 1}
    assert meetings == expected
    return {"labels": labels, "knots": len(supports), "distinctions": len(meetings)}


def check_matched_cycles(supports, rows):
    """The nested cyclic orders give a planar embedding of these two closures."""
    assert sorted(holder for row in rows for holder in row) == list(range(len(supports)))
    pairs = []
    for row in rows:
        pairs.extend(zip(row, row[1:] + row[:1], strict=True))
    for left, right in zip(rows, rows[1:]):
        pairs.extend(zip(left, right, strict=True))
    assert shared_meetings(supports) == {tuple(sorted(pair)) for pair in pairs}
    return rows


def check_companions(sources):
    companion = json.loads((EVIDENCE / "growth_histories.json").read_bytes())
    sample = Random(202611200131)
    checked = {}
    for case in companion:
        name = case["name"]
        family = case["family"]
        origin = case["provenance"]
        steps = 3
        if family == "archived_burst":
            result = check_archive(case, sources[name], steps)
        elif family == "uniform_tree":
            size = len(origin["prufer"]) + 2
            word = [sample.randrange(size) for _ in range(size - 2)]
            extras = [sample.randrange(4) == 0 for _ in range(size)]
            assert word == origin["prufer"] and extras == origin["extras"], name
            assert origin["words"] == size ** (size - 2)
            meetings = word_to_meetings(word)
            degrees = Counter(holder for pair in meetings for holder in pair)
            sizes = [max(degrees[holder], 3) + extras[holder] for holder in range(size)]
            result = {"laws": check_case(case, holdings(sizes, meetings), steps)}
        else:
            assert family == "built_subset"
            labels, spare = origin["k"], origin["extra_at_spent"]
            if origin["initial_single"]:
                result = {"laws": check_case(case, holdings([labels + spare], []),
                                             labels + spare, complete_to=3)}
            else:
                meetings = [(0, leaf) for leaf in range(1, labels + 1)]
                sizes = [labels + spare] + [labels] * labels
                result = {"laws": check_case(case, holdings(sizes, meetings), labels - 1, complete_to=3)}
            if "closed_supports" in result["laws"]["parity"]:
                closed = result["laws"]["parity"]["closed_supports"]
                result["closed_subset"] = check_subset_meetings(closed, labels + spare)
        cycle_rows = {
            "tree_4_0": [[0, 1, 4, 2], [3, 5, 8, 6], [7, 9, 11, 10]],
            "tree_4_3": [[0, 1, 4, 2], [3, 5, 7, 6]],
        }
        if name in cycle_rows:
            closed = result["laws"]["parity"]["closed_supports"]
            result["planar_matched_cycles"] = check_matched_cycles(closed, cycle_rows[name])
            assert case["laws"]["parity"]["stages"][-1]["operator_after_one_supplied_odd"] is False
        checked[name] = {"family": family, **result}
    return checked


def summarize_constructed(cases):
    summaries = {law: {"three_step_fates": Counter(), "overrun": [],
                       "early_still_open": [], "newly_computed": {}}
                 for law in ("parity", "nae")}
    for name, case in cases.items():
        if case["family"] != "built_subset":
            continue
        for law, result in case["laws"].items():
            summary = summaries[law]
            stages = result["stages"]
            original = result["recorded_steps_checked"]
            last = stages[min(3, len(stages)) - 1]["status"]
            assert len(stages) >= 3 or last in {"closed", "stall"}
            summary["three_step_fates"][last] += 1
            if original > 3:
                summary["overrun"].append({"name": name, "recorded_steps": original})
            if original < 3 and stages[original - 1]["status"] == "grown":
                summary["early_still_open"].append({"name": name, "recorded_steps": original})
            if result["newly_computed_steps"]:
                summary["newly_computed"][name] = result["newly_computed_steps"]
    return summaries


def main():
    start = perf_counter()
    pilot = sys.argv[1:] == ["--pilot"]
    if not pilot and sys.argv[1:]:
        raise SystemExit("Use --pilot or no arguments")
    archive_bytes = ARCHIVE.read_bytes()
    sources = json.loads(archive_bytes)["named_archive_starts"]
    case = json.loads((EVIDENCE / "supplemental_stress.json").read_bytes())
    freeze = ROOT / "research" / STUDY / "supplemental_stress_freeze.md"
    assert case["supplemental_freeze_sha256"] == sha256(freeze.read_bytes()).hexdigest()
    assert case["archived_source_sha256"] == sha256(archive_bytes).hexdigest()
    source = sources[SINGLETON]
    assert case["name"] == source["identifier"] and case["provenance"]["denominator"] == 1
    singleton = check_archive(case, source, 1 if pilot else 3)
    results = {"singleton": singleton}
    if pilot:
        companion = json.loads((EVIDENCE / "growth_histories.json").read_bytes())
        control = next(case for case in companion if case["name"] == "subsets_3_leaves_spare_1")
        supports = holdings([4, 3, 3, 3], [(0, leaf) for leaf in range(1, 4)])
        results["missing_step_pilot"] = check_case(control, supports, 2, complete_to=3)
    else:
        double_count = ROOT / "research/WALL-READ-20261119-001/posthoc/double_count.json"
        singleton["recorded_later_births"] = {
            7: source["round_junction_counts"][7],
            8: json.loads(double_count.read_bytes())["round8_junctions"],
        }
        results["companion_cases"] = check_companions(sources)
        results["constructed_horizons"] = summarize_constructed(results["companion_cases"])
    results["check_seconds"] = perf_counter() - start
    results["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
