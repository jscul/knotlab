"""Screen exactly the sixteen selected EXPLOSIVE histories through archived ages."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import cache
import gzip
import json
from math import comb
from pathlib import Path
import sys

from starts_predicates import Roster, components, exact_roster_map, partnered, structural_key

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
HUB = "HUB-GUIDED-SAMPLE-20261119-001"
HUB_ARTIFACTS = ROOT / "artifacts" / HUB / (HUB + "-E001_sampler")
PARTNER = "PARTNER-SEVEN-20261119-001"
PARTNER_SCREEN = ROOT / "artifacts" / PARTNER / (PARTNER + "-E001_seek") / "archive_screen.json"
MERGE = ROOT / "artifacts/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/results.json"
EXPORTS = Path("/var/tmp/hub-sample-20261119")
PARTNER_ORDER_LIMIT = 256
REPEAT_INCIDENCE_LIMIT = 4096
AGES_LITERAL = tuple(f"start-{i:02d}" for i in range(16))
sys.path.insert(0, str(ROOT / "experiments" / HUB / (HUB + "-E001_sampler")))
import stages as hub


@dataclass(frozen=True)
class Snapshot:
    roster: Roster
    births: int | None
    parent_sum: int | None
    parent_arities: dict | None
    small_arity_parents: dict
    method: str
    hashes: dict


def read(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as stream:
            return json.load(stream)
    return json.loads(path.read_text())


@cache
def archive_inputs():
    committed = read(HUB_ARTIFACTS / "stages.json")
    starts, walls = hub.archive_inputs()
    partner = {row["tag"]: row for row in read(PARTNER_SCREEN)["explosive"]["starts"]}
    assert starts == committed["literal_starts"]
    assert sorted(starts) == sorted(walls) == sorted(partner) == list(AGES_LITERAL)
    for case in AGES_LITERAL:
        assert starts[case]["sizes"] == partner[case]["sizes"]
        assert starts[case]["edges"] == partner[case]["links"]
    manifest = {(row["case"], row["age"]): row for row in committed["stages"]}
    merges = {entry["case"]: entry for entry in read(MERGE)["rows"]}
    later = {row["case"]: row["reported_births"] for row in read(HUB_ARTIFACTS / "applications.json")}
    return starts, walls, partner, manifest, merges, later


def snapshot_from_export(metadata):
    hashes = metadata["files"]

    def resolved(key):
        info = hashes[key]
        path = EXPORTS / info["name"]
        if not path.is_file():
            raise FileNotFoundError(f"{path}. Rebuild the HUB-GUIDED-SAMPLE export first.")
        assert hub.digest(path) == info["sha256"], path
        return path

    with resolved("blocks").open() as stream:
        size, block_count = map(int, next(stream).split())
        blocks = tuple(sorted(tuple(map(int, line.split())) for line in stream))
    assert size == metadata["live"] and len(blocks) == metadata["blocks"] == block_count
    assert all(b == tuple(sorted(set(b))) and len(b) >= 2 and 0 <= b[0] <= b[-1] < size for b in blocks)
    degrees = tuple(read(resolved("degrees")))
    assert len(degrees) == size and sum(degrees) == 2 * metadata["candidate_pairs"]
    supply = tuple(read(resolved("opens"))) if "opens" in hashes else None
    if supply is not None:
        assert len(supply) == size and all(s > 0 for s in supply)
    region = Roster(size, blocks, supply, degrees)
    arities = metadata["parent_arities"]
    singled = None if arities is None else metadata["single_parent_cases"]
    small = {}
    # For non-witness rows the independently verified parent summary excludes
    # single parents. Check all actual parent rows where there could be a witness.
    if singled:
        parents = read(resolved("parents"))
        assert len(parents) == size
        assert sum(map(len, parents)) == metadata["parent_sum"]
        assert Counter(map(len, parents)) == {int(p): n for p, n in arities.items()}
        small = {u: tuple(row) for u, row in enumerate(parents) if len(row) == 1}
        assert [[u, degrees[u], max(0, 2 - degrees[u])] for u in small] == singled
        for u in tuple(small):
            peer = actual_neighbors(region, u)
            assert len(peer) == degrees[u]
            assert all(small[u][0] in parents[v] for v in peer)
            for cousin in peer:
                small.setdefault(cousin, tuple(parents[cousin]))
    elif singled == []:
        assert not arities.get("1")
    if arities is not None:
        arities = {int(p): n for p, n in arities.items()}
        assert sum(arities.values()) == size
    if singled is not None:
        assert metadata["exact_offshoots"] == sum(s for _, _, s in singled) + degrees.count(0) - sum(
            degrees[u] == 0 for u, _, _ in singled
        )
    return Snapshot(region, metadata["births"], metadata["parent_sum"], arities, small,
                    metadata["engine"], {k: v["sha256"] for k, v in hashes.items()})


def actual_neighbors(roster, u):
    return tuple(sorted({x for block in roster.blocks if u in block for x in block} - {u}))


def as_groups(roster):
    return hub.archived.groups_of(range(roster.size), [frozenset(b) for b in roster.blocks])


def starting(sizes, edges):
    supplies, raw = hub.archived.roster_of(sizes, edges)
    blocks = tuple(sorted(tuple(sorted(b)) for b in raw))
    region = Roster(len(supplies), blocks, tuple(supplies), tuple(hub.exact_degrees(len(supplies), blocks)))
    return Snapshot(region, None, None, None, {}, "literal start", {})


def replay_early(case, ages, manifest):
    """Rebuild only the prefix before the first missing exported stage ends."""
    missing = [age for age in ages if age and (case, age) not in manifest]
    if case == "start-04":
        missing = [age for age in missing if age != 9]
    if not missing:
        return {}
    raw = {}
    hub.archive_replay(case, range(max(missing) + 1), lambda age, frame: raw.update({age: frame}))
    result = {}
    for age in missing:
        frame = raw[age]
        parents = [tuple(hub.vertices(m)) for m in frame.parent_masks]
        open_counts = None
        if age + 1 in raw:
            supply = [0] * frame.size
            for child in raw[age + 1].parent_masks:
                for v in hub.vertices(child):
                    supply[v] += 1
            open_counts = tuple(supply)
            assert all(open_counts)
        degrees = tuple(hub.exact_degrees(frame.size, frame.blocks))
        blocks = tuple(sorted(frame.blocks))
        roster = Roster(frame.size, blocks, open_counts, degrees)
        p = {u: row for u, row in enumerate(parents) if len(row) == 1}
        for u in list(p):
            for v in actual_neighbors(roster, u):
                assert parents[u][0] in parents[v]
                p[v] = parents[v]
        result[age] = Snapshot(roster, frame.births, sum(map(len, parents)), Counter(map(len, parents)), p,
                               "replay from literal start", {})
    return result


def onset_at_start(snapshot, physical_singulars):
    roster = snapshot.roster
    groups = as_groups(roster)
    demand = Counter(u for group in groups for u in group)
    assert all(demand[u] <= f for u, f in enumerate(roster.opens)), "Archive start is unfunded"
    total_born = len(groups) + sum(f - demand[u] for u, f in enumerate(roster.opens))
    return [{"junction": u, "physical_start_junction": physical_singulars[u], "open": f, "demand": demand[u],
             "offshoots": f - demand[u], "neighbors": actual_neighbors(roster, u),
             "all_multi_parent_groups": [sorted(g) for g in groups if u in g],
             "physical_start_groups": [sorted(physical_singulars[v] for v in g) for g in groups if u in g]}
            for u, f in enumerate(roster.opens) if f <= 2 and demand[u] < f and total_born > 1]


def onset_reached(frame):
    if frame.parent_arities is None:
        return None, []
    roster = frame.roster
    unary = {u: p for u, p in frame.small_arity_parents.items() if len(p) == 1}
    assert len(unary) == frame.parent_arities.get(1, 0)
    facts = []
    for u in sorted(unary):
        d = roster.degrees[u]
        if d > 1:
            continue
        neighbors = actual_neighbors(roster, u)
        assert len(neighbors) == d
        if roster.opens is not None:
            assert roster.opens[u] == 2
        facts.append({"junction": u, "parent": unary[u][0], "open": 2, "demand": d, "offshoots": 2 - d,
                      "neighbors": [{"junction": v, "parents": frame.small_arity_parents[v]} for v in neighbors]})
    for u, d in enumerate(roster.degrees):
        if d == 0 and u not in unary:
            assert roster.opens is None or roster.opens[u] == 1
            facts.append({"junction": u, "open": 1, "demand": 0, "offshoots": 1, "neighbors": []})
    return sum(f["offshoots"] for f in facts), facts


def closing_from(frame, age):
    roster = frame.roster
    m = roster.size
    if m == 0:
        return {"type": "implied_last_birth" if age else "closed_start", "terminal_birth_age": age or None,
                "first_zero_birth_age": age + 1}
    if m <= 2:
        exact_ones = roster.opens == (1,) * m
        reached_pair = age > 0 and m == 2 and frame.parent_arities is not None and not frame.parent_arities.get(1)
        if (exact_ones or reached_pair) and min(roster.degrees) == m - 1:
            return {"type": "small_implied_merge", "live": m, "each_open": 1, "exact_next_births": 1,
                    "terminal_birth_age": age + 1, "first_zero_birth_age": age + 2}
        return None
    if min(roster.degrees) != m - 1:
        return None
    if len(roster.blocks) == 1 and len(roster.blocks[0]) == m:
        if age > 0 and roster.opens is not None:
            assert roster.opens == (m - 1,) * m
        if age > 0 or roster.opens == (m - 1,) * m:
            return {"type": "single_full_block", "live": m, "each_open": m - 1, "exact_next_births": comb(m, 2),
                    "terminal_birth_age": age + m - 1, "first_zero_birth_age": age + m}
        return None
    if age > 0 or roster.opens == (1,) * m:
        assert frame.parent_arities is None or not frame.parent_arities.get(1)
        assert roster.opens is None or roster.opens == (1,) * m
        return {"type": "complete_unheld_graph", "live": m, "each_open": 1, "exact_next_births": 1,
                "terminal_birth_age": age + 1, "first_zero_birth_age": age + 2}
    return None


def current_open_sum(frame, following):
    if frame.roster.opens is not None:
        result = sum(frame.roster.opens)
        if following is not None and following.parent_sum and following.roster.size:
            assert result == following.parent_sum
        return result, "exact"
    if following is not None and following.parent_sum and following.roster.size:
        return following.parent_sum, "exact"
    if frame.roster.size == 0:
        return 0, "exact"
    arities = frame.parent_arities or {}
    return (frame.roster.size + sum(max(0, frame.roster.degrees[u] - 1, 1)
                                    for u, p in frame.small_arity_parents.items() if len(p) == 1),
            "lower bound")


def with_supply(frame):
    if frame.roster.opens is not None or frame.parent_arities is None:
        return frame.roster
    assert frame.roster.size <= REPEAT_INCIDENCE_LIMIT
    demands = Counter(u for group in as_groups(frame.roster) for u in group)
    if frame.parent_arities.get(1):
        one_parent = {u for u, p in frame.small_arity_parents.items() if len(p) == 1}
        assert len(one_parent) == frame.parent_arities[1]
    else:
        one_parent = set()
    supplies = tuple(max(demands[u], 2 if u in one_parent else 1) for u in range(frame.roster.size))
    return Roster(frame.roster.size, frame.roster.blocks, supplies, frame.roster.degrees)


def repetition(frames):
    equal_size, comparable, matched, unavailable = 0, 0, [], []
    for i, (age, frame) in enumerate(frames):
        for other_age, other in frames[:i]:
            if not frame.roster.size or frame.roster.size != other.roster.size:
                continue
            equal_size += 1
            if structural_key(frame.roster) != structural_key(other.roster):
                continue
            comparable += 1
            if sum(map(len, frame.roster.blocks)) > REPEAT_INCIDENCE_LIMIT:
                unavailable.append([other_age, age, "incidence cap"])
                continue
            a, b = with_supply(other), with_supply(frame)
            if a.opens is None or b.opens is None:
                unavailable.append([other_age, age, "supply unavailable"])
                continue
            image = exact_roster_map(a, b)
            if image is not None:
                matched.append({"ages": [other_age, age], "isomorphism": image})
    return {"pairs_at_same_live_size": equal_size, "pairs_surviving_structural_filter": comparable,
            "matches": matched, "unavailable": unavailable}


def score(case):
    starts, walls, partners, manifest, merges, later = archive_inputs()
    source, history = starts[case], walls[case]
    initial = starting(source["sizes"], source["edges"])
    share = Counter(u for link in source["edges"] for u in link)
    live_start_names = [u for u, arity in enumerate(source["sizes"]) if arity > share[u]]
    assert len(live_start_names) == initial.roster.size
    source_thin = onset_at_start(initial, live_start_names)
    ages = range(len(history["counts"]) + 1)
    replay = replay_early(case, ages, manifest)
    initial_closing = closing_from(initial, 0)
    found, table, first_closed = [(0, initial)], [], (0, initial_closing) if initial_closing else None
    seen_continuation = False
    for age, expected in enumerate(history["counts"], 1):
        if case == "start-04" and age == 9:
            # This retained incidence is known implicitly from the literal one-block predecessor.
            assert first_closed == (8, {"type": "single_full_block", "live": 781, "each_open": 780,
                                        "exact_next_births": expected, "terminal_birth_age": 788,
                                        "first_zero_birth_age": 789})
            continue
        metadata = manifest.get((case, age))
        frame = snapshot_from_export(metadata) if metadata is not None else replay[age]
        assert frame.births == expected
        assert max(map(len, frame.roster.blocks), default=0) == history["largest_block"][age - 1]
        found.append((age, frame))
        verdict = closing_from(frame, age)
        if verdict is not None and first_closed is None:
            first_closed = age, verdict
    width = sum(source["sizes"]) - len(source["edges"])
    width_exact = True
    junctions = len(source["sizes"])
    for i, (age, frame) in enumerate(found):
        roster = frame.roster
        partition = components(roster)
        assert len(partition) == int(bool(roster.size)), (case, age, "candidate component count changed")
        exact_offshoots, witness = onset_reached(frame)
        assert age == 0 or exact_offshoots is not None or first_closed is not None
        if witness and age > 0:
            seen_continuation = True
        if seen_continuation and exact_offshoots is not None:
            assert exact_offshoots > 0, (case, age, "fatally stopped thin offshoot")
        paired = [partnered(roster, c, reached=age > 0, maximum_order=PARTNER_ORDER_LIMIT) for c in partition]
        following = found[i + 1][1] if i + 1 < len(found) else None
        supply, level = current_open_sum(frame, following)
        if age > 0:
            junctions += frame.births
            width += supply
            width_exact &= level == "exact"
        table.append({"age": age, "births": frame.births, "live": roster.size,
                      "components": [len(c.points) for c in partition],
                      "maximal_blocks": len(roster.blocks), "largest_block": max(map(len, roster.blocks), default=0),
                      "candidate_pairs": sum(roster.degrees) // 2, "minimum_candidate_degree": min(roster.degrees, default=0),
                      "maximum_candidate_degree": max(roster.degrees, default=0), "open_sum": supply, "open_sum_kind": level,
                      "junctions_to_date": junctions, "distinctions_to_date": width,
                      "distinction_count_kind": "exact" if width_exact else "lower bound",
                      "positive_age_offshoots": exact_offshoots, "positive_age_thin_junctions": witness,
                      "thin_junction_check": ("initial exact group plan" if age == 0 else
                                              "excluded by finite closing certificate" if exact_offshoots is None else
                                              "literal incoming arities and current candidates"),
                      "partnered_component_checks": paired, "representation": frame.method, "sha256": frame.hashes})
    if case == "start-04":
        n = history["counts"][-1]
        k = first_closed[1]["live"]
        assert n == comb(k, 2) and n != 2 * (k - 2) + 2
        assert not any(r["live"] == n for r in table)
        table.append({"age": 9, "births": n, "live": n, "components": [n], "maximal_blocks": k,
                      "largest_block": k - 1, "candidate_pairs": n * (k - 2),
                      "minimum_candidate_degree": 2 * (k - 2), "maximum_candidate_degree": 2 * (k - 2),
                      "open_sum": n * (k - 2), "open_sum_kind": "exact",
                      "junctions_to_date": junctions + n, "distinctions_to_date": width + n * (k - 2),
                      "distinction_count_kind": "exact" if width_exact else "lower bound",
                      "positive_age_offshoots": 0, "positive_age_thin_junctions": [],
                      "thin_junction_check": "explicit pair-family with two parents per child",
                      "partnered_component_checks": [{"status": "wrong_candidate_degree"}],
                      "representation": "literal pair-family through the certified single block"})
    repeats = repetition(found)
    persisted = [r["age"] for r in table if r["positive_age_thin_junctions"]]
    last = table[-1]
    permanent_offshoot_absence = last["positive_age_offshoots"] == 0 and bool(last["live"])
    if permanent_offshoot_absence:
        assert not source_thin and not persisted
    if first_closed is not None:
        assert not source_thin and not persisted and not repeats["matches"]
    partnered_reached = [r["age"] for r in table if any(p["status"] == "partnered" for p in r["partnered_component_checks"])]
    assert not (partnered_reached and first_closed is not None)
    if source_thin:
        assert persisted and persisted[0] == 1
        linked = {entry["junction"] for entry in source_thin}
        for row in table[1:]:
            linked = {entry["junction"] for entry in row["positive_age_thin_junctions"] if entry["parent"] in linked}
            assert linked, (case, row["age"], "thin witness lineage changed")
    later_exact = later.get(case)
    count_readout = {"kind": "exact births only", "age": last["age"] + 1, "births": later_exact} if later_exact else None
    if case == "start-03":
        lower = read(HUB_ARTIFACTS / "structure_bound.json")["all_births_lower"]
        count_readout = {"kind": "deterministic lower bound", "age": 9, "births": lower}
    if not count_readout and first_closed is None:
        lower = history["best_bound_next"]
        if isinstance(lower, (int, float)) and lower > 0:
            count_readout = {"kind": "deterministic lower bound", "age": last["age"] + 1, "births": lower}
    return {"case": case, "source_sizes": source["sizes"], "source_meetings": source["edges"],
            "source_draw": {"stratum": partners[case]["source_case"], "index": partners[case]["source_draw"]},
            "canonical_source": partners[case]["canonical"], "source_funded": True,
            "initial_two_open_offshoots": source_thin, "thin_observed_ages": persisted,
            "first_closure": first_closed, "partnered_ages": partnered_reached, "repetition": repeats,
            "no_future_offshoot_at_last_open_archive": permanent_offshoot_absence,
            "classification": ("closing" if first_closed else "continuing" if
                               source_thin or persisted or partnered_reached or repeats["matches"] else "unresolved"),
            "archive_stop": {"EXPLOSIVE": source["outcome_then"], "MERGE-BURST": merges[case]["end"],
                             "WALL-READ": history["end"]},
            "last_archived_age": last["age"], "later_birth_data_without_roster": count_readout, "stages": table}


def controls():
    # Same live size but different held transversals must change the verdict.
    free = snapshot_from_export(archive_inputs()[3][("partner-3", 0)]).roster
    certified = partnered(free, components(free)[0], reached=False, maximum_order=PARTNER_ORDER_LIMIT)
    assert certified["status"] == "partnered" and certified["next_order"] == 4
    wrong = Roster(free.size, free.blocks, (3,) * free.size, free.degrees)
    assert partnered(wrong, components(wrong)[0], reached=False, maximum_order=PARTNER_ORDER_LIMIT)["status"] == "wrong_supply"
    held = tuple(sorted(b for b in free.blocks if not set(b) <= {0, 2, 4})) + ((0, 2, 4),)
    withheld = Roster(free.size, held, free.opens, free.degrees)
    assert partnered(withheld, components(withheld)[0], reached=False, maximum_order=PARTNER_ORDER_LIMIT)["status"] == (
        "held_not_complement_closed"
    )
    assert exact_roster_map(free, withheld) is None
    a, b = (snapshot_from_export(archive_inputs()[3][("partner-2", age)]).roster for age in (0, 1))
    ring = exact_roster_map(a, b)
    assert ring is not None
    separated = Roster(2, (), (1, 1), (0, 0))
    isolated = onset_at_start(Snapshot(separated, None, None, None, {}, "synthetic control", {}), range(2))
    assert len(isolated) == 2 and len(components(separated)) == 2
    singleton = Roster(1, (), (1,), (0,))
    assert not onset_at_start(Snapshot(singleton, None, None, None, {}, "synthetic control", {}), range(1))
    held_triple = Snapshot(Roster(3, ((0, 1, 2),), (2, 2, 2), (2, 2, 2)), 3, 6, {2: 3}, {}, "control", {})
    unheld_triple = Snapshot(Roster(3, ((0, 1), (0, 2), (1, 2)), (1, 1, 1), (2, 2, 2)), 3, 6, {2: 3}, {},
                             "control", {})
    assert closing_from(held_triple, 1)["terminal_birth_age"] == 3
    assert closing_from(unheld_triple, 1)["terminal_birth_age"] == 2
    return {"exact_partnered_order3": certified, "short_funding_rejected": True, "unpaired_held_word_rejected": True,
            "held_blocks_required_for_exact_repeat": True, "order2_exact_repeat_map": ring,
            "two_isolated_offshoots_propagate": True, "lone_implied_child_is_excluded": True,
            "complete_held_vs_unheld_closes_after_two_vs_one_rounds": True}


def cases():
    for case in AGES_LITERAL:
        yield case, case


def run(case_id, case):
    assert case_id == case
    return score(case)


def save(data, output):
    hub.write_at(output, lambda stream: json.dump(data, stream, indent=2, sort_keys=True))


def main():
    global EXPORTS
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--exports", type=Path, default=EXPORTS)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "starts_screen.json")
    command = parser.add_subparsers(dest="action", required=True)
    one = command.add_parser("one")
    one.add_argument("case", choices=AGES_LITERAL)
    command.add_parser("controls")
    command.add_parser("all")
    collect = command.add_parser("collect")
    collect.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    EXPORTS = args.exports
    if args.action == "controls":
        print(json.dumps(controls(), sort_keys=True))
        return
    if args.action == "one":
        print(json.dumps(score(args.case), sort_keys=True))
        return
    if args.action == "collect":
        sys.path.insert(0, str(ROOT / "scripts"))
        from longrun import load_results
        results = load_results(args.run_dir)
        assert sorted(results) == list(AGES_LITERAL) and all(r["status"] == "ok" for r in results.values())
        rows = [results[case]["result"] for case in AGES_LITERAL]
    else:
        rows = [score(case) for case in AGES_LITERAL]
    data = {"sources": {str(p.relative_to(ROOT)): hub.digest(p) for p in
                        (PARTNER_SCREEN, MERGE, hub.WALL, HUB_ARTIFACTS / "stages.json",
                         HUB_ARTIFACTS / "applications.json", HUB_ARTIFACTS / "structure_bound.json")},
            "limits": {"pairing_order": PARTNER_ORDER_LIMIT, "repeat_incidence": REPEAT_INCIDENCE_LIMIT,
                       "inputs": "archived complete ages only. Later birth counts without parent rosters are separate."},
            "original_resource_limits": {"EXPLOSIVE": {"rounds": 20, "junction_threshold": 6000, "seconds": 30,
                                                       "address_space_bytes": 2500000000},
                                         "MERGE-BURST": {"rounds": 60, "seconds": 900, "address_space_bytes": 6000000000},
                                         "WALL-READ": {"rounds": 40, "seconds": 1200, "address_space_bytes": 7 << 30}},
            "controls": controls(), "starts": rows, "classifications": dict(Counter(r["classification"] for r in rows)),
            "archive_ages_including_initial": sum(len(r["stages"]) for r in rows),
            "canonical_sources": sum(r["canonical_source"] for r in rows)}
    save(data, args.output)
    print(json.dumps(data["classifications"], sort_keys=True))


if __name__ == "__main__":
    main()
