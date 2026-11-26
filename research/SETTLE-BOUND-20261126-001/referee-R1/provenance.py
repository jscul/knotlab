"""Audit the recorded design, prior work, and the scope of the saved starts."""

import argparse
from collections import Counter
import gzip
import hashlib
from itertools import combinations, islice, product
import json
from math import comb
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.relative_to(ROOT)
NOTE = STUDY / "README.md"
PREDECESSOR = Path("research/LOOK-ALIKE-20261126-001")
FREEZE = "ec406f0ff7"
RESULTS = "0d3f180c31"
INDEX_UPDATE = "bf097af102"
PREDECESSOR_RESULTS = "89f8da21e9"
PREDECESSOR_REFEREE = "8de314b77c"
SEARCH_DATE = "2026-11-26"
QUERIES = (
    "local reader view settles polynomial counts birth kind cut",
    "settling round largest common neighbour block round one fresh distinctions",
    "ordinary growth parity not-all-equal implied closing top relay tail",
    "binomial burst maximal live neighbour set one block merge",
    "six knot census starts sample growth parity waiting",
    "pair agreement compared local birth kinds polynomial counts",
)


def run(command, *, data=None, env=None, check=True):
    return subprocess.run(
        command, cwd=ROOT, input=data, capture_output=True, env=env, check=check
    )


def git(*arguments):
    return run(["git", *map(str, arguments)]).stdout


def contents(revision, path):
    return git("show", f"{revision}:{path}")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def history(frozen):
    result_note = contents(RESULTS, NOTE)
    indexed_paths = ["docs/RESEARCH_GOALS.md", "docs/OBJECTS.md", "docs/LONG_RUNNING.md"]
    paths = [STUDY / "bound.py", PREDECESSOR / "alike.py", PREDECESSOR / "phase2.py"]
    return {
        "commits": [
            {"revision": revision, "commit_time": git("show", "-s", "--format=%cI", revision).decode().strip()}
            for revision in (PREDECESSOR_RESULTS, FREEZE, PREDECESSOR_REFEREE, INDEX_UPDATE, RESULTS)
        ],
        "freeze_changes": git("diff-tree", "--no-commit-id", "--name-status", "-r", FREEZE, "--", STUDY).decode().splitlines(),
        "result_changes": git("diff-tree", "--no-commit-id", "--name-status", "-r", RESULTS, "--", STUDY).decode().splitlines(),
        "first_committed_note_is_unchanged_prefix_of_results_note": result_note.startswith(frozen),
        "first_committed_note_is_unchanged_prefix_of_current_note": (ROOT / NOTE).read_bytes().startswith(frozen),
        "frozen_note_sha256": digest(frozen),
        "code": {
            str(path): {
                revision: digest(contents(revision, path))
                for revision in (FREEZE, RESULTS)
            }
            for path in paths
        },
        "index_update_paths": git("diff-tree", "--no-commit-id", "--name-only", "-r", INDEX_UPDATE, "--", *indexed_paths).decode().splitlines(),
        "frozen_note_sections": [line for line in frozen.decode().splitlines() if line.startswith("## ")],
        "limitations": "Commit order verifies the recorded design precedes the committed results. It cannot date an unrecorded pilot or show which prior runs had been read.",
    }


def prior_work(frozen, queries):
    track = [sys.executable, "-B", "scripts/track.py"]
    gates = []
    for label, argument, data in ((FREEZE, "/dev/stdin", frozen), ("current", str(NOTE), None)):
        command = track + ["objects-gate", argument]
        result = run(command, data=data, check=False)
        gates.append({
            "note": str(NOTE), "revision": label, "arguments": command[2:],
            "exit": result.returncode,
            "output": (result.stdout + result.stderr).decode().strip(),
        })
    tracking = ROOT / "research/tracking.db"
    before = digest(tracking.read_bytes())
    searches = []
    for query in queries:
        command = track + [
            "objects", query, "--until", SEARCH_DATE, "--exclude", STUDY.name, "--limit", "8", "--json",
        ]
        hits = json.loads(run(command).stdout)
        searches.append({
            "arguments": command[2:],
            **{
                kind: [{k: row[k] for k in ("id", "date", "record", "score", "matched")} for row in hits[kind]]
                for kind in ("index", "other_epics")
            },
        })
    return {
        "gates": gates,
        "searches": searches,
        "index_sha256_before": before,
        "index_sha256_after": digest(tracking.read_bytes()),
        "search_date_scope": "The day filter is inclusive. Same-day records require a Git chronology check.",
    }


def proper_supported_equations(holdings):
    """For each starting parity rule, find a narrower equation the whole start forces."""
    # Forgetting variables retains exactly the parity consequences supported
    # on the variables kept. A nonzero consequence on a proper part fails K2.
    rows = [sum(1 << distinction for distinction in places) for places in holdings]
    span = {0}
    for row in rows:
        span.update(prior ^ row for prior in tuple(span))
    restrictions = []
    for position, row in enumerate(rows):
        proper = [other for other in span if other and other != row and other & row == other]
        if proper:
            smallest = min(proper, key=lambda other: (other.bit_count(), other))
            support = [i for i in range(smallest.bit_length()) if smallest >> i & 1]
            restrictions.append({"starting_rule": position, "forced_parity_on": support})
    return restrictions


def check_witness(holdings, rule_position):
    """Check a selected projection independently in the canonical relation checker."""
    naming = {place: f"x{place}" for places in holdings for place in places}
    clauses = []
    for places in holdings:
        for bits in product((0, 1), repeat=len(places)):
            if sum(bits) % 2:
                clauses.append(" ".join(("~" if bit else "") + naming[place] for place, bit in zip(places, bits)))
    target = [naming[place] for place in holdings[rule_position]]
    witnesses = sorted(set(naming.values()) - set(target))
    command = [
        sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
        "--loops", *target[:-1], "--contact", target[-1], "--witnesses", *witnesses, "--json",
    ]
    relation = json.loads(run(command, env={**os.environ, "PYTHONPATH": "tools"}).stdout)
    return {
        "starting_rule": rule_position,
        "arguments": command[2:],
        "K1": relation["binding"], "K2": relation["loss_on_erasure"], "K3": relation["coexistence"],
        "allowed": relation["allowed"], "variables": relation["variables"],
    }


def first_round_groups(holdings):
    multiplicity = Counter(place for places in holdings for place in places)
    loose = [sum(multiplicity[place] == 1 for place in places) for places in holdings]
    live = {position for position, count in enumerate(loose) if count}
    neighbours = [set(places) for places in holdings]
    blocks = {
        frozenset(j for j in live if j != i and places & neighbours[j])
        for i, places in enumerate(neighbours)
    }
    maximal = {block for block in blocks if len(block) >= 2 and not any(block < other for other in blocks)}
    pairs = {frozenset(pair) for block in maximal for pair in combinations(block, 2)}
    larger = []
    for size in range(3, len(live) + 1):
        for members in combinations(live, size):
            group = frozenset(members)
            if all(frozenset(pair) in pairs for pair in combinations(group, 2)) and not any(group <= b for b in maximal):
                larger.append(group)
    groups = {group for group in larger if not any(group < other for other in larger)}
    groups |= {pair for pair in pairs if not any(pair <= larger_group for larger_group in groups)}
    demands = Counter(member for group in groups for member in group)
    short = [member for member in sorted(live) if demands[member] > loose[member]]
    return loose, maximal, groups, short


def block_case(row, loose, maximal, groups, short, block):
    holds = row["stars"]
    shared_holder = [
        i for i, places in enumerate(holds)
        if all(i != j and set(places).intersection(holds[j]) for j in block)
    ]
    cases = {
        "census_index": row["index"], "start_holdings": holds, "loose_counts": loose,
        "live_neighbour_set": sorted(block), "common_neighbours": shared_holder,
        "maximal_live_neighbour_sets": sorted(map(sorted, maximal)),
        "pairs_expected_from_unqualified_binomial_count": comb(len(block), 2),
        "derived_round_one_groups_before_shortage_check": sorted(map(sorted, groups)),
        "short_members": short,
        "derived_round_one_pair_joins_within_set": sum(len(group) == 2 and group <= block for group in groups) if not short else 0,
        "archive_round_one_kinds_and_counts": row["rows"][0]["sig0"] if row["rows"] else [],
        "archive_first_round_counts": [r["n"] for r in row["rows"][:6]],
        "archive_ending": row["end"],
    }
    return cases


def archive_scope(size, law, limit):
    file_tag = f"g{size}_{law}"
    recorded = json.loads((ROOT / STUDY / f"test_{file_tag}.json").read_text())
    miss_indices = {row[0] for row in recorded["bound misses"]}
    starts = dimensions = max_knots = 0
    end_counts = Counter()
    dimension_rounds = Counter()
    outside_parity_knot_scope = []
    block_examples = {}
    with gzip.open(ROOT / STUDY / f"grown_{file_tag}.jsonl.gz", "rt") as source:
        for line in islice(source, limit):
            row = json.loads(line)
            starts += 1
            end_counts[row["end"]] += 1
            max_knots = max(max_knots, row["knots"])
            has_dimension_label = row["kind"].startswith("dim ")
            dimensions += has_dimension_label
            if has_dimension_label:
                dimension_rounds[len(row["rows"])] += 1
            if size == 5 and law == "nae" and len(block_examples) < 3:
                loose, maximal, groups, short = first_round_groups(row["stars"])
                if row["index"] == 2077:
                    block = next(b for b in maximal if b == {1, 2, 4})
                    block_examples["overlapping_maximal_sets"] = block_case(row, loose, maximal, groups, short, block)
                if len(maximal) == 1:
                    block = next(iter(maximal))
                    if len(block) >= 3 and len(block) == sum(count > 0 for count in loose):
                        if short and "unique_maximal_set_stalls" not in block_examples:
                            block_examples["unique_maximal_set_stalls"] = block_case(row, loose, maximal, groups, short, block)
                        if not short and sum(loose) > len(block) * (len(block) - 1) and "unique_maximal_set_with_surplus" not in block_examples:
                            block_examples["unique_maximal_set_with_surplus"] = block_case(row, loose, maximal, groups, short, block)
            if law == "par" and (restrictions := proper_supported_equations(row["stars"])):
                outside_parity_knot_scope.append({
                    "census_index": row["index"], "holdings": row["stars"], "kind": row["kind"],
                    "has_dimension_label": has_dimension_label, "recorded_bound_miss": row["index"] in miss_indices,
                    "restrictions": restrictions,
                })
    return {
        "starts_read": starts, "dimension_labels": dimensions,
        "archived_end_counts": dict(sorted(end_counts.items())), "maximum_saved_knot_count": max_knots,
        "saved_rounds_by_dimension_labelled_start": dict(sorted(dimension_rounds.items())),
        "parity_start_rules_failing_K2_in_the_whole": outside_parity_knot_scope,
        "parity_starts_with_failed_K2_and_a_dimension_label": sum(row["has_dimension_label"] for row in outside_parity_knot_scope),
        "parity_starts_with_failed_K2_and_a_recorded_bound_miss": sum(row["recorded_bound_miss"] for row in outside_parity_knot_scope),
        "block_examples": block_examples,
    }


def surface_lines(path, phrase):
    return [
        {"line": number, "text": line}
        for number, line in enumerate((ROOT / path).read_text().splitlines(), start=1)
        if phrase.lower() in line.lower()
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="read the first 128 starts per archive and run one search")
    args = parser.parse_args()
    frozen = contents(FREEZE, NOTE)
    evidence = {
        "history": history(frozen),
        "prior_work": prior_work(frozen, QUERIES[:1] if args.pilot else QUERIES),
        "archives": {
            f"g{size}_{law}": archive_scope(size, law, 128 if args.pilot else None)
            for size in (5, 6) for law in ("nae", "par")
        },
        "surfaces": {
            str(path): surface_lines(path, STUDY.name)
            for path in (
                Path("docs/OBJECTS.md"), Path("docs/RESEARCH_GOALS.md"),
                Path("publication/knotlab/INTUITIONS.md"), Path("publication/knotlab/docs/RESEARCH_GOALS.md"),
                Path("publication/knotlab/HISTORY.md"),
            )
        },
        "guide_result_phrases": {
            phrase: surface_lines(Path("publication/knotlab/INTUITIONS.md"), phrase)
            for phrase in ("settling round", "local reader", "settled view", "M + 5", "round of the last merge")
        },
        "source_checks": {
            "previous_settling": [f"{PREDECESSOR}/referee-R1/report.md:7", f"{PREDECESSOR}/referee-R1/report.md:22"],
            "pair_exactness_implication_already_noted": [f"{PREDECESSOR}/README.md:141", f"{PREDECESSOR}/referee-R1/report.md:8"],
            "prior_growth_law_swap": ["research/NAE-GROWTH-20261119-001/nae_growth.md:95", "research/NAE-GROWTH-20261119-001/nae_growth.md:109", "research/NAE-GROWTH-20261119-001/nae_growth.md:112", "research/NAE-GROWTH-20261119-001/referee-R1/report.md:50"],
            "earlier_six_knot_roster_and_different_measurement": ["research/DESCENT-HELD-20261125-001/definitions.md:210", "research/DESCENT-HELD-20261125-001A/results.md:81"],
            "previous_parity_start_screen": ["research/DESCENT-HELD-20261125-001/definitions.md:189"],
            "maximal_sets_and_binomial_scope": {
                "group_rule": "proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md:29",
                "reduced_class_conditions": "proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md:75",
                "branch_system_with_extra_distinctions": "proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/proof.md:81",
                "recorded_isolated_bursts": "research/MERGE-BURST-20261119-001/referee-R1/report.md:21",
                "qualification": "A common-neighbour set supplies candidate pairs. A larger joining group can cover those pairs. For one maximal set all candidates inside it are pair groups, subject to the shortage rule. Extra loose distinctions produce offshoots and change the whole birth count. The earlier isolated bursts use the branch system with their measured loose counts, alongside the proof's other premises.",
            },
        },
    }
    for key in ("g5_par", "g6_par"):
        archive = evidence["archives"][key]
        invalid = archive["parity_start_rules_failing_K2_in_the_whole"]
        if invalid:
            first = invalid[0]
            archive["canonical_check_of_first_failed_rule"] = check_witness(
                first["holdings"], first["restrictions"][0]["starting_rule"]
            )
    target = HERE / ("provenance_pilot.json" if args.pilot else "provenance.json")
    target.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
