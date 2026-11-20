"""Read the earlier fixed-stage evidence without modifying it."""

from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
PREVIOUS = "MOTION-AT-EDDY-20261119-001"
PRIOR = ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_motion")
sys.path.insert(0, str(PRIOR))

from motion_stage import growth_engine
from nearness import ReturnRule, co_knotted_pairs


def cases():
    return [row for path in ("inputs.json", "holdout.json")
            for row in json.loads((PRIOR / path).read_text())["cases"]]


def source_and_stage(spec):
    grown = growth_engine().grow_case(spec, 1, {"junctions": 8192, "distinctions": 32768})
    assert grown["qualification"]["canonical"] and grown["qualification"]["DOUBLE_IDENT"]["in_class"]
    stars = grown["stages"]["1"]["stars"]
    return stars, ReturnRule(co_knotted_pairs(stars))
