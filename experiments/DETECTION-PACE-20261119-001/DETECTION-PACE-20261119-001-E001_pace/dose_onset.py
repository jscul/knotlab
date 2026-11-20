"""Nearest live loose-degree timing for every original doubled-ring loading."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from law_panel import AGES, CAPS, OUTPUT as LAW_PANEL, check_nearest, growth, holders, nearest_live, sources


OFFSETS = frozenset((1, 2, 3, 4, 6, 8))
OUTPUT = LAW_PANEL.with_name("dose_onset.json")
TABLE = ("P", "V")


def trace(stars, occupied, anchors, chosen):
    replay = growth.grow(stars, occupied, TABLE, rounds=AGES["J1x2"], caps=CAPS)
    frames = {}
    for age, frame in replay["stages"].items():
        assert set(frame["occupied"]) == occupied
        assert all(occupied.isdisjoint(row) for row in frame["loose"].values())
        reading = nearest_live(frame["stars"], anchors)
        if age in ("1", str(AGES["J1x2"])):
            check_nearest(frame["stars"], reading)
        frames[age] = {"knots": frame["junction_count"], "distinctions": frame["distinction_count"],
                       "readings": {str(mark): reading[str(mark)] for mark in chosen}}
    return {"frames": frames, "termination": replay["termination"]}


def first_change(common, quiet, loaded, mark, holder=None):
    readings = []
    for age in common:
        a, b = [trace["frames"][age]["readings"][mark] for trace in (quiet, loaded)]
        if holder is None:
            x, y = a["from_mark"], b["from_mark"]
            expected_hops = 2 * int(age) + 1
        else:
            x, y = a["from_holders"][holder], b["from_holders"][holder]
            expected_hops = 2 * int(age)
        assert x["incidence_hops"] == y["incidence_hops"] == expected_hops
        readings.append((age, x, y))
    first = next(((a, x, y) for a, x, y in readings if x["by_loose_degree"] != y["by_loose_degree"]), None)
    if first is None:
        return {"first_layer": None, "agree_through": int(common[-1])}
    age, q, l = first
    return {"first_layer": int(age), "agree_through": int(age) - 1,
            "quiet_at_first": q, "loaded_at_first": l}


def compare(quiet, loaded, chosen):
    common = sorted(set(quiet["frames"]) & set(loaded["frames"]), key=int)
    result = {}
    for mark in map(str, chosen):
        ids = quiet["frames"]["0"]["readings"][mark]["from_holders"]
        result[mark] = {"from_mark": first_change(common, quiet, loaded, mark),
                        "from_holders": {k: first_change(common, quiet, loaded, mark, k) for k in ids}}
    return {"last_common_layer": int(common[-1]), "onsets": result}


def timing_label(receipt):
    first = receipt["first_layer"]
    return (f"layer {first}" if first is not None
            else f"agreement through {receipt['agree_through']}")


def dose_summary(words, groups, marks):
    by_mark = {}
    for mark in map(str, marks):
        doses, attachments, witness = defaultdict(Counter), defaultdict(Counter), {}
        for word in words.values():
            result = groups[word["activity"]]["comparison"]["onsets"][mark]["from_mark"]
            doses[word["weight"]][timing_label(result)] += 1
            attachments[str(word["attachment_active"]).lower()][timing_label(result)] += 1
        for a, b in combinations(words, 2):
            k = words[a]["weight"]
            if k != words[b]["weight"] or k in witness:
                continue
            results = [groups[words[w]["activity"]]["comparison"]["onsets"][mark]["from_mark"] for w in (a, b)]
            if timing_label(results[0]) != timing_label(results[1]):
                witness[k] = [{"word": name, "ring_copies_loaded": words[name]["ring_copies_loaded"],
                               "attachment_active": words[name]["attachment_active"], **result}
                              for name, result in zip((a, b), results, strict=True)]
        by_mark[mark] = {"by_weight": {dose: dict(tally) for dose, tally in doses.items()},
                         "by_attachment_activity": {mode: dict(tally) for mode, tally in attachments.items()},
                         "same_weight_different_onset_examples": witness}
    return by_mark


def measure():
    spec = sources.cases()["J1x2"]
    roles = spec["roles"]
    original = growth.predecessor().source_stars(spec)
    incident = holders(original)
    anchors = roles["anchors"]
    seam, = roles["seams"]
    ring, = roles["rings"]
    original_ring, = roles["ring_edges"]
    meetings = list(zip(original_ring, roles["additional_ring_edges"], strict=True))
    marks = {}
    for i, d in enumerate(anchors):
        offset = min(abs(i - seam), abs(i + 1 - seam))
        if offset in OFFSETS:
            marks[d] = {"index": i, "offset": offset, "side": "left" if i < seam else "right",
                        "holders": sorted(incident[d])}
    words, preparations = {}, {}
    for name, occupied in sources.loads(spec).items():
        growth._state(original, occupied)
        assert occupied.isdisjoint(anchors) and all(len(incident[d]) == 2 for d in occupied)
        active = tuple(k for k in ring if not occupied.isdisjoint(original[k]))
        representative, _ = preparations.setdefault(active, (name, occupied))
        words[name] = {"occupied": sorted(occupied), "weight": len(occupied), "activity": representative,
                       "ring_copies_loaded": [len(occupied.intersection(pair)) for pair in meetings],
                       "active_ring_positions": [ring.index(v) for v in active], "attachment_active": seam in active}
    assert len(words) == 64 and len(preparations) == 17
    assert Counter(x["weight"] for x in words.values()) == {0: 1, 2: 5, 4: 10, 5: 32, 6: 10, 8: 5, 10: 1}
    groups = {}
    for name, occupied in preparations.values():
        groups[name] = trace(original, occupied, anchors, marks)
    quiet = groups["w00"]
    for rep in groups:
        groups[rep]["comparison"] = compare(quiet, groups[rep], marks)

    # Check that the new scoring used the exact corresponding structural
    # prefixes, with the same physical weighting, as the all-law replay.
    seed = LAW_PANEL.read_bytes()
    preceding = json.loads(seed)["cases"]["J1x2"]
    table = preceding["tables"]["PV"]
    for name, word in words.items():
        assert word["occupied"] == preceding["physical_loads"][name]["occupied"]
        before_id = table["first_by_activity"][preceding["physical_loads"][name]["activity"]]["continuation"]
        earlier = preceding["continuations"][before_id]
        current = groups[word["activity"]]
        assert current["termination"] == earlier["termination"]
        assert current["frames"].keys() == earlier["frames"].keys()
        for age, row in current["frames"].items():
            assert all(row[k] == earlier["frames"][age][k] for k in ("knots", "distinctions"))
    return {"schema": 1, "law": "cold P / hot V", "fixture": "one-spare ring on the 17-knot path, doubled meetings",
            "maximum_layer": AGES["J1x2"], "caps": CAPS, "law_panel_sha256": sha256(seed).hexdigest(),
            "marks": marks, "meetings_in_ring_order": meetings, "physical_words": words,
            "by_activity": groups, "mark_root_dose_distribution": dose_summary(words, groups, marks)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    options = parser.parse_args()
    result = measure()
    options.out.parent.mkdir(parents=True, exist_ok=True)
    options.out.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    for mark, row in result["mark_root_dose_distribution"].items():
        print(mark, result["marks"][int(mark)]["offset"], row["by_attachment_activity"])


if __name__ == "__main__":
    main()
