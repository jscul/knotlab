"""Direct finite replay of the selected shared births and a read of all saved results."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations, product
import json
from math import prod
from pathlib import Path
from random import Random
import resource
from time import process_time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PREVIOUS = STUDY.parent / "FORBID-EDITS-20261126-001"
SEED = 26112641
WEIGHTS = ("U", "S")


def read_rows(path):
    with gzip.open(path, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def key(row):
    return row["start"], tuple(map(tuple, row["readers"])), row["law"], row["arm"]


def holder_lists(start):
    count, shared, loose = start
    holders = [[] for _ in range(count)]
    next_id = 0
    for a, b, size in shared:
        for h in (a, b):
            holders[h].extend(range(next_id, next_id + size))
        next_id += size
    for row, size in zip(holders, loose, strict=True):
        row.extend(range(next_id, next_id + size))
        next_id += size
    return holders


def groups(neighbors):
    pairs = {pair for pair in combinations(neighbors, 2)
             if neighbors[pair[0]] & neighbors[pair[1]]}
    accepted = []
    for size in range(len(neighbors), 2, -1):
        for members in combinations(neighbors, size):
            if any(set(members).issubset(known) for known in accepted):
                continue
            if all(pair in pairs for pair in combinations(members, 2)):
                if not set.intersection(*(neighbors[h] for h in members)):
                    accepted.append(members)
    covered = {pair for group in accepted for pair in combinations(group, 2)}
    return sorted(accepted) + sorted(pairs - covered)


def passes(count, size, law):
    return count % 2 == 0 if law == "parity" else 0 < count < size


def mask(names):
    return sum(1 << name for name in names)


def satisfies(word, rule, law):
    return passes((word & rule).bit_count(), rule.bit_count(), law)


def allowed(rows, names, law):
    # Enumerate the active distinctions only. An optional edit can leave a gap in their IDs.
    constraints = set(map(mask, rows))
    full = mask(names)
    word = full
    while True:
        if all(satisfies(word, rule, law) for rule in constraints):
            yield word
        if not word:
            break
        word = (word - 1) & full


def births_for(edited, edited_states, law):
    uses = Counter(d for row in edited for d in row)
    loose = [[d for d in row if uses[d] == 1] for row in edited]
    neighbors = {h: {j for j, other in enumerate(edited) if h != j and set(row) & set(other)}
                 for h, row in enumerate(edited) if loose[h]}
    if not neighbors:
        return "closed", []
    parents = groups(neighbors)
    needs = Counter(h for family in parents for h in family)
    if any(needs[h] > len(loose[h]) for h in needs):
        return "stalled", []
    parents.extend((h,) for h, ds in enumerate(loose) for _ in range(len(ds) - needs[h]))
    following = groups({i: set(family) for i, family in enumerate(parents)})
    demand = Counter(i for family in following for i in family)
    births = []
    for i, family in enumerate(parents):
        inputs = tuple(sorted(loose[h].pop(0) for h in family))
        inputs_mask = mask(inputs)
        minimum = max(0, 3 - len(inputs))
        ordinary = max(demand[i], 1, minimum)
        if ordinary != demand[i] and all(satisfies(word, inputs_mask, law) for word in edited_states):
            ordinary = demand[i]
        fresh = min(ordinary, max(minimum, ordinary - 1))
        births.append((family, inputs, fresh))
    return "funded", births


def setting(base, readers, st, law):
    uses = Counter(d for row in base for d in row)
    first = max(uses) + 1
    edited = [row.copy() for row in base]
    marks = [next(d for d in base[h] if uses[d] == 1) for h in readers]
    for i, (h, add) in enumerate(zip(readers, st, strict=True)):
        if add:
            edited[h].append(first + i)
    names = sorted({d for row in edited for d in row})
    edited_states = list(allowed(edited, names, law))
    status, births = births_for(edited, edited_states, law)
    original = list(map(mask, base))
    local = [[b for b in births if h in b[0]] for h in readers]
    labels = [tuple(sorted(bs)) for bs in local]
    # This further reading retains the near holder's input and two counts, with no outside name.
    short = [tuple(sorted((next(d for d in ds if d in edited[h]), len(fam), fresh)
                          for fam, ds, fresh in bs)) for h, bs in zip(readers, local, strict=True)]
    completion = []
    for _, ds, fresh in births:
        size = len(ds)
        counts = [sum(passes(old_ones + word.bit_count(), size + fresh, law)
                      for word in range(1 << fresh)) for old_ones in range(size + 1)]
        completion.append((mask(ds), counts))
    hist = {w: [0] * (1 << len(st)) for w in WEIGHTS}
    kept = 0
    for word in edited_states:
        if not all(satisfies(word, rule, law) for rule in original):
            continue
        kept += 1
        # This is an exact sum over allowed complete assignments: each fresh
        # distinction occurs in one birth, so choices across births combine freely.
        count = prod(table[(word & bits).bit_count()] for bits, table in completion)
        if count:
            read = sum(((word >> d) & 1) << i for i, d in enumerate(marks))
            hist["U"][read] += count
            hist["S"][read] += 1
    assert all(sum(v) > 0 for v in hist.values())
    return status, labels, short, hist, kept


def distribution_summary(tables, n, w):
    single = [[] for _ in range(n)]
    parity_means = {}
    for st, (_, _, _, hist, _) in tables.items():
        counts = hist[w]
        for i in range(n):
            ones = sum(v for r, v in enumerate(counts) if r >> i & 1)
            single[i].append(Fraction(ones, sum(counts)))
        signed = sum((-1) ** r.bit_count() * v for r, v in enumerate(counts))
        parity_means[st] = Fraction(signed, sum(counts))
    if n == 2:
        score = max(sum(sign * mean for sign, mean in zip(signs, parity_means.values(), strict=True))
                    for signs in product((-1, 1), repeat=4) if prod(signs) == -1)
    else:
        games = [st for st in tables if sum(st) % 2 == 0]
        score = max(sum((1 + parity_means[st] * (-1) ** ((sum(st) // 2) +
                        sum(flips[2*i + s] for i, s in enumerate(st)))) / 2 for st in games) / 4
                    for flips in product(range(2), repeat=6))
    return {"score": str(score), "marked P(1) by reader": [sorted(set(map(str, p))) for p in single]}


def patterns(tables, index, n):
    # Equal entries mean exactly equal birth descriptions at the reader's fixed setting.
    result = []
    for reader in range(n):
        one_reader = []
        for own in (0, 1):
            labels = {}
            pattern = {}
            for st, table in tables.items():
                if st[reader] == own:
                    desc = table[index][reader]
                    far = "".join(str(b) for i, b in enumerate(st) if i != reader)
                    pattern[far] = labels.setdefault(desc, len(labels))
            one_reader.append(pattern)
        result.append(one_reader)
    return result


def replay(identity, base, archived):
    idx, groups_reading, law, grant = identity
    assert grant == "one_fewer"
    readers = [h for (h,) in groups_reading]
    n = len(readers)
    tables = {st: setting(base, readers, st, law) for st in product(range(2), repeat=n)}
    labelled = patterns(tables, 1, n)
    counted = patterns(tables, 2, n)
    scored = {w: distribution_summary(tables, n, w) for w in WEIGHTS}
    settings = {"".join(map(str, st)): {"status": t[0], "edited": t[4],
                "grown": sum(t[3]["U"]), "surviving": sum(t[3]["S"]), "read counts": t[3]}
                for st, t in tables.items()}
    assert {s: t["status"] for s, t in settings.items()} == archived["status"]
    for w in WEIGHTS:
        for i, own in enumerate(labelled):
            assert any(len(set(p.values())) > 1 for p in own), "equal shapes need a value-distribution comparison"
            assert archived[w]["record moves"][i] == {"largest total variation": "1",
                                                       "in the shape of its births": True}
        assert scored[w]["score"] == archived[w]["score"]
        assert archived[w]["single unchanged"]
        assert all(len(p) == 1 for p in scored[w]["marked P(1) by reader"])
    return {"start": idx, "holders": readers, "law": law, "settings": settings, "scores": scored,
            "birth patterns": labelled, "birth patterns without outside names": counted,
            "births by reader": {"".join(map(str, st)): t[1] for st, t in tables.items()}}


def read_archive():
    contacts, addressed = {}, []
    for r in read_rows(STUDY / "contact_runs.jsonl.gz"):
        if r["source"] == "census":
            assert key(r) not in contacts
            contacts[key(r)] = r
        else:
            assert r["source"] == "extension"
            addressed.append(r)
    prior = {}
    for path in sorted(PREVIOUS.glob("shared_*.jsonl.gz")):
        for r in read_rows(path):
            if r["kind"] == "shared birth, read" and "U" in r and all(r["forbidding changes with own setting"]):
                assert key(r) not in prior
                prior[key(r)] = r
    assert prior.keys() == contacts.keys()
    for identity, r in contacts.items():
        for w in WEIGHTS:
            assert all(m == {"largest total variation": "1", "in the shape of its births": True}
                       for m in r[w]["record moves"])
            assert r[w]["single unchanged"]
            assert r[w]["score"] == prior[identity][w]["scores"]["fixed old value"]
    return contacts, prior, addressed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--remainder", action="store_true", help="check the rows outside the seeded and maximum-score replay")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = process_time()
    contacts, prior, addressed = read_archive()
    by_kind = defaultdict(list)
    for identity in sorted(contacts):
        by_kind[(len(identity[1]), identity[2])].append(identity)
    random = Random(SEED)
    requested = {(2, "nae"): 12, (2, "parity"): 8, (3, "nae"): 1}
    random_sample, records = [], []
    archive_summary = {}
    extra = set()
    for group, keys in sorted(by_kind.items()):
        random_sample.extend(random.sample(keys, requested[group]))
        maxima = {}
        for w in WEIGHTS:
            peak = max(Fraction(contacts[k][w]["score"]) for k in keys)
            maxima[w] = str(peak)
            if group == (2, "nae"):
                extra.add(next(k for k in keys if Fraction(contacts[k][w]["score"]) == peak))
        archive_summary[str(group)] = {"rows": len(keys), "maxima": maxima}
    selected = random_sample + sorted(extra - set(random_sample))
    if args.remainder:
        selected = sorted(contacts.keys() - set(selected))
    if args.pilot:
        selected = [next(k for k in selected if (len(k[1]), k[2]) == group) for group in sorted(
            {(len(k[1]), k[2]) for k in selected})]
    starts = json.loads((PREVIOUS / "starts.json").read_text())
    summaries = Counter()
    for identity in selected:
        base = holder_lists(starts[identity[0]])
        assert base == prior[identity]["supports"]
        result = replay(identity, base, contacts[identity])
        no_names = result["birth patterns without outside names"]
        all_visible = all(any(len(set(p.values())) > 1 for p in own) for own in no_names)
        all_fair = all(p == ["1/2"] for s in result["scores"].values() for p in s["marked P(1) by reader"])
        summaries[(len(identity[1]), identity[2], all_visible, all_fair)] += 1
        if not args.remainder:
            result["selection"] = "seeded" if identity in random_sample else "archive maximum"
            records.append(result)
    other = Counter()
    for row in addressed:
        for w in WEIGHTS:
            for i, move in enumerate(row[w]["record moves"]):
                kind = "shape" if move["in the shape of its births"] else (
                    "values" if Fraction(move["largest total variation"]) else "unchanged")
                other[(i, kind)] += 1
    output = {"seed": SEED, "pilot": args.pilot, "remainder": args.remainder, "archive": archive_summary,
              "distinct shared holder placements": len({k[:2] for k in contacts}),
              "addressed archive record counts": {str(k): v for k, v in sorted(other.items())},
              "rebuilt (reader count, law, all visible without outside names, all marks fair)":
                  {str(k): v for k, v in sorted(summaries.items())},
              "records": records, "cpu seconds": round(process_time() - started, 3),
              "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.output:
        args.output.write_text(json.dumps(output, indent=1) + "\n")
    print({k: v for k, v in output.items() if k != "records"}, "rebuilt", len(selected))


if __name__ == "__main__":
    main()
