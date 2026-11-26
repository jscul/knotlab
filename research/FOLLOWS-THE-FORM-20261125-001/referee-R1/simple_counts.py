"""Measure which simpler readings distinguish the registered held-out classes."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
TICKET = HERE.parent.with_name(HERE.parent.name + "A")
DATA = next((HERE.parents[2] / "artifacts" / TICKET.name).glob("*E001*"))


def intern(store, record):
    return store.setdefault(record, len(store))


def descriptors(seed):
    knots = seed["knots"]
    held = knots[seed["at"]]
    holders = Counter(d for knot in knots for d in knot)
    loose = sum(holders[d] == 1 for d in held)
    partners = sum(1 for i, k in enumerate(knots) if i != seed["at"] and set(k) & set(held))
    return (len(held) + 1, loose, partners), len(knots), sum(n == 1 for n in holders.values())


def stats(values, classes):
    same = apart = 0
    for i, j in combinations(range(len(classes)), 2):
        if values[i] == values[j]:
            same += 1
            apart += classes[i] != classes[j]
    return Counter(studies=1, decides=int(apart == 0), pairs_sharing=same, of_those_apart=apart)


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true", help="one first seed, ration and treatment, without a take")
    args = p.parse_args()
    start = perf_counter()
    seeds = json.loads((TICKET / "seeds.json").read_text())
    static = {s["name"]: descriptors(s) for s in seeds["second"]["fresh"]}
    groups = defaultdict(dict)
    ms = {}
    for path in sorted(DATA.glob("runs_R2_*.jsonl.gz")):
        with gzip.open(path, "rt") as stream:
            for row in map(json.loads, stream):
                key = tuple(row[k] for k in ("first", "ration", "treatment", "take"))
                if args.pilot and key != ("K", "FLOOR1", "CANCEL-RETIRE", "none"):
                    continue
                g = groups[key]
                assert row["second"] not in g
                birth = [intern(ms, tuple(sorted(tuple(entry) for entry in items))) for items in row["make"]]
                wide = intern(ms, tuple(sorted(tuple(entry) for entry in row["wider"][0])))
                g[row["second"]] = (birth, wide, row["n_own"])
    output = defaultdict(Counter)
    by_take = defaultdict(lambda: defaultdict(Counter))
    for key, g in groups.items():
        assert len(g) == 61 and set(g) - {None} == static.keys()
        r = min(len(item[0]) for item in g.values())
        simple = defaultdict(list)
        classes = []
        for name, (own, wider1, n) in g.items():
            if name is None:
                continue
            held, size, loose = static[name]
            classes.append(own[:r])
            simple["seed size"].append(size)
            simple["seed size and total loose distinctions"].append((size, loose))
            simple["held knot, seed size and total loose distinctions"].append((held, size, loose))
            simple["round 1 own birth count"].append(n[0])
            simple["round 1 own entries"].append(own[0])
            simple["round 1 wider entries"].append(wider1)
            simple["own birth counts through common round"].append(n[:r])
        for name, values in simple.items():
            counts = stats(values, classes)
            output[name].update(counts)
            by_take[key[3]][name].update(counts)
    assert len(groups) == (1 if args.pilot else 90)
    if not args.pilot:
        (HERE / "simple_counts.json").write_text(json.dumps({"all": output, "by_take": by_take}, indent=2) + "\n")
    print(len(groups), "studies;", round(perf_counter()-start, 3), "s")


if __name__ == "__main__":
    main()
