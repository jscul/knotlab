"""Parse the raw paired records and recompute discovery scores and intervals."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import shutil
from statistics import mean
from time import perf_counter_ns, process_time_ns

from scipy.stats import beta, binomtest


HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "contract.json"
ROOT = HERE.parents[2]
CALIBRATION = ROOT / "artifacts" / HERE.parent.name / HERE.name / "calibration.json"
ARMS = ("independent", "diversity")
LAWS = ("parity", "nae")


def digest(path):
    with path.open("rb") as stream:
        return sha256_stream(stream)[0]


def sha256_stream(stream):
    digest = sha256()
    count = 0
    for chunk in iter(lambda: stream.read(1 << 20), b""):
        digest.update(chunk)
        count += len(chunk)
    return digest.hexdigest(), count


def gzip_copy(source, target):
    if source.suffix == ".gz":
        raise ValueError("gzip copy expects the original shared-runner record")
    with source.open("rb") as raw, target.open("xb") as out:
        with gzip.GzipFile(filename="", mode="wb", compresslevel=6, fileobj=out, mtime=0) as packed:
            shutil.copyfileobj(raw, packed, length=(1 << 20))
    with gzip.open(target, "rb") as opened, source.open("rb") as raw:
        archived = sha256_stream(opened)
        original = sha256_stream(raw)
    if original != archived:
        raise ValueError("compressed trace failed independent decompression and digest check")
    return {"path": str(target.relative_to(ROOT)) if target.is_relative_to(ROOT) else str(target),
            "gzip_sha256": digest(target), "gzip_bytes": target.stat().st_size,
            "raw_sha256": original[0], "raw_bytes": original[1]}


def cp(k, n):
    if not n:
        return None
    low = float(beta.ppf(0.025, k, n - k + 1)) if k else 0.0
    high = float(beta.ppf(0.975, k + 1, n - k)) if k < n else 1.0
    return {"count": k, "total": n, "rate": k / n, "ci95": [low, high]}


def signature(row, law):
    g = row.get("growth")
    if not g or g["stop"] != "horizon" or len(g["rounds"]) != 5:
        return None
    rates = [r["births"] for r in g["rounds"]]
    if law == "nae" and 1 in rates:
        return None
    rates = rates[1:]
    change = tuple((b > a) - (b < a) for a, b in zip(rates, rates[1:]))
    arities = {p for r in g["rounds"][2:] for p, _, _ in r["arity_and_fresh"]}
    return (*change, 1 in arities, any(p >= 3 for p in arities))


def collision_key(row):
    g = row.get("growth")
    if not g or len(g["rounds"]) < 3:
        return None
    first, second, third = (r["births"] for r in g["rounds"][:3])
    return (row["founder_count"], first, second), third


def read_arm(arm, law, known, count, endpoint):
    rows = arm["rows"][:count]
    if any(not row["eligible"] for row in rows):
        raise ValueError("chronological cutoff includes unfinished trial")
    founders = [row["founder"] for row in rows if "growth" in row]
    if len(founders) != len(set(founders)):
        raise ValueError("duplicate founder reached growth")
    proposals = Counter()
    collision_b = defaultdict(set)
    known_hits = 0
    for i, row in enumerate(rows):
        if row["index"] != i:
            raise ValueError("trial indices are not a contiguous prefix")
        code = row.get("founder")
        if row["status"] == "partition_refusal" and ("proposal" in row or code is not None):
            raise ValueError("out-of-partition source identity entered persisted records")
        proposed = signature(row, law)
        if (None if row.get("late_signature") is None else tuple(row["late_signature"])) != proposed:
            raise ValueError("persisted late read disagrees with completed rounds")
        if proposed is not None and proposed not in known:
            proposals[proposed] += 1
        elif proposed is not None:
            known_hits += 1
        comparison = collision_key(row)
        if comparison is not None:
            key, b3 = comparison
            collision_b[key].add(b3)
    verification = arm[endpoint]
    events = verification["events"]
    types, witnessed, failures = set(), [], Counter()
    for event in events:
        if event["status"] != "verified":
            failures[event["status"]] += 1
            continue
        i, j = event["attempts"]
        left, right = rows[i], rows[j]
        if not 0 <= i < j < count or left["founder"] == right["founder"]:
            raise ValueError("invalid independent witness pair")
        sizes = [left["founder_count"], right["founder_count"]]
        distinctions = [left["physical_distinctions"], right["physical_distinctions"]]
        expected_rank = [max(sizes), sum(sizes), max(distinctions), sum(distinctions),
                         sorted((left["founder"], right["founder"]))]
        if event["rank"] != expected_rank:
            raise ValueError("persisted witness rank differs from its source starts")
        width = 5 if event["kind"] == "novel" else 3
        for row, replay in zip((left, right), event["replays"], strict=True):
            if replay["rounds"] != row["growth"]["rounds"][:width]:
                raise ValueError("persisted literal replay does not match recorded observations")
        key = tuple(event["key"])
        if event["kind"] == "novel":
            if key in known or signature(left, law) != key or signature(right, law) != key:
                raise ValueError("invalid primary signature witness")
            types.add(key)
        elif event["kind"] == "collision":
            left_key, left_b3 = collision_key(left)
            right_key, right_b3 = collision_key(right)
            if left_key != key or right_key != key or left_b3 == right_b3:
                raise ValueError("invalid count collision")
        else:
            raise ValueError("unknown verification result")
        witnessed.append({**event, "founders": [left["founder"], right["founder"]],
                          "source_attempts": [left["proposal"], right["proposal"]],
                          "birth_counts": [[r["births"] for r in row["growth"]["rounds"]]
                                           for row in (left, right)]})
    return {"completed_attempts": count, "observed_founders": len(founders),
            "funded_first_round": sum(bool(row.get("growth", {}).get("rounds")) for row in rows),
            "observed_through_five": sum(len(row.get("growth", {}).get("rounds", ())) == 5 for row in rows),
            "known_dictionary_hits": known_hits, "raw_types_seen_once": sum(n == 1 for n in proposals.values()),
            "known_closure_relays": sum(bool(row.get("known_closure_relay")) for row in rows),
            "raw_absent_types": len(proposals), "raw_types_seen_twice": sum(n >= 2 for n in proposals.values()),
            "raw_collision_strata": sum(len(sizes) >= 2 for sizes in collision_b.values()),
            "literal_replays_completed": sum(len(event["replays"]) for event in events),
            "types": sorted(types), "witnesses": witnessed, "verification_failures": dict(failures),
            "verification_exhausted": verification["verification_exhausted"],
            "verification_budget": verification["budget"]}


def bootstrap(differences, law, analysis):
    if not differences:
        return None
    rng = Random(f"GROWTH-STATISTICS-20261121-001B/bootstrap/v1/{law}/{analysis}")
    n = len(differences)
    replicates = sorted(sum(rng.choice(differences) for _ in range(n)) / n for _ in range(10_000))
    return [replicates[249], replicates[9749]]


def compare(pairs, law, analysis):
    differences = [pair["diversity"] - pair["independent"] for pair in pairs]
    n = len(pairs)
    wins = sum(d > 0 for d in differences)
    losses = sum(d < 0 for d in differences)
    report = {"repeats": n, "differences": differences}
    if n:
        report.update({"mean_counts": {arm: mean(p[arm] for p in pairs) for arm in ARMS},
                       "mean_difference": mean(differences),
                       "W_T_L": [wins, n - wins - losses, losses],
                       "win": cp(wins, n), "tie": cp(n - wins - losses, n), "loss": cp(losses, n),
                       "any_difference": cp(wins + losses, n),
                       "any_novel": {arm: cp(sum(p[arm] > 0 for p in pairs), n) for arm in ARMS},
                       "two_sided_conditional_sign_p": (1.0 if wins + losses == 0
                                                        else float(binomtest(wins, wins + losses).pvalue)),
                       "bootstrap_mean_difference_ci95_descriptive": bootstrap(differences, law, analysis)})
    return report


def smallest(pair_records, law, analysis, kind):
    entries = [(event["rank"], case["case"], arm, event)
               for case in pair_records if case["law"] == law
               for arm, report in case[analysis].items()
               for event in report["witnesses"] if event["kind"] == kind]
    if not entries:
        return None
    _, case_id, arm, event = min(entries, key=lambda entry: entry[:3])
    return {"case": case_id, "arm": arm, **event}


def summarize(raw, phase):
    known = {law: set(map(tuple, values)) for law, values
             in json.loads(CALIBRATION.read_bytes())["signature_dictionary"].items()}
    wanted = {(law, i) for law in LAWS for i in range(48 if phase == "search" else 10)}
    records, seen = [], set()
    errors = []
    began, wall = process_time_ns(), perf_counter_ns()
    opener = gzip.open if raw.suffix == ".gz" else open
    with opener(raw, "rt", encoding="utf-8") as stream:
        for line in stream:
            outer = json.loads(line)
            if outer["status"] != "ok":
                errors.append({k: outer[k] for k in ("case", "status", "error")})
                continue
            result = outer["result"]
            law, index = result["law"], result["index"]
            if (law, index) in seen or (law, index) not in wanted or result["partition"] != phase:
                raise ValueError("unexpected paired case or duplicate in raw records")
            seen.add((law, index))
            common = min(r["completed_attempts"] for r in result["arms"].values())
            if common != result["common_completed_attempts"] or set(result["arms"]) != set(ARMS):
                raise ValueError("mismatched count sensitivity cutoff")
            by_window, by_count, resource = {}, {}, {}
            for arm, input_row in result["arms"].items():
                by_window[arm] = read_arm(input_row, law, known[law], input_row["completed_attempts"], "verification")
                by_count[arm] = read_arm(input_row, law, known[law], common, "equal_count_verification")
                resource[arm] = {"search_budget": input_row["budget"], "outcomes": input_row["outcomes"],
                                 "stop": input_row["stop"], "evaluated_founders": input_row["evaluated_founders"]}
            records.append({"case": outer["case"], "law": law, "index": index, "budget": resource,
                            "cpu": by_window, "equal_count": by_count, "seconds": outer["seconds"],
                            "peak_rss_mb": outer["peak_rss_mb"], "common_completed_attempts": common,
                            "shared_case_setup": result["shared_setup"],
                            "shared_setup_once": result.get("shared_setup_once")})
    records.sort(key=lambda r: (r["law"], r["index"]))
    analyses = {}
    for kind in ("cpu", "equal_count"):
        per_law = {}
        for law in LAWS:
            cases = [row for row in records if row["law"] == law]
            scored = [{arm: len(row[kind][arm]["types"]) for arm in ARMS} for row in cases]
            info = compare(scored, law, kind)
            info["arm_resource_totals"] = {
                arm: {"attempts": sum(row[kind][arm]["completed_attempts"] for row in cases),
                      "founders": sum(row[kind][arm]["observed_founders"] for row in cases),
                      "funded_first_round": sum(row[kind][arm]["funded_first_round"] for row in cases),
                      "observed_through_five": sum(row[kind][arm]["observed_through_five"] for row in cases),
                      "known_dictionary_hits": sum(row[kind][arm]["known_dictionary_hits"] for row in cases),
                      "known_closure_relays": sum(row[kind][arm]["known_closure_relays"] for row in cases),
                      "literal_replays_completed": sum(row[kind][arm]["literal_replays_completed"] for row in cases),
                      "raw_types_seen_once": sum(row[kind][arm]["raw_types_seen_once"] for row in cases),
                      "raw_types_seen_twice": sum(row[kind][arm]["raw_types_seen_twice"] for row in cases),
                      "raw_collision_strata": sum(row[kind][arm]["raw_collision_strata"] for row in cases),
                      "repeats_with_verified_collision": sum(
                          any(event["kind"] == "collision" for event in row[kind][arm]["witnesses"]) for row in cases),
                      "verification_cpu_ns": sum(row[kind][arm]["verification_budget"]["actual_cpu_ns"] for row in cases),
                      "search_cpu_ns": sum(row["budget"][arm]["search_budget"]["actual_cpu_ns"] for row in cases)}
                for arm in ARMS}
            for witness in ("novel", "collision"):
                info[f"smallest_{witness}"] = smallest(records, law, kind, witness)
            per_law[law] = info
        analyses[kind] = per_law
    primary = analyses["cpu"]
    if all("two_sided_conditional_sign_p" in d for d in primary.values()):
        lower = 0.0
        for i, law in enumerate(sorted(primary, key=lambda k: primary[k]["two_sided_conditional_sign_p"])):
            p = primary[law]["two_sided_conditional_sign_p"]
            lower = min(1.0, max(lower, (len(primary) - i) * p))
            primary[law]["holm_p"] = lower
    mismatch = sum(sum(v["verification_failures"].get("replay_disagrees", 0) for v in row[kind].values())
                   for row in records for kind in ("cpu", "equal_count"))
    with opener(raw, "rb") as stream:
        raw_sha, raw_bytes = sha256_stream(stream)
    return {"source_partition": phase, "complete": seen == wanted and not errors and not mismatch,
            "contract_sha256": digest(CONTRACT), "raw_sha256": raw_sha, "raw_bytes": raw_bytes,
            "calibration_sha256": digest(CALIBRATION), "missing": sorted(wanted - seen), "errors": errors,
            "witness_mismatches": mismatch, "analyses": analyses, "repeats": records,
            "postprocess_cpu_ns": process_time_ns() - began, "postprocess_wall_ns": perf_counter_ns() - wall}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--phase", choices=("development", "search"), required=True)
    parser.add_argument("--gzip-copy", type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    report = summarize(args.raw, args.phase)
    if args.gzip_copy:
        cpu, wall = process_time_ns(), perf_counter_ns()
        report["gzip_copy"] = gzip_copy(args.raw, args.gzip_copy.resolve())
        report["gzip_copy"].update(cpu_ns=process_time_ns() - cpu, wall_ns=perf_counter_ns() - wall)
    with args.out.open("x") as stream:
        json.dump(report, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    if not report["complete"]:
        raise SystemExit("incomplete raw experiment; summary retains errors")


if __name__ == "__main__":
    main()
