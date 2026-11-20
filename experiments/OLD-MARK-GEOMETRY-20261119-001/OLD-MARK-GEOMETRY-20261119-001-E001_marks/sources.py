"""Qualified old-mark preparations. Growth itself uses no scoring marks."""
from copy import deepcopy
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = ROOT / "experiments/STATE-FEEDS-GROWTH-20261119-001/STATE-FEEDS-GROWTH-20261119-001-E001_feedback"
sys.path.insert(0, str(PREDECESSOR))
import growth

DEFAULT_CAPS = {"junctions": 6000, "distinctions": 32000}


@cache
def cases():
    inputs = json.loads((HERE / "inputs.json").read_text())
    raw = (ROOT / inputs["source"]).read_bytes()
    assert sha256(raw).hexdigest() == inputs["sha256"]
    result = {case["id"]: case for case in json.loads(raw)["cases"] if case["id"] in inputs["cases"]}
    doubled = deepcopy(result["J1"])
    doubled["id"] = "J1x2"
    original = doubled["roles"]["ring_edges"][0]
    extra = []
    for mark in original:
        u, v = doubled["meetings"][mark]
        extra.append(len(doubled["meetings"]))
        doubled["meetings"].append([u, v])
        doubled["sizes"][u] += 1
        doubled["sizes"][v] += 1
    doubled["roles"]["additional_ring_edges"] = extra
    result["J1x2"] = doubled
    return result


def loads(spec):
    rings = spec["roles"]["ring_edges"]
    if spec["id"] == "J1x2":
        original = rings[0]
        extra = spec["roles"]["additional_ring_edges"]
        result = {}
        for word in range(64):
            occupied = set(original) if word & 32 else set()
            for i, (a, b) in enumerate(zip(original, extra, strict=True)):
                if word & (1 << i):
                    occupied.symmetric_difference_update((a, b))
            result[f"w{word:02d}"] = frozenset(occupied)
        return result
    return {str(mask): frozenset(mark for i, ring in enumerate(rings) if mask & (1 << i) for mark in ring)
            for mask in range(1 << len(rings))}


def generate(spec, occupied, max_age=6, caps=None):
    """Yield each completed stage in order. Returning on a limit never emits an incomplete stage."""
    caps = DEFAULT_CAPS if caps is None else caps
    stars = growth.predecessor().source_stars(spec)
    frame = growth.grow(stars, occupied, ("P","V"), rounds=0, caps=caps)["stages"]["0"]
    yield 0, frame
    for age in range(1, max_age + 1):
        frame = growth.step(frame["stars"], frame["occupied"], ("P","V"), caps=caps)
        if frame["status"] != "extend":
            return frame
        frame["age"] = age
        yield age, frame
    return {"status": "age_limit", "last_age": max_age}
