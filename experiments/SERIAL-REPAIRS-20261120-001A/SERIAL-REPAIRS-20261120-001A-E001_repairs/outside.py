"""Test the whole-current formation-size restriction and a directed local variant."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from random import Random
import json
import sys

from pysat.solvers import Minisat22
from cohort import current_decision, prioritize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / BASE / f"{BASE}-E001_ordinary"))
from end_operator import End, from_stars, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "outside.json"
OVERLAP = ("Sa", "Sb", "Sc", "Tb", "Tc", "Te")
CONTROL = ("US", "VS", "WS", "SA", "AB", "BW", "AZ")


def physical_source(meetings, openings, multiplicity):
    nodes = sorted(set("".join(meetings)))
    tags = {name: (0, i) for i, name in enumerate(nodes)}
    stars = {tag: [] for tag in tags.values()}
    label = 0
    for a, b in meetings:
        for _ in range(multiplicity):
            for holder in (a, b):
                stars[tags[holder]].append((0, label))
            label += 1
    for holder in openings:
        stars[tags[holder]].append((0, label))
        label += 1
    return {tag: tuple(star) for tag, star in stars.items()}, {tag: name for name, tag in tags.items()}


def physical_tables(stars):
    holders = defaultdict(list)
    neighbors = {v: set() for v in stars}
    for holder, star in stars.items():
        assert len(star) == len(set(star))
        for distinction in star:
            holders[distinction].append(holder)
    pairs = Counter()
    for hs in holders.values():
        assert 1 <= len(hs) <= 2
        if len(hs) == 2:
            a, b = sorted(hs)
            pairs[a, b] += 1
            neighbors[a].add(b)
            neighbors[b].add(a)
    return holders, neighbors, pairs


def rank_of(words):
    pivots = {}
    for word in words:
        while word:
            pivot = word.bit_length()
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    return len(pivots)


def verify_source(stars):
    holders, _, pairs = physical_tables(stars)
    ids = {bit: i for i, bit in enumerate(holders)}
    numeric = [tuple(ids[d] for d in row) for row in stars.values()]
    from_stars(tuple(numeric))  # Includes ordinary connectivity.
    masks = [sum(1 << d for d in row) for row in numeric]
    rank = rank_of(masks)
    assert all(len(row) >= 3 for row in numeric)
    assert all(rank - rank_of([word & ~mask for word in masks]) == 1 for mask in masks)
    clauses = [[sign * (d + 1) for d in row] for row in numeric for sign in (-1, 1)]
    tested_nae = 0
    with Minisat22(bootstrap_with=clauses) as solver:
        for row in numeric:
            for assignment in range(1, (1 << len(row)) - 1):
                tests = [(d + 1) * (1 if assignment & (1 << i) else -1)
                         for i, d in enumerate(row)]
                assert solver.solve(assumptions=tests)
                tested_nae += 1
    return {"source_knots": len(stars), "distinctions": len(holders),
            "parity_star_projections": len(stars), "legal_nae_star_rows_extended": tested_nae,
            "source_pair_multiplicities": sorted(pairs.values())}


@dataclass
class View:
    roots: set
    depths: dict
    neighbors: dict
    parents: dict
    opens: dict
    supply: dict


def decode(stars):
    holders, neighbors, pairs = physical_tables(stars)
    roots = {v for pair, count in pairs.items() if count > 1 for v in pair}
    if not roots:
        return None
    depths = dict.fromkeys(roots, 0)
    search = deque(roots)
    while search:
        v = search.popleft()
        for w in neighbors[v] - depths.keys():
            depths[w] = depths[v] + 1
            search.append(w)
    assert depths.keys() == stars.keys()
    parents = {v: set() for v in stars}
    supply = {v: [] for v in stars}
    opens = {v: [] for v in stars}
    for distinction, hs in holders.items():
        if len(hs) == 1:
            opens[hs[0]].append(distinction)
            supply[hs[0]].append(distinction)
        elif not set(hs) <= roots:
            a, b = sorted(hs, key=depths.__getitem__)
            assert depths[b] == depths[a] + 1
            parents[b].add(a)
            supply[a].append(distinction)
    assert all(parents[v] or v in roots for v in stars)
    return View(roots, depths, neighbors, parents, opens, supply)


def end_on(view, cohort):
    cohort = tuple(sorted(cohort))
    index = {v: i for i, v in enumerate(cohort)}
    source = set(cohort) <= view.roots
    witnesses = (lambda v: view.neighbors[v] & view.roots) if source else view.parents.__getitem__
    blocks = defaultdict(set)
    for v in cohort:
        for holder in witnesses(v):
            blocks[holder].add(index[v])
    end = End({index[v]: len(view.supply[v]) for v in cohort}, tuple(map(tuple, blocks.values())))
    return cohort, end


def turn_counter(turn, cohort):
    return Counter((tuple(cohort[i] for i in group), d, f)
                   for group, d, f in zip(turn.parents, turn.demand, turn.fresh, strict=True))


def min_depth_menu(stars, law):
    view = decode(stars)
    if view is None:
        return "undecodable", Counter()
    occupied_depths = [view.depths[v] for v, loose in view.opens.items() if loose]
    if not occupied_depths:
        return "closed", Counter()
    depth = min(occupied_depths)
    cohort, end = end_on(view, {v for v, rank in view.depths.items() if rank == depth and view.supply[v]})
    turn = step(end, law)
    if turn.status != "extend":
        return turn.status, Counter()
    remainder = turn_counter(turn, cohort)
    for child, rank in view.depths.items():
        if rank == depth + 1:
            group = tuple(sorted(view.parents[child]))
            written = [entry for entry in remainder if entry[0] == group]
            assert len(written) == 1
            assert len(view.supply[child]) == written[0][2]
            remainder[written[0]] -= 1
            assert remainder[written[0]] >= 0
    return "extend", +remainder


@dataclass(frozen=True)
class Event:
    tag: tuple
    parents: tuple
    inputs: tuple
    demand: int
    fresh: int

    @property
    def row(self):
        return self.parents, self.demand, self.fresh

    @property
    def star(self):
        return self.inputs + tuple((1, self.tag, j) for j in range(self.fresh))


def complete_reference(source, law, limit):
    stars = dict(source)
    layers = []
    for _ in range(limit):
        keys = tuple(sorted(stars))
        current = tuple(stars[k] for k in keys)
        turn = step(from_stars(current), law)
        if turn.status != "extend":
            break
        owners, _, _ = physical_tables(stars)
        slots = {v: iter(sorted(d for d in stars[v] if len(owners[d]) == 1)) for v in keys}
        events = []
        for (group, demand, fresh), count in sorted(turn_counter(turn, keys).items()):
            for occurrence in range(count):
                tag = (1, group, occurrence)
                inputs = tuple(next(slots[v]) for v in group)
                events.append(Event(tag, group, inputs, demand, fresh))
        assert all(next(line, None) is None for line in slots.values())
        assert all(e.tag not in stars for e in events)
        stars.update({e.tag: e.star for e in events})
        layers.append(tuple(events))
    return tuple(layers), stars


def baseline_summary(layers, names):
    ancestors = {tag: {name} for tag, name in names.items()}
    results = []
    for age, layer in enumerate(layers, 1):
        children = []
        for event in layer:
            ancestors[event.tag] = set().union(*(ancestors[v] for v in event.parents))
            children.append({"ancestors": "".join(sorted(ancestors[event.tag])),
                             "parent_ancestors": ["".join(sorted(ancestors[v])) for v in event.parents],
                             "demand": event.demand, "fresh": event.fresh})
        results.append({"age": age, "births": children})
    return results


def check_all_partial_steps(source, layers, law):
    stars = dict(source)
    checked = []
    rng = Random(20261120132)
    for age, layer in enumerate(layers, 1):
        count = 0
        joins_first_count = 0
        for mask in range(1 << len(layer)):
            selected = {e.tag: e.star for i, e in enumerate(layer) if mask & (1 << i)}
            state = stars | selected
            view = decode(state)
            assert view is not None and view.roots == source.keys()
            assert all(view.depths[e.tag] == age and view.parents[e.tag] == set(e.parents)
                       for e in layer if e.tag in selected)
            expected = Counter(e.row for e in layer if e.tag not in selected)
            if not expected and age < len(layers):
                expected = Counter(e.row for e in layers[age])
            if not expected and age == len(layers) and any(view.opens.values()):
                # The final full state is a continuing unmeasured complete end.
                continue
            status, actual = min_depth_menu(state, law)
            assert status == ("extend" if expected else "closed") and actual == expected
            keys = list(state)
            rng.shuffle(keys)
            index = {v: i for i, v in enumerate(keys)}
            bits = sorted(set().union(*(set(row) for row in state.values())))
            names = list(range(len(bits)))
            rng.shuffle(names)
            renaming = dict(zip(bits, names, strict=True))
            raw = tuple(tuple(renaming[d] for d in state[k]) for k in keys)
            expected_physical = Counter({(tuple(sorted(index[j] for j in group)), fresh): n
                                         for (group, _, fresh), n in expected.items()})
            decision = current_decision(raw, law)
            assert decision.status == ("ready" if expected else "closed")
            assert decision.remaining == expected_physical
            assert prioritize(decision.remaining, False) == expected_physical
            count += 1
            join = +Counter({item: n for item, n in expected_physical.items() if len(item[0]) > 1})
            written_unary = any(len(e.parents) == 1 and e.tag in selected for e in layer)
            if not (written_unary and join and mask != (1 << len(layer)) - 1):
                assert prioritize(decision.remaining, True) == (join or expected_physical)
                joins_first_count += 1
        checked.append({"unrestricted": count, "joins_first": joins_first_count})
        stars.update({e.tag: e.star for e in layer})
    return checked


def bound_panels():
    panels = {}
    for shifted in (False, True):
        source, names = physical_source(CONTROL, "UUVVZZ" + ("WW" if shifted else "ZZ"), 9)
        laws = {}
        for law in ("parity", "nae"):
            layers, _ = complete_reference(source, law, 3)
            first = baseline_summary(layers[:1], names)[0]["births"]
            marked = [row["fresh"] for row in first if row["parent_ancestors"] == ["U", "V"]]
            assert marked == [1 if shifted else 2]
            laws[law] = {"common_UV_fresh": marked[0], "layer_births": list(map(len, layers)),
                         "partial_snapshots_checked": check_all_partial_steps(source, layers, law)}
        panels["shifted" if shifted else "quiet"] = laws
    return panels


def source_pair_check(source, names, layers):
    holder_of = {name: key for key, name in names.items()}
    b, c = holder_of["b"], holder_of["c"]
    holders, neighbors, _ = physical_tables(source)
    opens = Counter(owners[0] for owners in holders.values() if len(owners) == 1)
    witnesses = neighbors[b] & neighbors[c]
    blocks = {names[witness]: "".join(sorted(names[v] for v in neighbors[witness] if opens[v]))
              for witness in witnesses}
    assert blocks == {"S": "abc", "T": "bce"} and [opens[b], opens[c]] == [3, 3]
    asserted_if_unguarded = {witness: max(1, opens[b] + opens[c] - len(block))
                             for witness, block in sorted(blocks.items())}
    actual = [e.fresh for e in layers[0] if e.parents == tuple(sorted((b, c)))]
    assert actual == [2] and set(asserted_if_unguarded.values()) == {3}
    return {"pair": ["b", "c"], "original_open_counts": [opens[b], opens[c]],
            "witness_blocks": dict(sorted(blocks.items())),
            "identified_formula_domain": "rejected: two witness knots",
            "unguarded_fresh_prediction_using_either_witness": asserted_if_unguarded,
            "ordinary_fresh": actual[0]}


def outside_panels():
    panels = {}
    for multiplicity in (1, 2):
        source, names = physical_source(OVERLAP, "aabbbcccee", multiplicity)
        laws = {}
        for law in ("parity", "nae"):
            limit = 4 if law == "parity" else 5
            layers, final = complete_reference(source, law, limit)
            observed = baseline_summary(layers, names)
            third = observed[2]["births"]
            assert len(third) == 2 and {row["ancestors"] for row in third} == {"abce"}
            assert {frozenset(row["parent_ancestors"]) for row in third} == {
                frozenset(("abc", "bce", "abe")), frozenset(("abc", "bce", "ace"))
            }
            assert [row["fresh"] for row in observed[3]["births"]] == [int(law == "nae")]
            assert len(observed) == limit and list(map(len, layers))[:4] == [5, 4, 2, 1]
            if law == "nae":
                assert [row["fresh"] for row in observed[4]["births"]] == [2]
            if multiplicity == 1:
                # No newly shared meeting has multiplicity >1 either, so the
                # same reader has no recognizable source at any tested layer.
                prefix = dict(source)
                for layer in layers:
                    assert min_depth_menu(prefix, law)[0] == "undecodable"
                    assert current_decision(tuple(prefix.values()), law).status == "source unrecognized"
                    prefix.update({e.tag: e.star for e in layer})
                assert min_depth_menu(final, law)[0] == "undecodable"
                assert current_decision(tuple(final.values()), law).status == "source unrecognized"
                checks = None
            else:
                checks = check_all_partial_steps(source, layers, law)
            laws[law] = {"age_rosters": observed, "partial_snapshots_checked": checks,
                         "bounded_source_pair_formula_control": source_pair_check(source, names, layers),
                         "reader_status_at_source": min_depth_menu(source, law)[0],
                         "reader_status_at_final_benchmark": min_depth_menu(final, law)[0],
                         "main_reader_status_at_source": current_decision(tuple(source.values()), law).status,
                         "main_reader_status_at_final_benchmark": current_decision(tuple(final.values()), law).status}
        panels[str(multiplicity)] = {"literal_source": [[d[1] for d in row] for row in source.values()],
                                    "source_names_evaluator_only": list(names.values()),
                                    "lawfulness": verify_source(source), "laws": laws}
    return panels


def main():
    primary = bound_panels()
    outside = outside_panels()
    receipt = {"reader": "current physical supports only; global source recovery and shallowest open depth",
               "order_scope": ("all subsets within each measured complete roster on a canonical slot allocation; "
                               "a full layer boundary can be counted again as the next layer's empty subset"),
               "checks": ("independent physical reconstruction plus adjacent cohort.current_decision and "
                          "cohort.prioritize on renamed input supports; all use the archived End/step arithmetic"),
               "primary_gate": primary, "outside_identified_class": outside}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
