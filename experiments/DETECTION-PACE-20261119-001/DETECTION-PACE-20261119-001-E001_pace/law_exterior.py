"""Compare actual even-hop exteriors under every supported feedback table."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from current import Stage, distances
from exterior_check import compare, view
from front_local import Incidence, MATCH_BUDGET
from law_panel import CAPS, OUTPUT as LAW_PANEL, TABLES, growth, sources


HERE = Path(__file__).resolve().parent
DESIGN = HERE.parents[2] / "research" / HERE.parent.name / "law_exterior_design.md"
OUTPUT = LAW_PANEL.with_name("law_exterior.json")
THROUGH = 4
DOMAINS = ("root_component", "union")


def material_stages(run, old_count, codes):
    """Use common ancestry-derived names only to propose a candidate bijection."""
    names = list(range(old_count))
    origins = [1 << v for v in range(old_count)]
    for age, frame in run["stages"].items():
        siblings = Counter()
        for birth in frame["births"]:
            parents = birth["parents"]
            signature = tuple(sorted(names[p] for p in parents))
            siblings[signature] += 1
            typed_group = (signature, siblings[signature])
            candidate = codes.setdefault(typed_group, old_count + len(codes))
            assert birth["knot"] == len(names)
            names.append(candidate)
            old = 0
            for p in parents:
                old |= origins[p]
            origins.append(old)
        assert len(names) == len(frame["stars"])
        yield Stage(frame["stars"], frame["occupied"], names, int(age), origins)


def prepare(stage, seam):
    physical = Incidence.from_stars(stage.stars, stage.occupied)
    hops = distances(physical.neighbors, [seam])
    projected = distances(stage.neighbors, [seam])
    assert len(hops) == len(physical.neighbors)
    assert all(hops[v] == 2 * projected[v] for v in range(physical.knot_count))
    assert all(hops[v] == 1 + min(hops[k] for k in physical.neighbors[v])
               for v in physical.distinctions.values())
    return physical, hops, projected


def first_verdict(rows):
    outcomes = [row["comparison"]["result"] for row in rows]
    assert outcomes[0] == "isomorphic"
    last = rows[-1]["age"]
    unresolved = [row["age"] for row in rows if row["comparison"]["result"] == "unresolved"]
    first_positive = next((row for row in rows if row["comparison"]["result"] == "different"), None)
    if first_positive is not None:
        age = first_positive["age"]
        uncertain_before = [a for a in unresolved if a < age]
        return {"status": "first bounded" if uncertain_before else "exact first",
                "first": None if uncertain_before else age,
                "first_possible": min(uncertain_before, default=age),
                "first_certified_difference": age, "last_common_layer": last,
                "unresolved_ages": unresolved,
                "quiet_loaded_at_first_certificate": [first_positive["quiet"], first_positive["loaded"]]}
    return {"status": "unresolved" if unresolved else "agrees through common layer",
            "first": None, "last_common_layer": last, "unresolved_ages": unresolved}


def according_to_prediction(table, d, domain, earliest):
    if table[0] == table[1]:
        certified_difference = "first_certified_difference" in earliest
        verdict = False if certified_difference else None if earliest["unresolved_ages"] else True
        return {"expected": "equal through common layers", "held": verdict}
    if table == "PV":
        expected = max(d - (1 if domain == "root_component" else 2), 1)
    elif table == "+V" and domain == "root_component" and d in (3, 4):
        expected = d - 1
    else:
        return None
    if expected > earliest["last_common_layer"]:
        verdict = (None if earliest["unresolved_ages"] else earliest["first"] is None)
    elif earliest["first"] is not None:
        verdict = earliest["first"] == expected
    elif earliest["status"] == "first bounded":
        verdict = None if earliest["first_possible"] <= expected <= earliest["first_certified_difference"] else False
    elif earliest["unresolved_ages"]:
        verdict = None if expected in earliest["unresolved_ages"] else False
    else:
        verdict = False
    return {"expected_first": expected, "held": verdict}


def run_table(table, spec, panel):
    raw = growth.predecessor().source_stars(spec)
    loads = sources.loads(spec)
    codes = {}
    scan = [(tag, growth.grow(raw, loads[tag], table, rounds=THROUGH, caps=CAPS)) for tag in ("0", "1")]
    stages = []
    for tag, run in scan:
        expected_law = panel["tables"][table]
        activity = panel["physical_loads"][tag]["activity"]
        trace = panel["continuations"][expected_law["first_by_activity"][activity]["continuation"]]
        for age, frame in run["stages"].items():
            assert (frame["junction_count"], frame["distinction_count"]) == (
                trace["frames"][age]["knots"], trace["frames"][age]["distinctions"])
        stages.append(list(material_stages(run, len(raw), codes)))
    seam, = spec["roles"]["seams"]
    anchors = spec["roles"]["anchors"]
    sites = [("left" if i < seam else "right",
              min(abs(i - seam), abs(i + 1 - seam)), mark) for i, mark in enumerate(anchors)]
    assert set(d for _, d, _ in sites) == set(range(12))
    results = {(side, d, domain): [] for side, d, _ in sites for domain in DOMAINS}
    whole = []
    for q, l in zip(*stages):
        assert q.age == l.age
        observed = [prepare(s, seam) for s in (q, l)]
        whole.append({"age": q.age, "quiet_loaded": [[len(s.stars), len(s.ends)] for s in (q, l)]})
        for side, d, mark in sites:
            assert all(known[1][known[0].distinctions[mark]] == 2 * d + 1 for known in observed)
            for domain in DOMAINS:
                pair = [view(stage, known, d, mark, domain) for stage, known in zip((q, l), observed, strict=True)]
                record = compare(pair)
                results[side, d, domain].append({"age": q.age, "quiet": pair[0][3],
                                                 "loaded": pair[1][3], "comparison": record})
    by_mark = []
    for side, d, mark in sites:
        for domain in DOMAINS:
            rows = results[side, d, domain]
            onset = first_verdict(rows)
            by_mark.append({"side": side, "offset": d, "physical_mark": mark, "domain": domain,
                            **onset, "prediction": according_to_prediction(table, d, domain, onset),
                            "comparisons": rows})
    summary = Counter(row["comparison"]["result"] for el in by_mark for row in el["comparisons"])
    returns = [{"state": tag, **run["termination"]} for tag, run in scan]
    print(table, "last paired age", whole[-1]["age"], dict(summary), flush=True)
    return {"last_common_layer": whole[-1]["age"], "arms": returns,
            "stage_sizes": whole, "comparison_counts": dict(summary), "onsets": by_mark}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    preceding = LAW_PANEL.read_bytes()
    prior = json.loads(preceding)["cases"]["J1"]
    result = {"schema": 1, "measurement": "typed induced current incidence at at least 2*d hops from the attachment",
              "shown_labels": ["physical type", "chosen old shared mark"],
              "through": THROUGH, "caps": CAPS, "exact_search_feasibility_cap": MATCH_BUDGET,
              "law_panel_sha256": sha256(preceding).hexdigest(),
              "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(), "tables": {}}
    spec = sources.cases()["J1"]
    assert spec["roles"] == prior["roles"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        result["tables"][table] = run_table(table, spec, prior)
        args.out.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
