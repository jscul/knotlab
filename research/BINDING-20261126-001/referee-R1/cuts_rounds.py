"""Compare both fresh-count cuts with ordinary growth on old and larger starts."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import resource
from random import Random
from time import perf_counter

from cuts_reader import Incidence, inspect
from replay_growth import ARMS, demand, grow, heldout, input_rows, start_items


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
SEED = 61261729
SIZES = (9, 12, 16, 20)
READERS = ("all listed supports", "only supports passing K1–K3")


def larger_starts(size, count):
    """A ring with uniformly added single shared distinctions and funded loose places."""
    rng = Random(SEED + size)
    ring = {tuple(sorted((i, (i + 1) % size))) for i in range(size)}
    possible = sorted(set(combinations(range(size), 2)) - ring)
    for _ in range(count):
        pairs = sorted(ring | set(rng.sample(possible, size // 2)))
        neighbors = [set() for _ in range(size)]
        for first, second in pairs:
            neighbors[first].add(second)
            neighbors[second].add(first)
        live = {i for i, others in enumerate(neighbors) if len(others) < 3 or rng.randrange(3) != 0}
        needed = Counter(k for group in demand([others & live for others in neighbors]) for k in group)
        loose = [max(1, needed[i], 3 - len(others)) + int(rng.randrange(4) == 0) if i in live else 0
                 for i, others in enumerate(neighbors)]
        yield input_rows([(a, b, 1) for a, b in pairs], loose)


def groups(suite, count):
    if suite == "archive":
        buckets = defaultdict(list)
        path = RESEARCH / "FORBID-EDITS-20261126-001" / "starts.json"
        for i, (n, meetings, loose) in enumerate(json.loads(path.read_text())):
            buckets[n].append((f"census {i}", input_rows(meetings, loose)))
        for size, starts in sorted(buckets.items()):
            yield f"census of {size} knots", starts
        for size in (6, 7, 8):
            yield f"conditioned draws of {size} knots", [
                (f"held out {size}-{i}", rows) for i, rows in enumerate(heldout(size))]
    elif suite == "larger":
        for size in SIZES:
            yield f"funded ring with additional shared distinctions, {size} knots", [
                (f"draw {i}", rows) for i, rows in enumerate(larger_starts(size, count))]
    else:
        yield "three built witnesses, the ten-knot draw, and the seven-knot draw", list(start_items("witnesses"))


def add_summary(tally, profile):
    tally["stages read"] += 1
    tally["maximum distinctions"] = max(tally["maximum distinctions"], profile["distinctions"])
    tally["forced dimension nonzero"] += int(profile["forced dimension"] > 0)
    tally["maximum forced dimension"] = max(tally["maximum forced dimension"], profile["forced dimension"])
    tally["old states removed"] += int(profile["old state rank removed"] > 0)
    tally["forced sum newly added by this growth"] += int(profile["forced dimension newly added by this growth"] > 0)
    tally["forced sum outside start laws"] += int(profile["forced dimension outside start laws"] > 0)
    tally["searched by separate blocks after initial cycle limit"] += int(
        profile.get("used independent block constraints on possible label cycles", False))
    if not profile["complete"]:
        tally["search incomplete"] += 1
    for reader in READERS:
        if reader not in profile:
            continue
        record = profile[reader]
        for field, threshold in (("candidate cycles", 1), ("candidate cycles", 3),
                                 ("eligible forced dimension", 1), ("complete splits", 1),
                                 ("minimal splits", 1), ("new since start", 1),
                                 ("new at this growth", 1)):
            tally[f"{reader}, stages with {field} >= {threshold}"] += int(record[field] >= threshold)
        for field in ("complete splits", "minimal splits"):
            tally[f"{reader}, sum of {field}"] += record[field]


def need_example(examples, group, arm, age, source, stage, name, profile):
    reasons = []
    if profile["forced dimension newly added by this growth"] > 0:
        reasons.append("a cut adds a new cycle-parity equation on preceding distinctions")
    if not profile["complete"]:
        reasons.append("a search reached a limit")
    for reader in READERS:
        if reader in profile:
            for field in ("complete splits", "minimal splits", "new since start", "new at this growth"):
                if profile[reader][field]:
                    reasons.append(f"{reader}, {field}")
    for reason in reasons:
        key = f"{arm}, {reason}"
        if key not in examples:
            examples[key] = {"group": group, "start": name, "round": age,
                             "start supports": source.supports, "stage supports": stage.supports,
                             "profile": profile}


def run(args):
    started = perf_counter()
    totals = {}
    ends = Counter()
    examples = {}
    times = {}
    pick_counts = {}
    for group, roster in groups(args.suite, args.count):
        if args.pilot:
            if args.suite == "witnesses":
                selected = roster[:1] + roster[-1:]
            else:
                indices = {0, len(roster) // 3, 2 * len(roster) // 3, len(roster) - 1}
                selected = [roster[i] for i in sorted(indices)]
        else:
            selected = roster if args.limit is None else roster[:args.limit]
        pick_counts[group] = {"available": len(roster), "read": len(selected)}
        group_started = perf_counter()
        for name, supports in selected:
            source = Incidence(supports)
            initial = inspect(source)
            for arm in ARMS:
                current = source
                add_summary(totals.setdefault((group, arm, 0), Counter()), initial)
                need_example(examples, group, arm, 0, source, current, name, initial)
                for age in range(1, args.rounds + 1):
                    rows, status = grow(current.supports, arm)
                    if status != "funded":
                        ends[group, arm, age, status] += 1
                        break
                    stage = Incidence(rows)
                    if len(stage.owners) > args.cap:
                        ends[group, arm, age, "over distinction cap, this and subsequent stages not read"] += 1
                        break
                    profile = inspect(stage, current, source)
                    if arm == "ordinary":
                        assert profile["old state rank removed"] == 0
                    add_summary(totals.setdefault((group, arm, age), Counter()), profile)
                    need_example(examples, group, arm, age, source, stage, name, profile)
                    current = stage
                else:
                    ends[group, arm, args.rounds, "studied through round limit"] += 1
        times[group] = round(perf_counter() - group_started, 5)
    return {
        "suite": args.suite, "pilot": args.pilot, "round limit": args.rounds,
        "distinction limit": args.cap, "larger draws requested per size": args.count,
        "prefix per group": args.limit, "roster": pick_counts,
        "weightings": {
            "archive": "The census weights each connected representation up to renaming once. The draws are the recorded 300 accepted labelled starts per size, with replacement.",
            "larger": f"For sizes {SIZES}, use seed {SEED} plus size independently. Keep the numbered ring. Sample floor(size/2) additional distinct unordered pairs uniformly without replacement, with one shared distinction each. Every knot with fewer than three shared distinctions is live. Other knots are live unless a uniform draw from three values is zero. Give each live knot max(1, funding demand, 3 minus its shared count) loose distinctions plus one with probability 1/4. Other knots get zero. Draws are independent with replacement within this seeded sequence.",
            "witnesses": "Five selected cases listed in the closed binding study. The seven-knot draw also occurs in the archive."
        }[args.suite],
        "reader definitions": {
            "all listed supports": "The frozen single-knot reading treats every listed support as available.",
            "only supports passing K1–K3": "Only listed supports whose full allowed-state image is their parity knot can read a carrier.",
            "complete split": "At least three distinction-disjoint simple cycles with nonconstant, invariant, individually unread parities, whose sum is forced.",
            "minimal split": "A complete split of m cycles with joint image of rank m-1. Every proper subfamily is free.",
            "new at this growth": "The minimal split's total parity was not forced by the preceding stage on these same distinctions. Every fresh distinction still has one holder in its birth round.",
            "outside start laws": "A forced sum outside the span of start equations. Some distinctions carrying it can have been born after the start.",
            "limits": "After 120000 direct simple-cycle visits, separate the meeting blocks and solve the move and cycle equations on each. Enumerate the remaining supports within a block of dimension at most 15, with a fallback to direct cycles. Each residual cover search has 120000 visits, with at most 16 dimensions after restricting forced sums to unread carriers. An incomplete search is counted separately."
        },
        "by group, growth law and round": [
            {"group": group, "growth law": arm, "round": age, **fields}
            for (group, arm, age), fields in sorted(totals.items())],
        "stopping states": [{"group": group, "growth law": arm, "round": age, "reason": reason, "starts": value}
                            for (group, arm, age, reason), value in sorted(ends.items())],
        "first example for each observed outcome and law": examples,
        "seconds per group, excluding roster preparation": times,
        "elapsed seconds": round(perf_counter() - started, 5),
        "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("archive", "larger", "witnesses"))
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--cap", type=int, default=512)
    parser.add_argument("--count", type=int, default=128)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    dest = HERE / args.output
    if dest.parent != HERE or not dest.name.startswith("cuts") or dest.suffix != ".json":
        raise ValueError("Use a cuts*.json name within this review")
    record = run(args)
    dest.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"file": dest.name, "seconds": record["elapsed seconds"],
                      "per group": record["seconds per group, excluding roster preparation"],
                      "peak resident KiB": record["peak resident KiB"]}))
