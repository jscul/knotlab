"""Recount the frozen bound from distinction holdings and saved round readings."""
import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice
import json
from math import comb
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SMALL = STUDY.parent / "LOOK-ALIKE-20261126-001" / "phase1_grown.jsonl.gz"
READINGS = ("sig0", "sig1")


def read_archive(path):
    with gzip.open(path, "rt") as stream:
        yield from map(json.loads, stream)


def name(value):
    return tuple(map(name, value)) if isinstance(value, list) else value


def view(rows, reading):
    result = []
    for row in rows:
        counts = {name(label): n for label, n in row[reading]}
        assert len(counts) == len(row[reading]) and sum(counts.values()) == row["n"]
        assert all(n > 0 for n in counts.values())
        result.append(counts)
    return result


def block_size(record):
    holdings = defaultdict(list)
    for knot, distinctions in enumerate(record["stars"]):
        for d in distinctions:
            holdings[d].append(knot)
    live = {knots[0] for knots in holdings.values() if len(knots) == 1}
    neighbours = defaultdict(set)
    for knots in holdings.values():
        assert 1 <= len(knots) <= 2
        if len(knots) == 2:
            a, b = knots
            if a in live:
                neighbours[b].add(a)
            if b in live:
                neighbours[a].add(b)
    block = max(map(len, neighbours.values()), default=0)
    fresh = max((label[2] for label, _ in record["rows"][0]["sig0"]), default=0) if record["rows"] else 0
    return block, fresh


def dimension(counts):
    if len(counts) < 10:
        return None
    tail = counts[-8:]
    for d in range(1, 5):
        if len(set(tail)) == 1 and tail[0] > 0:
            return d
        tail = [b - a for a, b in zip(tail, tail[1:])]
    return None


def earliest(readings, d, floor):
    # The Dth backward difference at t is the error in extrapolating from
    # the previous D observations. All errors after the cut must vanish.
    n = len(readings)
    last = max(d, floor)
    kinds = set().union(*readings)
    coefficients = [(-1)**j * comb(d, j) for j in range(d + 1)]
    for label in kinds:
        values = [row.get(label, 0) for row in readings]
        for t in range(n - 1, max(last - 1, d - 1), -1):
            if sum(c * values[t - j] for j, c in enumerate(coefficients)):
                last = max(last, t + 1)
                break
    return last if last <= n - 2 else None


def recount(path, limit, comparison):
    stream = read_archive(path)
    if limit:
        stream = islice(stream, limit)
    cnt = Counter()
    kinds, block_counts, horizon, tally = Counter(), Counter(), Counter(), Counter()
    combinations, examples, miss_rows = Counter(), {}, []
    first_round_groups = defaultdict(list)
    for x in stream:
        cnt["starts"] += 1
        b, f = block_size(x)
        m = max(b, f)
        if "M" in x:
            assert m == x["M"]
            cnt["stored M values matched"] += 1
        totals = [row["n"] for row in x["rows"]]
        d = None if x["end"].startswith(("stalls", "closes")) else dimension(totals)
        assert (None if not x["kind"].startswith("dim") else int(x["kind"].split()[1])) == d
        if d is None:
            continue
        kinds[d] += 1
        block_counts[m] += 1
        horizon[len(totals)] += 1
        kt = earliest([{0: total} for total in totals], d, 3)
        ks = []
        for reading, slack in zip(READINGS, (5, 7)):
            seen = view(x["rows"], reading)
            k = earliest(seen, d, 3)
            k0 = earliest(seen, d, 1)
            cut = m + slack
            passed = k is not None and k <= cut
            tally[reading + (" / within the bound" if passed else " / past the bound" if k else " / not settled in the rounds read")] += 1
            if k != k0:
                cnt[reading + " / floors give different K"] += 1
            if passed != (k0 is not None and k0 <= cut):
                cnt[reading + " / floors change verdict"] += 1
            if kt and kt > cut:
                cnt[reading + " / total alone exceeds cut"] += 1
            if not passed and kt and kt <= cut:
                cnt[reading + " / misses with total already predictable"] += 1
            if dimension(totals[:cut]) != d:
                cnt[reading + " / final dimension unavailable or different at cut"] += 1
                if not passed:
                    cnt[reading + " / late and final dimension unavailable or different at cut"] += 1
            if k is not None:
                combinations[(m, reading, k)] += 1
                examples.setdefault((m, reading, k), {"knots": len(x["stars"]), "index": x["index"], "stars": x["stars"], "D": d, "neighbours": b, "round 1 fresh maximum": f, "totals": totals})
            if not passed:
                miss_rows.append([x["index"], f"dim {d}", reading, m, k, len(totals)])
            first_round_key = (len(x["stars"]), d, m, reading, tuple(sorted(seen[0].items())))
            first_round_groups[first_round_key].append((passed, x["index"], k))
            ks.append(k)
        if all(k is not None for k in ks) and ((ks[0] > m + 5) != (ks[1] > m + 7)):
            cnt["different starts missed under the two readings"] += 1
    equality = {}
    for reading, slack in zip(READINGS, (5, 7)):
        triples = [(m, k, n) for (m, r, k), n in combinations.items() if r == reading]
        if triples:
            largest = max(k - m for m, k, n in triples)
            equality[reading] = {"max K minus M": largest,
                                 "at the frozen bound": sum(n for m, k, n in triples if k - m == slack),
                                 "at the largest difference": sum(n for m, k, n in triples if k - m == largest)}
    common = sorted({m for m, r, k in combinations if r == "sig0" and k > m + 5})
    same_m = []
    for m in common:
        for d in sorted(kinds):
            cells = sorted(k for (size, r, k), ex in examples.items() if size == m and r == "sig0" and ex["D"] == d)
            if cells and cells[0] <= m + 5 < cells[-1]:
                same_m = [dict(K=k, M=m, **examples[m, "sig0", k]) for k in (cells[0], cells[-1])]
                break
        if same_m:
            break
    if comparison and not limit:
        saved = json.loads(comparison.read_text())
        assert saved["bound misses"] == miss_rows and saved["bound"] == dict(tally)
        assert saved["starts of a dimension"] == sum(kinds.values())
        assert saved["M"] == {str(m): n for m, n in block_counts.items()}
    first_round = {r: {"matching pairs": 0, "opposite verdicts": 0} for r in READINGS}
    for (size, d, m, reading, first), group in first_round_groups.items():
        scores = first_round[reading]
        scores["matching pairs"] += comb(len(group), 2)
        passes = [row for row in group if row[0]]
        late = [row for row in group if not row[0]]
        scores["opposite verdicts"] += len(passes) * len(late)
        if passes and late and "witness" not in scores:
            scores["witness"] = {"knots": size, "D": d, "M": m, "first round": first,
                                 "passing index and K": passes[0][1:], "late index and K": late[0][1:]}
    return {"checks": dict(cnt), "dimension counts": dict(kinds), "M counts among dimension starts": dict(block_counts),
            "last observed round among dimension starts": dict(horizon),
            "settling counts": dict(tally), "offsets": equality, "late start-readings": miss_rows,
            "M reading K counts": [[m, r, k, n] for (m, r, k), n in sorted(combinations.items())],
            "size, D, M and full first-round reading equal": first_round,
            "same M and D, differing K without parents": same_m}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    answer = {}
    for path in [SMALL, *sorted(STUDY.glob("grown_*.jsonl.gz"))]:
        key = path.name.removeprefix("grown_").split(".")[0]
        before = time.monotonic()
        test = None if path == SMALL else STUDY / f"test_{key}.json"
        answer[key] = recount(path, 64 if args.pilot else None, test)
        answer[key]["elapsed seconds"] = round(time.monotonic() - before, 3)
    output = "settling_pilot.json" if args.pilot else "settling.json"
    (HERE / output).write_text(json.dumps(answer, indent=1) + "\n")
    print({key: (data["settling counts"], data["elapsed seconds"]) for key, data in answer.items()})


if __name__ == "__main__":
    main()
