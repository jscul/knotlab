"""Recover all presentations of the labelled not-all-equal states and marked loose set.

An input has up to two holders per distinction and a nonempty state set. Row
order is immaterial. This finder admits any number of rows of at least two
places, disconnected presentations, and even repeated supports (separately
counted). It reads no recorded presentation count until after each recount.

A support is entailed exactly when it is contained in no allowed state's set
of ones. This uses complement symmetry. Downward closure gives all such tests
at once. Every entailed support contains an inclusion-minimal entailed support.
Replace every proposed row by any such subset. The shrunken rows still allow
every original state and still exclude every originally forbidden state. Their
incidences use at most the marked multiplicities. If a forbidden state is
excluded by just one of the minimal supports, that support must occur among
the shrunken rows. Enumerate their multisets, then allocate every remaining
incidence to distinct rows that lack the distinction. At every enlargement
the excluded set can only shrink, so a lost forbidden state is decisive.
Sorting complete presentations removes alternative choices of minimal subset.
"""

import argparse
import hashlib
import json
import resource
import time
from collections import Counter
from functools import cache
from itertools import combinations, combinations_with_replacement, permutations
from math import comb
from pathlib import Path

from census_tools import SOURCE, connected, roster, tree


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent / "frozen_nae.jsonl"
RESULT = HERE / "nae_counts.json"
AS_LIMIT = 2_400_000_000
SEEN = 200
PREFIX = 1_194
PLANNED = 2_000


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def holdings(rows):
    used = twice = 0
    for mask in rows:
        if mask & twice:
            raise ValueError("A distinction has more than two holders")
        twice |= used & mask
        used |= mask
    return used, twice


@cache
def truth_tables(n):
    """Bit s describes the complete assignment with ones on the support s."""
    full = (1 << (1 << n)) - 1
    ones_by_bit = []
    all_ones = [full]
    all_zeroes = [full]
    for i in range(n):
        run = 1 << i
        period = ((1 << run) - 1) << run
        ones = period * (full // ((1 << (2 * run)) - 1))
        ones_by_bit.append(ones)
        all_ones += [x & ones for x in all_ones]
        all_zeroes += [x & (full ^ ones) for x in all_zeroes]
    fails = [one | zero for one, zero in zip(all_ones, all_zeroes)]
    return full, ones_by_bit, fails


def failed_states(rows, fails):
    forbidden = 0
    for row in rows:
        forbidden |= fails[row]
    return forbidden


def local_gates(rows, allowed, full, ones_by_bit, fails):
    """Check the earlier reconstruction theorem's projection and erasure hypotheses."""
    locally_full = []
    essential = []
    all_names = (1 << len(ones_by_bit)) - 1
    for j, mask in enumerate(rows):
        projection = allowed
        for i in indices(all_names ^ mask):
            projection = (projection | (projection >> (1 << i))) & (full ^ ones_by_bit[i])
        locally_full.append(projection.bit_count() == (1 << mask.bit_count()) - 2)
        others = failed_states(rows[:j] + rows[j + 1:], fails)
        essential.append(bool(fails[mask] & ~others))
    return locally_full, essential


def minimal_supports(allowed, full, ones_by_bit):
    """Downward closure of allowed ones-sets gives all possible monochrome subsets."""
    subsets = allowed
    for i, ones in enumerate(ones_by_bit):
        subsets |= (subsets & ones) >> (1 << i)
    entailed = full ^ subsets
    enlarged = 0
    for i, ones in enumerate(ones_by_bit):
        enlarged |= (entailed & (full ^ ones)) << (1 << i)
    return tuple(indices(entailed & ~enlarged))


def private_supports(small, fails):
    """A private forbidden assignment forces this minimal support after shrinking."""
    before = 0
    left = []
    for mask in small:
        left.append(before)
        before |= fails[mask]
    after = 0
    forced = []
    for mask, previous in reversed(list(zip(small, left))):
        if fails[mask] & ~(previous | after):
            forced.append(mask)
        after |= fails[mask]
    return sorted(forced)


def take_once(mask, left, double):
    """Subtract one occurrence of each named distinction in the row."""
    return left & ~(mask & ~double), double & ~mask


def all_presentations(rows):
    used, shared = holdings(rows)
    n = used.bit_length()
    if used != (1 << n) - 1:
        raise ValueError("Input distinction names must be consecutive from zero")
    full, ones_by_bit, fails = truth_tables(n)
    forbidden = failed_states(rows, fails)
    allowed = full ^ forbidden
    if not allowed:
        raise ValueError("The requested input has no allowed states")
    small = minimal_supports(allowed, full, ones_by_bit)
    locally_full, essential = local_gates(rows, allowed, full, ones_by_bit, fails)
    forced = private_supports(small, fails)
    left, double = used, shared
    for mask in forced:
        if mask & ~left:
            raise AssertionError("Forced rows exceed a multiplicity in a possible input")
        left, double = take_once(mask, left, double)
    options = [mask for mask in small if not mask & ~left]
    remaining_cover = [0] * (len(options) + 1)
    for j in reversed(range(len(options))):
        remaining_cover[j] = remaining_cover[j + 1] | fails[options[j]]
    solutions = set()
    cores = list(forced)
    core_multisets = 0

    def extend(missing, missing_twice):
        nonlocal core_multisets
        core_multisets += 1
        expanded = list(cores)
        needs = []
        for i in indices(missing):
            bit = 1 << i
            eligible = [j for j, mask in enumerate(expanded) if not mask & bit]
            count = 2 if missing_twice & bit else 1
            if len(eligible) < count:
                return
            needs.append((comb(len(eligible), count), bit, count, eligible))
        needs.sort()

        def fill(j):
            if j == len(needs):
                solutions.add(tuple(sorted(expanded)))
                return
            _, bit, count, eligible = needs[j]
            for selected in combinations(eligible, count):
                for index in selected:
                    expanded[index] |= bit
                if failed_states(expanded, fails) == forbidden:
                    fill(j + 1)
                for index in selected:
                    expanded[index] ^= bit

        fill(0)

    def choose(j, missing, missing_twice, excluded):
        if forbidden & ~(excluded | remaining_cover[j]):
            return
        if j == len(options):
            extend(missing, missing_twice)
            return
        mask = options[j]
        choose(j + 1, missing, missing_twice, excluded)
        count = 0
        while not (mask & ~missing):
            missing, missing_twice = take_once(mask, missing, missing_twice)
            cores.append(mask)
            count += 1
            choose(j + 1, missing, missing_twice, excluded | fails[mask])
        for _ in range(count):
            cores.pop()

    choose(0, left, double, failed_states(forced, fails))
    original = tuple(sorted(rows))
    if original not in solutions:
        raise AssertionError("The start itself must be a presentation")
    return sorted(solutions), {
        "distinctions": n,
        "allowed states": allowed.bit_count(),
        "full local projections": all(locally_full), "every rule essential": all(essential),
        "minimal entailed supports": len(small),
        "forced minimal supports": len(forced),
        "forced supports exactly the start": tuple(forced) == original,
        "entailed minimal supports exactly the start": tuple(sorted(small)) == original,
        "shrunken multisets covering all forbidden states": core_multisets,
    }


def literal_allowed(rows, used):
    return {state for state in range(used + 1)
            if all(0 < (state & mask) < mask for mask in rows)}


def direct_presentations(rows):
    """Independent small-case search, with literal states and no minimal-support step."""
    used, shared = holdings(rows)
    relation = literal_allowed(rows, used)
    possible = [mask for mask in range(1, used + 1) if mask.bit_count() >= 2
                and all(0 < (state & mask) < mask for state in relation)]
    found = set()

    def walk(left, double, chosen):
        if not left:
            if literal_allowed(chosen, used) == relation:
                found.add(tuple(sorted(chosen)))
            return
        bit = left & -left
        copies = 2 if double & bit else 1
        options = [mask for mask in possible if mask & bit and not mask & ~left]
        for batch in combinations_with_replacement(options, copies):
            need, twice = left, double
            for mask in batch:
                if mask & ~need:
                    break
                need, twice = take_once(mask, need, twice)
            else:
                walk(need, twice, chosen + batch)

    walk(used, shared, ())
    return found


def isomorphic(first, second):
    """A renaming is determined by singleton counts and counts for each holder pair."""
    if len(first) != len(second):
        return False
    degrees = tuple(mask.bit_count() for mask in first)
    for image in permutations(second):
        if tuple(mask.bit_count() for mask in image) != degrees:
            continue
        if all((first[i] & first[j]).bit_count() == (image[i] & image[j]).bit_count()
               for i, j in combinations(range(len(first)), 2)):
            return True
    return False


def controls(starts):
    # The four three-place knots with six shared distinctions have two named readings.
    # Two repeated, disconnected supports exercise admission of redundant rows.
    # Two alternating pairs entail a further law without demanding it be a row.
    cases = [("four three-place knots, every pair holds one shared distinction", starts[959]),
             ("two separate repeated two-place laws", (3, 3, 12, 12)),
             ("three consecutive two-place laws", (3, 6, 12)),
             ("a three-place law and a proper superset", (7, 15)),
             ("two intersecting three-place laws", (7, 28))]
    out = []
    for description, rows in cases:
        found, _ = all_presentations(rows)
        raw = direct_presentations(rows)
        if set(found) != raw:
            raise AssertionError((description, found, sorted(raw)))
        out.append({"description": description, "input masks": rows,
                    "exact solutions from both methods": found,
                    "row counts": sorted({len(p) for p in found})})
    return out


def matches_frozen(p, original):
    return (len(p) == len(original) and len(set(p)) == len(p)
            and min(mask.bit_count() for mask in p) >= 3 and connected(p))


def by_class(presentations):
    classes = []
    for p in presentations:
        if not any(isomorphic(q, p) for q in classes):
            classes.append(p)
    return len(classes)


def tally(counts, sol, trees, rows, frozen, stats):
    used, shared = holdings(rows)
    nloose = (used ^ shared).bit_count()
    genuine = [p for p in sol if len(set(p)) == len(p)]
    original = tuple(sorted(rows))
    families = {t[0] for t in trees}
    f = len(tree(original)[0])
    counts.update({
        "starts": 1, "source has no loose distinction": not nloose,
        "source has full local projections": stats["full local projections"],
        "source has every rule essential": stats["every rule essential"],
        "source has full local projections and every rule essential":
            stats["full local projections"] and stats["every rule essential"],
        "source has exactly one loose distinction": nloose == 1,
        "source has at least two loose distinctions": nloose >= 2,
        "source has exactly one family": f == 1, "source has at least two families": f >= 2,
        "one presentation in frozen scope": len(frozen) == 1,
        "one presentation with distinct supports, all sizes": len(genuine) == 1,
        "one presentation even allowing repeated supports": len(sol) == 1,
        "at least two presentations with distinct supports": len(genuine) > 1,
        "additional presentations outside frozen scope (including repetitions)": len(sol) > len(frozen),
        "number of frozen presentations": len(frozen),
        "number of distinct-support presentations": len(genuine), "number of presentations": len(sol),
        "pairs of distinct-support presentations": comb(len(genuine), 2),
        "multiple distinct supports readings, with loose distinctions": len(genuine) > 1 and nloose > 0,
        "multiple distinct supports readings, at least two loose distinctions": len(genuine) > 1 and nloose >= 2,
        "multiple distinct supports readings, at least two source families": len(genuine) > 1 and f >= 2,
        "multiple distinct supports readings, at least three source families": len(genuine) > 1 and f >= 3,
        "admits a different knot count": any(len(p) != len(rows) for p in sol),
        "admits a two-place support": any(any(m.bit_count() == 2 for m in p) for p in sol),
        "admits a disconnected presentation": any(not connected(p) for p in sol),
        "admits a repeated support": len(genuine) != len(sol),
        "admits different presentations up to renaming": len(sol) > 1 and by_class(sol) > 1,
        "same named families across all presentations": len(families) == 1,
        "same named tree across all presentations": len(trees) == 1,
    })


def check(starts, indices_to_run, archive):
    windows = {"all": Counter(), "first 200 seen before freezing": Counter(),
               "recorded prefix": Counter(), "after recorded prefix": Counter(),
               "rest of planned prefix": Counter(), "after planned prefix": Counter()}
    diagnostics = Counter()
    hist = Counter()
    literal = Counter()
    exceptional, differences = [], []
    for i in indices_to_run:
        rows = starts[i]
        solutions, stats = all_presentations(rows)
        if stats["distinctions"] <= 8:
            if direct_presentations(rows) != set(solutions):
                raise AssertionError(f"Literal comparison differs at census index {i}")
            literal[stats["distinctions"]] += 1
        frozen = [p for p in solutions if matches_frozen(p, rows)]
        trees = {tree(p) for p in solutions}
        keys = ["all", "recorded prefix" if i < PREFIX else "after recorded prefix"]
        if i < SEEN:
            keys.append("first 200 seen before freezing")
        if PREFIX <= i < PLANNED:
            keys.append("rest of planned prefix")
        if i >= PLANNED:
            keys.append("after planned prefix")
        row_counts = Counter()
        tally(row_counts, solutions, trees, rows, frozen, stats)
        for key in keys:
            windows[key].update(row_counts)
        diagnostics["source supports forced by private assignments"] += stats["forced supports exactly the start"]
        diagnostics["source is the entire list of minimal entailed supports"] += stats["entailed minimal supports exactly the start"]
        for key in ("minimal entailed supports", "forced minimal supports", "shrunken multisets covering all forbidden states"):
            diagnostics["maximum " + key] = max(diagnostics["maximum " + key], stats[key])
        hist[len(solutions)] += 1
        if len(solutions) > 1:
            exceptional.append({"census index": i, "number of source knots": len(rows),
                                "source masks": rows, "loose distinctions": list(indices(holdings(rows)[0] ^ holdings(rows)[1])),
                                **stats, "presentations in the frozen scope": len(frozen),
                                "classes up to renaming": by_class(solutions),
                                "solutions": [{"masks": p, "tree": tree(p)} for p in solutions]})
        if i < len(archive):
            frozen_trees = {tree(p) for p in frozen}
            actual = {"start": f"census {i}", "presentations": len(frozen),
                      "family partitions": len({t[0] for t in frozen_trees}),
                      "trees": len(frozen_trees), "own tree among them": tree(rows) in frozen_trees}
            bad = {k: [archive[i].get(k), v] for k, v in actual.items() if archive[i].get(k) != v}
            if bad:
                differences.append({"census index": i, "recorded and recounted": bad})
    return {"windows": windows, "number of starts by number of solutions": dict(sorted(hist.items())),
            "minimal-support search": diagnostics, "starts with alternatives": exceptional,
            "matching direct literal censuses by distinction count": dict(sorted(literal.items())),
            "differences from numbered rows of the frozen output": differences}


def pilot_indices(n):
    return sorted({0, 5, 959, 1193, n - 1, *range(0, n, 113)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Use the fixed pilot cases and write no file")
    args = parser.parse_args()
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = min([AS_LIMIT] + [limit for limit in (soft, hard) if limit != resource.RLIM_INFINITY])
    resource.setrlimit(resource.RLIMIT_AS, (cap, hard))
    starts = roster()
    archive = [r for line in ARCHIVE.read_text().splitlines() if "start" in (r := json.loads(line))]
    chosen = pilot_indices(len(starts)) if args.pilot else range(len(starts))
    start_time = time.perf_counter()
    reference = controls(starts)
    result = check(starts, chosen, archive)
    duration = time.perf_counter() - start_time
    summary = {"starts checked": len(chosen), "seconds": round(duration, 4),
               "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               "census indices with alternatives": [x["census index"] for x in result["starts with alternatives"]],
               "frozen record differences": len(result["differences from numbered rows of the frozen output"])}
    print(json.dumps(summary))
    if args.pilot:
        return
    result = {
        "scope": "Every archived census start once. Named distinctions, unordered knots, source loose multiplicities, at least two places per row, any number of rows, all connectivity patterns. Repeated supports are separately counted. The frozen scope requires the source knot count, distinct supports, at least three places and connectedness.",
        "weighting": "Each census start once up to renaming. Another presentation of its labelled allowed states is counted before renaming.",
        "mask encoding": "The least significant bit is distinction 0. Tree entries give first the sorted family masks, then each threshold and its group masks.",
        "source sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "archived output sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        "archived numbered rows": len(archive),
        "archived capped rows": sum(bool(r["capped"]) for r in archive),
        "direct literal controls": reference,
        **result,
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
