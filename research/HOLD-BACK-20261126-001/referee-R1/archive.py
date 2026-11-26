"""Count observations and their endpoints directly from the saved pair records."""
import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent


def records(file_name):
    with gzip.open(file_name, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def summarize(path, prefix):
    data = records(path)
    if prefix is not None:
        data = islice(data, prefix)
    groups = defaultdict(list)
    jobs = []
    seen = set()
    for row in data:
        if "law" not in row:
            jobs.append(row)
            continue
        law = " ".join(str(x) for x in row["law"] if x is not None)
        key = (row["A"], row["B"], law)
        assert key not in seen, key
        seen.add(key)
        groups[law].append(row)

    answer = {}
    for law, rows in groups.items():
        counts = Counter()
        ends, final, common, link3 = (Counter() for _ in range(4))
        first_at, changed_at, heard_by_change = (Counter() for _ in range(3))
        still_linked = []
        hearings = Counter()
        seen_pairs = set()
        for row in rows:
            n = row["rounds"]
            ends[row["ended"]] += 1
            final[n] += 1
            assert n == len(row["made short"]) == len(row["linked"])
            counts["rows"] += 1
            counts["with short made member"] += any(row["made short"])
            flags = row["linked"]
            value = "absent" if n < 3 else {None: "no own member on one or both sides",
                                             False: "both present and separate",
                                             True: "linked"}[flags[2]]
            link3[value] += 1
            if n >= 3 and flags[2] is True:
                still_linked.append([row["A"], row["B"], flags, row["ended"]])
            counts["linked after round 3 or later"] += any(x is True for x in flags[2:])
            if not row["changes"]:
                counts["rows with no changes"] += 1
            for c in row["changes"]:
                t, end, heard = c["t0"], c["rounds"], c["heard"]
                assert t < end <= n
                common[end] += 1
                changed_at[t] += 1
                counts["linked additions"] += c["linked"]
                if end >= 7:
                    counts["comparisons reaching late rounds"] += 1
                    counts["still awaiting first hearing entering round 7"] += heard is None or heard >= 7
                if heard is None:
                    continue
                assert t < heard <= end
                seen_pairs.add((row["A"], row["B"]))
                first_at[heard] += 1
                heard_by_change[t] += 1
                hearings[(t, heard, c["sharings"])] += 1
                if "births with" in c:
                    assert len(c["births with"]) >= end
                    both_grow = any(row["births"][heard:]) and any(c["births with"][heard:])
                    counts["heard and both grow later"] += both_grow
        counts["pairs hearing"] = len(seen_pairs)
        counts["additions"] = sum(common.values())
        counts["first hearings"] = sum(first_at.values())
        answer[law] = dict(counts=counts, stops=ends, unchanged_rounds=final,
                           common_rounds=common, link_after_3=link3,
                           additions_by_round=changed_at, first_hearings_by_round=first_at,
                           heard_by_addition_round=heard_by_change,
                           hearings_by_addition_hearing_sharings=[[*key, val] for key, val in sorted(hearings.items())])
        if law == "HOLD INHERIT":
            answer[law]["linked_exceptions"] = still_linked
    keys = {(a, b) for a, b, law in seen}
    return dict(laws=answer, interrupted_jobs=jobs, distinct_receivers=len({a for a, _ in keys}),
                distinct_senders=len({b for _, b in keys}), distinct_pairs=len(keys))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("part", choices=["B", "A"])
    p.add_argument("--prefix", type=int)
    args = p.parse_args()
    names = ["hold", "linked"] if args.part == "B" else ["takes"]
    print(json.dumps({name: summarize(STUDY / (name + "_runs.jsonl.gz"), args.prefix)
                      for name in names}, indent=2))
