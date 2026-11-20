"""Reconcile the canonical source frame with the three original study records."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import zlib

from sources_features import simple_class
from sources_run import ARTIFACTS, RETAINED, ROOT, archive, digest, independent_score, load_results, source_key
from sources_span import controls, qualify

EXPLOSIVE = ROOT / "artifacts/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/results.json"
MERGE = ROOT / "artifacts/MERGE-BURST-20261119-001B/MERGE-BURST-20261119-001B-E001_stages/results.json"
WALL = ROOT / "artifacts/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/results.json"
WALL_PROOF = ROOT / "proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/machine_check.json"
WALL_DOUBLE_COUNT = ROOT / "research/WALL-READ-20261119-001/posthoc/double_count.json"
EXP_REFEREE = ROOT / "research/EXPLOSIVE-20261119-001/referee-R1/referee_explosive.json"
MERGE_REFEREE = ROOT / "research/MERGE-BURST-20261119-001/referee-R1/referee_mb.json"
HUB = (ROOT / "artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/stages.json")
PARTNER = (ROOT / "artifacts/PARTNER-SEVEN-20261119-001/PARTNER-SEVEN-20261119-001-E001_seek/archive_screen.json")
FOLLOWUP_STREAMS = {
    "merge": "runs/merge-burst/results.jsonl",
    "wall_a": "runs/wall-read-a/results.jsonl",
    "wall_b": "runs/wall-read-b/results.jsonl",
}
EXCLUDED = {"start-08", "start-15"}


@dataclass(frozen=True)
class Sample:
    stratum: str
    draw: int
    datum: dict
    checked: dict

    @property
    def identifier(self):
        return f"{self.stratum}/{self.draw}"

    @property
    def population(self):
        tag = self.datum["tag"]
        return "ref" if tag.startswith("ref ") else tag

    @property
    def key(self):
        return source_key(self.datum["sizes"], self.datum["edges"])


def read(path):
    return json.loads(path.read_text())


def write(path, document, compressed=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(document, indent=None if compressed else 2, sort_keys=not compressed).encode() + b"\n"
    with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        pending = Path(stream.name)
        stream.write(gzip.compress(encoded, compresslevel=6, mtime=0) if compressed else encoded)
    pending.replace(path)


def historical_inputs(force_retained=False):
    cached = None
    results = {}
    for name, relative in FOLLOWUP_STREAMS.items():
        path = ROOT / relative
        if not force_retained and path.is_file():
            before = digest(path)
            raw = load_results(path)
            assert all(row["status"] == "ok" for row in raw.values()) and before == digest(path)
            results[name] = {"sha256": before, "tables": {case: row["result"] for case, row in raw.items()}}
        else:
            if cached is None:
                cached = json.loads(gzip.decompress(RETAINED.read_bytes()))["followups"]
            results[name] = cached[name]
    return results


def x1_population(row):
    return not any(row["b1"]) and row["measured"] != "undecided"


def x1_agrees(row):
    return row["reading"] == simple_class(row["measured"])


def population(samples):
    rows = [s.datum for s in samples]
    settled = [x for x in rows if x1_population(x)]
    cycle = [x for x in rows if any(x["b1"]) and x["measured"] != "undecided"]
    nonoverlap = [x for x in settled if not (x["overlap_point"] or x["overlap_block"])]
    both_at_seven = [x for x in rows if x["max_places"] == 7 and x["overlap_point"] and x["overlap_block"]]
    jumps = [x for x in rows if x["measured"] == "explosive"]
    within_size = Counter(x["n"] for x in rows)
    return {
        "starts": len(rows), "canonical_sources": sum(s.checked["canonical"] for s in samples),
        "forced_distinction_sources": sum(bool(s.checked["forced_distinctions"]) for s in samples),
        "measured": dict(Counter(x["measured"] for x in rows)),
        "X1_decided_zero_rank": {"agree": sum(map(x1_agrees, settled)), "total": len(settled)},
        "X1_failure_classes": dict(Counter(simple_class(x["measured"]) for x in settled if not x1_agrees(x))),
        "X1_nonoverlap_decided_zero_rank": {"agree": sum(map(x1_agrees, nonoverlap)), "total": len(nonoverlap)},
        "X1b_decided_positive_rank": {"failure": sum(simple_class(x["measured"]).startswith("dimension") or
                                                   x["measured"] == "closes" for x in cycle), "total": len(cycle)},
        "both_overlaps_at_seven_places": {"total": len(both_at_seven),
                                        "classes": dict(Counter(simple_class(x["measured"]) for x in both_at_seven))},
        "classified_explosive": len(jumps), "jump_outcomes": dict(Counter(x["outcome"] for x in jumps)),
        "jump_feature_rows": dict(Counter(
            f"b1={int(any(x['b1']))} b2={int(any(x['b2']))} "
            f"point={int(x['overlap_point'])} block={int(x['overlap_block'])} arity={x['max_places']}"
            for x in jumps
        )),
        "initial_size_counts": dict(within_size), "jump_size_counts": dict(Counter(x["n"] for x in jumps)),
        "largest_group": max((max(x["groups"]) for x in rows), default=None),
    }


def verdicts(populations):
    x1 = [r["X1_decided_zero_rank"] for r in populations.values()]
    return {"X1": all(row["agree"] == row["total"] for row in x1),
            "X1b": all(row["X1b_decided_positive_rank"]["failure"] == 0 for row in populations.values()),
            "X2": all(populations[name]["classified_explosive"] == 0 for name in ("cap5", "cycle5")),
            "X3": populations["cap7"]["classified_explosive"] > 0}


def by_frame(samples):
    split = defaultdict(list)
    for sample in samples:
        split[sample.population].append(sample)
    return {p: population(rows) for p, rows in split.items()}


def followup_names(samples):
    jumping = [s for s in samples if s.population == "cap7" and s.datum["measured"] == "explosive"]
    jumping.sort(key=lambda sample: (sample.datum["n"], sum(sample.datum["sizes"]), sample.key))
    result = {f"start-{i:02d}": row for i, row in enumerate(jumping)}
    literal = read(HUB)["literal_starts"]
    prior_check = {row["tag"]: row for row in read(PARTNER)["explosive"]["starts"]}
    assert set(result) == set(literal) == set(prior_check)
    for case, sample in result.items():
        named, prior = literal[case], prior_check[case]
        assert sample.key == source_key(named["sizes"], named["edges"])
        assert sample.key == source_key(prior["sizes"], prior["links"])
        assert (prior["source_case"], prior["source_draw"], prior["canonical"]) == (
            sample.stratum, sample.draw, sample.checked["canonical"]
        )
        assert sample.datum["counts"] == named["counts_then"]
    assert {name for name, row in result.items() if not row.checked["canonical"]} == EXCLUDED
    return result


def exp_referee(samples):
    records = read(EXP_REFEREE)
    by_key = {(s.stratum, s.key): s for s in samples}
    readout, horizon = [], []
    for case, checked in records.items():
        if case[0] not in "EF":
            continue
        study = checked["study"]
        raw = by_key[study["case"], source_key(study["sizes"], study["edges"])]
        assert study["measured"] == raw.datum["measured"]
        summary = {"referee_case": case, "identifier": raw.identifier, "canonical": raw.checked["canonical"],
                   "class": raw.datum["measured"], "filled_reading": raw.datum["reading"],
                   "referee_class": checked["referee's class"], "rounds": len(checked["referee"]["counts"]) - 1,
                   "counts_agree_on_common_rounds": checked["counts agree with the study's on common rounds"]}
        readout.append(summary)
        if (raw.population == "cap7" and x1_population(raw.datum) and not x1_agrees(raw.datum)
                and raw.datum["reading"] == simple_class(summary["referee_class"])):
            horizon.append(summary)
    # The referee checked a separate CRC-selected set of decided nonjump rows.
    selected = [s for s in samples if s.datum["measured"] not in ("undecided", "explosive") and
                zlib.crc32(repr(s.datum["edges"]).encode()) % 8 == 0][:400]
    checked_rows = [rec for key, bucket in sorted(records.items()) if key.startswith("L-") for rec in bucket["rows"]]
    assert len(selected) == len(checked_rows)
    for source, grade in zip(selected, checked_rows, strict=True):
        assert source.datum["tag"] == grade["tag"] and source.datum["measured"] == grade["study"]
    stages = [r for k, r in records.items() if k.startswith("R-")]
    return {"extended_jump_rows": sorted(x["identifier"] for x in readout if x["referee_case"].startswith("E-")),
            "horizon_reconciliations": sorted(horizon, key=lambda row: row["referee_case"]),
            "independent_filled_reading_rows": sum(x["counts"]["starts"] for x in stages),
            "independent_filled_reading_differences": sum(len(x["differ"]) for x in stages),
            "class_controls_to_40": {"original": len(selected),
                                     "canonical_subset": sum(s.checked["canonical"] for s in selected),
                                     "class_retained": sum(row["study"] == row["referee at 40"] for row in checked_rows)}}


def merge_rollup(rows, ref):
    unresolved = [r for r in rows if r["verdict"] == "unresolved"]
    read = [r for r in rows if r["verdict"] != "unresolved"]
    tests = [r for r in rows if not r["control"]]
    nontest = [r for r in read if r["control"]]
    admissions = [r for r in tests if r["verdict"] != "unresolved"]
    tested_stability = [r for r in read if r["stability"] not in (
        None, "stall", "two blocks share two points", "cycle of three blocks", "one loose or none"
    )]
    cycle = [r["case"] for r in unresolved if any(reason == "cycle of three blocks"
                                                   for _, reason in ref[r["case"]]["verdicts"])]
    return {"starts": len(rows), "rounds_built_before_read_checks": sum(r["rounds_reached"] for r in rows),
            "closing_readings": [r["case"] for r in read if r["verdict"] == "closes"],
            "reached_unresolved": [r["case"] for r in unresolved],
            "unresolved_stop_counts": dict(Counter(r["end"] for r in unresolved)),
            "read_and_checked_rounds": {r["case"]: r["checked_rounds"] for r in read},
            "noncontrol_panel": len(tests), "noncontrol_readings": len(admissions),
            "controls": [r["case"] for r in nontest], "referee_early_cycle_cases": cycle,
            "referee_all_unresolved_last_stage_overlap": all(
                ref[r["case"]]["verdicts"][-1][1] == "two blocks share two points" for r in unresolved
            ),
            "stability_rows_in_class": len(tested_stability),
            "predictions": {"R1": all(r["check_equal"] for r in read),
                            "R2a": all(r["maximal_blocks"] == 1 for r in admissions),
                            "R2b": all(r["verdict"] == "closes" for r in admissions),
                            "R3": len(admissions) >= 5,
                            "R4": all(r["stability"] == r["verdict"] for r in tested_stability)}}


def wall_rollup(summary):
    unread = {case: result for case, result in summary.items() if case not in ("start-00", "start-04")}
    other = {case: result for case, result in unread.items() if case != "start-03"}
    stages = [check for result in summary.values() for check in result["checks"]]
    bounded = [case for case, result in other.items() if result["best_bound_next"] > result["last_count"]]
    merged = [case for case, result in unread.items() if result["one_block_rounds"]]
    return {"starts": len(summary), "positive_birth_ages": sum(len(r["counts"]) for r in summary.values()),
            "stage_records_including_age_zero": sum(len(r["stages"]) for r in summary.values()),
            "archive_stop_counts": dict(Counter(r["end"] for r in summary.values())),
            "B3": {"checks": len(stages), "agreed": sum(row["ok"] for row in stages)},
            "B5": {"outperformed_last_count": bounded, "of": len(other), "historical_threshold": 10},
            "B6": {"one_block_observed": merged, "of": len(unread)},
            "unread_above_60000": sorted(case for case, r in unread.items() if r["last_count"] > 60_000)}


def sum_lemmas(data, omitted=frozenset()):
    tally = Counter()
    for case, result in data.items():
        if case.startswith("lem-") and case not in omitted:
            assert not result["bad"]
            tally.update(result["tally"])
    return dict(tally)


def followup_audit(names, streams):
    accepted = set(names) - EXCLUDED
    merge_table, wall_table = read(MERGE), read(WALL)
    merge_rows, stages = merge_table["rows"], wall_table["follow"]
    ref_records = {f"start-{row['start']:02d}": row for row in read(MERGE_REFEREE)["per start"]}
    raw_m, raw_a, raw_b = (streams[name]["tables"] for name in ("merge", "wall_a", "wall_b"))
    assert set(raw_m) == set(stages) == set(names) == set(ref_records)
    by_name = {}
    for row in merge_rows:
        case = row["case"]
        raw = raw_m[case]
        original = raw["start"]
        follow = raw["follow"]
        assert names[case].key == source_key(original["sizes"], original["edges"])
        assert [r["t"] for r in follow["rounds"]] == list(range(1, row["rounds_reached"] + 1))
        assert row["end"] == follow["end"] and row["checked_rounds"] == len(follow.get("check") or [])
        forecast = follow.get("reading")
        if forecast is not None:
            assert row["check_equal"] == ((follow.get("check") or []) == forecast["predicted"][:row["checked_rounds"]])
            assert row["read_at"] == forecast["t"]
            assert (row["verdict"], row["maximal_blocks"]) == (forecast["reading"], forecast["maximal_blocks"])
        else:
            assert row["verdict"] == "unresolved"
        assert row["rounds_reached"] == ref_records[case]["study rounds"] == ref_records[case]["referee rounds"]

        record = raw_b[f"follow-{case[-2:]}"]
        rounds = {r["t"]: r for r in record["records"] if r.get("kind") == "round" and "count" in r}
        current = {r["t"]: r for r in record["records"] if r.get("kind") == "stage"}
        assert case == record["start"] and stages[case]["counts"] == [r["count"] for r in rounds.values()]
        assert record["end"] == stages[case]["end"]
        assert len(current) == len(stages[case]["stages"])
        assert stages[case]["one_block_rounds"] == [t for t, r in rounds.items() if r["one_block"]]
        known = []
        for t, state in current.items():
            if t + 1 in rounds and "k_any" in state:
                groups = rounds[t + 1]["groups"]
                k, w = state["bound_k"], state.get("bound_w")
                known.append({"t": t, "groups_next": groups, "bound_k": k, "bound_w": w,
                              "ok": k <= groups and (w is None or w <= groups)})
        assert known == stages[case]["checks"]
        verdict = {k: row[k] for k in ("end", "rounds_reached", "verdict", "read_at", "largest_group")}
        by_name[case] = {"MERGE": verdict, "WALL": {"positive_ages": len(rounds), "stages": len(current),
                                                   "B3_checks": len(known), "last_count": stages[case]["last_count"],
                                                   "end": record["end"]}}
    raw = wall_rollup(stages)
    assert raw["B3"]["checks"] == wall_table["B3"]["checks"]
    raw_lemmas = sum_lemmas(raw_a)
    machine = read(WALL_PROOF)
    assert raw_lemmas == machine["M3_M4"]["tally"]
    independent = Counter()
    for case, result in raw_b.items():
        if case.startswith(("eq-census", "eq-rand")):
            independent.update({case.split("-")[1] + " " + key: count for key, count in result["tally"].items()})
        if case.startswith("eq-read"):
            assert result["result"]["equal"]
            independent["read equal"] += 1
    assert independent == wall_table["B1"]["tally"]
    omitted_cases = {f"lem-expl-{case[-2:]}" for case in EXCLUDED}
    return {"per_followup_start": by_name,
            "MERGE_BURST": {"original": merge_rollup(merge_rows, ref_records),
                            "canonical": merge_rollup([r for r in merge_rows if r["case"] in accepted], ref_records)},
            "WALL_READ_B": {"original": raw, "canonical": wall_rollup(
                {case: stages[case] for case in sorted(accepted)}),
                            "independent_B1_comparators": wall_table["B1"],
                            "B2_original_frozen_incomplete": wall_table["B2"],
                            "B2_completed_double_count": read(WALL_DOUBLE_COUNT),
                            "B4_original_bound": wall_table["B4"]["bound"]},
            "WALL_READ_A": {"original_mixed_panel": raw_lemmas,
                            "two_archive_starts_deleted_from_mixed_panel": sum_lemmas(raw_a, omitted_cases),
                            "deleted_machine_check_rows": {case: raw_a[case]["tally"] for case in sorted(omitted_cases)},
                            "independent_M1_and_M2_held": [machine["M1"]["held"], machine["M2"]["held"]]}}


def audit(frames, grades, streams):
    samples = [Sample(case, i, row, grade) for case, group in frames.items()
               for i, (row, grade) in enumerate(zip(group["starts"], grades[case], strict=True))]
    assert len(samples) == 3200 and all(not s.checked["independent_field_disagreement"] for s in samples)
    assert all(s.checked["first_round_funded"] and s.checked["at_most_one_common_holder"]
               for s in samples if s.population != "ref")
    names = followup_names(samples)
    bad_names = {row.identifier for name, row in names.items() if name in EXCLUDED}
    original = by_frame(samples)
    dropped = by_frame([s for s in samples if s.identifier not in bad_names])
    canonical = by_frame([s for s in samples if s.checked["canonical"]])
    published = read(EXPLOSIVE)
    for p, data in original.items():
        old = published["populations"][p]
        assert (data["starts"], data["classified_explosive"], data["X1_decided_zero_rank"]["agree"]) == (
            old["starts"], old["explosive"], old["agree_b1_zero"]
        )
    scores = [verdicts(group) for group in (original, dropped, canonical)]
    assert all(scores[0] == v for v in scores) and all(scores[0][k] == published[k] for k in scores[0])
    sources = {}
    for case, s in names.items():
        gate = qualify(s.datum["sizes"], s.datum["edges"], detail=True)
        assert gate["canonical"] == s.checked["canonical"]
        sources[case] = {"identifier": s.identifier, "sizes": s.datum["sizes"], "meetings": s.datum["edges"],
                         "outcome": s.datum["outcome"], "round_junction_counts": s.datum["counts"],
                         "round_largest_groups": s.datum["groups"], "tri": s.datum["tri"], "b1": s.datum["b1"],
                         "b2": s.datum["b2"], "overlap_point": s.datum["overlap_point"],
                         "overlap_block": s.datum["overlap_block"], "max_places": s.datum["max_places"],
                         "filled_reading": s.datum["reading"], "gate": gate}
    cap7 = original["cap7"]["starts"]
    named = len(names) - len(EXCLUDED)
    sampling = {"original_historical": [original["cap7"]["classified_explosive"], cap7],
                "qualifying_jump_rows_among_all_draws": [named, cap7],
                "deleting_only_08_15": [named, dropped["cap7"]["starts"]],
                "fully_gated_canonical_frame": [named, canonical["cap7"]["starts"]]}
    return {"scope": "the frozen weighted archive, with exact gates on all original trials",
            "sampling_frame": sampling, "named_archive_starts": sources,
            "all_independent_filled_and_class_rows_agreed": len(samples),
            "gates_by_draw": {case: [{"canonical": r["canonical"], "K2_failed_junctions": r["K2_failed_junctions"],
                                      "forced_distinctions": r["forced_distinctions"]} for r in rows]
                              for case, rows in grades.items()},
            "EXPLOSIVE": {"original": original, "deletion_only": dropped, "fully_gated": canonical,
                          "predictions": dict(zip(("original", "deletion_only", "fully_gated"), scores, strict=True)),
                          "referee": exp_referee(samples)},
            "followups": followup_audit(names, streams), "controls": controls()}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--runner-results", type=Path)
    parser.add_argument("--use-retained", action="store_true")
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "sources_audit.json")
    args = parser.parse_args()
    frames, fingerprint = archive(args.use_retained)
    followups = historical_inputs(args.use_retained)
    if args.runner_results:
        run = load_results(args.runner_results)
        assert set(run) == set(frames) and all(row["status"] == "ok" for row in run.values())
        grades = {case: run[case]["result"] for case in frames}
    else:
        grades = {case: [independent_score(r) for r in frame["starts"]] for case, frame in frames.items()}
    result = audit(frames, grades, followups)
    if not args.use_retained and args.output == ARTIFACTS / "sources_audit.json":
        write(RETAINED, {"frames": frames, "sha256": fingerprint, "followups": followups}, compressed=True)
    result["source_sha256"] = {"runs/explosive/results.jsonl": fingerprint, **{
        FOLLOWUP_STREAMS[name]: record["sha256"] for name, record in followups.items()
    }, **{str(path.relative_to(ROOT)): digest(path) for path in (EXPLOSIVE, MERGE, WALL, WALL_PROOF, WALL_DOUBLE_COUNT,
                                                                 EXP_REFEREE, MERGE_REFEREE, HUB, PARTNER)}}
    result["retained_input_sha256"] = digest(RETAINED) if RETAINED.is_file() else None
    write(args.output, result)
    print(json.dumps(result["sampling_frame"], sort_keys=True))


if __name__ == "__main__":
    main()
