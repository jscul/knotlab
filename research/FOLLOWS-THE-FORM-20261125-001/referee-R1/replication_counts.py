"""Recount the replication rows and audit gate and control coverage from the archived records."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random
from typing import NamedTuple
import zlib


ROOT = Path(__file__).resolve().parents[3]
EPIC = "FOLLOWS-THE-FORM-20261125-001"
TICKET = f"{EPIC}A"
EXPERIMENT = f"{TICKET}-E001_place_fixed_form_changed"
ARCHIVE = ROOT / "artifacts" / TICKET / EXPERIMENT
DESIGN = ROOT / "research" / TICKET
LAWS = tuple(product(
    ("none", "sole"), ("FLOOR1", "CAP-3", "ORD"),
    ("CANCEL-RETIRE", "CANCEL-OFFSHOOT", "CANCEL-WAIT"),
))
RUN_FAMILIES = {
    "R1": (("ABCDE", ("mixed", "chains")), ("FGHIJ", ("second",))),
    "R2": (("KLMNO", ("fresh",)),),
    "R3": (("KLMNO", ("chains",)),),
    "R4": (("KLMNO", ("fresh",)),),
}
AFTER = "after the first round"
FATES = "fates on the window"
PROFILE = "the count profile (studies in which the class is a function of it)"
DEPTH = "depth, chains, first seeds A to E together (told apart / pairs)"
READS = "R*"


class Job(NamedTuple):
    runset: str
    first: str
    family: str
    take: str
    ration: str
    treatment: str
    second: str | None

    @property
    def knot_law(self):
        return "parity" if self.runset == "R4" else "nae"

    def archive_key(self):
        take = "MET-SOLE" if self.take == "sole" else "None"
        return "|".join(map(str, (
            self.runset, self.knot_law, self.family, self.first, take,
            self.ration, self.treatment, self.second, True,
        )))


def load_json(path):
    with path.open() as source:
        return json.load(source)


def json_rows(path):
    with gzip.open(path, "rt") as source:
        yield from map(json.loads, source)


def seed_maps():
    seeds = load_json(DESIGN / "seeds.json")
    forms = {family: {entry["name"]: entry for entry in entries}
             for family, entries in seeds["second"].items()}
    assert all(len(entries) == len(forms[family]) for family, entries in seeds["second"].items())
    return seeds["first"], forms


def scheduled(runset, forms):
    return [
        Job(runset, first, family, take, ration, treatment, second)
        for first_names, families in RUN_FAMILIES[runset]
        for first in first_names for family in families
        for take, ration, treatment in LAWS for second in (None, *forms[family])
    ]


def build_start(first, second):
    """Construct the numbered start directly from FF 2."""
    places = [list(knot) for knot in first["knots"]]
    first_names = set().union(*map(set, places))
    assert first_names == set(range(len(first_names)))
    link = len(first_names)
    places[first["site"]].append(link)
    if second is not None:
        additions = [[d + link + 1 for d in knot] for knot in second["knots"]]
        additions[second["at"]].append(link)
        places.extend(additions)
    return places


def load_runs(runset, forms, smoke=False):
    jobs = scheduled(runset, forms)
    if smoke:
        jobs = [job for job in jobs if job.first == RUN_FAMILIES[runset][0][0][0]]
    wanted = set(jobs)
    rows = {}
    for shard in range(8):
        path = ARCHIVE / f"runs_{runset}_{shard}of8.jsonl.gz"
        for row in json_rows(path):
            key = Job(*(row[field] for field in Job._fields))
            if smoke and key.first != jobs[0].first:
                break
            assert key in wanted and key not in rows and row["knot_law"] == key.knot_law and row["linked"]
            rows[key] = row
    assert rows.keys() == set(jobs), runset
    return rows


def prepared_studies(rows, first_seeds, forms):
    """Use the count of each multiset entry, independently of record order."""
    studies = defaultdict(dict)
    for job, row in rows.items():
        for field in ("make", "wider"):
            row[field] = tuple(tuple(sorted(map(tuple, entries))) for entries in row[field])
        rounds = row["rounds_read"]
        assert all(len(row[field]) == rounds for field in
                   ("make", "wider", "n_own", "n_of_first", "n_both", "sec_only"))
        assert [sum(entry[-1] for entry in entries) for entries in row["make"]] == row["n_own"]
        assert [sum(entry[-1] for entry in entries) for entries in row["wider"]] == row["n_of_first"]
        assert [sum(entry[-1] for entry in entries if not entry[-2]) for entries in row["wider"]] == row["n_both"]
        for own, wide in zip(row["make"], row["wider"], strict=True):
            assert tuple(e[:5] + e[-1:] for e in wide if e[-2]) == own
        n_seed_knots = len(first_seeds[job.first]["knots"])
        if job.second is not None:
            n_seed_knots += len(forms[job.family][job.second]["knots"])
        assert row["knots"] == n_seed_knots + sum(row["n_of_first"]) + sum(row["sec_only"])
        studies[job[1:-1]][job.second] = row
    return studies


def classes(runs, horizon, field="make"):
    groups = defaultdict(set)
    for name, row in runs.items():
        groups[row[field][:horizon]].add("(none)" if name is None else name)
    return frozenset(map(frozenset, groups.values()))


def fate(row, horizon):
    if horizon < 4:
        return "not read"
    a, b, c = own = row["n_own"][horizon - 3:horizon]
    if not any(own):
        return ("ends, taken up" if any(row["n_of_first"][horizon - 3:horizon])
                else "ends, no births")
    if a == b == c:
        return "steady"
    if a < b < c:
        return "grows"
    if a > b > c:
        return "shrinks"
    return "other"


def profile(seed):
    held = set(seed["knots"][seed["at"]])
    neighbours = [set(knot) for index, knot in enumerate(seed["knots"]) if index != seed["at"]]
    return len(held) + 1, len(held.difference(*neighbours)), sum(bool(held & other) for other in neighbours)


def profile_determines_class(rows):
    profile_to_class = {}
    for key, cls in rows:
        if profile_to_class.setdefault(key, cls) != cls:
            return False
    return True


def chain_pairs(seeds):
    loose_counts = {}
    for name, seed in seeds.items():
        knots = list(map(set, seed["knots"]))
        assert seed["at"] == 0
        for i, j in combinations(range(len(knots)), 2):
            assert len(knots[i] & knots[j]) == int(j == i + 1)
        holders = Counter(d for knot in knots for d in knot)
        loose_counts[name] = tuple(sum(holders[d] == 1 for d in knot) for knot in knots)
        assert all(count in (2, 3) for count in loose_counts[name])
    pairs = []
    for (name_a, a), (name_b, b) in combinations(loose_counts.items(), 2):
        if len(a) == len(b):
            different = [i for i, (x, y) in enumerate(zip(a, b, strict=True)) if x != y]
            if len(different) == 1:
                pairs.append((f"depth {different[0]}", name_a, name_b))
        elif len(a) + 1 == len(b) and a == b[:-1]:
            pairs.append((f"{len(a)} against {len(b)} knots", name_a, name_b))
        elif len(b) + 1 == len(a) and b == a[:-1]:
            pairs.append((f"{len(b)} against {len(a)} knots", name_a, name_b))
    return pairs


def depth_table(studies, pairs):
    table = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for (_, family, *law), runs in studies.items():
        if family != "chains":
            continue
        horizon = min(run["rounds_read"] for run in runs.values())
        for cell, a, b in pairs:
            count = table[", ".join(law)][cell]
            count[0] += runs[a]["make"][:horizon] != runs[b]["make"][:horizon]
            count[1] += 1
    return table


def replication_tables(studies, seeds, chains):
    table = {
        name: defaultdict(lambda: defaultdict(Counter))
        for name in ("first told apart", AFTER, FATES, READS)
    }
    table[PROFILE] = defaultdict(Counter)
    table[DEPTH] = depth_table(studies, chains)
    fates_vary = Counter()
    for (_, family, take, _, treatment), runs in studies.items():
        group = f"{take}, {treatment}"
        lengths = [run["rounds_read"] for run in runs.values()]
        horizon, longest = min(lengths), max(lengths)
        forms = {name: run for name, run in runs.items() if name is not None}
        table[READS][family][group][str(horizon)] += 1
        fate_counts = Counter(fate(run, horizon) for run in forms.values())
        table[FATES][family][group].update(fate_counts)
        fates_vary[family] += sum((
            bool(fate_counts["ends, taken up"] + fate_counts["ends, no births"]),
            bool(fate_counts["steady"]), bool(fate_counts["grows"]),
        )) >= 2
        profile_rows = table[PROFILE][family]
        profile_rows["studies"] += 1
        comparison = [
            (profile(seeds[family][name]), tuple(run["sec_only"][:horizon]), run["make"][:horizon])
            for name, run in forms.items()
        ]
        for label, fields in (("the held knot", (0,)), ("the second seed's births by round", (1,)), ("both", (0, 1))):
            profile_rows[label] += profile_determines_class(
                (tuple(row[index] for index in fields), row[2]) for row in comparison
            )
        first_told_apart = table["first told apart"][family][group]
        after = table[AFTER][family][group]
        for a, b in combinations(forms.values(), 2):
            pair_horizon = min(a["rounds_read"], b["rounds_read"])
            first = next((t for t in range(1, pair_horizon + 1) if a["make"][t - 1] != b["make"][t - 1]), 0)
            first_told_apart[str(first) if first else "never" if pair_horizon == longest else "not read further"] += 1
            after["pairs"] += 1
            after["told apart at R*"] += 0 < first <= horizon
            after["first told apart in round 2 or later"] += first >= 2
            after["of those, the wider record of round 1 the same"] += first >= 2 and a["wider"][:1] == b["wider"][:1]
            after["in round 3 or later with the wider records the same through round 2"] += (
                first >= 3 and a["wider"][:2] == b["wider"][:2]
            )
    return table, fates_vary


def flattened_cells(table, prefix=""):
    if isinstance(table, dict):
        return {key: cell for name, value in table.items()
                for key, cell in flattened_cells(value, f"{prefix}/{name}").items()}
    return {prefix: table}


def compare_tables(recomputed, disclosed):
    have = flattened_cells(recomputed)
    want = flattened_cells(disclosed)
    differences = {key: {"recount": have.get(key), "disclosed": want.get(key)}
                   for key in sorted(have.keys() | want.keys()) if have.get(key) != want.get(key)}
    return {"cells_compared": len(have.keys() | want.keys()), "differences": differences}


def compare_replication(studies, forms, chains):
    archive = load_json(DESIGN / "disclosed.json")
    table, fates_vary = replication_tables(studies, forms, chains)
    differences = []
    reads_differ = []
    for published in archive["studies"]:
        key = tuple(published[field] for field in ("first", "family", "take", "ration", "treatment"))
        runs = studies[key]
        lengths = [run["rounds_read"] for run in runs.values()]
        horizon = min(lengths)
        if (horizon != published["R*"] or
                classes(runs, horizon) != frozenset(map(frozenset, published["classes"]))):
            differences.append(key)
        if [sum(r >= t for r in lengths) for t in range(1, max(lengths) + 1)] != published["runs read by round"]:
            reads_differ.append(key)
    assert len(studies) == len(archive["studies"])
    want = archive["tables"]
    pr2_tables = {f"first told apart, {f}": table["first told apart"][f] for f in ("mixed", "second")}
    pr5_tables = {name: {f: table[name][f] for f in ("mixed", "second")} for name in (AFTER, FATES, PROFILE, READS)}
    return {
        "PR1": {"studies_compared": len(studies), "horizon_or_partition_differs": differences,
                "run_count_by_round_differs_outside_prediction": reads_differ},
        "PR2": compare_tables(pr2_tables, {name: want[name] for name in pr2_tables}),
        "PR3": compare_tables(table[DEPTH], want[DEPTH]),
        "PR5": compare_tables(pr5_tables, {name: want[name] for name in pr5_tables}),
        "R1_studies_with_two_of_ends_steady_grows": fates_vary,
        "tables": {**pr2_tables, DEPTH: table[DEPTH], **pr5_tables},
    }


def start_membership(*runsets):
    counts = defaultdict(Counter)
    for runs in runsets:
        for job, row in runs.items():
            if job.family == "chains":
                continue
            treatment = "waiting" if job.treatment == "CANCEL-WAIT" else "retiring or offshoots"
            count = counts[f"{job.runset} {job.family}, {treatment}"]
            count["runs"] += 1
            count["start_knot_in_later_roster"] += row["last_member_round"] > 1
            count["start_knot_in_next_roster"] += row["start_member_final"]
            count["either"] += row["last_member_round"] > 1 or row["start_member_final"]
    return counts


def fresh_checks(nae, parity, nae_studies, parity_studies, depth_studies, chains):
    total_classes = Counter()
    bare_own_class = 0
    partitions_differ = []
    wider_partitions_differ = []
    horizons_differ = []
    common_horizon = {}
    for key, nae_runs in nae_studies.items():
        parity_runs = parity_studies[key]
        n = min(row["rounds_read"] for row in nae_runs.values())
        p = min(row["rounds_read"] for row in parity_runs.values())
        nae_classes, parity_classes = classes(nae_runs, n), classes(parity_runs, p)
        bare_own_class += frozenset({"(none)"}) in nae_classes
        total_classes["NAE studies with at least two form classes"] += sum(bool(group - {"(none)"}) for group in nae_classes) >= 2
        total_classes["parity studies with at least three form classes"] += sum(bool(group - {"(none)"}) for group in parity_classes) >= 3
        if nae_classes != parity_classes:
            partitions_differ.append(key)
        if classes(nae_runs, n, "wider") != classes(parity_runs, p, "wider"):
            wider_partitions_differ.append(key)
        if n != p:
            horizons_differ.append(key)
        common_horizon[key] = min(n, p)
    changed = defaultdict(list)
    changed_through_horizon = []
    fields = ("make", "wider", "sec_only", "rounds_read", "stop", "knots")
    for job, row in nae.items():
        under_parity = parity[job._replace(runset="R4")]
        diff = tuple(field for field in fields if row[field] != under_parity[field])
        if diff:
            changed[diff].append(job.archive_key())
        horizon = common_horizon[job[1:-1]]
        if row["make"][:horizon] != under_parity["make"][:horizon]:
            changed_through_horizon.append(job.archive_key())
    return {
        "S1_bare_class": bare_own_class,
        "S2_PN6": total_classes,
        "S3_first_knot_against_two": {law: cells["1 against 2 knots"]
                                      for law, cells in depth_table(depth_studies, chains).items()},
        "paired_runs": len(nae),
        "studies": len(nae_studies),
        "fields_used_for_parity_comparison": fields,
        "differences_by_field": {" ".join(fields): jobs for fields, jobs in changed.items()},
        "own_descent_differs_through_common_horizon": changed_through_horizon,
        "parity_studies_with_different_membership": partitions_differ,
        "parity_studies_with_different_wider_membership": wider_partitions_differ,
        "parity_studies_with_different_horizon": horizons_differ,
    }


def gate_sample(forms):
    return random.Random(1).sample(scheduled("R1", forms) + scheduled("R2", forms), 400)


def gate_records():
    archive = {}
    for i in range(8):
        for row in json_rows(ARCHIVE / f"gate_{i}of8.jsonl.gz"):
            index = row["sample_index"]
            assert index % 8 == i and index not in archive
            archive[index] = row
    return archive


def gate_counts(first_seeds, forms):
    examples = (
        ("B", forms["mixed"]["one:2"], [[0, 1, 2, 6], [0, 3, 4, 5], [7, 8, 6]]),
        ("D", forms["mixed"]["two:1,2"], [[0, 2, 3, 8], [0, 1, 4], [1, 5, 6, 7], [9, 10, 8], [9, 11, 12]]),
        ("A", None, [[0, 1, 2, 3]]),
    )
    starts = [build_start(first_seeds[first], second) == want for first, second, want in examples]
    sampled = gate_sample(forms)
    archive = gate_records()
    assert set(archive) == set(range(len(sampled)))
    growth = []
    takes = []
    for idx, job in enumerate(sampled):
        row = archive[idx]
        assert row["key"] == job.archive_key()
        if job.take == "none":
            assert row["check"] == "second growth"
            assert row["rounds_compared"] == row["rounds_read"] + 1
            growth.append(row)
        else:
            assert row["check"] == "takes"
            takes.append(row)
    return {
        "starts_as_written": sum(starts),
        "sample_by_runset": Counter(job.runset for job in sampled),
        "no_take_sample": len(growth),
        "no_take_exact": sum(row["exact_equal"] and not row["diffs"] for row in growth),
        "no_take_invariant_equal": sum(row["wl_equal"] and not row["wl_diff_rounds"] for row in growth),
        "no_take_snapshots_compared_including_starts": sum(row["rounds_compared"] for row in growth),
        "sole_take_sample": len(takes),
        "sole_take_exact": sum(row["exact_equal"] and not row["bad"] for row in takes),
        "births_checked_for_takes": sum(row["births"] for row in takes),
        "takes_checked": sum(row["takes"] for row in takes),
    }


def control_schedule(forms):
    nae, parity = scheduled("R2", forms), scheduled("R4", forms)
    rng = random.Random(2)
    renumber = rng.sample([job for job in nae if job.take == "none"], 100)
    renumber += rng.sample([job for job in nae if job.take == "sole"], 100)
    renumber += random.Random(7).sample(parity, 100)
    rng = random.Random(6)
    knot_tests = rng.sample(nae, 200) + rng.sample(parity, 100)
    return renumber, knot_tests


def read_controls():
    rows = {}
    truncated = {}
    by_launch = defaultdict(Counter)
    for path in sorted(ARCHIVE.glob("controls_*of*.jsonl.gz")):
        # The two stopped jobs left an incomplete gzip member. Only whole JSON lines survive it.
        inflater = zlib.decompressobj(31)
        data = inflater.decompress(path.read_bytes())
        assert not inflater.unused_data
        lines = data.splitlines()
        if data and not data.endswith(b"\n"):
            assert not inflater.eof
            lines.pop()
        if not inflater.eof:
            truncated[path.name] = len(lines)
        for line in lines:
            row = json.loads(line)
            assert row["job"] not in rows
            rows[row["job"]] = row
            launch = "after cut" if path.name.startswith("controls_rest_") else "original"
            by_launch[launch][row["kind"]] += 1
    return rows, truncated, by_launch


def control_counts(nae, parity, forms):
    archive, truncated, by_launch = read_controls()
    renumber, knot_tests = control_schedule(forms)
    backgrounds = nae | parity
    renumber_fail = []
    secondary_renumber_fail = []
    for index in range(900):
        job, variant = renumber[index % 300], index // 300 + 1
        changed = archive[index]
        assert changed["kind"] == "renumber" and changed["key"] == job.archive_key()
        assert changed["j"] == variant and changed["seed"] == variant + 2
        original = backgrounds[job]
        for field in ("make", "wider"):
            changed[field] = tuple(tuple(sorted(map(tuple, entries))) for entries in changed[field])
        if any(changed[field] != original[field] for field in ("make", "rounds_read", "stop")):
            renumber_fail.append(index)
        if any(changed[field] != original[field] for field in ("wider", "sec_only", "knots")):
            secondary_renumber_fail.append(index)
    groups = defaultdict(Counter)
    absent = {}
    for index, job in enumerate(knot_tests, 900):
        prefix = 900 <= index < 1000 or 1100 <= index < 1150
        stats = groups[f"{job.knot_law} {'in' if prefix else 'outside'} retained half"]
        if index not in archive:
            absent[str(index)] = job.archive_key()
            stats["not_run"] += 1
            continue
        test = archive[index]
        baseline = backgrounds[job]
        assert test["key"] == job.archive_key() and test["kind"] == "knot test"
        assert test["knots"] == baseline["knots"] and test["rounds_read"] == baseline["rounds_read"]
        assert test["n_fail"] == len(test["fails"]) and test["n_disagree"] == len(test["disagree"])
        stats["completed"] += 1
        for field in ("verdicts", "n_fail", "n_disagree", "n_untested", "birth_vs_direct"):
            stats[field] += test[field]
    assert all(0 <= index < 1200 for index in archive)
    return {"renumber_jobs_compared": 900, "renumber_fail": renumber_fail,
            "secondary_renumber_fail": secondary_renumber_fail,
            "knot_test_groups": groups, "knot_test_jobs_not_run": absent,
            "records_by_launch": by_launch,
            "truncated_control_shards_and_recovered_rows": truncated}


def frozen_digests():
    contract = load_json(ROOT / "experiments" / TICKET / EXPERIMENT / "contract.json")
    paths = {contract[name]: contract[f"{name}_sha256"] for name in
             ("claim", "preregistration", "definitions", "growth_engine",
              "growth_definitions", "second_growth_engine")}
    paths.update(contract["data_files"])
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
            for name, expected in paths.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    first, forms = seed_maps()
    chains = chain_pairs(forms["chains"])
    runs = {runset: load_runs(runset, forms, args.smoke) for runset in RUN_FAMILIES}
    studies = {key: prepared_studies(rows, first, forms) for key, rows in runs.items()}
    if args.smoke:
        replication_tables(studies["R1"], forms, chains)
        print(json.dumps({"smoke_run_counts": {key: len(value) for key, value in runs.items()}}))
        return
    result = compare_replication(studies["R1"], forms, chains)
    result["run_counts"] = {key: len(value) for key, value in runs.items()}
    result["PR4"] = start_membership(runs["R1"], runs["R2"])
    result["fresh_sanity_and_parity"] = fresh_checks(
        runs["R2"], runs["R4"], studies["R2"], studies["R4"], studies["R3"], chains,
    )
    result["G"] = gate_counts(first, forms)
    result["controls"] = control_counts(runs["R2"], runs["R4"], forms)
    result["frozen_digests_match"] = frozen_digests()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
