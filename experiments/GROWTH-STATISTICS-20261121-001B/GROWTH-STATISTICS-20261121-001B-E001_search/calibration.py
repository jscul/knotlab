"""Freeze shared references from development-bucket proposals and published traces."""

from collections import Counter
from hashlib import sha256
import json
from time import perf_counter_ns, process_time_ns

from growth import HORIZON, compact_growth, late_signature, sign
from search import LAWS, rng_for
from source import ROOT, Start, certify, decode, founder_code, independent_proposal, partition


CALIBRATION_COUNT = 128
CALIBRATION_ATTEMPTS = 4096
ORDINARY_DATA = (ROOT / "artifacts/ORDINARY-DYNAMICS-20261120-001A/"
                 "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/source_cert.json")
GENERATOR_DATA = (ROOT / "artifacts/GENERATORS-20261120-001A/"
                  "GENERATORS-20261120-001A-E001_generators/fixtures.json")
GENERATOR_CONTROLS = ("T4", "T8", "bare5", "bare7", "spare5", "two_relay_tips")


def start_from_stars(stars):
    owners = {}
    for knot, row in enumerate(stars):
        for bit in row:
            owners.setdefault(bit, []).append(knot)
    loose = Counter(row[0] for row in owners.values() if len(row) == 1)
    meetings = tuple(sorted(tuple(row) for row in owners.values() if len(row) == 2))
    return Start(meetings, tuple(loose[v] for v in range(len(stars))))


def in_source_family(start):
    n = len(start.loose)
    e = len(start.meetings)
    deg = Counter(k for pair in start.meetings for k in pair)
    return (n in (4, 5, 6) and e in (n-1, n) and len(set(start.meetings)) == e and
            all(loose - max(0, 3 - deg[k]) in (0, 1) for k, loose in enumerate(start.loose)))


def from_shape_counts(shapes, b):
    if len(b) <= HORIZON or sum(f * k for _, f, k in shapes[str(HORIZON)]) == 0:
        return None
    parents = {p for r in range(3, HORIZON + 1) for p, _, _ in shapes[str(r)]}
    return (sign(b[3] - b[2]), sign(b[4] - b[3]), sign(b[5] - b[4]),
            1 in parents, any(p >= 3 for p in parents))


def generator_signature(case, law, source):
    frames = case["stages"]
    if len(frames) <= HORIZON or frames[HORIZON]["closed"]:
        return None
    if case["source"] != [list(row) for row in source]:
        raise ValueError("published source mismatch")
    b = [r["born"] for r in frames]
    late_unary = any(r["born"] > r["proposed_previous_multi"] for r in frames[3:6])
    high = sum(k for p, k in case["replay"]["earliest_ready"]["input_arity_checks"] if p >= 3)
    outside = sum(r["proposed_previous_multi"] for r in frames[1:3] + frames[6:])
    if not high or high > outside:
        return (sign(b[3] - b[2]), sign(b[4] - b[3]), sign(b[5] - b[4]), late_unary, bool(high))
    if in_source_family(start_from_stars(source)):
        raise ValueError("a public control in the source family needs a recorded signature")
    # The published one-spare five-knot ring gives one knot six places and
    # puts three loose distinctions on a degree-two founder. It lies outside
    # this experiment's source weighting. Reconstruct when archived totals
    # cannot determine the per-round high-arity flag.
    growth = compact_growth(source, law)
    if [r["births"] for r in growth["rounds"]] != b[1:6]:
        raise ValueError("public control count replay disagrees")
    return late_signature(growth)


def references():
    records = {law: [] for law in LAWS}
    excluded = set()
    ordinary = json.loads(ORDINARY_DATA.read_bytes())
    for key, case in sorted(ordinary["source_cases"].items()):
        start = start_from_stars(case["literal_stars"])
        code = founder_code(start) if in_source_family(start) else None
        if code is not None:
            excluded.add(code)
        for law, field in (("parity", "parity"), ("nae", "NAE")):
            signature = from_shape_counts(case[field + "_shapes"], case[field + "_birth_counts_including_source"])
            records[law].append({"source": "ORDINARY-DYNAMICS", "case": key, "profile": signature,
                                 "excluded_founder": code})
    gener = json.loads(GENERATOR_DATA.read_bytes())["laws"]
    for law in LAWS:
        for key in GENERATOR_CONTROLS:
            case = gener[law][key]
            source = tuple(map(tuple, case["source"]))
            start = start_from_stars(source)
            code = founder_code(start) if in_source_family(start) else None
            if code is not None:
                excluded.add(code)
            signature = generator_signature(case, law, source)
            records[law].append({"source": "GENERATORS", "case": key, "profile": signature,
                                 "excluded_founder": code})
    return records, sorted(excluded)


def calibrate():
    cpu, wall = process_time_ns(), perf_counter_ns()
    public, excluded = references()
    needs = {law: {r["profile"] for r in records if r["profile"] is not None}
             for law, records in public.items()}
    rng = rng_for("development", "calibration-fixed")
    rows, counts = [], Counter()
    for index in range(CALIBRATION_ATTEMPTS):
        began, now = process_time_ns(), perf_counter_ns()
        proposal = independent_proposal(rng)
        start = decode(proposal)
        code = founder_code(start)
        if code in excluded:
            counts["public_reference"] += 1
            continue
        if partition(code) != "development":
            counts["partition_refusal"] += 1
            continue
        certificate = certify(start.stars)
        if certificate["failures"]:
            counts["invalid_projection"] += 1
            continue
        record = {"index": index, "proposal": proposal.record(), "founder": code,
                  "source_lawfulness": certificate, "growth": {}}
        for law in LAWS:
            growth = compact_growth(start.stars, law)
            record["growth"][law] = growth
            signature = late_signature(growth)
            if signature is not None:
                needs[law].add(signature)
        record["cpu_ns"] = process_time_ns() - began
        record["wall_ns"] = perf_counter_ns() - now
        rows.append(record)
        if len(rows) == CALIBRATION_COUNT:
            break
    if len(rows) != CALIBRATION_COUNT:
        raise ValueError("insufficient admitted development samples at the frozen calibration cap")
    manifest = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                for p in (ORDINARY_DATA, GENERATOR_DATA)}
    return {"admitted": rows, "outside_exclusions": dict(counts), "attempted": index + 1,
            "reference_sources": public, "reference_sha256": manifest, "excluded_founders": excluded,
            "signature_dictionary": {law: sorted(values) for law, values in needs.items()},
            "cpu_ns": process_time_ns() - cpu, "wall_ns": perf_counter_ns() - wall}
