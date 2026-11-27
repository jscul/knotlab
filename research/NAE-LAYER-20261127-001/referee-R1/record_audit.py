"""Audit the frozen record, census coverage, and prior credit without importing study code."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
STUDY_ID = "NAE-LAYER-20261127-001"
STUDY = f"research/{STUDY_ID}"
FREEZE = "643e5a85a90477bbf8b63050c2c3c9c029a3013b"
RESULT = "b2dc53d665e3649960bfcea756854a48ce6b968e"
INDEX = "8a4f08870e2322d7024f9be254e9a1aaf09e837f"
HANDOFF = "d642a52c42"
STARTS = "research/FORBID-EDITS-20261126-001/starts.json"
GUIDE = "publication/knotlab/INTUITIONS.md"
PILOT_SIZE = 32
PASCH_INDEX = 959

QUERIES = (
    "Pasch",
    "not-all-equal loose patterns tree rings erase composition forcing",
    "whole-held facts not-all-equal growth weighting correlations",
    "not-all-equal state recovery essential Pasch loose marked",
    "two knots sharing one distinction compose projection opposite values",
)

CREDIT = {
    "research/BASE-THREE-20261021-001/base_three.md": (
        "Opposite forcing at one shared distinction gives the two-knot composition rule."
    ),
    "research/FRESH-COUNT-20261118-001/preregistration.md": (
        "The complete-round groups and the fewest-fresh rule predate the study."
    ),
    "research/NAE-GROWTH-20261119-001/nae_growth.md": (
        "T1 gives old-state extension with private fresh distinctions. T2 gives the ordinary not-all-equal fresh floor. "
        "T3 gives the parity projection by summing the laws of a connected part."
    ),
    "research/BASES-WITHIN-20261112-001/bases_within.md": (
        "The earlier nested construction recovers the supplied outer law. Ordinary growth supplies a different test of a further layer."
    ),
    "research/TWO-CLASS-SIGN-20261126-001/referee-R1/report.md": (
        "Earlier sampled census starts and ring profiles had one not-all-equal class wherever read. "
        "The referee checked connectivity directly under single changes on 22 starts and 11 grown stages."
    ),
    "research/CUT-BINDING-20261126-001/README.md": (
        "Ring parities on three built not-all-equal starts took every joint tuple through two rounds. "
        "Those supplied parities differ from the full projection onto the currently loose distinctions."
    ),
    "research/SIGNED-COUNT-20261126-001/README.md": (
        "The ring of four has 82 states and a measured correlation under equal weighting. "
        "Its published read uses shared distinctions."
    ),
    "research/OVERLAP-READ-20261111-001/overlap_read.md": (
        "The pair-count result and the six-distinction Pasch example already give identical states in the two presentations."
    ),
    "research/STATES-GROWTH-20261119-001/states_growth.md": (
        "The 18-state four-knot ambiguity, two irredundant presentations, and the limitation from redundant laws were already recorded."
    ),
    "research/THREE-READERS-AND-GROWTH-20261120-001B/classification.md": (
        "This is the complete finite classification within connected presentations with two holders at most, arity at least three, "
        "full local projections and each law essential in both presentations. The closed Pasch case is the sole exception there."
    ),
    "research/ONE-STATEMENT-20261127-001/referee-R1/report.md": (
        "The earlier full census established 7,074 unique marked presentations out of 7,075. Its ten-knot witness outside the census "
        "keeps the same marked loose distinctions and allows the same 209,952 states, with two families in one presentation and one "
        "in the other. This already refutes unrestricted recovery."
    ),
    "research/BINDING-20261126-001/referee-R1/report.md": (
        "The earlier parity review found bindings on disjoint cycle and path carriers and left a further layer open. "
        "It explicitly established preservation of old projections under ordinary growth."
    ),
    "research/NAE-WEIGHTS-20261127-001/README.md": (
        "The equal-weighting study was first committed after this freeze. The dated search can return it because the cutoff includes that day."
    ),
}


# The numbered corrections and proposed replacements are in report.md.
WORDING = (
    (
        RESULT, f"{STUDY}/README.md", 6,
        'The sections down to "Frozen" were committed before the runs.',
    ),
    (
        RESULT, f"{STUDY}/README.md", 5,
        "Under not-all-equal no law is a sum of others, so parity's facts (sums kept by every small change) have no analogue to lean on.",
    ),
    (
        RESULT, f"{STUDY}/README.md", 5,
        "Census start 959, the one start whose not-all-equal states admit a second presentation, is the record's Pasch pattern "
        "(its distinctions fall into three pairs no knot holds together; exchanging one pair's members exchanges the two presentations).",
    ),
    (
        RESULT, f"{STUDY}/README.md", 3,
        "**The census.** On all 7,075 starts the not-all-equal states form one class under single-distinction changes (C1) and "
        "no pair of distinctions is tied (C2); on all 6,845 starts with loose distinctions the loose patterns number 2^m − 2 on "
        "the 15 tree-shaped ones and 2^m on the other 6,830 (C3); after one round all 2^m occur on all 500 starts read (C4). "
        "Under parity 2^(m − 1) on every start (C3').",
    ),
    (
        RESULT, f"{STUDY}/README.md", 1,
        "**So, under not-all-equal.** A fact held by the whole is a relation among separately carried values that no proper part "
        "implies: on a part with no ring it exists (exactly two loose patterns missing), and it is the first knots' own law read "
        "through relays (whenever a relayed value is nonzero it fixes the first knot's distinction), not a new law. A ring "
        "erases it, and so does one round of growth, since growth's joins close rings. Nothing is kept by small changes (one "
        "class) and nothing is tied. **On the owner's rungs:** repetition, in the weak form of the first layer composed with "
        "itself; no second layer; and growth removes even the composed relation after one round. Under parity it is the reverse: "
        "rings carry the facts, and growth makes them last.",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 3,
        "Under not-all-equal nothing is kept by small changes and nothing is tied",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 1,
        "The only relations are compositions over parts with no ring.",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 2,
        "**Rings and growth erase them.** Closing a ring of five makes every loose pattern occur; after one round of growth "
        "every pattern occurs (the seven-knot tree, and all 500 census starts read).",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 1,
        "**On the owner's rungs:** repetition in the weak form (the first layer composed with itself); no second layer; and "
        "growth removes even that. Under parity the reverse: rings carry the facts and growth makes them last.",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 2,
        "Not-all-equal's whole-held relations are compositions that rings and growth erase",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 5,
        "under not-all-equal the states fix the knots but growth keeps no whole-held fact",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 2,
        "Nothing survives one round of growth",
    ),
    (
        RESULT, f"{STUDY}/decision.md", 5,
        "A law between the two: one whose states fix its knots (like not-all-equal) and whose rings carry facts that growth keeps (like parity), "
        "for example mixed knots or a three-valued law",
    ),
    (
        HANDOFF, f"{STUDY}/referee_handoff.md", 1,
        "the first layer read through relays; rings and growth erase it; no second layer",
    ),
    (
        RESULT, f"tickets/{STUDY_ID}.json", 1,
        "the only whole-held relations are compositions over parts with no ring, which rings and one round of growth erase; no second layer.",
    ),
    (
        INDEX, "docs/OBJECTS.md", 3,
        "All 7,075 census starts (500 grown one round)",
    ),
    (
        INDEX, "docs/OBJECTS.md", 2,
        "T7: 25 of 27 triples, 510 of 512, ring and growth erase",
    ),
    (
        INDEX, "docs/RESEARCH_GOALS.md", 5,
        "Under not-all-equal nothing is kept by small changes and nothing is tied on any census start; the only whole-held relations "
        "are compositions over parts with no ring (the advisor's seven-knot tree: 25 of 27 triples), which a ring or one round of growth "
        "erases (every loose pattern after one round on all 500 starts read). Parity keeps facts but does not fix the second layer's knots; "
        "not-all-equal fixes the knots but keeps no fact.",
    ),
)


def git(*args):
    return subprocess.check_output([
        "git", "-c", "core.packedGitWindowSize=16m", "-c", "core.packedGitLimit=96m", *args,
    ], cwd=ROOT)


def blob(revision, path):
    return git("show", f"{revision}:{path}")


def tracked(revision, path):
    return bool(git("ls-tree", "--name-only", revision, "--", path).strip())


def history():
    revised_note = blob(RESULT, f"{STUDY}/README.md")
    frozen_note = blob(FREEZE, f"{STUDY}/README.md")
    scripts = [f"{STUDY}/{name}" for name in ("census.py", "t7.py")]
    records = [f"{STUDY}/{name}" for name in ("census.jsonl", "t7.json")]
    anchored = {path: (FREEZE if path == STARTS else RESULT) for path in (STARTS, *scripts, *records)}
    assert revised_note.startswith(frozen_note)
    assert git("rev-parse", f"{RESULT}^").decode().strip() == FREEZE
    assert all(blob(FREEZE, path) == blob(RESULT, path) for path in scripts)
    assert all(not tracked(FREEZE, path) for path in records)
    return {
        "commits": {
            label: dict(zip(("revision", "committed_at"), git("show", "-s", "--format=%H%n%cI", rev).decode().splitlines()))
            for label, rev in (("freeze", FREEZE), ("results", RESULT), ("goals_and_objects", INDEX), ("handoff", HANDOFF))
        },
        "results_are_direct_child_of_freeze": True,
        "frozen_note_is_unchanged_prefix_of_result_note": True,
        "scripts_unchanged_between_freeze_and_result": True,
        "archives_first_present_at_result": True,
        "scope": "The committed predictions, code and thresholds precede the committed outputs. These timestamps cannot establish when local output was produced or read.",
        "inputs": {
            path: {
                "sha256": sha256(blob(revision, path)).hexdigest(),
                "working_copy_matches": (ROOT / path).read_bytes() == blob(revision, path),
            }
            for path, revision in anchored.items()
        },
    }


def groups(neighbours, live):
    pairs = {frozenset((a, b)) for a, b in combinations(live, 2) if neighbours[a] & neighbours[b]}
    larger = []
    for arity in range(3, len(live) + 1):
        for group in combinations(live, arity):
            if any(frozenset(pair) not in pairs for pair in combinations(group, 2)):
                continue
            if not set.intersection(*(neighbours[knot] for knot in group)):
                larger.append(frozenset(group))
    maximal = [group for group in larger if all(not group < other for other in larger)]
    return maximal + [pair for pair in pairs if all(not pair < group for group in maximal)]


def inspect_start(start):
    knot_count, shared, loose = start
    if not any(loose):
        return "closed", None, None
    neighbours = [set() for _ in range(knot_count)]
    for a, b, _ in shared:
        neighbours[a].add(b)
        neighbours[b].add(a)
    live = [k for k, count in enumerate(loose) if count]
    parents = groups(neighbours, live)
    demand = Counter(knot for group in parents for knot in group)
    if any(demand[k] > loose[k] for k in live):
        return "stalled", None, None
    for k in live:
        parents.extend(frozenset((k,)) for _ in range(loose[k] - demand[k]))
    newborn = list(range(knot_count, knot_count + len(parents)))
    for child, group in zip(newborn, parents):
        neighbours.append(set(group))
        for k in group:
            neighbours[k].add(child)
    next_demand = Counter(knot for group in groups(neighbours, newborn) for knot in group)
    # Every ordinary not-all-equal birth has a private fresh distinction (earlier T2).
    fresh = sum(max(1, 3 - len(group), next_demand[child]) for child, group in zip(newborn, parents))
    shared_after = sum(mult for _, _, mult in shared) + sum(loose)
    tree_after = shared_after == knot_count + len(parents) - 1
    return "funded", fresh, tree_after


def census(census_archive, source_archive, pilot):
    rows = census_archive[:PILOT_SIZE] if pilot else census_archive
    tallies = Counter()
    by_knot_count = {str(k): Counter() for k in (3, 4, 5)}
    sample_fresh = Counter()
    eligible = []
    recorded = []
    prefix_coverage = Counter()
    total_tested_grown_patterns = 0
    for index, row in enumerate(rows):
        start = source_archive[index]
        knot_count, shared, loose = start
        distinct_count = sum(mult for _, _, mult in shared) + sum(loose)
        places = Counter(knot for a, b, mult in shared for _ in range(mult) for knot in (a, b))
        assert all(places[k] + count >= 3 and 0 <= count <= 2 for k, count in enumerate(loose))
        assert distinct_count <= 12 and all(mult in (1, 2) for _, _, mult in shared)
        tree = sum(mult for _, _, mult in shared) == knot_count - 1
        m = sum(loose)
        assert row["start"] == f"census {index}"
        assert row["loose"] == m and row["tree-shaped"] == tree
        tallies["recorded_C1_successes"] += row["C1"]
        tallies["recorded_C2_successes"] += row["C2"]
        tallies["C2_pair_opportunities_across_starts"] += distinct_count * (distinct_count - 1) // 2
        tallies["source_starts_with_loose_distinctions"] += bool(m)
        tallies["source_tree_shaped_starts"] += tree
        assert row["C3 predicted"] == 2 ** m - 2 * tree
        tallies["recorded_C3_pattern_count_matches"] += row["C3 patterns"] == row["C3 predicted"]
        if m:
            tallies["recorded_parity_matches_among_starts_with_loose_distinctions"] += row["C3' parity patterns"] == 2 ** (m - 1)
        else:
            assert row["C3' parity patterns"] is None
        status, fresh, grown_tree = inspect_start(start)
        coverage = status
        if status == "funded":
            tallies["funded_tree_shaped_sources"] += tree
            tallies["funded_stages_still_tree_shaped"] += grown_tree
            if fresh <= 14:
                coverage = "eligible_at_cap"
                eligible.append(index)
            else:
                coverage = "funded_over_cap"
        by_knot_count[str(knot_count)][coverage] += 1
        if len(recorded) < 500:
            prefix_coverage[coverage] += 1
        if "C4 after one round" in row:
            recorded.append(index)
            assert coverage == "eligible_at_cap"
            seen, possible = row["C4 after one round"]
            assert possible == 2 ** fresh
            tallies["recorded_C4_full_projections"] += seen == possible
            tallies["recorded_C4_tree_shaped_sources"] += tree
            tallies["recorded_C4_tree_shaped_stages"] += grown_tree
            sample_fresh[fresh] += 1
            total_tested_grown_patterns += possible
            by_knot_count[str(knot_count)]["recorded"] += 1
    assert recorded == eligible[:500]
    coverage_totals = sum(by_knot_count.values(), Counter())
    return {
        "source_roster": "Connected starts of three to five knots once up to renaming. At most twelve distinctions. "
        "Each knot has at least three places and at most two loose distinctions. Each pair of knots shares at most two distinctions.",
        "archive_rows_inspected": len(rows),
        "counts": dict(tallies),
        "coverage_by_source_knot_count": by_knot_count,
        "coverage_totals": {status: coverage_totals[status] for status in ("closed", "stalled", "eligible_at_cap", "funded_over_cap", "recorded")},
        "C4_prefix_including_skipped_rows": prefix_coverage,
        "C4_first_and_last_recorded_zero_based_indices": [recorded[0], recorded[-1]],
        "C4_recorded_stage_loose_distinctions_histogram": sample_fresh,
        "C4_total_loose_patterns_offered_in_reported_checks": total_tested_grown_patterns,
        "C4_funded_eligible_omitted_after_prefix": len(eligible) - len(recorded),
    }


def pasch(start):
    knot_count, shared, loose = start
    assert knot_count == 4 and not any(loose)
    supports = [set() for _ in range(knot_count)]
    for name, (a, b, count) in enumerate(shared):
        assert count == 1
        supports[a].add(name)
        supports[b].add(name)
    source = {tuple(sorted(row)) for row in supports}
    names = range(len(shared))
    coheld = {pair for knot in source for pair in combinations(knot, 2)}
    unmatched = sorted(set(combinations(names, 2)) - coheld)
    assert len(unmatched) == 3 and len({name for pair in unmatched for name in pair}) == 6

    def states(rows):
        return {
            word for word in product((0, 1), repeat=len(names))
            if all(len({word[name] for name in row}) == 2 for row in rows)
        }

    source_words = states(source)
    rival = {tuple(sorted(row)) for row in product(*unmatched)} - source
    assert source_words == states(rival)
    assert source_words == {
        word for word in product((0, 1), repeat=len(names))
        if {(word[a], word[b]) for a, b in unmatched} >= {(0, 0), (1, 1)}
    }
    a, b = unmatched[0]
    swap = {a: b, b: a}
    assert {tuple(sorted(swap.get(name, name) for name in row)) for row in source} == rival
    candidates = [row for row in combinations(names, 3) if all(len({word[k] for k in row}) == 2 for word in source_words)]
    closed_presentations = [
        rows for rows in combinations(candidates, 4)
        if Counter(k for row in rows for k in row) == Counter({k: 2 for k in names}) and states(rows) == source_words
    ]
    assert {frozenset(rows) for rows in closed_presentations} == {frozenset(source), frozenset(rival)}
    return {
        "description": "The four ternary knots in which each pair of knots shares one distinction. Every distinction has two holders.",
        "zero_based_archive_index": PASCH_INDEX,
        "source_supports": sorted(source),
        "rival_supports": sorted(rival),
        "pairs_held_together_by_no_knot": unmatched,
        "loose_distinctions": 0,
        "allowed_states_in_both_presentations": len(source_words),
        "implied_ternary_not_all_equal_supports": candidates,
        "closed_four_knot_presentations": len(closed_presentations),
    }


def prior_work(pilot):
    search_results = []
    for query in QUERIES[:1] if pilot else QUERIES:
        args = ["objects", query, "--until", "2026-11-27", "--exclude", STUDY_ID, "--deep", "--json"]
        result = subprocess.check_output([sys.executable, "-B", "scripts/track.py", *args], cwd=ROOT)
        rows = json.loads(result)
        hits = {
            section: [{"record": row["record"], "present_at_freeze": tracked(FREEZE, row["record"])} for row in entries[:3]]
            for section, entries in rows.items()
        }
        search_results.append({"arguments": args, "first_three_paths_per_section": hits})
    gate = subprocess.run(
        [sys.executable, "-B", "scripts/track.py", "objects-gate", f"{STUDY}/README.md"],
        cwd=ROOT, check=False, text=True, capture_output=True,
    )
    return {
        "searches": search_results,
        "cutoff_scope": "The date is inclusive. Git checks whether each returned path was present at the freeze.",
        "retrospective_prior_work_gate": {"exit_status": gate.returncode, "result": gate.stdout.strip()},
        "credit": {
            path: {"present_at_freeze": tracked(FREEZE, path), "relation": relation}
            for path, relation in CREDIT.items()
        },
    }


def wording_targets():
    fixes = []
    for revision, path, report_fix, quote in WORDING:
        lines = blob(revision, path).decode().splitlines()
        parts, offsets = [], []
        offset = 0
        for number, line in enumerate(lines, 1):
            text = " ".join(line.split())
            if text:
                parts.append(text)
                offsets.append((number, offset))
                offset += len(text) + 1
        offset = " ".join(parts).index(quote)
        line = next(number for number, start in reversed(offsets) if start <= offset)
        fixes.append({
            "report_fix": report_fix, "revision": revision, "path": path, "line": line,
            "archived_excerpt": quote,
        })
    return fixes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="read the first 32 archived rows and one prior-work query")
    args = parser.parse_args()
    starts = json.loads(blob(FREEZE, STARTS))
    rows = [json.loads(line) for line in blob(RESULT, f"{STUDY}/census.jsonl").splitlines()]
    tally = rows.pop()["tally"]
    assert len(rows) == len(starts) == tally["starts"]
    assert len({row["start"] for row in rows}) == len(rows)
    output = {
        "mode": "pilot" if args.pilot else "full",
        "history": history(),
        "t7_archived_observations": json.loads(blob(RESULT, f"{STUDY}/t7.json")),
        "census_archived_tally": tally,
        "census_coverage": census(rows, starts, args.pilot),
        "pasch": pasch(starts[PASCH_INDEX]),
        "prior_work": prior_work(args.pilot),
        "wording_targets": wording_targets(),
        "frozen_stop": "Keep the historical stopping rule in the frozen text. Annotate it with the scope of the current-loose projection test and the preservation of source projections.",
        "guide": {
            "study_is_cited_at_handoff": STUDY_ID in blob(HANDOFF, GUIDE).decode(),
            "relevant_sections": ["4.7 Knots alone", "12.3 Whether it happens again, one pattern up"],
            "scope": "The guide already cites the Pasch example and leaves a repeated tower step open. No passage attributes the closed study's headline to its census.",
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
