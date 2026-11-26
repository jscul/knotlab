"""Check the complete starting relation and compare older archives by identity."""

from collections import Counter
from functools import lru_cache
import gzip
from itertools import combinations, product
import json
from random import Random
import sys

from sampleaudit import (RESEARCH, ROOT, SHARE_ONE, canonical_start, growth_weighted_draws,
                         holdings_of, joins_all, members, neighbour_masks, parse_holdings, read_rows)


@lru_cache(maxsize=None)
def binary_variables(count):
    """Each bit denotes a state of the shared distinctions, least significant first."""
    states = 1 << count
    low_masks = (0x55, 0x33, 0x0f)
    zeros, zeros_or_ones = [], (1 << states) - 1
    for index in range(count):
        if index < 3:
            packed = bytes([low_masks[index]]) * ((states + 7) // 8)
        else:
            byte_run = 1 << (index - 3)
            packed = (bytes(byte_run) + b"\xff" * byte_run) * (states // (16 * byte_run))
        zeros.append(int.from_bytes(packed, "little") & zeros_or_ones)
    return zeros_or_ones, tuple(zeros)


@lru_cache(maxsize=None)
def feasible_shared(n, shared, dead):
    full, zeros = binary_variables(len(shared))
    per_knot = [[] for _ in range(n)]
    for place, (a, b) in enumerate(shared):
        per_knot[a].append(place)
        per_knot[b].append(place)
    possible = full
    for knot in dead:
        all_zero, all_one = full, full
        for place in per_knot[knot]:
            all_zero &= zeros[place]
            all_one &= zeros[place] ^ full
        possible &= full ^ (all_zero | all_one)
    local_states = []
    for local in per_knot:
        images = {0: possible}
        for label, place in enumerate(local):
            append = {}
            for prefix, allowed in images.items():
                left = allowed & zeros[place]
                right = allowed & ~zeros[place]
                if left:
                    append[prefix] = left
                if right:
                    append[prefix | (1 << label)] = right
            images = append
        local_states.append((len(local), tuple(images)))
    return tuple(local_states)


@lru_cache(maxsize=None)
def nae_projected_rows(shared_arity, shared_states, loose):
    arity = shared_arity + loose
    all_ones = (1 << arity) - 1
    return frozenset((state | (external << shared_arity)) for state in shared_states for external in range(1 << loose)) - {0, all_ones}


@lru_cache(maxsize=None)
def nae_rule(shared_arity, shared_states, loose):
    arity = shared_arity + loose
    allowed = nae_projected_rows(shared_arity, shared_states, loose)
    return all(len({state & ~(1 << dropped) for state in allowed}) == 1 << (arity - 1) for dropped in range(arity))


def nae_failures(shared, loose):
    # When all rules have their own loose distinction, all assignments of the
    # shared distinctions can be completed, and each projection is full NAE.
    dead = tuple(i for i, count in enumerate(loose) if not count)
    if not dead:
        return ()
    return tuple(knot for knot, (arity, states) in enumerate(feasible_shared(len(loose), shared, dead))
                 if not nae_rule(arity, states, loose[knot]))


def parity_failures(shared, loose):
    # A proper nonzero row-space restriction supported inside one holding
    # fails K2 for that rule. All-zero witnesses K3 and each row gives K1.
    if all(loose):
        return ()
    rows = [sum(1 << place for place in row) for row in holdings_of(shared, loose)]
    restrictions = [0]
    for row in rows:
        restrictions.extend([r ^ row for r in restrictions])
    return tuple(knot for knot, row in enumerate(rows)
                 if any(r and r != row and not (r & ~row) for r in restrictions))


def read_admission(census, structures, indices):
    issues = {"nae": {}, "parity": {}}
    for index in indices:
        number, loose = census.entries[index]
        shared = census.patterns[number][0]
        for law, failed in (("nae", nae_failures(shared, loose)), ("parity", parity_failures(shared, loose))):
            if failed:
                issues[law][index] = failed
    def filters(admission, weights):
        outcome = Counter()
        for index, weight in zip(indices, weights, strict=True):
            if index in admission:
                outcome["excluded from " + structures[index].read] += weight
                continue
            shape = structures[index]
            label = shape.read
            if shape.stratum == "one loose distinction" and shape.read == "accepted" and admission is issues["parity"]:
                label = "one loose"
            outcome[label] += weight
        return outcome
    return issues, {law: {"failed starts": len(failed), "failed starting rules": sum(map(len, failed.values())),
                          "coverage in the census weighting": filters(failed, [1] * len(indices)),
                          "coverage with knots numbered": filters(failed, [census.weights[i] for i in indices])}
                    for law, failed in issues.items()}


def admission_controls(census, cases, tested):
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    controls = []
    candidates = [min(tested, key=lambda i: len({p for row in census.holdings(i) for p in row}))]
    sampled_failures = [i for i in cases["uniform"]["parity"] if i in tested and
                        parity_failures(census.patterns[census.entries[i][0]][0], census.entries[i][1])]
    if sampled_failures:
        candidates.append(min(sampled_failures, key=lambda i: len({p for row in census.holdings(i) for p in row})))
    for index in set(candidates):
        stars = census.holdings(index)
        shared, loose = parse_holdings(stars)
        distinctions = 1 + max(map(max, stars))
        if distinctions > 16:
            continue
        for law in ("nae", "parity"):
            valid = [assignment for assignment in range(1 << distinctions)
                     if all((sum(bool(assignment & (1 << d)) for d in row) % 2 == 0) if law == "parity"
                            else (0 < sum(bool(assignment & (1 << d)) for d in row) < len(row)) for row in stars)]
            expected = (nae_failures if law == "nae" else parity_failures)(shared, loose)
            groups = []
            for knot, row in enumerate(stars):
                labels = tuple(f"x{d}" for d in row)
                allowed = frozenset(tuple(bool(assignment & (1 << position)) for position in row) for assignment in valid)
                checked = check_knot(Relation(labels, allowed), labels[:-1], labels[-1])
                assert checked.is_knot == (knot not in expected), (index, law, knot)
                groups.append({"K1": checked.binding, "K2": checked.loss_on_erasure, "K3": checked.coexistence,
                               "allowed states": len(allowed)})
            controls.append({"census index": index, "holdings": stars, "law": law, "rules in starting order": groups})
    return controls


def archives_of_ordinary_parity(census, failed, pilot):
    path = (ROOT / "artifacts" / "RING-IN-BALANCE-20261123-001B" / "RING-IN-BALANCE-20261123-001B-E001_reference" / "census")
    statuses = {}
    records = ["results.jsonl.gz", "extra_blocks.jsonl"]
    selected = (0, 3, 150, 401) if pilot else None
    for name in records:
        for line in read_rows(path / name):
            if not line["case"].startswith("n6-") or line["status"] != "ok":
                continue
            block = line["result"]
            if pilot and block["block"] not in selected:
                continue
            assert (block["rounds"], block["cap"]) == (10, 1500)
            base = 200 * block["block"] + line.get("start_range", [0])[0]
            for index, case in enumerate(block["starts"], base):
                assert index not in statuses and census.entries[index] == (case["g"], tuple(case["loose"]))
                if not pilot or index in failed:
                    assert case["set_aside"] == bool(failed.get(index))
                    assert tuple(case["kt"]["rank_fail"]) == tuple(case["kt"]["cut_fail"]) == failed.get(index, ())
                if case["set_aside"]:
                    statuses[index] = "set aside by knot test"
                elif case["laws"]["ordinary"].get("not_completed"):
                    statuses[index] = "run incomplete"
                else:
                    statuses[index] = "ordinary run completed"
    if not pilot:
        assert len(statuses) == len(census.entries)
    return statuses


def waiting_law_archive(parity_issues, n):
    descent = (ROOT / "artifacts" / "DESCENT-HELD-20261125-001A" /
               "DESCENT-HELD-20261125-001A-E001_order_in_own_places" / "part1_runs.json.gz")
    with gzip.open(descent, "rt") as source:
        actual = [row["idx6"] for row in json.load(source)["six_rows"]]
    if parity_issues is not None:
        numbered = list(range(n))
        Random("DESCENT-HELD-20261125-001|six|v2").shuffle(numbered)
        order = [i for i in numbered if i not in parity_issues]
        assert actual == order[:len(actual)]
    return set(actual)


def older_six_draws(census, pilot):
    known = RESEARCH / "NAE-GROWTH-20261119-001" / "referee-R1" / "referee_nae_growth.json"
    size = json.loads(known.read_text())["six"]["starts"]
    matched = []
    pairs = tuple(combinations(range(6), 2))
    for seed in range(80_000, 80_000 + (64 if pilot else size)):
        random = Random(seed)
        while True:
            loose = [random.randint(3, 5) for _ in range(6)]
            shared = []
            for _ in range(random.randint(5, 12)):
                a, b = random.choice(pairs)
                if loose[a] and loose[b]:
                    loose[a] -= 1
                    loose[b] -= 1
                    shared.append((a, b))
            if joins_all(neighbour_masks(6, shared)):
                break
        index = census.lookup(tuple(sorted(shared)), tuple(loose))
        if index is not None:
            matched.append(index)
    return matched


def check_admission_and_prior_overlap(censuses, by_n, cases, relations, prior_draws, pilot):
    six, structures = censuses[6], by_n[6]
    small = set(cases["uniform"]["nae"]) | set(cases["stratified"]["nae"]) | set(range(128))
    indices = sorted(small) if pilot else range(len(structures))
    issues, whole = read_admission(six, structures, indices)
    controls = admission_controls(six, cases, indices)
    outcomes = {}
    for which, laws in cases.items():
        outcomes[which] = {}
        for law, rows in laws.items():
            failed = nae_failures if law == "nae" else parity_failures
            retained, excluded = Counter(), []
            for index, (read, miss, _) in rows.items():
                shared, loose = relations[which][index]
                rules = failed(shared, loose)
                label = ("differ" if miss is not None else "agree") if read == "predicted" else read
                if rules:
                    excluded.append({"index": index, "rules failing K2": rules, "outcome": label})
                else:
                    retained[label] += 1
            outcomes[which][law] = {"outcomes after requiring all starting rules to pass": retained,
                                    "excluded": excluded}

    ordinary = archives_of_ordinary_parity(six, issues["parity"], pilot)
    waiting = waiting_law_archive(None if pilot else issues["parity"], len(structures))
    earlier = older_six_draws(six, pilot)
    earlier_set = set(earlier)
    prev_a, prev_b = map(set, prior_draws)
    by_six_set = {set_name: set(cases[set_name]["nae"]) for set_name in ("uniform", "stratified", "horizon")}
    by_six_set["hand-built in census at six"] = {
        index for shared, loose in relations["handbuilt"].values() if len(loose) == 6
        if (index := six.lookup(shared, loose)) is not None}
    prior_overlap = {}
    for which, selected in by_six_set.items():
        current = cases.get(which, {}).get("nae", {})
        accepted = {i for i, row in current.items() if row[0] == "predicted" and i in selected}
        if which == "hand-built in census at six":
            accepted = {i for entry, (shared, loose) in relations["handbuilt"].items() if len(loose) == 6
                        if (i := six.lookup(shared, loose)) is not None and cases["handbuilt"]["nae"][entry][0] == "predicted"}
        prior_overlap[which] = {"earlier ordinary parity runs": Counter(ordinary.get(i, "no archived block checked") for i in selected),
                                "accepted with an earlier ordinary parity run": sum(ordinary.get(i) == "ordinary run completed" for i in accepted),
                                "first prior seeded six knot sample": sorted(selected & prev_a),
                                "second prior seeded six knot sample": sorted(selected & prev_b),
                                "earlier six-knot waiting law archive": sorted(selected & waiting),
                                "earlier six-knot two-law sample": sorted(selected & earlier_set)}

    sharing = {index for index, shape in enumerate(structures) if SHARE_ONE in shape.memberships}
    omitted = {}
    combined = by_six_set["uniform"] | by_six_set["stratified"]
    for index in sorted(sharing - combined):
        number, loose = six.entries[index]
        shape = structures[index]
        omitted[index] = {"historical meeting pattern": number, "loose counts": loose, "holdings": six.holdings(index),
                          "groups": [list(members(group)) for group in shape.groups],
                          "cells": [list(members(cell)) for cell in shape.cells],
                          "first prior six-knot draw": index in prev_a, "second prior six-knot draw": index in prev_b,
                          "earlier ordinary parity run": ordinary.get(index), "earlier waiting sample": index in waiting,
                          "earlier two-law sample": index in earlier_set}

    weighted_overlap = {}
    for n in (6, 7):
        old_weighted, _ = growth_weighted_draws(64 if pilot else 2000, n, f"weightings-grow-n{n:02d}")
        old = {canonical_start(*parse_holdings(row["stars"])) for row in old_weighted}
        if n == 6:
            panels = {key: [relations[key][i] for i in ids] for key, ids in by_six_set.items() if key in relations}
        else:
            panels = {"grow7": relations["grow7"].values()}
        weighted_overlap[n] = {"prior draws regenerated": len(old_weighted), "prior distinct starts": len(old),
                               "matched draws in current sets": {key: sum(canonical_start(*row) in old for row in values)
                                                                 for key, values in panels.items()},
                               "matched distinct starts in current sets": {key: len({canonical_start(*row) for row in values} & old)
                                                                          for key, values in panels.items()}}

    return {"census starting admission": whole, "six-knot census admission cases tested under each law": len(indices),
            "direct allowed-state control": controls, "sample starting admission": outcomes,
            "ordinary parity archive coverage": Counter(ordinary.values()), "prior six knot identity intersections": prior_overlap,
            "earlier six-knot waiting archive identities checked": len(waiting),
            "earlier six-knot two-law sample identities in the census": len(earlier_set),
            "earlier six-knot two-law draws in the census": len(earlier),
            "earlier classification archive under growth weighting": weighted_overlap,
            "accepted starts with cells sharing a knot": {"all in census": len(sharing),
                                                         "all in uniform": sorted(sharing & by_six_set["uniform"]),
                                                         "all in stratified": sorted(sharing & by_six_set["stratified"]),
                                                         "outside current samples": omitted}}
