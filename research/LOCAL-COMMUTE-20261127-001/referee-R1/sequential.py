"""Exact prefix-extension tests and a replay of the recorded random choices."""

import argparse
import json
import random
import resource
import time
from bisect import bisect_left
from collections import Counter
from itertools import combinations
from pathlib import Path

from core import closing_cost, commutation, history, read_starts


HERE = Path(__file__).resolve().parent
SEED = 20261127


def reduce_low(row, basis):
    while row:
        earlier = basis.get(row & -row)
        if earlier is None:
            break
        row ^= earlier
    return row


def add_rows(basis, rows):
    for row in rows:
        row = reduce_low(row, basis)
        if row:
            basis[row & -row] = row


def eliminate_new(rows, old_width):
    """Eliminate new columns. Any remaining old-only row restricts a prefix."""
    pivots = {}
    residuals = []
    for row in rows:
        while row.bit_length() > old_width:
            index = row.bit_length() - 1
            if index not in pivots:
                pivots[index] = row
                break
            row ^= pivots[index]
        else:
            if row:
                residuals.append(row)
    return dict(sorted(pivots.items())), residuals


def one_extension(previous, current, pair_bits):
    """A linear choice of the new pair bits as functions of the old ones.

    One fresh distinction of each birth takes the old inputs' total
    commutation against each old distinction. Only nonzero functions are kept.
    """
    images = {}
    for knot in current.knots[len(previous.knots):]:
        inputs = [d for d in knot if d in previous.holders]
        fresh = [d for d in knot if d not in previous.holders]
        if not fresh:
            continue
        chosen = min(fresh)
        for old in previous.holders:
            form = 0
            for d in inputs:
                form ^= pair_bits.get((d, old), 0)
            if form:
                # A missing key would give a forbidden nonzero choice.
                images[pair_bits[chosen, old]] = form
    return images


def pull_back(row, old_mask, images):
    value = row & old_mask
    new = row ^ value
    while new:
        bit = new & -new
        value ^= images.get(bit, 0)
        new ^= bit
    return value


def draw(steps, cost, rng):
    chosen = 0
    for turn, (pivots, conditions, free) in enumerate(steps):
        if any((row & chosen).bit_count() % 2 for row in conditions):
            return ["dead end", turn]
        for bit in free:
            if rng.random() < 0.5:
                chosen |= bit
        for index, row in pivots.items():
            if (row & chosen).bit_count() % 2:
                chosen |= 1 << index
    sign = None if cost is None else ("odd" if (chosen & cost).bit_count() % 2 else "even")
    return ["kept", sign]


def new_tally():
    return {
        "end": Counter(), "rounds": {}, "non-surjective projections": [],
        "constructed extension failures": [], "forced-even closures": 0,
        "odd-attainable closures": 0, "latest sign decision": {},
        "completed choices on all closures": 0, "odd choices on all closures": 0,
        "control requiring all new pairs to commute": None,
        "already closed at the start": {
            "starts": 0, "starts allowing an odd product": 0,
            "sampled starts": 0, "sampled starts allowing an odd product": 0,
            "draws by product parity": Counter(), "first sampled odd product": None,
        },
    }


def measure(path, start_id, tally, draws, rng, from_round=0):
    tally["end"][path.end] += 1
    if path.end == "cut":
        return None

    states = path.states
    final = states[-1]
    # The recorded random stream assigns free bits in pair-name order in each round.
    blocks = [sorted(state.new_birth_pairs) for state in states]
    pairs = [pair for block in blocks for pair in block]
    pair_bits = {(a, b): 1 << i for i, (a, b) in enumerate(pairs)}
    pair_bits.update({(b, a): bit for (a, b), bit in tuple(pair_bits.items())})
    rows_at = [[] for _ in states]
    for (_, second), row in zip(combinations(range(len(final.knots)), 2),
                                commutation(final, pairs), strict=True):
        if row:
            rows_at[final.knot_round[second]].append(row)

    previous_rank_basis = {}
    all_pivots = {}
    steps = []
    widths = []
    free_total = 0
    width = 0
    for turn, (state, rows, block) in enumerate(zip(states, rows_at, blocks, strict=True)):
        old_width = width
        width += len(block)
        widths.append(width)
        assert all(row.bit_length() <= width for row in rows)
        pivots, residuals = eliminate_new(rows, old_width)
        free = [1 << i for i in range(old_width, width) if i not in pivots]
        free_total += len(free)
        steps.append((pivots, residuals, free))
        all_pivots.update(pivots)

        unexplained = any(reduce_low(row, previous_rank_basis) for row in residuals)
        old_mask = (1 << old_width) - 1
        failed_witness = False
        if turn:
            images = one_extension(states[turn - 1], state, pair_bits)
            failed_witness = any(
                reduce_low(pull_back(row, old_mask, images), previous_rank_basis) for row in rows
            )
            if turn >= from_round and tally["control requiring all new pairs to commute"] is None:
                restricted = previous_rank_basis.copy()
                add_rows(restricted, (row & old_mask for row in rows))
                lost = len(restricted) - len(previous_rank_basis)
                if lost:
                    tally["control requiring all new pairs to commute"] = {
                        "census index": start_id, "starting knot supports": states[0].knots,
                        "round": turn, "additional independent restrictions on the prefix": lost,
                    }

        previous_rank = len(previous_rank_basis)
        add_rows(previous_rank_basis, rows)
        # dim(S_old) - dim(projection(S_now)) = rank_now - rank_old - rank_new_columns.
        deficit = len(previous_rank_basis) - previous_rank - len(pivots)
        assert deficit >= 0 and bool(deficit) == unexplained
        if turn < from_round:
            continue
        info = tally["rounds"].setdefault(turn, {
            "structures": 0, "onto": 0, "minimum free new bits": len(free),
            "maximum free new bits": len(free), "constructed extensions checked": 0,
        })
        info["structures"] += 1
        info["onto"] += int(not deficit)
        info["minimum free new bits"] = min(info["minimum free new bits"], len(free))
        info["maximum free new bits"] = max(info["maximum free new bits"], len(free))
        if turn:
            info["constructed extensions checked"] += 1
        if failed_witness:
            tally["constructed extension failures"].append([start_id, turn])
        if deficit:
            tally["non-surjective projections"].append([start_id, turn, deficit])

    cost = None
    odd = None
    if path.end == "closed" and final.round == 0 and not from_round:
        # These starts have no closing birth. Their check product can still be -I.
        initial = tally["already closed at the start"]
        cost = closing_cost(final, pairs)
        can_be_odd = bool(reduce_low(cost, previous_rank_basis))
        initial["starts"] += 1
        initial["starts allowing an odd product"] += can_be_odd
        initial["sampled starts"] += bool(draws)
        initial["sampled starts allowing an odd product"] += bool(draws) and can_be_odd
        runs = [draw(steps, cost, rng) for _ in range(draws)]
        for draw_index, (status, sign) in enumerate(runs):
            assert status == "kept"
            group = "odd attainable" if can_be_odd else "odd unattainable"
            initial["draws by product parity"][f"{group}: {sign}"] += 1
            if sign == "odd" and initial["first sampled odd product"] is None:
                initial["first sampled odd product"] = {
                    "census index": start_id, "starting knot supports": final.knots,
                    "draw (one-based)": draw_index + 1,
                }
        return [["kept", None] for _ in runs], None

    if path.end == "closed" and final.round >= from_round:
        cost = closing_cost(final, pairs)
        odd = bool(reduce_low(cost, previous_rank_basis))
        tally["odd-attainable closures" if odd else "forced-even closures"] += 1
        choices = 1 << (width - len(previous_rank_basis))
        tally["completed choices on all closures"] += choices
        tally["odd choices on all closures"] += choices // 2 if odd else 0
        if free_total == width - len(previous_rank_basis):
            # Express the closing sign in the independent free bits of the successive draws.
            form = cost
            for index in sorted(all_pivots, reverse=True):
                if form & (1 << index):
                    form ^= all_pivots[index]
            assert bool(form) == odd
            last = str(bisect_left(widths, form.bit_length())) if form else "fixed before any choice"
            tally["latest sign decision"].setdefault(final.round, Counter())[last] += 1

    return [draw(steps, cost, rng) for _ in range(draws)], odd


def audit(limit=None):
    starts = read_starts()
    sample = set(random.Random(SEED).sample(range(len(starts)), 500))
    rng = random.Random(SEED)
    tally = new_tally()
    runs = {}
    signs = Counter()
    cut_sample = []
    growing = []
    for i, start in enumerate(starts[:limit]):
        path = history(start)
        result = measure(path, i, tally, 5 if i in sample else 0, rng)
        if path.end == "growing":
            growing.append(i)
        if i not in sample:
            continue
        if result is None:
            cut_sample.append(i)
            continue
        runs[i], odd = result
        for outcome, value in runs[i]:
            if outcome == "dead end":
                signs["dead ends"] += 1
            elif odd is not None:
                group = "odd attainable" if odd else "odd unattainable"
                signs[f"{group}: {value}"] += 1

    # Compare only after recomputing the choices. No recorded row enters the solver.
    with (HERE.parent / "results.jsonl").open() as fh:
        recorded = {row["start"]: row["random local rule runs"] for row in map(json.loads, fh)
                    if "random local rule runs" in row and (limit is None or row["start"] < limit)}
    differing = [i for i in sorted(runs.keys() | recorded.keys()) if runs.get(i) != recorded.get(i)]
    result = {
        "scope": "Up to four funded rounds, with starts exceeding 40 knots excluded.",
        "census starts visited": len(starts[:limit]), "four rounds": tally,
        "seeded replay": {
            "seed": SEED, "sampled before cap": len(runs) + len(cut_sample),
            "sampled after cap": len(runs), "cut census indices": cut_sample,
            "draws": sum(map(len, runs.values())), "dead ends": signs["dead ends"],
            "signs": {key: signs[key] for key in ("odd attainable: odd", "odd attainable: even",
                                                  "odd unattainable: odd", "odd unattainable: even")},
            "starts differing from the archived draw sequence": differing,
        },
    }
    if limit is None:
        fifth = new_tally()
        for i in random.Random(SEED).sample(growing, 200):
            measure(history(starts[i], rounds=5), i, fifth, 0, rng, from_round=5)
        result["fifth round on the original seeded sample"] = fifth
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="time a census prefix and print it without writing a file")
    args = parser.parse_args()
    started = time.monotonic()
    result = audit(args.limit)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.limit is None:
        (HERE / "sequential.json").write_text(output)
    else:
        print(output, end="")
    print(f"Elapsed {time.monotonic() - started:.2f} s, peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KiB")
