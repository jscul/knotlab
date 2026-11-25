"""Compare exact masks and route evidence against the separate replay."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from io import BytesIO
from itertools import groupby, zip_longest
import json
from pathlib import Path

from job import HERE, event_key, from_jsonl, load_results, route_key, split_arm_rows
from truth import canonical_receipt, classify


def outputs(path):
    records = {}
    for attempt in load_results(path).values():
        if attempt["status"] != "ok":
            continue
        row = attempt["result"]
        key = row["case"], row["rule"], row["kl"]
        if key in records:
            raise ValueError(f"duplicate completed trajectory {key}")
        records[key] = row
    return records


def normal_event(event):
    routes = []
    for route in sorted(event["routes"], key=route_key):
        record = [
            *route_key(route),
            *(route[field] for field in ("contacts", "x_arms", "y_arms", "a", "b")),
        ]
        if route["route"] == "take":
            actor = route.get("recipient", route.get("newborn"))
            record.extend([actor, route["pre_holder"], route["near_eligible"]])
        routes.append(record)
    phase_name = {"group": "met", "demand group": "demand"}
    phases = sorted(phase_name.get(kind, kind) for kind in event["meeting_types"])
    return [*event_key(event), phases, routes]


def digest_rows(rows):
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def first_difference(first, second):
    for i, (left, right) in enumerate(zip_longest(first, second), start=1):
        if left != right:
            return {"row": i, "primary": left, "referee": right}
    return None


def trace_path(root, trace):
    path = (root / trace["file"]).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError(f"projection trace escaped its artifact directory: {path}")
    return path


def verify_trace(root, trace):
    path = trace_path(root, trace)
    with gzip.open(path, "rb") as stream:
        digest, rows = receipt_from(stream)
    if digest != trace["sha256"] or rows != trace["rows"]:
        raise ValueError(f"projection trace digest or row count differs: {path}")
    return path


def receipt_from(stream):
    digest = hashlib.sha256()
    rows = 0
    while block := stream.read(1_048_576):
        digest.update(block)
        rows += block.count(b"\n")
    return digest.hexdigest(), rows


def ordered_referee_events(root):
    with gzip.open(root / "first_meetings.jsonl.gz", "rb") as stream:
        lines = (json.loads(line) for line in stream)
        for key, rows in groupby(lines, lambda row: (row["case"], row["rule"], row["kl"])):
            if key[1] == "MOST":
                yield key, sorted(rows, key=event_key)


def ref_member(root, row):
    size = row["projection_gzip_bytes"]
    with (root / "literal_masks.jsonl.gz").open("rb") as stream:
        stream.seek(row["projection_gzip_offset"])
        compressed = stream.read(size)
    if len(compressed) != size or size <= 0:
        raise ValueError(f"incomplete independent mask member for {row['case']}/{row['kl']}")
    return compressed


def compare(key, primary, referee, referee_events, receipt, producer_root, projection_root, referee_root):
    if (primary["support_sha256"], primary["events_sha256"]) != (
        receipt["support_sha256"], receipt["events_sha256"],
    ):
        raise ValueError(f"projection lost its input digest at {key}")
    source_events = from_jsonl(producer_root, receipt["events_file"], receipt["events_sha256"])
    left = [normal_event(event) for event in sorted(source_events, key=event_key)]
    right = [normal_event(event) for event in referee_events]
    result = {
        "rounds_match": primary["rounds_read"] == referee["rounds_read"],
        "terminal_count_matches": receipt["knots"] == referee["knots"],
        "event_rows": len(left),
        "referee_event_rows": len(right),
        "event_difference": first_difference(left, right),
        "event_digests": {"primary": digest_rows(left), "referee": digest_rows(right)},
        "literal_annotations_match": primary["literal_annotations"] == referee["literal_annotations"],
    }
    triples = primary["triple"]
    primary_trace = verify_trace(projection_root, triples)
    if sum(primary["masks"].values()) != triples["rows"]:
        raise ValueError(f"primary triple mask tally wrong at {key}")
    compressed = ref_member(referee_root, referee)
    with gzip.GzipFile(fileobj=BytesIO(compressed), mode="rb") as stream:
        ref_digest, ref_count = receipt_from(stream)
    if (ref_digest, ref_count) != (
        referee["projection_sha256"], referee["counts"]["literal_occurrences"],
    ):
        raise ValueError(f"independent mask count or digest differs from receipt at {key}")
    result["triple_rows"] = triples["rows"]
    result["referee_triple_rows"] = ref_count
    result["triple_digests"] = {"primary": triples["sha256"], "referee": ref_digest}
    result["triple_difference"] = None
    if (triples["sha256"], triples["rows"]) != (ref_digest, ref_count):
        with gzip.open(primary_trace, "rb") as primary_rows:
            with gzip.GzipFile(fileobj=BytesIO(compressed), mode="rb") as ref_rows:
                result["triple_difference"] = first_difference(
                    map(json.loads, primary_rows), map(json.loads, ref_rows),
                ) or {"reason": "compact JSONL encoding differs"}

    split = primary["split_arms"]
    split_rows = from_jsonl(projection_root, split["file"], split["sha256"])
    if len(split_rows) != split["rows"]:
        raise ValueError(f"primary split-arm count differs from its receipt at {key}")
    case, _, law = key
    ref_split = [
        json.loads(json.dumps(row)) for row in split_arm_rows(case, law, referee_events)
    ]
    result["split_arm_rows"] = len(split_rows)
    result["referee_split_arm_rows"] = len(ref_split)
    result["split_arm_digests"] = {"primary": split["sha256"], "referee": digest_rows(ref_split)}
    result["split_arm_difference"] = first_difference(split_rows, ref_split)
    result["agrees"] = (
        result["rounds_match"] and result["terminal_count_matches"] and result["literal_annotations_match"]
        and all(result[field] is None for field in ("event_difference", "triple_difference", "split_arm_difference"))
    )
    return result


def summarize(producer_path, primary_path, producer_root, projection_root, referee_root):
    frozen = json.loads((HERE.parent / "cases.json").read_bytes())
    ordered = [(spec["id"], "MOST", law) for spec in frozen for law in ("nae", "parity")]
    sequence = {key: i for i, key in enumerate(ordered)}
    producer = outputs(producer_path)
    referee = {}
    with (referee_root / "cases.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            key = (row["case"], row["rule"], row["kl"])
            if key[1] != "MOST":
                continue
            if key in referee:
                raise ValueError(f"duplicate independent case {key}")
            referee[key] = row
    event_groups = ordered_referee_events(referee_root)
    pending = next(event_groups, None)
    primary = outputs(primary_path)
    checked = []
    missing = []
    totals = defaultdict(Counter)
    confirmed_masks = defaultdict(Counter)
    primary_masks = defaultdict(Counter)
    confirmed_prior = defaultdict(lambda: defaultdict(Counter))
    confirmed_origin = defaultdict(lambda: defaultdict(Counter))
    confirmed_categories = defaultdict(Counter)
    first_by_category = defaultdict(dict)
    work = defaultdict(Counter)
    for key in ordered:
        _, _, law = key
        totals[law]["expected"] += 1
        ref_events = []
        if pending is not None:
            if pending[0] == key:
                ref_events = pending[1]
                pending = next(event_groups, None)
            elif sequence[pending[0]] < sequence[key]:
                raise ValueError(f"independent event groups out of frozen order at {key}")
        own = primary.get(key)
        if own is not None:
            totals[law]["primary"] += 1
            primary_masks[law].update(own["masks"])
            work[law].update({name: own[name] for name in (
                "unique_triples", "unique_prior_pairs", "projection_calls",
            )})
        if key not in producer or key not in referee or own is None:
            missing.append({
                "case": key, "producer": key in producer, "referee": key in referee, "projection": own is not None,
            })
            continue
        comparison = compare(
            key, own, referee[key], ref_events, producer[key], producer_root, projection_root, referee_root,
        )
        checked.append({"case": key, **comparison})
        if comparison["agrees"]:
            totals[law]["independent_agreement"] += 1
            totals[law]["first_meetings"] += own["events"]
            totals[law]["without_qualified_routes"] += own["events_without_qualified_routes"]
            totals[law]["routes"] += own["routes"]
            totals[law]["split_arms"] += own["split_arms"]["rows"]
            totals[law]["triples"] += own["triple"]["rows"]
            confirmed_masks[law].update(own["masks"])
            for mask, count in own["masks"].items():
                confirmed_categories[law][classify(int(mask))["category"]] += count
            for context in own["by_route_and_origin"]:
                text = f"{context['route']}/{context['origin']}"
                confirmed_origin[law][text].update(context["masks"])
            for category, counts in own["category_by_prior_side_case"].items():
                confirmed_prior[law][category].update(counts)
            for category, row in own["first_by_category"].items():
                first_by_category[law].setdefault(category, row)
        else:
            totals[law]["disagreement"] += 1
    if pending is not None:
        raise ValueError(f"unexpected independent event group {pending[0]}")
    seen = {int(mask) for tally in primary_masks.values() for mask in tally}
    canonical = {mask: canonical_receipt(mask) for mask in sorted(seen)}
    return {
        "totals": totals,
        "primary_masks": primary_masks,
        "independently_confirmed_masks": confirmed_masks,
        "independently_confirmed_categories": confirmed_categories,
        "independently_confirmed_masks_by_route_and_origin": confirmed_origin,
        "independently_confirmed_prior_by_category": confirmed_prior,
        "first_confirmed_mask_per_category": first_by_category,
        "canonical_receipts": canonical,
        "projection_work": work,
        "missing": missing,
        "checks": checked,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for source in (
        "producer", "referee", "primary", "producer-artifacts", "projection-artifacts",
    ):
        parser.add_argument(f"--{source}", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(
        args.producer, args.primary,
        args.producer_artifacts.resolve(strict=True), args.projection_artifacts.resolve(strict=True),
        args.referee.resolve(strict=True),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
