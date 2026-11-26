"""Compare archived birth multisets with a lone three-place knot and two-chain growth.

Run beside this file with --limit 300 --out tails_pilot.json before the full
run with --out tails.json. The limit is a prefix of each pair of archives.
"""

import argparse
import gzip
import json
from collections import Counter, defaultdict
from itertools import islice
from math import comb
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
LONE_ARCHIVE = STUDY.parent / "LOOK-ALIKE-20261126-001" / "phase1_grown.jsonl.gz"
READINGS = ("sig0", "sig1")
OFFSHOOT = ("offshoot", 1, 2, 3)
TWO_PARENT_JOIN = ("join", 2, 2, 4)


def read_row(row):
    simple = Counter({tuple(birth): count for birth, count in row["sig0"]})
    parents = Counter()
    for (birth, old), count in row["sig1"]:
        parents[tuple(birth), tuple(sorted(tuple(parent) for parent in old))] += count
    reduced = Counter()
    for (birth, _), count in parents.items():
        reduced[birth] += count
    if reduced != simple or simple.total() != row["n"]:
        raise ValueError("Birth totals or parent descriptions disagree within a row.")
    return {"sig0": simple, "sig1": parents}


def read_lone():
    with gzip.open(LONE_ARCHIVE, "rt") as records:
        for line in records:
            start = json.loads(line)
            if start["stars"] == [[0, 1, 2]]:
                return [read_row(row) for row in start["rows"]]
    raise ValueError("The lone three-place knot is missing from its archive.")


def settling(rows, degree_plus_one):
    """The last nonzero difference of order D must have ended by the fit."""
    d = degree_plus_one
    weights = [(-1) ** (d - j) * comb(d, j) for j in range(d + 1)]
    for end in range(len(rows), d, -1):
        window = rows[end - d - 1:end]
        keys = set().union(*window)
        if any(sum(w * row.get(key, 0) for w, row in zip(weights, window))
               for key in keys):
            fit_end = max(3, end)
            return fit_end if fit_end <= len(rows) - 2 else None
    return max(3, d) if len(rows) >= max(3, d) + 2 else None


def two_chains(top, length):
    """The T+1 offshoot followed by pairs (i,j) of nonnegative chain lengths."""
    rows = []
    previous = {}
    for total in range(length):
        current = {}
        simple, parents = Counter(), Counter()
        for i in range(total + 1):
            j = total - i
            parent_types = []
            if i:
                parent_types.append(previous[i - 1, j])
            if j:
                parent_types.append(previous[i, j - 1])
            if total == 0:
                parent_types = [top]
            birth = TWO_PARENT_JOIN if len(parent_types) == 2 else OFFSHOOT
            current[i, j] = birth
            simple[birth] += 1
            parents[birth, tuple(sorted(parent_types))] += 1
        previous = current
        rows.append({"sig0": simple, "sig1": parents})
    return rows


def first_singleton_relay(totals):
    for round_no in range(2, len(totals) - 2):
        if totals[round_no - 2] > 1 and totals[round_no - 1:] == (
                [1] + list(range(1, len(totals) - round_no + 1))):
            return round_no
    return None


def last_round(rows, predicate):
    return next((i for i, row in reversed(list(enumerate(rows, 1)))
                 if any(predicate(kind) for kind in row["sig0"])), None)


def drop_round(totals):
    return max((t for t, (a, b) in enumerate(zip(totals, totals[1:]), 2) if b < a),
               default=None)


def numbers_after(rows, t, reading, reference):
    """Compare T with lone round 3, including every subsequent common round."""
    pairs = list(zip(rows[t - 1:], reference[2:]))
    misses = [offset for offset, (observed, expected) in enumerate(pairs)
              if observed[reading] != expected[reading]]
    return {
        "last common start round": t - 1 + len(pairs),
        "last common reference round": 2 + len(pairs),
        "mismatch offsets from T": misses,
        "first offset equal thereafter": 1 + max(misses, default=-1),
    }


def local_relay(rows, t, dimension):
    """Test the last one-fresh join and remove only the specified birth counts."""
    tops = {kind: count for kind, count in rows[t - 1]["sig0"].items()
            if kind[0] == "join" and kind[2] == 1}
    sources = sum(tops.values())
    next_parents = rows[t]["sig1"] if t < len(rows) else {}
    launches = sum(min(n, next_parents.get((OFFSHOOT, (top,)), 0))
                   for top, n in tops.items())
    expected = [(n, two_chains(top, len(rows) - t)) for top, n in tops.items()]
    result = {"last one-fresh join round": t, "joins there": sources,
              "descriptions and counts": [[list(k), v] for k, v in sorted(tops.items())],
              "offshoots next with those parent descriptions": launches}
    for reading in READINGS:
        residual = []
        for offset, observed in enumerate(rows[t:]):
            rest = observed[reading].copy()
            for n, chain in expected:
                for key, count in chain[offset][reading].items():
                    rest[key] -= n * count
            residual.append({k: v for k, v in rest.items() if v})
        fits = settling(residual, dimension)
        result[reading] = {
            "two-chain counts contained at every later round": all(
                all(value >= 0 for value in rest.values()) for rest in residual),
            "two-chain counts exactly equal every later round": all(not rest for rest in residual),
            "remainder fits degree at most D-1 throughout rounds after T":
                len(residual) > dimension and all(
                    all(sum((-1) ** (dimension - j) * comb(dimension, j) * window[j].get(k, 0)
                            for j in range(dimension + 1)) == 0 for k in set().union(*window))
                    for window in (residual[i:i + dimension + 1]
                                   for i in range(len(residual) - dimension))),
            "first fit of the remainder, local round floored at 3": fits,
        }
    return result


def observed_fits(start, rows):
    if not start["kind"].startswith("dim "):
        return {}
    d = int(start["kind"].split()[1])
    return {reading: settling([row[reading] for row in rows], d) for reading in READINGS}


def counts_tree(row):
    if isinstance(row, dict):
        return {str(k): counts_tree(v) for k, v in sorted(row.items(), key=lambda item: str(item[0]))}
    return row


def add_gap(tally, name, amount):
    tally[name]["absent" if amount is None else amount] += 1


def record_falls(tallies, law, k, totals, initial_size, cohort):
    fall = drop_round(totals)
    # A distinct convention includes the number of start knots as round zero.
    inclusive_fall = fall if fall is not None or totals[0] >= initial_size else 1
    for read, fit_end in k.items():
        for group in (cohort, "all"):
            name = f"{law} {group} / {read} / K minus last fall"
            add_gap(tallies, name, fit_end - fall if fall is not None else None)
            add_gap(tallies, name + " including start count",
                    fit_end - inclusive_fall if inclusive_fall is not None else None)
            for sentinel in (0, 1):
                add_gap(tallies, name + f" assigning round {sentinel} when absent",
                        fit_end - (fall if fall is not None else sentinel))


def trade_laws(nae, parity):
    end = parity["end"]
    if not end.startswith("closes at round "):
        return {"parity end": end, "both saved histories identical": nae["rows"] == parity["rows"]}
    t = len(parity["rows"])
    first_empty = int(end.split()[-1])
    parity_top, nae_top = parity["rows"][-1], nae["rows"][t - 1]
    return {
        "parity end": end, "last parity birth": t, "first empty parity round": first_empty,
        "histories identical before last birth": nae["rows"][:t - 1] == parity["rows"][:t - 1],
        "totals identical through last parity birth":
            [row["n"] for row in nae["rows"][:t]] == [row["n"] for row in parity["rows"]],
        "last parity sig0": parity_top["sig0"], "same round under not-all-equal": nae_top["sig0"],
    }


def study_size(n, limit, late, reference):
    tallies = defaultdict(Counter)
    cases, old_burst = [], []
    controls = {}
    with gzip.open(STUDY / f"grown_g{n}_nae.jsonl.gz", "rt") as nae_file, gzip.open(
            STUDY / f"grown_g{n}_par.jsonl.gz", "rt") as parity_file:
        for a, b in islice(zip(nae_file, parity_file, strict=True), limit):
            nae, parity = json.loads(a), json.loads(b)
            index = nae["index"]
            if (index, nae["stars"]) != (parity["index"], parity["stars"]):
                raise ValueError("The laws were paired on different starts.")
            tallies["starts"]["all matched by index and holdings"] += 1
            chosen = index in late[f"g{n}_nae"]
            if not nae["kind"].startswith("dim "):
                if chosen or index in late[f"g{n}_par"]:
                    raise ValueError("Expected a classified start.")
                continue
            observed = [read_row(row) for row in nae["rows"]]
            totals = [row["n"] for row in nae["rows"]]
            k = observed_fits(nae, observed)
            d = int(nae["kind"].split()[1])
            t = first_singleton_relay(totals)
            fall = drop_round(totals)
            fresh = last_round(observed, lambda kind: kind[0] == "join" and kind[2] == 1)
            last_join = last_round(observed, lambda kind: kind[0] == "join")
            last_three = last_round(observed, lambda kind: kind[1] >= 3)
            fits = tuple(k[r] > nae["M"] + slack for r, slack in zip(READINGS, (5, 7)))
            if fits != (chosen, chosen) or (chosen and k != late[f"g{n}_nae"][index]):
                raise ValueError("The reference list and recalculated late starts disagree.")
            cohort = "late" if chosen else "within bound"
            narrow = "falls to 1,1,2,3" if t is not None else "other counts"
            tallies["not-all-equal dimension starts"][f"{cohort} / {narrow}"] += 1
            record_falls(tallies, "not-all-equal", k, totals, n, cohort)
            if parity["kind"].startswith("dim "):
                if nae["rows"] != parity["rows"] or nae["kind"] != parity["kind"]:
                    raise ValueError("A dimensioned parity counterpart has a different view.")
                record_falls(tallies, "parity", k, totals, n, cohort)
            for read, fit_end in k.items():
                for group in (cohort, "all"):
                    name = f"not-all-equal {group} / {read}"
                    add_gap(tallies, name + " / K minus last one-fresh join",
                            fit_end - fresh if fresh else None)
                    if t:
                        add_gap(tallies, name + " / K minus first singleton", fit_end - t)
            if t is not None:
                top = observed[t - 1]["sig0"]
                tallies["first singleton description / " + cohort][str(next(iter(top)))] += 1
                tallies["singleton and parity / " + cohort][parity["kind"]] += 1
            if index in late[f"g{n}_par"]:
                if not chosen or t is not None or nae["rows"] != parity["rows"]:
                    raise ValueError("The late parity set differs from its proposed counterpart.")
                if observed_fits(parity, observed) != late[f"g{n}_par"][index]:
                    raise ValueError("The parity settling rounds disagree.")
                tallies["starts"]["late under parity with identical full history"] += 1
            if n == 5 and k == {"sig0": 14, "sig1": 16} and nae["M"] == 10:
                old_burst.append({"census index of five-knot start": index, "counts": totals,
                                  "K": k, "singleton round": t, "swapping laws": trade_laws(nae, parity)})
            if not chosen:
                key = f"{narrow} / {parity['kind']}"
                if key not in controls:
                    controls[key] = {"census index": index, "M": nae["M"], "K": k,
                                     "counts": totals, "first singleton relay": t}
                continue

            case = {
                "census index": index, "loose distinctions on start knots": nae["loose"],
                "start holdings": nae["stars"], "M": nae["M"], "dimension": d,
                "K": k, "not-all-equal counts": totals, "last strict fall": fall,
                "first singleton relay": t, "last observed join": last_join,
                "joins in last recorded round": sum(v for kind, v in observed[-1]["sig0"].items()
                                                    if kind[0] == "join"),
                "last join of at least three parents": last_three,
                "swapping laws": trade_laws(nae, parity),
            }
            tallies["late / minimum births in an observed round"][min(totals)] += 1
            tallies["late / last observed join round"][last_join] += 1
            tallies["late / last join of at least three parents"][last_three] += 1
            if t is not None:
                case["knots present at singleton round"] = n + sum(totals[:t])
                case["first singleton birth with parents"] = nae["rows"][t - 1]["sig1"]
                case["at least one increase before the drop to one"] = any(
                    b > a for a, b in zip(totals[:t - 1], totals[1:t - 1]))
                case["compared with actual lone three-place knot"] = {
                    read: numbers_after(observed, t, read, reference) for read in READINGS}
                swap = case["swapping laws"]
                tallies["late singleton / last parity birth"][swap["last parity birth"]] += 1
                tallies["late singleton / first empty parity round"][swap["first empty parity round"]] += 1
                rise = case["at least one increase before the drop to one"]
                tallies["late singleton / a prior rise in positive birth counts"][str(rise)] += 1
                aligned = case["compared with actual lone three-place knot"]
                offsets = tuple(aligned[r]["first offset equal thereafter"] for r in READINGS)
                tallies["late singleton / first equal offset, sig0 then sig1"][str(offsets)] += 1
                tallies["late singleton / last common round of direct reference comparison"][
                    aligned["sig0"]["last common start round"]] += 1
            if fresh is not None and fresh < len(observed):
                comparison = local_relay(observed, fresh, d)
                case["last one-fresh join as a relay"] = comparison
                for read in READINGS:
                    for test, val in comparison[read].items():
                        if isinstance(val, bool):
                            tallies[f"last one-fresh join, {narrow} / {read} / {test}"][str(val)] += 1
            cases.append(case)
    return {"counts": counts_tree(tallies), "late starts": cases, "on-time controls": controls,
            "prior seven five-knot starts with M=10": old_burst}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = perf_counter()
    reference = read_lone()
    reference_prototype = next(iter(reference[2]["sig0"]))
    reference_chain = two_chains(reference_prototype, len(reference) - 3)
    if reference[3:] != reference_chain:
        raise ValueError("The two-chain description differs from the actual lone-knot archive.")
    late = {}
    for name, data in json.loads((HERE / "settling.json").read_text()).items():
        by_start = defaultdict(dict)
        for index, _, read, _, fit_end, _ in data["late start-readings"]:
            by_start[index][read] = fit_end
        late[name] = by_start
    result = {
        "prefix per paired archive": args.limit,
        "population": "Five-knot census once per start up to its symmetries; "
                      "the original uniform seeded sample of 1,000 six-knot census starts.",
        "method": "Each drop is a strict decrease between two observed positive birth counts; "
                  "the start is excluded. A singleton relay requires a drop to one and the full "
                  "suffix 1,1,2,3,... with at least four observed rounds. T is its first one. "
                  "The reference alignment pairs T with the actual lone three-place knot's third round. "
                  "Both readings count anonymous births, preserving multiplicity. Additional columns "
                  "allow a decrease from the start knot count to the first birth total, or assign "
                  "round zero or round one if the positive birth totals never decrease.",
        "lone three-place reference": {
            "source": "../LOOK-ALIKE-20261126-001/phase1_grown.jsonl.gz, one start knot on three distinctions",
            "birth counts": [row["sig0"].total() for row in reference],
            "round 3 description": list(reference_prototype),
            "two-chain formula matches both readings from round 4 through": len(reference)},
    }
    for n in (5, 6):
        before = perf_counter()
        result[str(n)] = study_size(n, args.limit, late, reference)
        result[str(n)]["elapsed seconds"] = round(perf_counter() - before, 4)
    result["elapsed seconds"] = round(perf_counter() - started, 4)
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    for n in ("5", "6"):
        print(n, result[n]["counts"]["starts"], result[n]["counts"]["not-all-equal dimension starts"],
              "seconds", result[n]["elapsed seconds"])


if __name__ == "__main__":
    main()
