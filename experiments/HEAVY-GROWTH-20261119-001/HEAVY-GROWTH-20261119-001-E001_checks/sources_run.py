"""Screen each original EXPLOSIVE sampling case with the exact support test."""

from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

from sources_features import filled_features, measured
from sources_span import qualify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
RAW = ROOT / "runs/explosive/results.jsonl"
RETAINED = ARTIFACTS / "sources_inputs.json.gz"
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results


def digest(path):
    with path.open("rb") as document:
        return sha256(document.read()).hexdigest()


@cache
def archive(force_retained=False):
    if force_retained or not RAW.is_file():
        payload = json.loads(gzip.decompress(RETAINED.read_bytes()))
        return payload["frames"], payload["sha256"]
    before = digest(RAW)
    runs = load_results(RAW)
    assert len(runs) == 21 and all(record["status"] == "ok" for record in runs.values())
    frames = {case: row["result"] for case, row in runs.items()}
    assert before == digest(RAW)
    return frames, before


def source_key(sizes, edges):
    return tuple(sizes), tuple(sorted(tuple(sorted(e)) for e in edges))


def independent_score(record):
    grade = qualify(record["sizes"], record["edges"])
    features = filled_features(record["sizes"], record["edges"])
    observed = measured(record["outcome"], record["counts"])
    assert record["n"] == len(record["sizes"]) and record["max_places"] == max(record["sizes"])
    fields = {"reading": record["reading"], "tri": record["tri"], "overlap_point": record["overlap_point"],
              "overlap_block": record["overlap_block"], "filled_b1": sorted(record["b1"]),
              "filled_b2": sorted(record["b2"]), "measured": record["measured"]}
    replay = {k: features[k] for k in fields if k != "measured"}
    replay.update({"filled_b1": sorted(replay["filled_b1"]), "filled_b2": sorted(replay["filled_b2"]),
                   "measured": observed})
    mismatch = {k: [expected, replay[k]] for k, expected in fields.items() if replay[k] != expected}
    assert grade["canonical"] == (grade["K1_all"] and grade["K2_all"] and grade["K3_all"])
    return {"canonical": grade["canonical"], "K2_failed_junctions": grade["K2_failed_junctions"],
            "forced_distinctions": grade["forced_distinctions"], "literal_span_rank": grade["span_rank"],
            "first_round_funded": features["first_round_funded"],
            "at_most_one_common_holder": features["at_most_one_common_holder"],
            "independent_field_disagreement": mismatch}


def cases():
    for name in archive()[0]:
        yield name, name


def run(case_id, name):
    assert case_id == name
    return [independent_score(row) for row in archive()[0][name]["starts"]]
