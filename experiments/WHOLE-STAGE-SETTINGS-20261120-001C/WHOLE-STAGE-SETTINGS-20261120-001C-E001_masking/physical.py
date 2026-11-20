"""Literal ordinary growth and exact physical checks for the frozen address experiment."""

import argparse
from collections import Counter, defaultdict, deque
from functools import cache
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
DONOR = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"
sys.path.insert(0, str(DONOR))
from end_operator import from_stars, proposals, step

BITS = (0, 1)
TRIPLES = tuple(product(BITS, repeat=3))
IDENTITY = (0, 1, 2)
P = (1, 0, 2)
Q = (0, 2, 1)
MODES = ("primary", "reversed", "commuting", "identity")


def columns(u, v, mode):
    if mode == "identity":
        return (IDENTITY,) * 8
    left = P if u else IDENTITY
    right = (P if mode == "commuting" else Q) if v else IDENTITY
    core = (left, right, left, right)
    if mode == "reversed":
        core = core[::-1]
    return (IDENTITY, IDENTITY, *core, IDENTITY, IDENTITY)


def local_supports(end, deficient, terminals, setting=None, saturated=False):
    center_links = tuple(f"{end}.meet{i}.{j}" for i in range(2) for j in range(2))
    center_detector = f"{end}.center_detector"
    rows = {f"{end}.center": (*center_links, center_detector)}
    for address in range(2):
        owned = center_links[2*address:2*address+2]
        owned += (f"{end}.address{address}.open0",)
        if address != deficient:
            owned += (f"{end}.address{address}.open1",)
        elif saturated:
            owned += (f"{end}.saturation_open",)
        if address == setting:
            owned += (f"{end}.setting_open",)
        rows[f"{end}.address{address}"] = owned
    rows[f"{end}.detector"] = (center_detector, f"{end}.mark", f"{end}.other", *terminals)
    return rows


def physical(u, v, mode, x=None, y=None, saturated=False):
    wiring = columns(u, v, mode)
    boundary = [tuple(f"terminal{c}.{i}" for i in range(3)) for c in range(9)]
    rows = local_supports("A", u, boundary[0], x, saturated) | local_supports("B", v, boundary[8], y, saturated)
    lanes = []
    for c, permutation in enumerate(wiring):
        for i, destination in enumerate(permutation):
            middle = (f"column{c}.{i}.mid0", f"column{c}.{i}.mid1")
            left, right = f"column{c}.{i}.left", f"column{c}.{i}.right"
            rows[left] = (boundary[c][i], *middle)
            rows[right] = (boundary[c+1][destination], *middle)
            lanes.append((left, right))
    correspondence = tuple(range(3))
    for permutation in wiring:
        correspondence = tuple(permutation[i] for i in correspondence)
    return rows, lanes, correspondence


def index(rows):
    holders = defaultdict(list)
    for holder, support in rows.items():
        assert len(support) >= 3 and len(set(support)) == len(support)
        for name in support:
            holders[name].append(holder)
    assert all(1 <= len(v) <= 2 for v in holders.values())
    return holders


def literal_round(rows, law, recode=False, offer_swap=False):
    holders = index(rows)
    keys = tuple(rows)
    order = keys[::-1] if recode else keys
    ids = {name: i for i, name in enumerate(holders)}
    if recode:
        ids = {name: 10_000 - i for name, i in ids.items()}
    end = from_stars([tuple(ids[d] for d in rows[knot]) for knot in order])
    planned = step(end, law=law)
    original_order = {name: i for i, name in enumerate(keys)}

    def group_key(group):
        return (-int(len(group) > 2), len(group), tuple(original_order[name] for name in group))

    def named(group):
        return tuple(sorted((order[i] for i in group), key=original_order.get))

    proposed = sorted((named(p) for p in proposals(end)), key=group_key)
    loose = {k: [d for d in support if len(holders[d]) == 1] for k, support in rows.items()}
    if offer_swap:
        seq = loose["A.detector"]
        seq[0], seq[1] = seq[1], seq[0]
    demand = Counter(k for group in proposed for k in group)
    deficits = {k: {"required": demand[k], "available": len(v), "shortage": demand[k] - len(v)}
                for k, v in loose.items() if demand[k] > len(v)}
    assert deficits == {order[i]: {"required": demand[order[i]], "available": len(loose[order[i]]), "shortage": shortage}
                        for i, shortage in planned.shortages}
    answer = {"status": planned.status, "proposed_groups": proposed, "deficits": deficits, "births": []}
    if deficits:
        assert planned.status == "stall"
        return answer, rows
    assert planned.status == "extend"
    # Fund each pair before spending leftover openings on their unary births.
    # Transport the physical offer order with the knot and distinction names.
    roster = proposed + [(k,) for k, ds in loose.items() for _ in range(len(ds) - demand[k])]
    by_group = defaultdict(deque)
    for g, d, q in zip(planned.parents, planned.demand, planned.fresh, strict=True):
        by_group[named(g)].append((d, q))
    assert Counter(roster) == Counter(named(g) for g in planned.parents)
    remaining = {k: iter(ds) for k, ds in loose.items()}
    grown = dict(rows)
    for i, group in enumerate(roster):
        d, q = by_group[group].popleft()
        consumed = tuple(next(remaining[k]) for k in group)
        fresh = tuple(f"birth{i}.fresh{j}" for j in range(q))
        knot = f"birth{i}"
        grown[knot] = consumed + fresh
        answer["births"].append(dict(knot=knot, parents=group, p=len(group), D=d, q=q,
                                     consumed=consumed, fresh=fresh))
    assert all(next(it, None) is None for it in remaining.values())
    assert not any(len({p[0] for p in birth["parents"]}) > 1 for birth in answer["births"])
    return answer, grown


def allowed(word, law):
    return sum(word) % 2 == 0 if law == "parity" else 0 < sum(word) < len(word)


@cache
def endpoint_factor(end, deficient, setting, law, saturated=False):
    terminals = tuple(f"terminal.{j}" for j in range(3))
    rows = local_supports(end, deficient, terminals, setting, saturated)
    internal = tuple(d for d in index(rows) if d not in terminals)
    counts = []
    projections = {k: set() for k in rows}
    for terminal_word in TRIPLES:
        count = 0
        for word in product(BITS, repeat=len(internal)):
            values = dict(zip((*terminals, *internal), (*terminal_word, *word), strict=True))
            local = {k: tuple(values[d] for d in support) for k, support in rows.items()}
            if all(allowed(vals, law) for vals in local.values()):
                count += 1
                for k, vals in local.items():
                    projections[k].add(vals)
        counts.append(count)
    assert all(counts)
    return tuple(counts), projections


@cache
def pad_factor(law):
    projections = (set(), set())
    weights = [[0, 0], [0, 0]]
    for a, b, m, n in product(BITS, repeat=4):
        if allowed((a, m, n), law) and allowed((b, m, n), law):
            weights[a][b] += 1
            projections[0].add((a, m, n))
            projections[1].add((b, m, n))
    assert all(weights[b][b] > 0 for b in BITS)
    return tuple(map(tuple, weights)), projections


def path_factor(weights, steps):
    result = ((1, 0), (0, 1))
    for _ in range(steps):
        result = tuple(tuple(sum(result[i][j] * weights[j][k] for j in BITS) for k in BITS) for i in BITS)
    return result


def terminal_weights(rows, lanes, u, v, law, correspondence, saturated=False):
    left, _ = endpoint_factor("A", u, None, law, saturated)
    right, _ = endpoint_factor("B", v, None, law, saturated)
    weights, _ = pad_factor(law)
    neighbors = {}
    for a, b in lanes:
        left_terminal, right_terminal = rows[a][0], rows[b][0]
        assert left_terminal not in neighbors
        neighbors[left_terminal] = right_terminal
    lengths, destinations = [], []
    for i in range(3):
        terminal = f"terminal0.{i}"
        depth = 0
        while terminal in neighbors:
            terminal = neighbors[terminal]
            depth += 1
        assert terminal.startswith("terminal8.")
        lengths.append(depth)
        destinations.append(int(terminal.rsplit(".", 1)[1]))
    assert tuple(destinations) == correspondence and lengths == [8, 8, 8]
    matrix = path_factor(weights, 8)
    if law == "parity":
        assert weights == ((2, 0), (0, 2)) and matrix == ((2**8, 0), (0, 2**8))
    else:
        diagonal, off = (5**8 + 1) // 2, (5**8 - 1) // 2
        assert weights == ((3, 2), (2, 3)) and matrix == ((diagonal, off), (off, diagonal))
    counts = []
    for li, a in enumerate(TRIPLES):
        row = []
        for ri, b in enumerate(TRIPLES):
            mass = left[li] * right[ri]
            for i, j in enumerate(destinations):
                mass *= matrix[a[i]][b[j]]
            row.append(mass)
        counts.append(row)
    return dict(order=["".join(map(str, bits)) for bits in TRIPLES], counts=counts, old_assignments=sum(map(sum, counts)),
                physical_lane_lengths=lengths, destinations=destinations, pad_weights=weights, path_weights=matrix,
                local_completions_A=left, local_completions_B=right)


@cache
def canonical_check(arity, words):
    names = tuple(f"x{i}" for i in range(arity))
    banned = [word for word in product(BITS, repeat=arity) if word not in words]
    cnf = ";".join(" ".join(("~" if bit else "") + name for bit, name in zip(word, names, strict=True))
                   for word in banned)
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
               "--loops", *names[:-1], "--contact", names[-1], "--json"]
    process = subprocess.run(command, cwd=ROOT, env=os.environ | {"PYTHONPATH": str(ROOT / "tools")},
                             text=True, capture_output=True, check=True)
    result = json.loads(process.stdout)
    assert result["is_knot"] and len(result["allowed"]) == len(words)
    return dict(arity=arity, allowed=len(words), K1_K2_K3=True)


def physical_projections(rows, lanes, u, v, x, y, law, births=(), saturated=False):
    # Every endpoint terminal word has a completion on its own. All pad
    # diagonals are positive, so any individual endpoint/pad allowed tuple
    # extends along each unrelated segment and through the other endpoint.
    _, left = endpoint_factor("A", u, x, law, saturated)
    _, right = endpoint_factor("B", v, y, law, saturated)
    weights, pad = pad_factor(law)
    assert all(weights[b][b] for b in BITS)
    projected = left | right
    for a, b in lanes:
        projected[a], projected[b] = pad
    for birth in births:
        # Every marked input combination is realizable: for each distinct
        # parent repair one other private old opening. Other births independently
        # have private fresh bits. Thus every word below extends to the full cut.
        assert birth["p"] in (1, 2) and birth["q"] > 0
        counts = Counter(d for k, ds in rows.items() if not k.startswith("birth") for d in ds)
        assert all(sum(counts[d] == 1 for d in rows[k]) >= 2 for k in birth["parents"])
        arity = birth["p"] + birth["q"]
        projected[birth["knot"]] = {word for word in product(BITS, repeat=arity) if allowed(word, law)}
    assert set(projected) == set(rows)
    return {name: canonical_check(len(rows[name]), frozenset(words)) for name, words in projected.items()}


def shortest(adjacency, sources, targets):
    targets = set(targets)
    seen = set(sources)
    pending = deque((s, 0) for s in sources)
    while pending:
        item, d = pending.popleft()
        if item in targets:
            return d
        for other in adjacency[item] - seen:
            seen.add(other)
            pending.append((other, d+1))
    return None


def separations(rows):
    holder_adj = {k: set() for k in rows}
    mark_adj = defaultdict(set)
    holders = index(rows)
    for owners in holders.values():
        if len(owners) == 2:
            a, b = owners
            holder_adj[a].add(b)
            holder_adj[b].add(a)
    for support in rows.values():
        for a, b in combinations(support, 2):
            mark_adj[a].add(b)
            mark_adj[b].add(a)
    live = {owners[0] for owners in holders.values() if len(owners) == 1}
    end_adj = {k: set() for k in live}
    for neighbors in holder_adj.values():
        for a, b in combinations(neighbors & live, 2):
            end_adj[a].add(b)
            end_adj[b].add(a)
    return dict(address_holder_steps=shortest(holder_adj, ["A.address0", "A.address1"], ["B.address0", "B.address1"]),
                detector_holder_steps=shortest(holder_adj, ["A.detector"], ["B.detector"]),
                detector_mark_steps=shortest(mark_adj, ["A.mark"], ["B.mark"]),
                detector_witnessed_steps=shortest(end_adj, ["A.detector"], ["B.detector"]),
                separation_invariant="No shared descendant across the distinct witnessed parts in funded continuing rounds.")


def accessible(rows, end):
    column = 0 if end == "A" else 7
    local = {name: ds for name, ds in rows.items() if name.startswith((f"{end}.", f"column{column}."))}
    old_local_names = {d for ds in local.values() for d in ds}
    births = {name: ds for name, ds in rows.items() if name.startswith("birth") and old_local_names.intersection(ds)}
    local.update(births)
    holders = index(rows)
    return dict(supports=local, own_birth_supports=births,
                owned_distinctions={d: holders[d] for ds in local.values() for d in ds})


def check_exposed_incidence(by_type, births_per_side=3):
    old, final = {}, {}
    for type_word, record in by_type.items():
        for i, end in enumerate("AB"):
            key = end, type_word[i]
            local = record["pre_accessible"][end]
            assert old.setdefault(key, local) == local
        for law, values in record["laws"].items():
            for setting_word, trial in values["trials"].items():
                funded = trial["ordinary_round"]["status"] == "extend"
                for i, end in enumerate("AB"):
                    key = law, end, type_word[i], setting_word[i], funded
                    local = trial["post_accessible"][end]
                    assert len(local["own_birth_supports"]) == births_per_side * funded
                    assert final.setdefault(key, local) == local
    return dict(old_local_regions=len(old), final_local_regions=len(final),
                verdict="Exposed incidence depends only on own label, own setting and whether the round funds.")


def saturated_control():
    types = {}
    for u, v in product(BITS, repeat=2):
        old, lanes, correspondence = physical(u, v, "primary", saturated=True)
        record = dict(old_supports=old, correspondence=correspondence,
                      pre_accessible={e: accessible(old, e) for e in "AB"}, laws={})
        types[f"{u}{v}"] = record
        for law in ("parity", "nae"):
            old_checks = physical_projections(old, lanes, u, v, None, None, law, saturated=True)
            trials = {}
            record["laws"][law] = dict(old_terminal_weights=terminal_weights(old, lanes, u, v, law, correspondence,
                                                                           saturated=True), trials=trials,
                                       old_projection_arities=sorted({test["arity"] for test in old_checks.values()}))
            for x, y in product(BITS, repeat=2):
                edited, _, _ = physical(u, v, "primary", x, y, saturated=True)
                turn, grown = literal_round(edited, law)
                assert turn["status"] == "extend" and not turn["deficits"]
                assert Counter((b["p"], b["D"], b["q"]) for b in turn["births"]) == {(2,2,2): 4, (2,1,1): 2, (1,2,2): 2}
                unary_inputs = {b["consumed"] for b in turn["births"] if b["p"] == 1}
                assert unary_inputs == {("A.setting_open",), ("B.setting_open",)}
                holders = index(grown)
                mark_holders = {e: holders[f"{e}.mark"] for e in "AB"}
                assert all(len(owners) == 2 for owners in mark_holders.values())
                recoded, restored = literal_round(edited, law, recode=True)
                assert turn == recoded and grown == restored
                checks = physical_projections(grown, lanes, u, v, x, y, law, turn["births"], saturated=True)
                trials[f"{x}{y}"] = dict(edited_supports={k: edited[k] for k in edited if edited[k] != old[k]},
                                           ordinary_round=turn, post_mark_holders=mark_holders,
                                           post_accessible={e: accessible(grown, e) for e in "AB"},
                                           recoding_matches=True, supports_passing_K1_K2_K3=len(checks))

    exposure = check_exposed_incidence(types, births_per_side=4)
    # Keep one exact copy of each repeated exposed record and refer to it by key.
    regions = {}
    for type_word, record in types.items():
        for law, values in record["laws"].items():
            for setting_word, trial in values["trials"].items():
                keys = {e: f"{law}.{e}.{type_word[i]}.{setting_word[i]}" for i, e in enumerate("AB")}
                for e, local in trial.pop("post_accessible").items():
                    regions[keys[e]] = local
                trial["post_accessible_keys"] = keys
    return dict(types=types, exposure=exposure, distinct_post_accessible_records=regions)


def run():
    receipts = {}
    for mode in MODES:
        by_type = {}
        receipts[mode] = by_type
        for u, v in product(BITS, repeat=2):
            base, lanes, correspondence = physical(u, v, mode)
            record = dict(old_supports=base, correspondence=correspondence, pre_accessible={e: accessible(base, e) for e in "AB"},
                          separations=separations(base), laws={})
            by_type[f"{u}{v}"] = record
            for law in ("parity", "nae"):
                trials = {}
                record["laws"][law] = dict(old_projection_checks=physical_projections(base, lanes, u, v, None, None, law),
                                            old_terminal_weights=terminal_weights(base, lanes, u, v, law, correspondence),
                                            trials=trials)
                for x, y in product(BITS, repeat=2):
                    edited, _, _ = physical(u, v, mode, x, y)
                    round_result, grown = literal_round(edited, law)
                    funded = x == u and y == v
                    assert (round_result["status"] == "extend") == funded
                    expected_deficits = {f"{e}.address{r}" for e, r, setting in (("A", u, x), ("B", v, y)) if r != setting}
                    assert round_result["deficits"].keys() == expected_deficits
                    assert all(row["shortage"] == 1 for row in round_result["deficits"].values())
                    mark_holders = {e: index(grown)[f"{e}.mark"] for e in "AB"}
                    assert all(len(mark_holders[e]) == 1 + funded for e in "AB")
                    recoded, restored = literal_round(edited, law, recode=True)
                    assert recoded == round_result and restored == grown
                    swapped, swapped_grown = literal_round(edited, law, offer_swap=True)
                    assert all(len(index(swapped_grown)[f"{e}.mark"]) == 1 + funded for e in "AB")
                    swapped_changes = [b["knot"] for a, b in zip(round_result["births"], swapped["births"], strict=True)
                                       if a["consumed"] != b["consumed"]]
                    assert len(swapped_changes) == 2 * funded
                    after = physical_projections(grown, lanes, u, v, x, y, law, round_result["births"])
                    assert after == physical_projections(swapped_grown, lanes, u, v, x, y, law, swapped["births"])
                    trials[f"{x}{y}"] = dict(edited_supports={k: edited[k] for k in edited if edited[k] != base[k]},
                                               edited_projection_checks=physical_projections(edited, lanes, u, v, x, y, law),
                                               post_projection_checks=after,
                                               ordinary_round=round_result, post_mark_holders=mark_holders, recoding_matches=True,
                                               offer_swap_changed_births=swapped_changes, offer_swap_round=swapped,
                                               post_accessible={e: accessible(grown, e) for e in "AB"})
    return dict(freeze="0bccf6f1c0", receiver_marks={e: f"{e}.mark" for e in "AB"},
                detector_terminals=("terminal0.0", "terminal8.0"), guards_each_end=2, observer_guard_columns=(0, 7),
                exposed_incidence={mode: check_exposed_incidence(cases) for mode, cases in receipts.items()},
                saturated=saturated_control(),
                expanded_access=("Support ownership at a remote switch reveals its preparation bit. With own setting "
                                 "equal to own label, the event remote label zero and funded occurs for remote setting "
                                 "zero only. Each additional identity pad per lane delays switch visibility by two "
                                 "shared-holder steps."), modes=receipts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(), sort_keys=True, separators=(",", ":")) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
