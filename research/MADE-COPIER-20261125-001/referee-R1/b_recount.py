"""Recount ticket B from the stored job records and frozen starts."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import permutations, product
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = (
    ROOT / "artifacts" / "MADE-COPIER-20261125-001B"
    / "MADE-COPIER-20261125-001B-E001_two_from_both"
)
STARTS = ROOT / "research" / "MADE-COPIER-20261125-001B" / "starts_b.json"


def job_records(name, damage):
    """Recover complete records even when a stopped job left a broken gzip tail."""
    path = ARTIFACTS / (name + ".jsonl.gz")
    decompressor = zlib.decompressobj(31)
    pending = b""
    with path.open("rb") as handle:
        while block := handle.read(65536):
            pending += decompressor.decompress(block)
            lines = pending.split(b"\n")
            pending = lines.pop()
            for line in lines:
                yield json.loads(line)
    pending += decompressor.flush()
    if not decompressor.eof:
        damage[name] = {"gzip member incomplete": True, "tail bytes": len(pending)}
        if pending:
            try:
                last_record = json.loads(pending)
            except json.JSONDecodeError:
                pass
            else:
                yield last_record
    elif pending:
        yield json.loads(pending)


def signature(form):
    """Exact canonical form for a small set of roster members."""
    colours = [tuple(hk) for hk in form["hk"]]
    if form["marks"] is not None:
        colours = [(*hk, mark) for hk, mark in zip(colours, form["marks"])]
    if len(form["maxsets"]) == 1 and len(form["maxsets"][0]) == len(colours):
        return tuple(sorted(colours)), (tuple(range(len(colours))),)
    colour_classes = defaultdict(list)
    for member, colour in enumerate(colours):
        colour_classes[colour].append(member)
    orders = [list(permutations(colour_classes[c])) for c in sorted(colour_classes)]
    best = None
    for ordering in product(*orders):
        rename = {member: new for new, member in enumerate(sum(ordering, ()))}
        sets = tuple(sorted(tuple(sorted(rename[m] for m in s)) for s in form["maxsets"]))
        if best is None or sets < best:
            best = sets
    return tuple(sorted(colours)), best


def pairs_in_round(job, run, target):
    exact_forms = job.setdefault("_small form cache", {})
    target_form = job["forms"][target]
    n_members = len(target_form["hk"])
    assert n_members <= 6
    if target not in exact_forms:
        target_signature = signature(target_form)
        exact_forms[target] = {
            i for i, form in enumerate(job["forms"])
            if len(form["hk"]) == n_members
            and sorted(form["hk"]) == sorted(target_form["hk"])
            and signature(form) == target_signature
        }
    candidates = exact_forms[target]
    return [sum(n for code, n in row if code in candidates) for row in run["both forms"]]


def control_counts(alone, target):
    return [row.get(str(target), 0) for row in alone["counts"]]


def starts_row(job, run, target, second_alone):
    rows = run["per_round"]
    joint = pairs_in_round(job, run, target)
    assert len(joint) == len(rows)
    assert joint == [r["Y form from both"] for r in rows]
    a = run["B_X"]["Y form"]
    b = second_alone
    d = control_counts(job["alone"]["X alone|" + run["X kind"]], target)
    horizon = min(len(rows), len(a), len(b), len(d))
    assert run["T"] == horizon and [r["t"] for r in rows] == list(range(1, len(rows) + 1))
    return rows, joint, (a, b, d), horizon


def tally_pair(result, job, key, rows, joint, controls, horizon, argument):
    for bound in (6, 8, 10):
        counts = result.setdefault(str(bound), Counter())
        end = min(horizon, bound)
        rows_read = rows[:end]
        both = [r for r in rows_read if joint[r["t"] - 1] >= 2]
        ended = [r for r in both if r["Y only ended"]]
        blocked = [max(control[:end], default=0) >= 2 for control in controls]
        b_only = bool(ended) and blocked[1] and (
            not blocked[0] or controls[0][:end] == controls[1][:end]
        )
        counts["runs"] += 1
        counts["rounds read"] += end
        counts["runs with fewer than bound rounds"] += int(end < bound)
        counts["two after common horizon"] += int(max(joint[end:bound], default=0) >= 2)
        counts["argument exclusions"] += int(argument)
        counts["all paired conditions pass"] += int(not any(blocked))
        counts["all paired conditions pass, without argument exclusions"] += int(
            not argument and not any(blocked)
        )
        counts["matched two and Y-only ended"] += int(bool(ended))
        counts["CB-1 before any renaming"] += int(bool(ended) and not any(blocked))
        if not both:
            continue
        first_round = both[0]["t"]
        counts["two from both"] += 1
        counts["joint count at first hit exactly two"] += int(joint[first_round - 1] == 2)
        counts["(a) fails among hits"] += int(blocked[0])
        counts["(b) fails among hits"] += int(blocked[1])
        counts["(d) fails among hits"] += int(blocked[2])
        counts["(b) alone under DB 4.4"] += int(b_only)
        counts["(b) alone under DB 4.4 with (d) also fails"] += int(b_only and blocked[2])
        counts["Y alone has two at first joint hit"] += int(controls[1][first_round - 1] >= 2)
        counts["Y alone matches joint count at first joint hit"] += int(
            controls[1][first_round - 1] == joint[first_round - 1]
        )
        if ended:
            case_round = ended[0]["t"]
            counts["Y alone has two at first joint hit with Y-only ended"] += int(
                controls[1][case_round - 1] >= 2
            )
            counts["all three controls below two through the first joint hit with Y-only ended"] += int(
                all(max(control[:case_round], default=0) < 2 for control in controls)
            )
        counts["Y alone and X barred have identical arrays among hits"] += int(
            controls[0][:end] == controls[1][:end]
        )
        counts["X-only ended at first joint hit"] += int(both[0]["X only ended"])
        details = job["starts"].get(key, {}).get("details", {}).get(str(first_round), {})
        for field in (
            "X returns (a part of X's form, every member from X only)",
            "a part of X's form descended from both",
        ):
            counts[field] += int(details.get(field, False))


def arm_one(names, damage, limit):
    tallies = {}
    parts = Counter()
    causal_examples = []
    mixed = Counter()
    same_ab = Counter()
    undecided_case = Counter()
    predictions = defaultdict(Counter)
    renumbered = defaultdict(set)
    knot_tests = Counter()
    main_knot_tests = Counter()
    registered_controls = {}
    for name in names:
        for i, job in enumerate(job_records(name, damage)):
            family = "CAP-3" if job["law"].startswith("CAP-3") else "COPY-LAW"
            groups = defaultdict(dict)
            for run in job["alone"].values():
                add_knot_tests(knot_tests, run["knot_tests"])
                if name == "b1":
                    add_knot_tests(main_knot_tests, run["knot_tests"])
            if name == "b1" and family == "COPY-LAW":
                for kind in ("one-2", "two-22"):
                    target = job["kind_forms"][kind]
                    registered_controls[f"{job['law']} | {kind}"] = control_counts(
                        job["alone"]["Y alone|" + kind], target
                    )
            for key, run in job["starts"].items():
                x, y, way = (run["X kind"], run["Y kind"], run["way"])
                control = "same kind" if x == y else "other kind"
                target = job["kind_forms"][y]
                alone = control_counts(job["alone"]["Y alone|" + y], target)
                rows, joint, controls, horizon = starts_row(job, run, target, alone)
                for tests in run["knot_tests"].values():
                    add_knot_tests(knot_tests, tests)
                    if name == "b1":
                        add_knot_tests(main_knot_tests, tests)
                argument = family == "COPY-LAW" and y not in ("one-2", "two-22")
                tally_pair(
                    tallies.setdefault(f"{name} {family} {control}", {}),
                    job, key, rows, joint, controls, horizon, argument,
                )
                count = max(joint[:horizon], default=0)
                if count >= 2:
                    parts[f"{name} {family} {control} {y}"] += 1
                    t = joint.index(next(n for n in joint if n >= 2))
                    if name == "b1" and x != y and controls[1][t] < 2:
                        causal_examples.append({
                            "law": job["law"], "start": key, "first both round": t + 1,
                            "both": joint[:horizon], "Y alone": alone[:horizon],
                            "Y only ended at first both round": rows[t]["Y only ended"],
                        })
                if name != "b1":
                    continue
                assert run["first_two"] == next(
                    (r["t"] for r in rows[:horizon] if joint[r["t"] - 1] >= 2), None
                )
                assert run["case_round"] == next(
                    (r["t"] for r in rows[:horizon]
                     if joint[r["t"] - 1] >= 2 and r["Y only ended"]), None
                )
                if controls[0][:horizon] != alone[:horizon]:
                    same_ab[f"{way} {y}"] += 1
                if family == "CAP-3":
                    mixed[f'{job["law"].split("/")[1]} | {control}'] += sum(
                        r["Y form mixed"] >= 1 for r in rows[:min(horizon, 6)]
                    )
                if family == "COPY-LAW" and y == "one-2" and "RETIRE" in job["law"]:
                    undecided_case[f"{control} runs"] += 1
                    undecided_case[f"{control} with one"] += int(count == 1)
                    undecided_case[f"{control} with two"] += int(count >= 2)
                groups[x, way][y] = run["both forms"]
            for group in groups.values():
                by_form = defaultdict(set)
                predictions[family]["X and meeting groups"] += 1
                for y, rounds in group.items():
                    for row in rounds:
                        for form, n in row:
                            by_form[form].add(y)
                            if n >= 2:
                                signature_text = json.dumps(job["forms"][form], sort_keys=True)
                                renumbered[family].add(signature_text)
                predictions[family]["groups with a form found with just one Y"] += int(
                    any(len(ys) == 1 for ys in by_form.values())
                )
            for item in job["perlaw"]:
                form = item["form"]
                alone = item["Y alone"]["own form"]
                add_knot_tests(knot_tests, item["Y alone"]["knot_tests"])
                for key, run in item["starts"].items():
                    rows, joint, controls, horizon = starts_row(job, run, form, alone)
                    for tests in run["knot_tests"].values():
                        add_knot_tests(knot_tests, tests)
                    tally_pair(
                        tallies.setdefault(f"per-law {family}", {}), job, key,
                        rows, joint, controls, horizon, False,
                    )
            if limit and i + 1 == limit:
                break
    return {
        "counts by arm and comparison scope": tallies,
        "two from both by file, law family, control, and Y form": parts,
        "examples where Y alone has fewer than two at the first joint hit": causal_examples,
        "CAP-3 mixed form run-rounds through round 6": mixed,
        "(a) and (b) differ by meeting and Y form": same_ab,
        "lone member with two under retiring": undecided_case,
        "stored knot tests, full set": knot_tests,
        "stored knot tests, main set": main_knot_tests,
        "PB16 alone controls": registered_controls,
        "PB13": {
            family: {
                **counts,
                "stored forms with two from both": [json.loads(x) for x in sorted(renumbered[family])],
            } for family, counts in predictions.items()
        },
    }


def arm_two(names, damage, starts, limit):
    cuts = []
    counts = defaultdict(Counter)
    all_jobs = set()
    file_jobs = defaultdict(Counter)
    form_limits = Counter()
    knot_tests = Counter()
    main_knot_tests = Counter()
    single_hits = []
    for name in names:
        for i, job in enumerate(job_records(name, damage)):
            if "error" in job:
                file_jobs[name]["error records"] += 1
                continue
            file_jobs[name]["completed records"] += 1
            assert job["law"] not in all_jobs
            all_jobs.add(job["law"])
            runs = job["starts"]
            n_read = len(runs)
            assert set(runs) == set(starts[:n_read])
            assert job.get("starts read", n_read) == n_read
            assert job.get("starts not run", 0) == len(starts) - n_read
            if n_read < len(starts):
                assert job["first start not run"] == starts[n_read]
                cuts.append({
                    "law": job["law"], "file": name, "read": n_read,
                    "not run": len(starts) - n_read, "first not run": starts[n_read],
                })
            family = job["job"]["base"].split("(")[0]
            counts[family]["jobs"] += 1
            counts[family]["starts not run"] += len(starts) - n_read
            counts[family]["jobs cut"] += int(n_read < len(starts))
            counts[family]["starts of ticket A"] += len(job["designs"])
            counts[family]["starts of ticket B"] += n_read
            for key, run in (*job["designs"].items(), *runs.items()):
                if key in job["designs"]:
                    origin = "ticket A"
                    target = run["Y form"]
                    joint = pairs_in_round(job, run, target)
                    assert joint == [r["Y form from both"] for r in run["per_round"]]
                    comparison_horizon = run["T"] - run["s"]
                    assert 0 <= comparison_horizon <= len(joint)
                    add_knot_tests(knot_tests, run["knot_tests"])
                    add_knot_tests(main_knot_tests, run["knot_tests"])
                else:
                    origin = "ticket B"
                    target = job["kind_forms"][run["Y kind"]]
                    joint = pairs_in_round(job, run, target)
                    assert joint == [r["Y form from both"] for r in run["per_round"]]
                    comparison_horizon = run["T"]
                    assert 0 <= comparison_horizon <= len(joint)
                    add_knot_tests(main_knot_tests, run["knot_tests"]["A"])
                    for tests in run["knot_tests"].values():
                        add_knot_tests(knot_tests, tests)
                counts[family]["after last comparison round"] += len(joint) - comparison_horizon
                if run["guard"] is not None:
                    counts[family][f"{origin} runs stopped at a guard"] += 1
                if run["stop"] is not None:
                    counts[family][f'{origin} stop: {run["stop"]}'] += 1
                max_joint = max(joint, default=0)
                counts[family]["max parts from both"] = max(
                    counts[family]["max parts from both"], max_joint
                )
                counts[family]["runs with one or more"] += int(max_joint >= 1)
                counts[family]["runs with two or more"] += int(max_joint >= 2)
                if max_joint:
                    single_hits.append({
                        "law": job["law"], "file": name, "origin": origin, "start": key,
                        "same kind": run.get("X kind") == run.get("Y kind") if origin == "ticket B" else None,
                        "rounds and counts": [[r["t"], n] for r, n in zip(run["per_round"], joint) if n],
                    })
            if name == "b3_cut2":
                form_limits["large parts classed by hash"] += job[
                    "parts classed by invariants and hash alone (deviations 33)"
                ]
                form_limits["exact form tests undecided"] += job[
                    "form tests undecided (deviations 33)"
                ]
                for size, n in job["undecided tests by members of the part"].items():
                    form_limits[f"undecided tests with {size} members"] += n
            if limit and i + 1 == limit:
                break
    return {
        "result by law family": counts,
        "cut jobs": cuts,
        "file job counts": file_jobs,
        "form comparison limits": form_limits,
        "stored knot tests, full set": knot_tests,
        "stored knot tests, main set": main_knot_tests,
        "runs with a jointly descended part of Y's form": single_hits,
    }


def add_knot_tests(total, tests):
    for field in ("verdicts", "n_fails", "n_untested", "n_disagree", "birth_vs_direct"):
        total[field] += tests[field]
    for kind, n in tests.get("fail_kinds", {}).items():
        total["fails for " + kind] += n


def recount_ticket_a():
    path, = (ROOT / "artifacts" / "MADE-COPIER-20261125-001A").glob("*/run2.jsonl.gz")
    counts = {"all designs": Counter(), "without made-2-exchanged": Counter()}
    with gzip.open(path, "rt") as source:
        for line in source:
            job = json.loads(line)
            for scope, result in counts.items():
                result["jobs"] += 1
                for design, run in job["designs"].items():
                    if scope == "without made-2-exchanged" and design == "made-2-exchanged":
                        continue
                    result["design runs"] += 1
                    for row in run["per_round"]:
                        for descents, count in row["form"]["by_descent"].items():
                            if count:
                                result[f"run-rounds with {descents}"] += 1
                                result[f"parts with {descents}"] += count
    return counts


def structural_checks(damage):
    renamings = defaultdict(Counter)
    extensions = {"knot order reversed"}
    for job in job_records("b4", damage):
        family = job["job"]["take"] or "no taking rule"
        for row in job["rows"]:
            renamings[family][row["verdict"]] += 1
            if row["renaming"] not in extensions and not row["renaming"].startswith("two usable"):
                renamings[family]["registered replication subset: " + row["verdict"]] += 1
    counts = Counter()
    for job in job_records("b5", damage):
        for stats in job["PB3"].values():
            for field in ("steps", "distinct", "repeats", "steps from a roster with no member",
                          "closing steps", "closing steps leaving a member", "n_conflicts"):
                counts["PB3 " + field] += stats.get(field, 0)
        if job["PB2"] is not None:
            counts["PB2 pairs"] += job["PB2"]["pairs"]
            counts["PB2 same"] += job["PB2"]["identical"]
        if job["PB5"] is not None:
            counts.update(job["PB5"])
        if job["PB8"] is not None and job["job"]["release"] == "RELEASE":
            counts["PB8 pairs"] += job["PB8"]["pairs"]
            counts["PB8 same up to first closing"] += job["PB8"][
                "identical up to the first closing"
            ]
            counts["PB8 closing pairs"] += len(job["PB8"]["closing_runs"])
    return {"stored renaming checks": renamings, "stored structural checks": counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--one-job-per-file", action="store_true")
    args = parser.parse_args()
    limit = 1 if args.one_job_per_file else None
    start_data = json.loads(STARTS.read_text())
    starts = [key for key in start_data["starts"] if not key.endswith("-other")]
    assert len(starts) == 256
    damage = {}
    result = {
        "arm one": arm_one(("b1", "b2_hold", "b2_other"), damage, limit),
        "arm two": arm_two(("b3", "b3_small", "b3_cut", "b3_cut2"), damage, starts, limit),
        "damaged raw files": damage,
    }
    if not limit:
        result.update(structural_checks(damage))
        result["PB17 ticket A run 2 raw record"] = recount_ticket_a()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
