"""Physical replay of all-parent packets and witness erasure under ordinary growth."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from random import Random
import json
import sys

from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / BASE / f"{BASE}-E001_ordinary"))
from end_operator import End, from_stars, neighbors, restricted, step

LAWS = ("parity", "nae")
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "controls.json"


def supports(size, meetings, loose):
    stars = [[] for _ in range(size)]
    for distinction, (a, b) in enumerate(meetings):
        stars[a].append(distinction)
        stars[b].append(distinction)
    for distinction, a in enumerate(loose, len(meetings)):
        stars[a].append(distinction)
    return tuple(map(tuple, stars))


def owners_of(stars):
    owners = defaultdict(list)
    for knot, star in enumerate(stars):
        assert len(star) == len(set(star))
        for distinction in star:
            owners[distinction].append(knot)
    assert all(1 <= len(row) <= 2 for row in owners.values())
    return owners


def reachable(adj, root, ignore=None):
    seen = {root}
    todo = [root]
    for v in todo:
        added = adj[v] - seen - {ignore}
        seen.update(added)
        todo.extend(added)
    return seen


def certify_source(stars):
    owners = owners_of(stars)
    assert all(len(row) >= 3 for row in stars)
    exterior = len(stars)
    wired = [set() for _ in range(exterior + 1)]
    for holders in owners.values():
        a, b = holders if len(holders) == 2 else (*holders, exterior)
        wired[a].add(b)
        wired[b].add(a)
    assert all(len(reachable(wired, exterior, v)) == exterior for v in range(exterior))
    from_stars(stars)  # Ordinary connectivity before attaching the auxiliary exterior.
    clauses = [[(d + 1) * sign for d in row] for row in stars for sign in (-1, 1)]
    local_rows = 0
    with Minisat22(bootstrap_with=clauses) as sat:
        for star in stars:
            for assignment in range(1, (1 << len(star)) - 1):
                assert sat.solve(assumptions=[
                    (d + 1) * (1 if assignment & (1 << i) else -1) for i, d in enumerate(star)
                ])
                local_rows += 1
    return {"knots": len(stars), "distinctions": len(owners), "supports": stars,
            "parity_full_star_projections": len(stars), "nae_local_rows_extended": local_rows}


@dataclass(frozen=True)
class Frame:
    stars: tuple
    parents: dict
    fresh: dict

    @property
    def end(self):
        return from_stars(self.stars)


def grow(frame, law):
    turn = step(frame.end, law)
    assert turn.status == "extend"
    owners = owners_of(frame.stars)
    use = [iter(d for d in row if len(owners[d]) == 1) for row in frame.stars]
    fresh_bit = max(owners) + 1
    parents, fresh = {}, {}
    new = list(frame.stars)
    for group, arity in zip(turn.parents, turn.fresh, strict=True):
        parents[len(new)], fresh[len(new)] = group, arity
        spent = tuple(next(use[parent]) for parent in group)
        new.append(spent + tuple(range(fresh_bit, fresh_bit + arity)))
        fresh_bit += arity
    assert all(next(slots, None) is None for slots in use)
    return Frame(tuple(new), parents, fresh)


def history(stars, law, rounds):
    frames = [Frame(stars, {}, {})]
    for _ in range(rounds):
        if not frames[-1].end.opens:
            break
        frames.append(grow(frames[-1], law))
    return frames


def components(end):
    adjacency = neighbors(end)
    left = set(adjacency)
    result = []
    while left:
        component = reachable(adjacency, min(left))
        left -= component
        result.append(component)
    return sorted(result, key=lambda row: (len(row), min(row)))


def book(frame):
    return {"new_knots": len(frame.parents), "live_knots": len(frame.end.opens),
            "accumulated_knots": len(frame.stars), "distinct_positions": len(owners_of(frame.stars)),
            "component_widths": list(map(len, components(frame.end)))}


def check_relabeling(frame, law):
    rng = Random(20261120711)
    count = len(frame.stars)
    order = list(range(count))
    rng.shuffle(order)
    translated_knot = {old: new for new, old in enumerate(order)}
    bits = sorted(owners_of(frame.stars))
    translations = bits.copy()
    rng.shuffle(translations)
    translated_bit = dict(zip(bits, translations, strict=True))
    relabeled = tuple(tuple(translated_bit[d] for d in frame.stars[v]) for v in order)
    first, second = step(frame.end, law), step(from_stars(relabeled), law)
    assert first.status == second.status and first.implied == second.implied
    expected = Counter((tuple(sorted(translated_knot[v] for v in parents)), fresh)
                       for parents, fresh in zip(first.parents, first.fresh, strict=True))
    assert Counter(zip(second.parents, second.fresh, strict=True)) == expected
    return True


def ring_stars(width, spare=False):
    meetings = [(i, (i + 1) % width) for i in range(width)]
    loose = [i for i in range(width) for _ in range(2)] + ([0] if spare else [])
    return supports(width, meetings, loose)


def run_lengths(selected, width):
    if len(selected) == width:
        return [width]
    first_missing = next(i for i in range(width) if i not in selected)
    lengths, run = [], 0
    for offset in range(1, width + 1):
        if (first_missing + offset) % width in selected:
            run += 1
        elif run:
            lengths.append(run)
            run = 0
    return lengths


def ring_control(width, law):
    source = ring_stars(width)
    frames = history(source, law, width)
    # Physical source witness k connects its two live ordinary neighbors. This
    # returns the candidate cyclic order for odd width, rather than input order.
    order = [(2 * i) % width for i in range(width)]
    provenance = {holder: 1 << i for i, holder in enumerate(order)}
    all_provenances = [list(provenance.values())]
    for age, frame in enumerate(frames):
        adjacency = neighbors(frame.end)
        assert set(order) == set(adjacency) and len(order) == width
        assert all(adjacency[v] == {order[i - 1], order[(i + 1) % width]}
                   for i, v in enumerate(order))
        assert set(frame.end.opens.values()) == {2}
        if age == width:
            break
        next_frame = frames[age + 1]
        child_of = {frozenset(parent): child for child, parent in next_frame.parents.items()}
        assert len(child_of) == width and all(next_frame.fresh[child] == 2 for child in child_of.values())
        order = [child_of[frozenset((order[i], order[(i + 1) % width]))] for i in range(width)]
        new = {}
        for child in order:
            a, b = next_frame.parents[child]
            new[child] = provenance[a] | provenance[b]
        provenance = new
        all_provenances.append([new[child] for child in order])
    assert len(all_provenances) == width + 1
    interval_counts = {}
    for pattern in range(1 << width):
        selected = {i for i in range(width) if pattern & (1 << i)}
        runs = run_lengths(selected, width)
        gaps = run_lengths(set(range(width)) - selected, width)
        pure = []
        inclusive = []
        for depth, actual in enumerate(all_provenances):
            pure.append(sum(mask & ~pattern == 0 for mask in actual))
            inclusive.append(sum(bool(mask & pattern) for mask in actual))
            pure_ref = width if len(selected) == width else sum(max(r - depth, 0) for r in runs)
            weak_ref = (width - sum(max(r - depth, 0) for r in gaps)) if selected else 0
            assert (pure[-1], inclusive[-1]) == (pure_ref, weak_ref)
        if pattern == (1 << len(selected)) - 1:
            interval_counts[len(selected)] = {"all_parents": pure, "some_parent": inclusive}
    return {"literal_layers": [book(frame) for frame in frames],
            "prefix_masks_checked": 1 << width,
            "mask_layer_comparisons": (1 << width) * len(frames),
            "joint_relabeling_at_age_two_agrees": check_relabeling(frames[2], law),
            "interval_size_histories": interval_counts,
            "least_width_for_unending_all_parent_line": width,
            "largest_proper_extinction_depth": width - 1}


def one_spare_control(law):
    frames = history(ring_stars(5, spare=True), law, 6)
    chosen = [child for child, parents in frames[1].parents.items() if parents == (0,)]
    assert len(chosen) == 1 and frames[1].fresh[chosen[0]] == 2
    strong, weak = set(chosen), set(chosen)
    pure_widths, inclusive_widths = [1], [1]
    for frame in frames[2:]:
        strong = {child for child, parents in frame.parents.items() if set(parents) <= strong}
        weak = {child for child, parents in frame.parents.items() if weak.intersection(parents)}
        pure_widths.append(len(strong))
        inclusive_widths.append(len(weak))
    assert not any(pure_widths[1:]) and all(inclusive_widths)
    return {"literal_layers": [book(frame) for frame in frames],
            "first_spare_child_all_parent_counts": pure_widths,
            "first_spare_child_any_parent_counts": inclusive_widths}


def relay_control(law):
    meetings = ((0, 1), (0, 2), (0, 3))
    pin = (0, 1, 1, 2, 2, 3, 3)
    active = supports(4, meetings, pin)
    quiet = supports(4, meetings, pin[1:])
    frames = history(active, law, 10)
    folded = history(quiet, law, 5)
    near = [row[0] for row in (components(frame.end) for frame in frames[2:])]
    top, relay = (next(iter(row)) for row in near[:2])
    assert frames[2].fresh[top] == 1 and len(frames[2].parents[top]) == 3
    assert frames[3].parents[relay] == (top,) and frames[3].fresh[relay] == 2
    only_top = step(End({top: 1}, ()), law)
    assert only_top.fresh == ((0,) if law == "parity" else (2,))
    solitary_top = next(iter(folded[2].parents))
    assert folded[2].fresh[solitary_top] == (1 if law == "nae" else 0)
    if law == "parity":
        assert len(folded) == 3 and not folded[-1].end.opens
    else:
        assert folded[3].fresh == {next(iter(folded[3].fresh)): 2}
    part_rows = []
    for i in range(3, len(frames)):
        frame, following = frames[i - 1:i + 1]
        part, children = near[i - 3], near[i - 2]
        assert all(set(following.parents[v]) <= part for v in children)
        predicted = step(restricted(frame.end, part), law)
        expected = Counter((following.parents[v], following.fresh[v]) for v in children)
        agrees = Counter(zip(predicted.parents, predicted.fresh, strict=True)) == expected
        assert agrees == (i >= 4 or law == "nae")
        if i >= 4:
            assert set(predicted.fresh) == {2}
        part_rows.append({"age": i, "own_births": len(children),
                          "same_fresh_and_roster_after_end_restriction": agrees,
                          "own_number_of_unaries": sum(len(following.parents[v]) == 1 for v in children)})

    release = near[2]
    assert len(release) == 2
    own = [{v} for v in sorted(release)]
    after_release = []
    for i in range(5, len(frames)):
        previous, frame = frames[i - 1:i + 1]
        graph = neighbors(previous.end)
        assert all(len(graph[next(iter(row))]) == 1 for row in own)
        solo = step(End({0: 2}, ()), law)
        assert solo.parents == ((0,), (0,)) and solo.fresh == (2, 2)
        previous_own = own
        own = [{v for v, parents in frame.parents.items() if set(parents) <= row}
               for row in previous_own]
        assert all(len(row) == 1 and frame.fresh[next(iter(row))] == 2 for row in own)
        assert all(frame.parents[next(iter(row))] == (next(iter(old)),)
                   for row, old in zip(own, previous_own, strict=True))
        part = near[i - 2]
        graph = neighbors(frame.end)
        recognized = {v for v in part if len(graph[v]) == 1 and frame.end.opens[v] == 2}
        assert recognized == own[0] | own[1]
        mixed = part - recognized
        assert len(mixed) == i - 4 and all(frame.fresh[v] == 2 for v in mixed)
        if i == 5:
            assert {frame.parents[v] for v in mixed} == {tuple(sorted(release))}
        after_release.append({"age": i, "each_pure": 1, "pure_fresh": 2, "mixed": len(mixed),
                              "mixed_fresh_histogram": {2: len(mixed)}})
    return {"active": [book(frame) for frame in frames],
            "quiet": [book(frame) for frame in folded], "relay_age": 3, "axial_launch_age": 4,
            "release_component_knots": len(release), "relay_top_fresh_if_only_live": only_top.fresh,
            "joint_relabeling_at_release_agrees": check_relabeling(frames[4], law),
            "reduced_whole_part_literal_costs": part_rows,
            "following_axial_and_mixed_births": after_release}


def witness_erasure(law):
    spent = list(combinations((2, 3, 4, 5), 2))
    left = [(0, 2), (0, 3)]
    joined = supports(6, (*left, (1, 2), (1, 4), *spent), (0, 0, 1, 1))
    separate = supports(6, (*left, (1, 5), (1, 4), *spent), (0, 0, 1, 1))
    assert joined[:2] == separate[:2]
    assert all((len(owners_of(joined)[d]) == 1) == (len(owners_of(separate)[d]) == 1)
               for d in joined[0] + joined[1])
    result = []
    for stars in (joined, separate):
        frames = history(stars, law, 5)
        result.append({"source": certify_source(stars),
                       "live_stars": stars[:2],
                       "joint_relabeling_of_source_agrees": check_relabeling(frames[0], law),
                       "layer1_parents": tuple(frames[1].parents.values()),
                       "layer1_fresh": tuple(frames[1].fresh.values()),
                       "layers": list(map(book, frames))})
    assert len(result[0]["layer1_parents"]) == 3 and len(result[1]["layer1_parents"]) == 4
    assert result[0]["layer1_parents"].count((0, 1)) == 1 and (0, 1) not in result[1]["layer1_parents"]
    return {"joined": result[0], "separate": result[1]}


def minimal_competition(law):
    # A--W, followed by adding C at a loose distinction of W.
    before = ((0, 1, 2), (0, 3, 4))
    after = (*before, (3, 5, 6))
    rows = []
    for source in (before, after):
        frames = history(source, law, 5)
        n_first = sum(parents == (0,) for parents in frames[1].parents.values())
        pure = {0}
        pure_widths = [1]
        for frame in frames[1:]:
            pure = {v for v, parents in frame.parents.items() if set(parents) <= pure}
            pure_widths.append(len(pure))
        rows.append({"source": certify_source(source), "first_pure_unaries": n_first,
                     "A_pure_widths": pure_widths, "layers": list(map(book, frames))})
    assert [row["first_pure_unaries"] for row in rows] == [2, 1]
    return rows


def main():
    bare = {str(n): certify_source(ring_stars(n)) for n in (5, 7)}
    spare = certify_source(ring_stars(5, spare=True))
    star_meetings = ((0, 1), (0, 2), (0, 3))
    relay_sources = {
        "center_with_one_loose": certify_source(supports(4, star_meetings, (0, 1, 1, 2, 2, 3, 3))),
        "center_spent": certify_source(supports(4, star_meetings, (1, 1, 2, 2, 3, 3))),
    }
    results = {
        law: {"bare": {str(n): ring_control(n, law) for n in (5, 7)},
              "one_spare_five": one_spare_control(law), "relay": relay_control(law),
              "spent_witness": witness_erasure(law), "minimal_competition": minimal_competition(law)}
        for law in LAWS
    }
    payload = {"bare_sources": bare, "one_spare_source": spare,
               "relay_sources": relay_sources, "laws": results}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()
