"""Recount the exploratory fixed-place probe from its saved output tables."""

import argparse
from collections import Counter, defaultdict
from functools import cache
import gzip
from itertools import combinations, islice, permutations
import json
from math import comb
from pathlib import Path


PROBE = Path(__file__).resolve().parents[1] / "checks" / "form_at_a_fixed_place"
REPLICATION = PROBE.parents[3] / "artifacts" / "FOLLOWS-THE-FORM-20261125-001A"
BARE = "(none)"
MADE = "classes by what it makes"
COURSE = "classes"
COUNTS = "per round (X only births, fresh, takes; second only births; of both)"


def records(filename, limit):
    with gzip.open(PROBE / filename, "rt") as source:
        return list(map(json.loads, islice(source, limit)))


def row_name(row):
    spec = row["spec"]
    return " / ".join((spec["take"] or "no take", spec["treatment"]))


@cache
def seed(label):
    kind, counts = label.split(":")
    counts, _, holder = counts.partition("@")
    loose = tuple(map(int, counts.replace(";", ",").split(",")))
    held = int(holder in {"mid", "arm"})
    partners = {
        "one": (), "two": ((0, 1),), "chain3": ((0, 1), (1, 2)),
        "ring3": ((0, 1), (1, 2), (0, 2)), "star3": ((0, 1), (0, 2), (0, 3)),
        "chain": tuple((i, i + 1) for i in range(len(loose) - 1)),
    }[kind]
    meets = tuple(frozenset(b if a == i else a for a, b in partners if i in (a, b))
                  for i in range(len(loose)))
    return loose, held, meets


@cache
def local_profiles(label):
    loose, held, meets = seed(label)
    held_counts = (loose[held], len(meets[held]))
    partners_loose = tuple(sorted(loose[i] for i in meets[held]))
    # The induced meeting pattern with the held knot fixed, to two partner steps.
    within_two = set(meets[held]).union(*(meets[i] for i in meets[held])) - {held}
    patterns = []
    for rest in permutations(sorted(within_two)):
        order = (held,) + rest
        patterns.append((tuple(loose[i] for i in order),
                         tuple(j in meets[i] for i, j in combinations(order, 2))))
    # The third profile also used by the probe's feature script records the
    # loose counts down two steps, without recording identities at the second step.
    two_step_counts = tuple(sorted(
        (loose[i], tuple(sorted(loose[j] for j in meets[i] - {held})))
        for i in meets[held]
    ))
    return {
        "held knot counts": held_counts,
        "held and partners' loose counts": (held_counts, partners_loose),
        "counts through two partner steps": (held_counts, two_step_counts),
        "induced meeting pattern through two partner steps": min(patterns),
    }


def fate(counts):
    if len(counts) < 4:
        return "not read"
    first_only = [r[0] for r in counts[-3:]]
    if not any(first_only):
        return "taken up" if any(r[4] for r in counts[-3:]) else "no births of the first"
    if len(set(first_only)) == 1:
        return "steady"
    a, b, c = first_only
    if a < b < c:
        return "grows"
    if a > b > c:
        return "shrinks"
    return "other"


def observed_fate_category(label):
    if label in {"taken up", "no births of the first"}:
        return "ends in the own descent"
    return label


def assert_saved_partitions(row, read_lengths):
    for key, lengths_key in ((MADE, "classes by round, by what it makes"),
                             (COURSE, "classes by round")):
        past = None
        for round_index, (partition, size) in enumerate(zip(row[key], row[lengths_key], strict=True), 1):
            assert set(partition) == {label for label, n in read_lengths.items() if n >= round_index}
            assert len(set(partition.values())) == size
            if past:
                old_classes = defaultdict(set)
                for label, group in partition.items():
                    old_classes[group].add(past[label])
                assert all(len(labels) == 1 for labels in old_classes.values())
            past = partition


def matched_pairs(names, profiles, final_classes):
    groups = defaultdict(list)
    for name in names:
        groups[profiles[name]].append(name)
    return Counter({
        "compared pairs": comb(len(names), 2),
        "profiles": len(groups),
        "repeated profiles": sum(len(members) > 1 for members in groups.values()),
        "pairs sharing the profile": sum(comb(len(members), 2) for members in groups.values()),
        "pairs sharing the profile but in different classes": sum(
            final_classes[a] != final_classes[b]
            for members in groups.values() for a, b in combinations(members, 2)
        ),
    })


def profile_tests(names, counts, last_common, final_classes):
    profiles = defaultdict(dict)
    for name in names:
        history = counts[name][:last_common]
        round_one = history[0]
        for label, profile in local_profiles(name).items():
            profiles[label][name] = profile
        held = profiles["held knot counts"][name]
        profiles["held knot counts and second-only birth counts by round"][name] = (
            held, tuple(r[3] for r in history))
        profiles["held knot counts and all birth counts of the second by round"][name] = (
            held, tuple(r[3] + r[4] for r in history))
        profiles["round-one sum of first-only fresh distinctions"][name] = round_one[1]
        profiles["round-one five saved counts"][name] = tuple(round_one)
        profiles["first-only birth, fresh and take counts by round"][name] = tuple(tuple(r[:3]) for r in history)
        profiles["all five saved counts by round"][name] = tuple(map(tuple, history))
    return {label: matched_pairs(names, table, final_classes) for label, table in profiles.items()}


def pair_timing(row, names, counts, read_lengths, final):
    out = Counter()
    partitions = row[MADE]
    courses = row[COURSE]
    last_common = min(read_lengths.values())
    for a, b in combinations(names, 2):
        matched_to = min(read_lengths[a], read_lengths[b])
        first = next((i for i in range(matched_to)
                      if partitions[i][a] != partitions[i][b]), None)
        category = str(first + 1) if first is not None else (
            "equal through last round" if matched_to == len(partitions) else "not read further")
        out[category] += 1
        made_diff = final[a] != final[b]
        course_diff = courses[last_common - 1][a] != courses[last_common - 1][b]
        out["apart by common last round"] += made_diff
        out["course only at common last round"] += course_diff and not made_diff
        out["making only at common last round"] += made_diff and not course_diff
        if (len(seed(a)[0]) == 1) != (len(seed(b)[0]) == 1):
            out["single knot versus longer pairs"] += 1
            out["single knot versus longer apart by common last round"] += made_diff
            out["single knot versus longer apart by pair's last round"] += first is not None
        if first is None or first == 0:
            continue
        u, v = counts[a][0], counts[b][0]
        out["late pairs"] += 1
        out["late pairs both without a mixed birth in round one"] += u[4] == v[4] == 0
        out["late pairs with matched round-one mixed birth counts"] += u[4] == v[4]
        out["late pairs with all five round-one counts matched"] += u == v
    return out


def summarize_study(row):
    counts = row[COUNTS]
    read_lengths = {name: n for name, (n, _, _) in row["stops"].items()}
    assert all(len(counts[name]) == n for name, n in read_lengths.items())
    assert row["last"] == max(read_lengths.values())
    assert_saved_partitions(row, read_lengths)
    last_common = min(read_lengths.values())
    assert last_common >= 1
    names = sorted(set(counts) - {BARE})
    assert len(names) == row["forms"]
    final = row[MADE][last_common - 1]
    courses = row[COURSE][last_common - 1]
    actual_fates = {name: fate(history) for name, history in counts.items()}
    for name, category in actual_fates.items():
        saved = row["fate"][name]
        if saved.startswith("steady at "):
            saved = "steady"
        if saved == "ends":
            saved = "ends in the own descent"
        assert saved == observed_fate_category(category), (row["spec"], name, saved, category)
    return {
        "first seed": row["first"],
        "law": row["law"],
        "pair row": row_name(row),
        "rounds read by all": last_common,
        "rounds requested": row["spec"]["rounds"],
        "runs": len(counts),
        "stops": Counter(stop or "completed" for _, stop, _ in row["stops"].values()),
        "classes including bare": len(set(final.values())),
        "classes among forms": len({final[name] for name in names}),
        "course classes including bare": len(set(courses.values())),
        "pair counts": pair_timing(row, names, counts, read_lengths, final),
        "profile tests": profile_tests(names, counts, last_common, final),
        "fates including bare, at each run's last round": Counter(actual_fates.values()),
        "fates of forms, at each run's last round": Counter(actual_fates[name] for name in names),
        "fates of forms, at common last round": Counter(fate(counts[name][:last_common]) for name in names),
    }


def fate_varies(fates, old_reading):
    kinds = {observed_fate_category(key) if old_reading else key for key in fates}
    chosen = {"steady", "grows", "ends in the own descent"} if old_reading else {
        "steady", "grows", "taken up", "no births of the first"}
    return len(kinds & chosen) >= 2


def summarize_family(studies):
    rows = defaultdict(list)
    profiles = defaultdict(Counter)
    for study in studies:
        rows[study["pair row"]].append(study)
        for descriptor, counts in study["profile tests"].items():
            profiles[descriptor].update(counts)
            ties = counts["pairs sharing the profile"]
            violations = counts["pairs sharing the profile but in different classes"]
            profiles[descriptor]["studies with a repeated profile"] += ties > 0
            profiles[descriptor]["studies with no counterexample"] += violations == 0
            profiles[descriptor]["studies with a repeated profile and no counterexample"] += ties > 0 and violations == 0
    by_rule = {}
    for no_take in (True, False):
        selected = [s for s in studies if s["pair row"].startswith("no take") == no_take]
        if selected:
            by_rule["no take" if no_take else "take of sole candidate"] = {
                "classes including bare, range": [min(s["classes including bare"] for s in selected),
                                                   max(s["classes including bare"] for s in selected)],
                "classes among forms, range": [min(s["classes among forms"] for s in selected),
                                              max(s["classes among forms"] for s in selected)],
                "fates of forms, at each run's last round": sum(
                    (s["fates of forms, at each run's last round"] for s in selected), Counter()),
            }
    pair_rows = {}
    for key, members in rows.items():
        pair_rows[key] = {
            "compared pairs": sum(comb(s["runs"] - 1, 2) for s in members),
            "pair counts": sum((s["pair counts"] for s in members), Counter()),
        }
    return {
        "studies": len(studies),
        "runs": sum(s["runs"] for s in studies),
        "stops": sum((s["stops"] for s in studies), Counter()),
        "last common round": Counter(s["rounds read by all"] for s in studies),
        "course classes minus making classes, including bare": Counter(
            s["course classes including bare"] - s["classes including bare"] for s in studies),
        "cap of three maximum classes including bare": max(
            (s["classes including bare"] for s in studies if s["law"].startswith("CAP-3/")), default=None),
        "by take": by_rule,
        "rows": pair_rows,
        "profile tests pooled across studies": profiles,
        "fate varies, own descent, each run's last round, including bare": sum(
            fate_varies(s["fates including bare, at each run's last round"], True) for s in studies),
        "fate varies, own descent, each run's last round, forms alone": sum(
            fate_varies(s["fates of forms, at each run's last round"], True) for s in studies),
        "fate varies, own descent, common last round, forms alone": sum(
            fate_varies(s["fates of forms, at common last round"], True) for s in studies),
        "fate varies, with both endings distinguished, common last round, forms alone": sum(
            fate_varies(s["fates of forms, at common last round"], False) for s in studies),
        "studies below three classes among forms or four including bare": [
            {key: s[key] for key in ("first seed", "law", "classes among forms", "classes including bare")}
            for s in studies if s["classes among forms"] < 3 or s["classes including bare"] < 4],
    }


def depth_tally(rows):
    result = defaultdict(lambda: defaultdict(Counter))
    for row in rows:
        final = row[MADE][min(s[0] for s in row["stops"].values()) - 1]
        chains = sorted((seed(name)[0], group) for name, group in final.items() if name != BARE)
        for (a, group_a), (b, group_b) in combinations(chains, 2):
            if len(a) == len(b):
                differing_sites = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
                if len(differing_sites) != 1:
                    continue
                key = f"depth {differing_sites[0]}"
            else:
                shorter, longer = sorted((a, b), key=len)
                if len(longer) != len(shorter) + 1 or longer[:-1] != shorter:
                    continue
                key = f"length {len(shorter)} against {len(longer)}"
            result[row["law"]][key].update({"pairs": 1, "apart": int(group_a != group_b)})
    return result


def depth_edits(rows):
    result = defaultdict(lambda: defaultdict(Counter))
    failures = []
    for row in rows:
        if "error" in row:
            failures.append({key: row[key] for key in ("spec", "returncode")})
            continue
        for edit in row["rows"]:
            summary = result[row["law"]][str(edit["depth"])]
            course = edit["course first differs"]
            crude = edit["crude first differs"]
            summary["pairs"] += 1
            summary["course and coarse reading disagree on first difference"] += course != crude
            summary[f"course difference round {course}"] += 1
            summary[f"coarse difference round {crude}"] += 1
    return {"studies": len(rows), "failed": failures, "successful studies by law and depth": result}


def examples(mixed):
    rows = [r for r in mixed if r["law"] == "ORD/CANCEL-RETIRE/RELEASE/no-take/nae"]
    matched = [r for r in rows if r["first"] in {"A one knot", "B two knots"}]
    if len(matched) != 2:
        return {}
    a, b = matched
    left, right = (r[MADE][min(s[0] for s in r["stops"].values()) - 1] for r in (a, b))
    pair_comparison = Counter()
    for x, y in combinations(set(left) - {BARE}, 2):
        l, r = left[x] != left[y], right[x] != right[y]
        pair_comparison["both" if l and r else "one only" if l or r else "neither"] += 1
    return {
        "A and B under ordinary count, retiring, no take": pair_comparison,
        "a one-knot and a three-knot second seed tied for all nine rounds": {
            "law": b["law"], "first seed": b["first"],
            "second seeds": ["one:2", "ring3:2,1,1"],
            "class pairs by round": [[p["one:2"], p["ring3:2,1,1"]] for p in b[MADE]],
            "all five counts matched by round": [a == c for a, c in zip(
                b[COUNTS]["one:2"], b[COUNTS]["ring3:2,1,1"], strict=True)],
        },
        "B under ordinary count, retiring, no take": {
            name: [[r[0], r[4]] for r in history] for name, history in b[COUNTS].items()
        },
    }


def saved_checks(rows):
    return {
        "cases": rows,
        "renumbering": sum((Counter(row["renumbering"]) for row in rows), Counter()),
        "knot test": sum((Counter(row["knot test"]) for row in rows), Counter()),
        "base runs": sum(r["forms"] for r in rows),
        "round-one-only roster counts directly recorded": sum(
            n for row in rows if row["spec"]["treatment"] != "CANCEL-WAIT"
            for last, n in row["last round with a start knot in the roster (runs)"] if last == 1),
    }


def signature(entries):
    return tuple(sorted(tuple(entry) for entry in entries))


def replication_key(first, ration, treatment, take):
    return first.split()[0], ration, treatment, "MET-SOLE" if take == "sole" else (take or "none")


def later_replication(mixed, limit):
    """Recount FF 5b from the registered successor's matching mixed cohort."""
    original = {}
    for row in mixed:
        spec = row["spec"]
        key = replication_key(row["first"], spec["ration"], spec["treatment"], spec["take"])
        original[key] = row

    folders = tuple(REPLICATION.glob("*/runs_R1_*of8.jsonl.gz"))
    assert len(folders) == 8
    studies = defaultdict(dict)
    for file in sorted(folders):
        with gzip.open(file, "rt") as source:
            for line in islice(source, limit):
                row = json.loads(line)
                if row["runset"] != "R1" or row["family"] != "mixed":
                    continue
                assert row["linked"] and row["knot_law"] == "nae"
                key = replication_key(row["first"], row["ration"], row["treatment"], row["take"])
                name = row["second"] or BARE
                assert name not in studies[key]
                studies[key][name] = row

    if limit is None:
        assert set(studies) == set(original)
        assert all(set(records) == set(original[key]["stops"]) for key, records in studies.items())
    aggregate = defaultdict(Counter)
    matched_probe_rounds = 0
    roster = Counter()
    for key, panel in sorted(studies.items()):
        _, _, treatment, take = key
        counts = aggregate[f"{take if take != 'none' else 'no take'} / {treatment}"]
        own = {name: tuple(map(signature, row["make"])) for name, row in panel.items()}
        wider_first = {name: signature(row["wider"][0]) for name, row in panel.items()}
        for name, row in panel.items():
            assert row["rounds_read"] == len(own[name]) == len(row["wider"])
            assert all(sum(entry[-1] for entry in made) == n
                       for made, n in zip(row["make"], row["n_own"], strict=True))
            assert all(sum(entry[-1] for entry in wider if entry[-2] == 0) == n
                       for wider, n in zip(row["wider"], row["n_both"], strict=True))
            assert all(signature([entry[:5] + [entry[-1]] for entry in wider if entry[-2] == 1])
                       == made for wider, made in zip(row["wider"], own[name], strict=True))
            if key in original:
                prior = original[key]
                assert [row["rounds_read"], row["stop"], row["knots"]] == prior["stops"][name]
                for made, count, second, both in zip(
                    own[name], prior[COUNTS][name], row["sec_only"], row["n_both"], strict=True
                ):
                    births = sum(entry[-1] for entry in made)
                    fresh = sum(entry[3] * entry[-1] for entry in made)
                    takes = sum(entry[4] * entry[-1] for entry in made)
                    assert [births, fresh, takes, second, both] == count
                matched_probe_rounds += row["rounds_read"]
            if treatment != "CANCEL-WAIT" and name != BARE:
                roster["runs"] += 1
                roster["runs with last start member in round one"] += row["last_member_round"] == 1
        last_common = min(len(history) for history in own.values())
        for a, b in combinations(sorted(set(panel) - {BARE}), 2):
            h1, h2 = own[a], own[b]
            equal_wider = wider_first[a] == wider_first[b]
            counts["pairs"] += 1
            counts["pairs with the same wider round-one multiset"] += equal_wider
            first_diff = None
            for i, (x, y) in enumerate(zip(h1, h2), 1):
                if key in original:
                    prior = original[key][MADE][i - 1]
                    # Saved class labels encode equality of the whole prefix.
                    assert (prior[a] != prior[b]) == (x != y), (key, a, b, i)
                if x != y:
                    first_diff = i
                    break
            if first_diff is None or first_diff == 1:
                continue
            counts["late at pair's own horizon"] += 1
            counts["late at all-forms common horizon"] += first_diff <= last_common
            counts["late and same wider round-one multiset, pair's own horizon"] += equal_wider
            counts["late and same wider round-one multiset, all-forms common horizon"] += (
                equal_wider and first_diff <= last_common)
            counts[f"pairs first told apart in round {first_diff}"] += 1
            counts[f"pairs first told apart in round {first_diff}, with wider round-one match"] += equal_wider
    return {
        "scope": "Independent reading in the registered successor, same probe starts and laws, not a new growth run.",
        "wider reading": "Match the multiset of (kind, number of parents, places, fresh distinctions, takes, own-descent flag) for all round-one births of the first seed. Birth identities, parents' identities and the held distinctions are not part of the match.",
        "studies": len(studies),
        "runs including bare": sum(map(len, studies.values())),
        "probe run-rounds with matching five saved counts": matched_probe_rounds,
        "start roster, retiring and making offshoots, linked forms only": roster,
        "pair rows": aggregate,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Read only the first N study rows of each file.")
    args = parser.parse_args()
    report = {
        "stage": "exploratory, saved-output recount",
        "limits": [
            "The class tables contain equality labels rather than the underlying per-birth signatures.",
            "The five per-round counts contain no per-birth mixed signature or full roster. A matched nonzero mixed count can hide different births.",
            "With no mixed birth in either run, a pair still equal by the own-descent reading in round one also matches the wider per-birth reading in that round.",
            "Bare-start records have no second seed. They do not represent the same two seeds with their common distinction removed.",
            "Check rows contain aggregate verdict counts. The individual knot tests and renumbered states are not in those rows.",
            "Retiring and making offshoots eliminate start knots from the parent roster after round one. The growth still reads their shared distinctions when it builds the roster or decides what a birth may take.",
        ],
    }
    for label, filename in (("mixed", "form_b.jsonl.gz"), ("chains", "chains_a.jsonl.gz"),
                            ("second family", "unseen.jsonl.gz")):
        rows = records(filename, args.limit)
        successful = [r for r in rows if "error" not in r]
        studies = [summarize_study(r) for r in successful]
        report[label] = summarize_family(studies)
        report[label]["input"] = filename
        report[label]["failed studies"] = [r["spec"] for r in rows if "error" in r]
        if label == "mixed":
            report[label]["examples"] = examples(successful)
            report["later replication of mixed cohort"] = later_replication(successful, args.limit)
        if label == "chains":
            report[label]["chain edits, by law"] = depth_tally(successful)
    report["single edits"] = depth_edits(records("depth_a.jsonl.gz", args.limit))
    report["saved checks"] = saved_checks(records("checks.jsonl.gz", args.limit))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
