#!/usr/bin/env python3
"""Check v2 using the two existing smoke runs and explicit smoke-derived controls.

No census, solver, full-run input, or network is used. Temporary fault-injection
files live beside this script and are removed before the receipt is written.
"""

from collections import Counter, defaultdict
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
import random
import tempfile
import time

import summarize_v2 as summary


ROOT = Path(__file__).resolve().parent
CHECKS = []


def check(name, condition, **evidence):
    if not condition:
        raise AssertionError(name)
    CHECKS.append({"name": name, "status": "passed", **evidence})


def read_rows(directory):
    return [json.loads(line) for path in sorted((directory / "keys").glob("worker-*.jsonl"))
            for line in path.read_text().splitlines() if line.strip()]


def reference_units(draws, keys, population, split_class):
    groups = defaultdict(list)
    for draw in draws:
        if draw["population"] != population or draw.get("rejected") is not None or draw.get("key_id") not in keys:
            continue
        record = keys[draw["key_id"]]
        identity = (record["pattern_hash"], record["rel_class"]) if split_class else (record["pattern_hash"],)
        groups[identity].append(record)
    expected = {}
    for identity, records in groups.items():
        members = {row["key_id"]: row for row in records}
        first = min(members.values(), key=lambda row: row["key"])
        expected[identity] = {
            "first_key_id": first["key_id"], "first_key": first["key"],
            "cluster": json.dumps(first["automaton_class"], sort_keys=True, separators=(",", ":")),
            "letter_class": first["letter_class"], "letter_degree": first["letter_degree"],
            "s": min(row["key"][0] for row in members.values()),
            "settled": any(row["flags"]["single_placement"] or row["flags"]["first_letter_settled"]
                           for row in members.values()),
            "description_count": len(members), "draw_frequency": len(records), "fate": first["fate"]}
    return expected


def reference_bootstrap(left, right, unit):
    """Independently use resampling multiplicities against fixed arm totals."""
    import numpy as np
    generator = np.random.default_rng(random.Random(summary.BOOTSTRAP_SEED).getrandbits(64))
    arms = []
    for rows in (left, right):
        if unit == "draw":
            groups = [[row] for row in rows]
        else:
            clusters = defaultdict(list)
            for row in rows:
                clusters[row["cluster"]].append(row)
            groups = [clusters[label] for label in sorted(clusters)]
        arms.append(np.array([[sum(row["fate"] in ("F1", "F2") for row in group),
                               sum(row["fate"] == "FU" for row in group), len(group)]
                              for group in groups], dtype=np.int64))
    result = {"FU_alive": [], "FU_dead": []}
    for start in range(0, 2000, 64):
        batch = min(64, 2000 - start)
        totals = []
        for arm in arms:
            selected = generator.integers(0, len(arm), size=(batch, len(arm)))
            totals.append([np.bincount(indices, minlength=len(arm)) @ arm for indices in selected])
        for left_total, right_total in zip(*totals):
            result["FU_alive"].append(float(left_total[0] / left_total[2] - right_total[0] / right_total[2]))
            result["FU_dead"].append(float((left_total[0] + left_total[1]) / left_total[2]
                                           - (right_total[0] + right_total[1]) / right_total[2]))
    return {key: sorted(values) for key, values in result.items()}


def revised(row, verdicts):
    """A fault-injection copy, never a new observed census result."""
    row = deepcopy(row)
    row["verdict_n"] = list(verdicts)
    active = [v for v, count in zip(verdicts, row["knots_n"]) if count]
    row["fate"] = ("F0" if not active else "F1" if active[0] == 0 else
                   "F2" if active[0] == 1 and 0 in active[1:] else
                   "F3" if all(v == 1 for v in active) else "FU")
    row["first_death"] = next((i + 1 for i, v in enumerate(verdicts) if v == 0), None)
    row["return"] = any(v == 0 and 1 in verdicts[i + 1:] for i, v in enumerate(verdicts))
    return row


def main():
    started = time.monotonic()
    protected = {"addr.py": "39b28de4c395a7afe38a5a47887842ca895ffed33aa8de25531ef8c868db8288",
                 "run_census.py": "74e4806a1fce5f931f1210459a0eb25d4081b12338d103e4a44225049c3f978d",
                 "summarize.py": "33c568ab9fb4abc81b58d4e04b3988c5c6767ecefbe97287c9678f41bf0fc212",
                 "validation.json": "e4dfe5395bfc9e33fb433d848e7edc94cdfb168d1e904abe62e69834592b6b62",
                 "smoke_uninterrupted/summary.json": "9fb10332a11a72c1891158bce231d58f219e79de0de4d4662e8a1e95fe79c8fb",
                 "smoke_uninterrupted/summary.md": "e82dadf698f6e724209bad91d9d392fa960d60499a57dbb61769ae43c95d027a"}
    for directory in ("smoke_uninterrupted", "smoke_resumed"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and not path.name.startswith("summary_v2"):
                protected.setdefault(str(path.relative_to(ROOT)), hashlib.sha256(path.read_bytes()).hexdigest())
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in protected}
    check("protected original inputs match baseline", before == protected)
    report_prefix = (ROOT / "REPORT.md").read_bytes().split(b"\n## Addendum\n", 1)[0]
    check("original report is an unchanged prefix", hashlib.sha256(report_prefix).hexdigest()
          == "59efc90cb5a61216caee25038049ec4cf1699f46adea528716857331316299f3")

    directory = ROOT / "smoke_uninterrupted"
    raw = read_rows(directory)
    keys = {row["key_id"]: row for row in raw}
    with gzip.open(directory / "draws.jsonl.gz", "rt") as stream:
        draws = [json.loads(line) for line in stream if line.strip()]
    check("smoke has the disclosed records and fates", len(raw) == 300
          and Counter(row["fate"] for row in raw) == {"F0": 123, "F2": 37, "F3": 140})

    reports = []
    for name in ("smoke_uninterrupted", "smoke_resumed"):
        with redirect_stdout(io.StringIO()):
            code = summary.main([str(ROOT / name), "--output-prefix", "summary_v2"])
        result = json.loads((ROOT / name / "summary_v2.json").read_text())
        check(name + " CLI produces both summaries", code == 0 and (ROOT / name / "summary_v2.md").is_file())
        markdown = (ROOT / name / "summary_v2.md").read_text()
        check(name + " Markdown points to its versioned JSON", "summary_v2.json" in markdown
              and "in summary.json" not in markdown)
        reports.append(result)
    result = reports[0]
    check("resumed and uninterrupted v2 summaries are identical", reports[0] == reports[1])
    check("smoke remains incomplete with zero unresolved ambiguities", not result["registered_run_ready_for_interpretation"]
          and not result["coverage"]["registered_coverage_complete"] and result["ambiguities"] == [])
    check("raw and merged smoke verdicts coincide", result["verdict_merge"]["patterns"] == 154
          and result["verdict_merge"]["resolutions"] == [] and result["verdict_merge"]["changed_description_fates"] == [])

    for population in ("E", "W"):
        for split_class, field in ((False, "unsplit_units"), (True, "class_units")):
            expected = reference_units(draws, keys, population, split_class)
            actual = {tuple(row["unit_id"]): row for row in result["units"][population][field]}
            check(f"{population} {field} match independent grouping", set(actual) == set(expected)
                  and all(all(actual[key][field] == value for field, value in row.items())
                          for key, row in expected.items()), units=len(actual))
        expected = reference_units(draws, keys, population, False)
        for minimum in (2, 3):
            selected = [row for row in expected.values() if row["s"] >= minimum]
            condition = result["fate_shares"][population][f"given_s_ge_{minimum}"]
            counts = Counter(row["fate"] for row in selected)
            weighted = Counter()
            for row in selected:
                weighted[row["fate"]] += row["draw_frequency"]
            check(f"{population} s >= {minimum} uses unit minimum and accepted frequency",
                  condition["distinct_patterns"]["denominator"] == len(selected)
                  and condition["draw_frequencies"]["denominator"] == sum(weighted.values())
                  and all(condition["distinct_patterns"]["counts"][fate] == counts[fate]
                          and condition["draw_frequencies"]["counts"][fate] == weighted[fate]
                          for fate in summary.FATES))
        matrices = result["logistic"][population]["assignments"]
        check(population + " writes two non-null logistic matrices", set(matrices) == {"FU_alive", "FU_dead"}
              and all(row["death"] in (0, 1) for case in matrices.values() for row in case["design_matrix"])
              and all(case["fit"]["status"] == "skipped_statsmodels_unavailable" for case in matrices.values()))

    items, prepared, coverage = summary.load_records(directory)
    merged, _ = summary.merge_pattern_verdicts(prepared)
    records = list(merged.values())
    shuffled = records[:]
    random.Random(20261115).shuffle(shuffled)
    check("labels are independent of shard and input order",
          summary.group_patterns(records, True) == summary.group_patterns(shuffled, True))
    grouped = defaultdict(list)
    for row in records:
        grouped[row["pattern_hash"]].append(row)
    pair = next(members[:2] for members in grouped.values() if len(members) >= 2 and members[0]["fate"] == "F3")
    a, b = deepcopy(pair)
    level = next(i for i, count in enumerate(a["knots_n"]) if count)
    verdicts = a["verdict_n"][:]
    verdicts[level] = None
    unknown = revised(a, verdicts)
    healed, receipt = summary.merge_pattern_verdicts({a["key_id"]: unknown, b["key_id"]: b})
    check("decided pattern verdict heals null and recomputes fate", healed[a["key_id"]]["verdict_n"][level] == 1
          and healed[a["key_id"]]["fate"] == "F3" and receipt["resolved_description_levels"] == 1
          and unknown["verdict_n"][level] is None)

    verdicts = b["verdict_n"][:]
    bad_levels = [i for i, count in enumerate(b["knots_n"]) if count][:2]
    for i in bad_levels:
        verdicts[i] = 0
    bad = revised(b, verdicts)
    try:
        summary.merge_pattern_verdicts({a["key_id"]: a, b["key_id"]: bad})
        raise AssertionError("conflicting decided verdict accepted")
    except summary.PatternVerdictConflict as error:
        check("contradictions list all affected pattern levels and key IDs", len(error.conflicts) == len(bad_levels)
              and all(a["key_id"] in conflict["alive_key_ids"] and b["key_id"] in conflict["dead_key_ids"]
                      for conflict in error.conflicts))
    for scenario in ("distinct", "duplicate", "same-key-other-id", "invalid-derived-metadata"):
        incoming = revised(a if scenario in ("duplicate", "same-key-other-id") else b, verdicts)
        with tempfile.TemporaryDirectory(prefix=".summary_v2_controls_", dir=ROOT) as scratch:
            scratch = Path(scratch)
            (scratch / "keys").mkdir()
            # Strip summary-only fields: these remain two smoke-derived raw rows.
            outgoing = [keys[a["key_id"]], {**keys[incoming["key_id"]],
                        **{field: incoming[field] for field in ("verdict_n", "fate", "first_death", "return")}}]
            if scenario == "same-key-other-id":
                outgoing[1]["key_id"] += "-replay-control"
            if scenario == "invalid-derived-metadata":
                outgoing[1]["fate"] = "FU"  # fails row validation, still exposes a contradiction
            (scratch / "keys" / "worker-0.jsonl").write_text("".join(json.dumps(row) + "\n" for row in outgoing))
            stderr = io.StringIO()
            with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                code = summary.main([str(scratch), "--output-prefix", "must_not_exist"])
            diagnostic = json.loads(stderr.getvalue())
            check(scenario + " conflict stops CLI without summaries",
                  code == 2 and diagnostic["status"] == "stopped_contradictory_decided_verdicts"
                  and len(diagnostic["conflicts"]) == len(bad_levels)
                  and not (scratch / "must_not_exist.json").exists() and not (scratch / "must_not_exist.md").exists(),
                  conflicts=diagnostic["conflicts"])

    with tempfile.TemporaryDirectory(prefix=".summary_v2_controls_", dir=ROOT) as scratch:
        scratch = Path(scratch)
        (scratch / "keys").mkdir()
        original = keys[a["key_id"]]
        altered = {**deepcopy(original), "automaton_class": "replay-metadata-control",
                   "rel_class": "bounded" if original["rel_class"] != "bounded" else "exponential"}
        path = scratch / "keys" / "worker-0.jsonl"
        path.write_text(json.dumps(original) + "\n" + json.dumps(altered) + "\n")
        _, replay_keys, replay_coverage = summary.load_records(scratch)
        check("a repeated key cannot silently replace scientific metadata",
              any(error.get("error") == "conflicting repeated key records" for error in replay_coverage["errors"])
              and replay_keys[a["key_id"]]["automaton_class"] == original["automaton_class"]
              and replay_keys[a["key_id"]]["rel_class"] == original["rel_class"])

        unresolved = revised(original, unknown["verdict_n"])
        path.write_text(json.dumps(unresolved) + "\n" + json.dumps(original) + "\n")
        _, replay_keys, replay_coverage = summary.load_records(scratch)
        check("a compatible replay resolves a previously undecided key",
              replay_keys[a["key_id"]]["verdict_n"] == original["verdict_n"]
              and replay_keys[a["key_id"]]["fate"] == original["fate"]
              and not any(error.get("error") == "conflicting repeated key records"
                          for error in replay_coverage["errors"]))

    # A deliberately unresolved smoke record exercises both logistic responses.
    candidate = next(row for row in records if row["fate"] == "F3" and not row["settled"])
    verdicts = candidate["verdict_n"][:]
    verdicts[next(i for i, count in enumerate(candidate["knots_n"]) if count)] = None
    fu = revised(candidate, verdicts)
    control_items = [{"population": "W", "record": fu}] * 37
    logistic = summary.logistic_matrix(control_items, "W")
    left = logistic["assignments"]["FU_alive"]["design_matrix"][0]
    right = logistic["assignments"]["FU_dead"]["design_matrix"][0]
    check("FU matrices differ only in the unresolved response", left["death"] == 0 and right["death"] == 1
          and {k: v for k, v in left.items() if k != "death"} == {k: v for k, v in right.items() if k != "death"}
          and left["frequency_weight"] == 37)
    unit = summary.group_patterns([candidate] * 100, True)
    stats = summary.arm_stats(unit, weighted=True)
    check("100 repeated W draws do not become 30 decided units", stats["weight"] == 100
          and stats["decided"] == 1 and not summary.ordinary_eligible(stats))
    # Different descriptions of one pattern are merged before this stage; use
    # separate existing patterns for the weighted-share arithmetic control.
    dead = next(row for row in records if row["fate"] == "F2")
    weighted_units = summary.group_patterns([candidate] * 3 + [dead], True)
    stats = summary.arm_stats(weighted_units, weighted=True)
    check("W death share uses frequency rather than unit count", stats["units"] == 2 and stats["weight"] == 4
          and stats["death_share_FU_alive"] == 0.25)

    for population, unit_type in (("E", "automaton_class"), ("W", "draw")):
        units = summary.group_patterns((item["record"] for item in items if item["population"] == population), True)
        units = [unit for unit in units if unit["fate"] != "F0"]
        middle = len(units) // 2
        arms = [deepcopy(units[:middle]), deepcopy(units[middle:])]
        arms[0][0]["fate"] = "FU"  # response-treatment control, not observed evidence
        if unit_type == "draw":
            arms = [summary.expand_draws(arm) for arm in arms]
        actual = summary.bootstrap_deltas(*arms, random.Random(20261115), unit_type)
        expected = reference_bootstrap(*arms, unit_type)
        check(population + " bootstrap matches independent multiplicity calculation", actual == expected
              and all(len(values) == 2000 for values in actual.values()), resamples=2000, seed=20261115)

    check("P1 excludes and counts all F0 descriptions", result["predictions"]["P1"]["descriptions_checked"] == 88
          and result["predictions"]["P1"]["descriptions_excluded_F0"] == 123
          and result["predictions"]["P1"]["settled_descriptions_excluded_F0"] == 45
          and not result["predictions"]["P1"]["invalidates_run"])
    check("one smoke return is preserved", result["predictions"]["P2"]["returns"] == 1)
    after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in protected}
    check("all protected inputs and original summaries remain unchanged", before == after)
    receipt = {"status": "passed", "checks": CHECKS, "check_count": len(CHECKS),
               "elapsed_seconds": time.monotonic() - started,
               "inputs": ["smoke_uninterrupted", "smoke_resumed"],
               "controls": "in-memory mutations and temporary copies of smoke records only; no generated census data",
               "limitations": "smoke has no observed FU, no s=1 descriptions and no eligible matched cells; "
                              "FU and bootstrap response handling exercised with labelled controls, not registered evidence",
               "full_run_accessed": False, "protected_sha256": after,
               "summarizer_sha256": hashlib.sha256((ROOT / "summarize_v2.py").read_bytes()).hexdigest()}
    (ROOT / "summary_v2_validation.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: receipt[key] for key in ("status", "check_count", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
