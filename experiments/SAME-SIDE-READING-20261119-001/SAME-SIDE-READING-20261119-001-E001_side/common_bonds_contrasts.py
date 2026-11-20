"""Read common-bond factorial contrasts and physical-dose frequencies."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
INFINITY = "infinity"


def contrast(q, a, b, both):
    if any(r[0] == INFINITY for r in (q, a, b, both)):
        return "infinite reading"
    if any(r[1] == INFINITY for r in (q, a, b, both)):
        return "unbounded interaction"
    return [both[0] - a[1] - b[1] + q[0], both[1] - a[0] - b[0] + q[1]]


def two_rings(case):
    traces = [case["activity_traces"][case["assignments"][str(code)]["activity"]]["frames"]
              for code in range(4)]
    result = {}
    for age in sorted(set.intersection(*(set(trace) for trace in traces)), key=int):
        states = Counter()
        values = []
        for i, readings in enumerate(zip(*(t[age]["readings"] for t in traces), strict=True)):
            value = contrast(*readings)
            values.append(value)
            if value == [0, 0]:
                state = "zero"
            elif isinstance(value, str):
                state = value
            elif value[0] > 0 or value[1] < 0:
                state = "nonzero"
            else:
                state = "bounded"
            states[state] += 1
        result[age] = {"counts_including_pair_vectors": dict(states), "interaction": values}
    return result


def by_dose(case):
    words = defaultdict(list)
    for record in case["assignments"].values():
        words[len(record["occupied"])].append(case["activity_traces"][record["activity"]]["frames"])
    ages = sorted(set.intersection(*(set(t) for ts in words.values() for t in ts)), key=int)
    result = {}
    for age in ages:
        records = {}
        for dose, traces in sorted(words.items()):
            rows = []
            for readings in zip(*(t[age]["readings"] for t in traces), strict=True):
                exact = Counter(r[0] for r in readings if r[0] == r[1])
                known = [value for value in exact if value != INFINITY]
                numeric = sum(exact[value] for value in known)
                rows.append({"sizes": dict(exact), "bounded": len(traces) - sum(exact.values()),
                             "finite_min": min(known, default=None), "finite_max": max(known, default=None),
                             "finite_sum": sum(v * exact[v] for v in known), "finite_words": numeric})
            result_for_dose = {"total_physical_assignments": len(traces), "values": rows}
            records[dose] = result_for_dose
        result[age] = records
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=OUTPUT / "common_bonds_contrasts.json")
    args = parser.parse_args()
    data = {}
    for path in args.inputs:
        raw = path.read_bytes()
        table = json.loads(raw)
        item = {}
        for name, case in table["cases"].items():
            if len(case["assignments"]) == 4:
                item[name] = {"factorial": two_rings(case)}
            if len(case["assignments"]) == 64:
                item[name] = {"dose_frequencies": by_dose(case)}
        data[path.name] = {"sha256": sha256(raw).hexdigest(), "cases": item}
    args.out.write_text(json.dumps({"schema": 1, "unit": "physical bond size",
                                   "row_order": "query_indices of the named input",
                                   "profiles": data}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
