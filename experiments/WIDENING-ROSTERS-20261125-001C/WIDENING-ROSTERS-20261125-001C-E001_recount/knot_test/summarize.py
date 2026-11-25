"""Reconcile history certificates, independent roster totals, and CLI receipts."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from canonical import load_results, relation_key
from projection import Projection

HERE = Path(__file__).resolve().parent


def load_referee(path):
    records = {}
    with (path / "terminal.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            key = f"{row['case']}/{row['kl']}"
            if key in records:
                raise ValueError(f"duplicate independent terminal for {key}")
            records[key] = {"status": "ok", "result": {"terminal": row, "stages": []}}
    with (path / "stages.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            key = f"{row['case']}/{row['kl']}"
            records[key]["result"]["stages"].append(row)
    return records


def read_stages(record):
    stages = {}
    for stage in record["stages"]:
        t = stage["round"]
        if t in stages:
            raise ValueError(f"round {t} appeared more than once")
        stages[t] = stage
    return stages


def summarize(producer, referee, histories, canonical, stock):
    frozen = json.loads((HERE.parent / "cases.json").read_bytes())
    totals = defaultdict(Counter)
    evidence = Counter()
    relation_counts = {}
    failures = []
    fallen_back = []
    missing = []
    differences = []
    closed = []
    omitted = []
    for cfg in frozen:
        case = cfg["id"]
        raw = producer.get(case, {})
        for law in ("nae", "parity"):
            key = f"{case}/{law}"
            status = totals[law]
            status["frozen_trajectories"] += 1
            primary = histories.get(key, {})
            if raw.get("status") != "ok" or primary.get("status") != "ok":
                missing.append({
                    "case": key, "producer": raw.get("status", "not_run"),
                    "certificate": primary.get("status", "not_run"),
                    "error": raw.get("error") or primary.get("error"),
                })
                continue
            raw_law = next(row for row in raw["result"]["laws"] if row["kl"] == law)
            result = primary["result"]
            if (result["case"], result["kl"], result["support_sha256"]) != (
                case, law, raw_law["support_sha256"],
            ):
                raise ValueError(f"certificate and support identity mismatch at {key}")
            if raw_law["parity_closing_rounds"]:
                closed.append({"case": key, "rounds": raw_law["parity_closing_rounds"]})
            if raw_law["missing_rounds"]:
                omitted.append({"case": key, "rounds": raw_law["missing_rounds"], "stop": raw_law["stop"]})
            evidence.update(result["evidence"])
            fallback = result["birth_method_fallback"]
            if fallback is not None:
                fallen_back.append({"case": key, **fallback})
            failures.extend({"case": key, **row} for row in result["failure_details"])
            status["certified_trajectories"] += 1
            by_round = read_stages(result)
            terminal = result["stages"][-1]
            status["terminal_knots"] += terminal["knots"]
            status["terminal_passed"] += terminal["passed"]
            status["terminal_failed"] += terminal["failed"]
            status["terminal_unclassified"] += terminal["unclassified"]
            if terminal["knots"] != raw_law["knots"] or terminal["round"] != raw_law["rounds_done"]:
                raise ValueError(f"producer and certificate terminal mismatch at {key}")
            status["all_reached_stages"] += len(by_round)
            status["scheduled_reached_stages"] += len(result["scheduled"])
            raw_stages = read_stages(raw_law)
            if set(raw_stages) != set(result["scheduled"]):
                raise ValueError(f"producer and certificate schedule mismatch at {key}")
            reference = referee.get(key, {})
            reference_ok = reference.get("status") == "ok" and "stages" in reference["result"]
            reference_stages = read_stages(reference["result"]) if reference_ok else {}
            if reference_ok:
                end = reference["result"]["terminal"]
                if (end["round"], end["knots"]) == (terminal["round"], terminal["knots"]):
                    status["matching_independent_terminals"] += 1
                else:
                    differences.append({
                        "case": key, "scope": "terminal", "certificate": [terminal["round"], terminal["knots"]],
                        "referee": [end["round"], end["knots"]],
                    })
            for t, stage in by_round.items():
                status["all_stage_knots"] += stage["knots"]
                status["all_stage_passed"] += stage["passed"]
                status["all_stage_failed"] += stage["failed"]
                status["all_stage_unclassified"] += stage["unclassified"]
                count = Counter()
                for row in stage["relations"]:
                    projection = Projection.from_spec(row["projection"])
                    receipt = relation_key(projection)
                    verdict = projection.report()
                    if any(verdict[field] != row[field] for field in verdict):
                        raise ValueError(f"invalid verdict at {key} round {t}")
                    category = "passed" if verdict["is_knot"] else "failed"
                    count[category] += row["knots"]
                    relation = relation_counts.setdefault(receipt, {"projection": row["projection"], "laws": Counter()})
                    relation["laws"][law] += row["knots"]
                if (
                    count["passed"] != stage["passed"]
                    or count["failed"] != stage["failed"]
                    or sum(count.values()) + stage["unclassified"] != stage["knots"]
                    or stage["independent_agreements"] != sum(count.values())
                ):
                    raise ValueError(f"certificate coverage is inconsistent at {key} round {t}")
                if t not in raw_stages:
                    continue
                status["scheduled_stage_knots"] += stage["knots"]
                status["scheduled_stage_passed"] += stage["passed"]
                status["scheduled_stage_failed"] += stage["failed"]
                status["scheduled_stage_unclassified"] += stage["unclassified"]
                if raw_stages[t]["knots"] != stage["knots"]:
                    raise ValueError(f"producer and certificate knot count differs at {key} round {t}")
                if t in reference_stages and reference_stages[t]["knots"] == stage["knots"]:
                    status["matching_both_engines_stages"] += 1
                    status["matching_both_engines_stage_knots"] += stage["knots"]
                else:
                    differences.append({
                        "case": key, "scope": "scheduled", "round": t, "certificate": stage["knots"],
                        "referee": reference_stages[t]["knots"] if t in reference_stages else None,
                    })
            for t in sorted(set(reference_stages) - set(raw_stages)):
                differences.append({
                    "case": key, "scope": "referee_only_scheduled", "round": t,
                    "referee": reference_stages[t]["knots"],
                })
    for receipt, relation in relation_counts.items():
        reported = canonical.get(receipt, {})
        standard = stock.get(receipt, {})
        if reported.get("status") != "ok":
            relation["status"] = reported.get("status", "not_run")
        else:
            result = reported["result"]
            if result["projection"] != relation["projection"]:
                raise ValueError(f"canonical receipt and projection identity mismatch at {receipt}")
            relation["status"] = result["status"]
        if standard.get("status") == "ok" and reported.get("status") == "ok":
            if standard["result"] != reported["result"]:
                raise ValueError(f"stock and optimized canonical receipts disagree at {receipt}")
            relation["stock_comparison"] = "all_fields_equal"
        elif relation["projection"]["width"] > 12 and not standard:
            relation["stock_comparison"] = "not_run_measured_prefix"
        else:
            relation["stock_comparison"] = standard.get("status", "not_run")
        for law, n in relation["laws"].items():
            totals[law][f"all_stage_canonical_{relation['status']}"] += n
    return {
        "totals": totals, "method_counts": evidence, "failures": failures, "birth_method_fallbacks": fallen_back,
        "missing_trajectories": missing, "independent_count_differences": differences,
        "actual_parity_closings": closed, "scheduled_rounds_omitted_at_growth_stop": omitted,
        "canonical_relations": relation_counts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for source in ("producer", "referee", "histories", "canonical", "stock"):
        parser.add_argument(f"--{source}", type=Path, required=True)
    args = parser.parse_args()
    summary = summarize(
        load_results(args.producer), load_referee(args.referee), load_results(args.histories),
        load_results(args.canonical), load_results(args.stock),
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
