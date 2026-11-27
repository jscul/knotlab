"""Try small changes of the ten starting knots while keeping their four loose inputs."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
from time import perf_counter

from witness_states import BORN, CARRIERS, CHOICES, START, advance, gather, meet, same_part


def inputs():
    n = 1 << 19
    columns = []
    for i in range(19):
        width = 1 << i
        run = ((1 << width) - 1) << width
        while width < n // 2:
            width *= 2
            run |= run << width
        columns.append(run)
    return (1 << n) - 1, columns


def normalized(knots):
    return tuple(sorted(tuple(sorted(k)) for k in knots))


def exchanges(source):
    for i, j in combinations(range(len(source)), 2):
        a, b = set(source[i]), set(source[j])
        for x, y in product(sorted(a - b), sorted(b - a)):
            if x <= 3 or y <= 3:
                continue
            changed = list(source)
            changed[i] = tuple(sorted(a - {x} | {y}))
            changed[j] = tuple(sorted(b - {y} | {x}))
            yield normalized(changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1000000)
    parser.add_argument("--depth", type=int, choices=(1, 2), default=1)
    parser.add_argument("--stop-exact", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    began = perf_counter()
    full, bits = inputs()
    law_cache = {}

    def law(k):
        key = tuple(sorted(k))
        if key not in law_cache:
            a, b, c = (bits[x] for x in key)
            law_cache[key] = (a ^ b) | (a ^ c)
        return law_cache[key]

    agreements = [full ^ law(c) for c in CARRIERS]
    forbidden = [agreements[i] & agreements[j] & agreements[k] for i, j, k in CHOICES]
    words = {}
    for six in range(64):
        if any(gather(six, pick) == 7 for pick in CHOICES):
            continue
        allowed = full
        for j, yes in enumerate(agreements):
            allowed &= yes if (six >> j) & 1 else full ^ yes
        words[six] = allowed
    start = normalized(START)
    stages = {start}
    known = set(stages)
    outcomes = []
    complete = True
    for depth in range(1, args.depth + 1):
        front = set()
        totals = Counter()
        cases = Counter()
        example = {}
        for source in sorted(stages):
            for trial in exchanges(source):
                if trial in known:
                    continue
                known.add(trial)
                if depth < args.depth:
                    front.add(trial)
                totals["distinct_exchanges"] += 1
                allowed = law(BORN[0]) & law(BORN[1])
                for k in trial:
                    allowed &= law(k)
                if all(not (allowed & bad) for bad in forbidden):
                    totals["all_eight_exclusions"] += 1
                    seen = sum(bool(allowed & w) for w in words.values())
                    if same_part(meet(trial)):
                        growth = advance(trial)
                        if growth.status == "funded" and normalized(growth.supports) == normalized((*trial, *BORN)):
                            cases[seen] += 1
                            if str(seen) not in example:
                                example[str(seen)] = trial
                            if args.stop_exact and seen == 37:
                                complete = False
                                break
                if totals["distinct_exchanges"] >= args.limit:
                    complete = False
                    break
            if not complete:
                break
        outcomes.append({"depth": depth, **totals, "connected_matches_reached_by_the_two_births_by_six_words": cases,
                         "first_per_six_word_count": example, "exhausted_depth": complete})
        stages = front
        if not complete:
            break
    result = {"search": "Swap two distinct numbered shared distinctions between two start laws, retaining all "
                        "loose inputs and the six candidate carriers. Deduplicate by sorted literal supports. "
                        "Enumerate increasing exchange count, then preceding support tuple, law indices and labels.",
              "results": outcomes, "seconds": round(perf_counter() - began, 6)}
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: v for k, v in r.items() if k != "first_per_six_word_count"} for r in outcomes]))
    print("seconds", result["seconds"])


if __name__ == "__main__":
    main()
