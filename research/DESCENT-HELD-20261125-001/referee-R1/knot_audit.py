"""Recount part 7 and project allowed states for small independent runs."""

import argparse
from collections import Counter, defaultdict
from gzip import open as gzip_open
from itertools import combinations, product
from json import dumps, load, loads
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "DESCENT-HELD-20261125-001A"
INPUT = ROOT / "research" / TICKET
ARTIFACTS = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_order_in_own_places"
FORMS = {
    "base": "None",
    "NEXT3-PLACES (usable)": "PU",
    "NEXT3-PLACES (barred)": "PB",
    "NEXT3-BARRED": "BB",
}
STARTS = loads((INPUT / "starts.json").read_text())["starts"]
LAWS = loads((INPUT / "laws.json").read_text())
RING = tuple(tuple(row) for row in STARTS["TRIANGLE"]["stars"])
SEPARATE = RING + ((6, 7, 8),)
TWO_PLACE_CLOSING_START = ((0, 1, 4), (2, 3, 5), (0, 1, 2, 3))


def source(name):
    path = ARTIFACTS / name
    if path.suffix == ".gz":
        with gzip_open(path, "rt") as stream:
            return load(stream)
    return loads(path.read_text())


def recount(part4):
    recorded = source("part7.json")
    part6 = source("part6.json")["rows"]
    sizes = {}
    for row in part4["runs"]:
        for form, outcome in row["forms"].items():
            short_form = FORMS.get(form, form)
            key = ("part4", row["start"], row["law"], short_form, row["knot_law"])
            sizes[key] = outcome["knots"]
    for row in part6:
        key = ("part6", row["start"], row["law"], FORMS[row["form"]], "parity")
        sizes[key] = row["knots"]

    bases = [law["name"] for law in LAWS["recorded"] + LAWS["holding"] if law["base"]]
    order = [
        ("part4", start, base, form, knot_law)
        for start, base, form, knot_law in product(
            STARTS, bases, FORMS.values(), ("parity", "nae")
        )
    ]
    order += [
        ("part6", row["start"], row["law"], FORMS[row["form"]], "parity")
        for row in part6
    ]
    assert len(order) == len(set(order)) == len(sizes) == recorded["jobs"]
    assert set(order) == set(sizes)

    def job(row):
        return row["from"], row["start"], row["law"], FORMS[row["form"]], row["knot_law"]

    prefix = recorded["runs"]
    later = recorded[
        "finished_beyond_prefix (run past the registered order of the cut, reported separately)"
    ]
    missing = [tuple(row) for row in recorded["not_run"]]
    assert [job(row) for row in prefix] == order[: len(prefix)]
    positions = {key: index for index, key in enumerate(order)}
    finished_keys = set()
    for row in prefix + later:
        key = job(row)
        assert key not in finished_keys
        finished_keys.add(key)
        assert row["knots"] == sizes[key]
        for count, examples in (("n_fail", "fail"), ("n_disagree", "disagree"),
                                ("n_untested", "untested")):
            assert len(row.get(examples, [])) == min(50, row.get(count, 0))
    assert [positions[job(row)] for row in later] == sorted(positions[job(row)] for row in later)
    assert missing == [key for key in order if key not in finished_keys]
    assert len(prefix) == positions[missing[0]] == recorded["prefix_jobs"]

    results = {}
    for label, rows in (("registered_prefix", prefix), ("completed_after_prefix", later)):
        by_law = {}
        for knot_law in ("parity", "nae"):
            subset = [row for row in rows if row["knot_law"] == knot_law]
            start_knots = sum(STARTS[row["start"]]["knots"] for row in subset)
            final_knots = sum(row["knots"] for row in subset)
            compared = []
            for row in subset:
                if knot_law == "parity":
                    compared.append((row["knots"], STARTS[row["start"]]["knots"]))
                elif row["knots"] <= 150:
                    small_starts = sum(len(places) <= 7 for places in STARTS[row["start"]]["stars"])
                    assert row["n_untested"] == 0
                    assert small_starts <= row["direct_checked"]
                    compared.append((row["direct_checked"], small_starts))
                else:
                    assert row["direct_checked"] == 0
                    compared.append((0, 0))
            two_methods = sum(total for total, _ in compared)
            compared_starts = sum(starts for _, starts in compared)
            by_law[knot_law] = {
                "runs": len(subset),
                "final_knots": final_knots,
                "start_knots": start_knots,
                "new_knots": final_knots - start_knots,
                "two_methods_runs": sum(total > 0 for total, _ in compared),
                "two_methods_knots": two_methods,
                "two_methods_start_knots": compared_starts,
                "two_methods_new_knots": two_methods - compared_starts,
                "reported_failures": sum(row["n_fail"] for row in subset),
                "reported_disagreements": sum(row["n_disagree"] for row in subset),
                "reported_untested_knots_within_completed_runs": sum(
                    row.get("n_untested", 0) for row in subset
                ),
            }
        results[label] = by_law

    results["without_results"] = {}
    for knot_law in ("parity", "nae"):
        subset = [key for key in missing if key[-1] == knot_law]
        untested_final = sum(sizes[key] for key in subset)
        untested_start = sum(STARTS[key[1]]["knots"] for key in subset)
        results["without_results"][knot_law] = {
            "runs": len(subset),
            "by_source": dict(Counter(key[0] for key in subset)),
            "by_form": dict(Counter(key[3] for key in subset)),
            "by_start": dict(Counter(key[1] for key in subset)),
            "final_knots_recorded_in_parts_4_and_6": untested_final,
            "start_knots": untested_start,
            "new_knots_recorded_in_parts_4_and_6": untested_final - untested_start,
            "largest_final_roster": max(sizes[key] for key in subset),
        }
    results["first_run_without_result"] = list(missing[0])
    results["methods"] = {
        "parity": "ranks and kernel",
        "nae": "decomposed for every final knot in a completed run and direct for arity at most 7 in a final roster of at most 150 knots",
        "two_methods_start_knots": "final roster sizes and unchanged arities of the start knots determine the direct-test start count",
        "without_results": "roster sizes were recorded by the growth runs and were counted here as untested in part 7",
    }
    return results


def closing_control():
    rows = [row for row in source("part8.json.gz")["named"] if row["knot_law"] == "parity"]
    tested = [row for row in rows if row["closing_swap"].get("closing_knots")]
    knots = [knot for row in tested for knot in row["closing_swap"]["closing_knots"]]
    assert all(len(row["closing_swap"]["closing_knots"]) == row["closing_swap"]["closing_births"]
               for row in tested)
    return {
        "named_parity_runs": len(rows),
        "runs_with_a_swapped_closing_birth": len(tested),
        "swapped_closing_births": len(knots),
        "swapped_closing_births_with_fresh_distinctions": sum(k["F"] + k["s"] > 0 for k in knots),
        "swapped_closing_births_failing_at_their_own_round": sum(
            k["fails_parity_after_its_round"] for k in knots
        ),
        "reported_disagreements": sum(len(row["closing_swap"]["parity_disagree"]) for row in tested),
    }


def holders(places):
    out = defaultdict(set)
    for knot, distinctions in enumerate(places):
        for distinction in distinctions:
            out[distinction].add(knot)
    assert all(len(owners) <= 2 for owners in out.values())
    return out


def groups(places, roster):
    meetings = [set() for _ in places]
    for owners in holders(places).values():
        if len(owners) == 2:
            first, second = sorted(owners)
            meetings[first].add(second)
            meetings[second].add(first)
    met_sets = [meet & roster for meet in meetings if len(meet & roster) >= 2]
    joinable = {frozenset(pair) for met in met_sets for pair in combinations(met, 2)}
    large_groups = []
    assert len(roster) < 20, "Subset search is restricted to the selected small runs"
    for size in range(len(roster), 2, -1):
        for group in combinations(sorted(roster), size):
            members = frozenset(group)
            if any(members <= met for met in met_sets + large_groups):
                continue
            if all(frozenset(pair) in joinable for pair in combinations(group, 2)):
                large_groups.append(members)
    pairs = [pair for pair in joinable if all(not pair <= group for group in large_groups)]
    return sorted(tuple(sorted(group)) for group in large_groups + pairs)


def advance(places, barred, knot_law, ration, treatment, form, closing_swap, fillers=False):
    ownership = holders(places)
    loose = {distinction for distinction, owners in ownership.items() if len(owners) == 1}
    usable = {
        knot: sorted(set(row) & (loose - barred))
        for knot, row in enumerate(places)
        if set(row) & (loose - barred)
    }
    all_groups = groups(places, set(usable))
    owing = Counter(knot for group in all_groups for knot in group)
    short = {knot for knot in usable if owing[knot] > len(usable[knot])}
    if treatment == "STALL" and short:
        return places, barred, [], "stall"
    assert not short or treatment == "CANCEL-OFFSHOOT"
    parents = [group for group in all_groups if not short.intersection(group)]
    taken = [tuple(usable[knot].pop(0) for knot in group) for group in parents]
    for knot, distinctions in usable.items():
        for distinction in distinctions:
            parents.append((knot,))
            taken.append((distinction,))
    if not taken:
        return places, barred, [], "no change"
    first = len(places)
    demand = Counter(
        knot for group in groups(places + tuple(taken), set(range(first, first + len(taken))))
        for knot in group
    )
    next_distinction = max(ownership) + 1
    births = []
    new_places = []
    new_barred = set(barred)
    for index, (taken_row, parent_group) in enumerate(zip(taken, parents, strict=True), first):
        closes = knot_law == "parity" and set(taken_row) == loose
        if ration == "ORD":
            count = max(demand[index], 3 - len(taken_row), 1)
        elif ration.startswith("CAP-"):
            count = min(int(ration.removeprefix("CAP-")), max(demand[index], 3 - len(taken_row), 1))
        elif ration.startswith("RATION-"):
            count = max(int(ration.removeprefix("RATION-")), 3 - len(taken_row))
        else:
            assert ration == "FLOOR1"
            count = max(3 - len(taken_row), 1)
        if closes and not closing_swap:
            count = 0
        extra = 0
        if form != "None" and (not closes or closing_swap):
            if form == "BB":
                parent_counts = {len(barred.intersection(places[knot])) % 3 for knot in parent_group}
                initial_count = max(count - demand[index], 0) if fillers else 0
            else:
                parent_counts = {len(places[knot]) % 3 for knot in parent_group}
                initial_count = len(taken_row) + count
            if len(parent_counts) == 1:
                extra = (parent_counts.pop() + 1 - initial_count) % 3
        fresh = tuple(range(next_distinction, next_distinction + count + extra))
        next_distinction += len(fresh)
        if fillers:
            fresh_for_base = fresh if form == "PU" else fresh[:count]
            new_barred.update(fresh_for_base[demand[index]:])
        if form in {"PB", "BB"}:
            new_barred.update(fresh[count:])
        new_places.append(taken_row + fresh)
        births.append({
            "knot": index, "parents": parent_group, "taken": taken_row, "fresh": fresh,
            "closing_candidate": closes, "demand": demand[index],
        })
    return places + tuple(new_places), frozenset(new_barred), births, "birth"


def registered_closing_arities(part4):
    parity_part7 = source("part7.json")
    tested = {
        (row["start"], row["law"], FORMS[row["form"]])
        for row in parity_part7["runs"]
        + parity_part7["finished_beyond_prefix (run past the registered order of the cut, reported separately)"]
        if row["knot_law"] == "parity"
    }
    laws = {law["name"]: law for law in LAWS["recorded"] + LAWS["holding"]}
    arities = Counter()
    rows = []
    for row in part4["runs"]:
        if row["knot_law"] != "parity":
            continue
        start = row["start"]
        law = laws[row["law"]]
        for form, recorded in row["forms"].items():
            if not recorded["closing_births"]:
                continue
            form = FORMS.get(form, form)
            places = tuple(tuple(p) for p in STARTS[start]["stars"])
            barred = frozenset()
            by_round = []
            closings = []
            for _ in recorded["births"]:
                places, barred, births, _ = advance(
                    places, barred, "parity", law["ration"], law["treatment"], form, False,
                    fillers="FILLERS" in law.get("extras", []),
                )
                by_round.append(len(births))
                closings.extend(len(birth["taken"]) for birth in births if birth["closing_candidate"])
            assert by_round == recorded["births"] and len(places) == recorded["knots"]
            assert len(closings) == recorded["closing_births"]
            assert (start, row["law"], form) in tested
            arities.update(closings)
            rows.append({"start": start, "ration_and_treatment": row["law"], "form": form,
                         "closing_arities": closings})
    return {
        "scope": "all recorded parity closing births in part 4, each of which received its part 7 test",
        "closing_runs": len(rows),
        "arities": dict(sorted(arities.items())),
        "rows": rows,
    }


def completion(row_masks, fixed, ones, knot_law):
    """Decide extension by searching assignments and enforcing each allowed row."""
    while True:
        prior = fixed
        choice = 0
        choice_size = float("inf")
        for row in row_masks:
            missing = row & ~fixed
            present_ones = row & ones
            if knot_law == "parity":
                required = present_ones.bit_count() % 2
                if not missing:
                    if required:
                        return False
                    continue
            else:
                present_zeroes = row & fixed & ~ones
                if present_ones and present_zeroes:
                    continue
                if not missing or (not (present_ones or present_zeroes) and missing.bit_count() == 1):
                    return False
                required = bool(present_zeroes)
            size = missing.bit_count()
            if size == 1:
                fixed |= missing
                if required:
                    ones |= missing
            elif size < choice_size:
                choice, choice_size = missing & -missing, size
        if fixed == prior:
            if not choice:
                return True
            fixed |= choice
            return completion(row_masks, fixed, ones, knot_law) or completion(
                row_masks, fixed, ones | choice, knot_law
            )


def projection(places, knot, knot_law):
    row_masks = [sum(1 << d for d in row) for row in places]
    target = places[knot]
    return {
        "".join(map(str, bits))
        for bits in product((0, 1), repeat=len(target))
        if completion(
            row_masks,
            row_masks[knot],
            sum(1 << d for d, bit in zip(target, bits, strict=True) if bit),
            knot_law,
        )
    }


def brute_projection(places, knot, knot_law):
    distinct = sorted(holders(places))
    row_masks = [sum(1 << distinct.index(d) for d in row) for row in places]
    projected = set()
    for state in range(1 << len(distinct)):
        if knot_law == "parity":
            allowed = all((state & row).bit_count() % 2 == 0 for row in row_masks)
        else:
            allowed = all((state & row) not in (0, row) for row in row_masks)
        if allowed:
            projected.add("".join(str((state >> distinct.index(d)) & 1) for d in places[knot]))
    return projected


def gates(relation, arity):
    erased = [{row[:i] + row[i + 1 :] for row in relation} for i in range(arity)]
    return {
        "K1": len(relation) < 2**arity,
        "K2": all(len(part) == 2 ** (arity - 1) for part in erased),
        "K3": bool(relation),
        "arity_allows_two_loops_and_contact": arity >= 3,
        "forgetting_counts": [len(part) for part in erased],
    }


def snapshot_check(places, knot_law, first_seen):
    tables = [projection(places, knot, knot_law) for knot in range(len(places))]
    verdicts = [gates(table, len(places[knot])) for knot, table in enumerate(tables)]
    return {
        "knots": len(places),
        "failed_knots": [knot for knot, result in enumerate(verdicts)
                         if not all(result[g] for g in ("K1", "K2", "K3"))],
        "changed_since_birth": [knot for knot, (old, new) in enumerate(zip(first_seen, tables))
                                if old != new],
    }, tables


def replay(places, knot_law, ration, treatment="STALL", form="None", closing_swap=False, limit=8):
    snapshots = []
    first_seen = []
    born_rows = []
    starts = places
    barred = frozenset()
    births_by_round = []
    for round_number in range(limit + 1):
        if round_number:
            places, barred, births, status = advance(
                places, barred, knot_law, ration, treatment, form, closing_swap
            )
            births_by_round.append(len(births))
            born_rows.extend({"round": round_number, **row} for row in births)
        else:
            status = "start"
        summary, tables = snapshot_check(places, knot_law, first_seen)
        first_seen.extend(tables[len(first_seen) :])
        snapshots.append({"round": round_number, "outcome": status, **summary})
        if status in {"stall", "no change"}:
            break
    return {
        "knot_law": knot_law,
        "start_places": starts,
        "births_by_round": births_by_round,
        "snapshots": snapshots,
        "first_birth": born_rows[0],
        "closing_candidates": [row for row in born_rows if row["closing_candidate"]],
    }, places


def certificate(places, knot, knot_law):
    target = places[knot]
    table = projection(places, knot, knot_law)
    assert table == brute_projection(places, knot, knot_law)
    return {
        "knot_law": knot_law, "places_by_knot": places, "target_knot": knot,
        "target_places": target, "allowed_states": sorted(table), **gates(table, len(target)),
    }


def small_checks(part4, pilot):
    cases = [
        ("three-knot ring with one loose distinction each", "TRIANGLE", RING,
         "parity", "ORD", "STALL", "None", False, 8),
        ("three-knot ring with one loose distinction each and a separate three-place knot",
         None, SEPARATE, "parity", "ORD", "STALL", "None", False, 1),
        ("two live three-place knots meeting one dead four-place common knot",
         None, TWO_PLACE_CLOSING_START, "parity", "ORD", "STALL", "None", False, 2),
    ]
    if not pilot:
        cases += [
            ("lone three-place knot", "LONE-THREE", ((0, 1, 2),), "parity", "ORD", "STALL", "None", False, 8),
            ("lone three-place knot", "LONE-THREE", ((0, 1, 2),), "parity", "FLOOR1", "CANCEL-OFFSHOOT", "None", False, 8),
            ("lone three-place knot", "LONE-THREE", ((0, 1, 2),), "nae", "FLOOR1", "CANCEL-OFFSHOOT", "None", False, 8),
            ("three-knot ring with one loose distinction each", "TRIANGLE", RING, "nae", "ORD", "STALL", "None", False, 8),
            ("three-knot ring with one loose distinction each, barred-count form", "TRIANGLE", RING,
             "parity", "ORD", "STALL", "BB", False, 8),
            ("three-knot ring with one loose distinction each, barred-count form", "TRIANGLE", RING,
             "nae", "ORD", "STALL", "BB", False, 8),
            ("three-knot ring with one loose distinction each, closing swap and places count", "TRIANGLE", RING,
             "parity", "ORD", "STALL", "PB", True, 2),
            ("three-knot ring with one loose distinction each, closing swap and barred count", "TRIANGLE", RING,
             "parity", "ORD", "STALL", "BB", True, 2),
            ("three-knot ring with one loose distinction each and a separate three-place knot",
             None, SEPARATE, "nae", "ORD", "STALL", "None", False, 1),
            ("three-knot ring with one loose distinction each and a separate three-place knot, barred-count form",
             None, SEPARATE, "parity", "ORD", "STALL", "BB", False, 1),
        ]
    by_part4_run = {(row["start"], row["law"], row["knot_law"]): row["forms"] for row in part4["runs"]}
    audit = []
    certificates = []
    for label, start, places, knot_law, ration, treatment, form, swap, limit in cases:
        result, final_places = replay(places, knot_law, ration, treatment, form, swap, limit)
        result.update({"case": label, "ration": ration, "form": form, "closing_swap": swap})
        if start and not swap:
            law_name = "ORD" if ration == "ORD" else "F1O"
            key = "base" if form == "None" else form
            recorded = by_part4_run[start, law_name, knot_law][key]
            assert result["births_by_round"] == recorded["births"]
            assert len(final_places) == recorded["knots"]
            assert not any(s["failed_knots"] or s["changed_since_birth"] for s in result["snapshots"])
            result["recorded_final_count_and_births_match"] = True
        if label.endswith("separate three-place knot") and knot_law == "parity":
            assert result["snapshots"][0]["failed_knots"] == []
            assert result["snapshots"][1]["failed_knots"] == [4]
            certificates.append({"case": label, **certificate(final_places, 4, knot_law)})
        elif places == TWO_PLACE_CLOSING_START:
            assert not any(s["failed_knots"] or s["changed_since_birth"] for s in result["snapshots"])
            assert result["births_by_round"] == [1, 0]
            certificates.extend(
                {"case": label, **certificate(final_places, knot, knot_law)}
                for knot in range(len(final_places))
            )
        elif swap or label.endswith("barred-count form") and start is None:
            first_places, _, _, _ = advance(places, frozenset(), knot_law, ration, treatment, form, swap)
            certificates.append({"case": label, **certificate(first_places, len(places), knot_law)})
        elif start == "TRIANGLE" and limit == 8 and form == "None":
            first_places, _, _, _ = advance(places, frozenset(), knot_law, ration, treatment, form, swap)
            certificates.append({"case": label, **certificate(first_places, len(places), knot_law)})
        audit.append(result)

    connected = ((0, 1, 2), (0, 1, 2, 3))
    for knot_law in ("parity", "nae"):
        certificates.append({
            "case": "connected allowed start sharing all three places of one knot with a four-place knot",
            **certificate(connected, 1, knot_law),
        })
    initial_knots = {}
    for knot_law in ("parity", "nae"):
        by_start = {}
        for start, data in (list(STARTS.items())[:2] if pilot else STARTS.items()):
            summary, _ = snapshot_check(tuple(tuple(row) for row in data["stars"]), knot_law, [])
            by_start[start] = summary
        initial_knots[knot_law] = by_start
    return {"runs": audit, "explicit_projection_certificates": certificates, "named_start_knots": initial_knots}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Run the same checks on the initial small cases")
    args = parser.parse_args()
    part4 = source("part4.json")
    result = {
        "part7_recount": recount(part4),
        "part8_closing_swap_recount": closing_control(),
        "registered_parity_closing_arities": registered_closing_arities(part4),
        "independent_allowed_state_checks": small_checks(part4, args.pilot),
    }
    output = dumps(result, indent=2) + "\n"
    if args.pilot:
        print(output, end="")
    else:
        (HERE / "knot_counts.json").write_text(output)


if __name__ == "__main__":
    main()
