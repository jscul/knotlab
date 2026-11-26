"""Press three literal readings of the proposed merge on the late starts."""
import argparse
from collections import Counter
import json
from pathlib import Path
import time

from regrow import grow
from settling import HERE, STUDY, READINGS, read_archive


def only_component(live, groups):
    """Whether join parent sets connect the entire incoming live roster."""
    if not live:
        return False
    names = {i: {i} for i in live}
    for g in groups:
        merged = set().union(*(names[p] for p in g))
        for p in merged:
            names[p] = merged
    return len(names[next(iter(live))]) == len(live)


def events(record):
    memberships = Counter(d for knot in record["stars"] for d in knot)
    live = {i for i, knot in enumerate(record["stars"]) if any(memberships[d] == 1 for d in knot)}
    live_start = live.copy()
    descent = [{i} for i in range(len(record["stars"]))]
    rounds = {"any join": [], "join has all live parents": [], "all live connected by joins": [],
              "sole birth is a join": [], "single incoming live knot": [],
              "birth descends from all live start knots": []}

    def observe(t, parents, fresh):
        nonlocal live, descent
        joins = [set(family) for family in parents if len(family) >= 2]
        assert all(family <= live for family in joins)
        if joins:
            rounds["any join"].append(t)
        if live in joins:
            rounds["join has all live parents"].append(t)
        if only_component(live, joins):
            rounds["all live connected by joins"].append(t)
        if len(parents) == 1 and joins:
            rounds["sole birth is a join"].append(t)
        if len(live) == 1:
            rounds["single incoming live knot"].append(t)
        descent = [set().union(*(descent[p] for p in family)) for family in parents]
        if live_start in descent:
            rounds["birth descends from all live start knots"].append(t)
        live = {i for i, amount in enumerate(fresh) if amount > 0}

    grow(record["stars"], record["knot law"], rounds=len(record["rows"]), cap=30000, observe=observe)
    return rounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    checked = json.loads((HERE / "settling.json").read_text())
    result = {}
    for path in sorted(STUDY.glob("grown_*.jsonl.gz")):
        key = path.name.removeprefix("grown_").split(".")[0]
        late = {}
        for i, _, reading, _, k, _ in checked[key]["late start-readings"]:
            late.setdefault(i, {})[reading] = k
        output = []
        started = time.monotonic()
        for x in read_archive(path):
            i = x["index"]
            if i not in late:
                continue
            e = events(x)
            output.append({"index in census": i, "last saved round": len(x["rows"]), "K": late[i], "rounds": e})
            if args.pilot:
                break
        metrics = {}
        for event in output[0]["rounds"]:
            occurrences = [row for row in output if row["rounds"][event]]
            metrics[event] = {
                "starts with event": len(occurrences),
                "event in final saved round": sum(r["last saved round"] == r["rounds"][event][-1] for r in occurrences),
            }
            for which, j in [("first", 0), ("last", -1)]:
                for reading in READINGS:
                    gaps = Counter(r["K"][reading] - r["rounds"][event][j] for r in occurrences)
                    metrics[event][f"K minus {which} event, {reading}"] = dict(sorted(gaps.items()))
        result[key] = {"late starts": len(output), "counts": metrics, "records": output,
                       "elapsed seconds": round(time.monotonic() - started, 3)}
        assert args.pilot or len(output) == len(late)
    result["conventions"] = {
        "event round": "Round making the births; parent identities refer to the incoming live roster.",
        "all live connected by joins": "On the incoming live knots, take the transitive closure of sharing a join as parents. A single live knot is connected.",
        "join has all live parents": "A single join names every incoming live knot. Other births may occur in that round.",
        "sole birth is a join": "Exactly one birth, and it has at least two parents.",
        "birth descends from all live start knots": "Take the union of the known start ancestors of each parent at each birth.",
        "last": "Last event through the final saved round. An event there is censored on the right.",
    }
    (HERE / ("meetings_pilot.json" if args.pilot else "meetings.json")).write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    main()
