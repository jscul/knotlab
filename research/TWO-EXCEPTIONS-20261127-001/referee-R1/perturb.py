"""Vary the number of loose distinctions on one or two knots of a supplied witness."""
import argparse
import json
from collections import Counter
from itertools import combinations, product

from rebuild import HERE, first_failure


def variants(stars):
    held = Counter(d for star in stars for d in star)
    shared = [[d for d in star if held[d] == 2] for star in stars]
    original = [len(s) - len(a) for s, a in zip(stars, shared)]
    live = [i for i, n in enumerate(original) if n]
    for size in (1, 2):
        for positions in combinations(live, size):
            for deltas in product((-1, 1), repeat=size):
                opening = original.copy()
                for k, delta in zip(positions, deltas):
                    opening[k] += delta
                if any(len(a) + n < 3 for a, n in zip(shared, opening)) or sum(opening) < 2:
                    continue
                nxt = max(held) + 1
                edited = []
                for a, n in zip(shared, opening):
                    edited.append(a + list(range(nxt, nxt+n)))
                    nxt += n
                yield list(zip(positions, deltas)), edited


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    records = [json.loads(l) for l in (HERE.parent / "referee_witnesses.jsonl").read_text().splitlines()]
    responses = []
    for line in (1, 2, 3, 7):
        for edits, stars in variants(records[line-1]["stars"]):
            if args.limit and len(responses) >= args.limit:
                break
            try:
                r = first_failure(stars, horizon=15, width_cap=180)
            except ValueError as e:
                if str(e) != "shortage":
                    raise
                r = dict(status="shortage")
            result = dict(line=line, edits=edits, status=r["status"])
            if r["status"] == "failure":
                result.update(child_round=r["child_round"], twins=r["twins"], splits=r["splits"],
                              other=len(r["unexplained_gains"])+len(r["unexplained_losses"]))
            responses.append(result)
    print(Counter(r["status"] for r in responses))
    print("Other", [r for r in responses if r.get("other")])
    if args.save:
        (HERE / "perturbations.json").write_text(json.dumps(responses, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
