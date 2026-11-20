"""Literal four-load growth, local incidence, and first-birth ancestry checks."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from functools import reduce
from hashlib import sha256
from itertools import combinations
import json
from operator import or_
from pathlib import Path
from random import Random
import sys
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = json.loads((HERE / "inputs.json").read_text())
SIDE = INPUT["same_side"]
sys.path.insert(0, str(ROOT / "experiments" / SIDE / f"{SIDE}-E001_side"))
from side_sources import cases, generate, loads, padded


CAPS = dict(zip(("junctions", "distinctions"), INPUT["path_caps"], strict=True))
MAX_AGE = 10
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name / "two_loops.json"


def fixtures():
    old = cases()
    return [old["T4"], old["T8"], padded("T12", 28, [8, 20])]


def names(mask):
    out = []
    while mask:
        low = mask & -mask
        out.append(low.bit_length() - 1)
        mask ^= low
    return out


def incidence(stars):
    n = len(stars)
    result = {v: tuple(n + d for d in row) for v, row in enumerate(stars)}
    holders = defaultdict(list)
    for v, row in enumerate(stars):
        for d in row:
            holders[n + d].append(v)
    result.update((d, tuple(row)) for d, row in holders.items())
    return result


def view(roster, root, kind, width, max_radius, ring_knots, born, occupied):
    """Compare only the displayed bipartite incidence; birth/ancestry are separate grades."""
    center = tuple(root if kind == "knot" else (width + d for d in root))
    dist = {v: 0 for v in center}
    queue = deque(center)
    by_age = []
    while queue:
        current = queue.popleft()
        depth = dist[current]
        if depth < max_radius:
            for nxt in roster[current]:
                if nxt not in dist:
                    dist[nxt] = depth + 1
                    queue.append(nxt)
    typed = [(v, depth, int(v >= width), int(v in center),
              sum(dist.get(w, max_radius + 2) < depth + 1 for w in roster[v]), len(roster[v]))
             for v, depth in dist.items()]
    values = {width + d for d in occupied}
    for radius in range(max_radius + 1):
        degrees = Counter((t, mark, depth, boundary if depth == radius else complete)
                          for _, depth, t, mark, boundary, complete in typed if depth <= radius)
        body = {v for v, d in dist.items() if d <= radius}
        by_age.append({"knots": sum(v < width for v in body), "distinctions": sum(v >= width for v in body),
                       "born_knots": len(body & born), "old_ring_seen": [bool(body & row) for row in ring_knots],
                       "occupied_distinctions": sorted(d - width for d in body & values),
                       "typed_shell_degree_counts": [[*key, count] for key, count in sorted(degrees.items())]})
    return by_age


def roots(spec):
    s, t = spec["roles"]["seams"]
    middle = (s + t) // 2
    return {"midpoint": ("knot", (middle,)), "middle_left": ("distinction", (middle - 1,)),
            "middle_right": ("distinction", (middle,)), "inside_left": ("distinction", (s + 1,)),
            "inside_right": ("distinction", (t - 2,)), "beyond_left": ("distinction", (s - 3,)),
            "beyond_right": ("distinction", (t + 2,)), "both_exteriors": ("distinction", (s - 3, t + 2)),
            "far_left_holder": ("knot", (s - 2,)), "far_right_holder": ("knot", (t + 2,))}


def digest(stars):
    return sha256(json.dumps(stars, separators=(",", ":")).encode()).hexdigest()


def first_groups(frame, s, t, arm):
    unary = defaultdict(list)
    pairs = {}
    bparents = frame["parent_sets"]
    for v, row in bparents.items():
        if len(row) == 1:
            unary[row[0]].append(v)
        else:
            assert len(row) == 2 and tuple(row) not in pairs
            pairs[tuple(row)] = v
    track = tuple(range(s + 2, t, 2))
    chain = []
    interior = []
    if arm in ("1", "2"):
        direct = range(s + 2, t + 3, 2) if arm == "1" else range(t - 2, s - 3, -2)
        released, = unary[direct[0]]
        chain = [released, *(pairs[tuple(sorted(pair))] for pair in zip(direct, direct[1:]))]
    elif arm == "3":
        if len(track) == 1:
            u, w = unary[track[0]]
        else:
            u, = unary[track[0]]
            w, = unary[track[-1]]
        interior = [u, *(pairs[tuple(pair)] for pair in zip(track, track[1:])), w]
        for i, v in enumerate(interior):
            others = {u for u, row in bparents.items() if u != v and not set(row).isdisjoint(bparents[v])}
            assert others == set(interior[max(i - 1, 0):i] + interior[i + 1:i + 2])
            assert len(frame["fresh"][v]) == 2
    return unary, chain, interior


def compress_chain(chain):
    return [v for i, v in enumerate(chain) if i == 0 or chain[i - 1] != v]


def merge_chain(chain, frame):
    pairs = {frozenset(pair) for pair in zip(chain, chain[1:])}
    child = {}
    for v, parents in frame["parent_sets"].items():
        for pair in combinations(parents, 2):
            key = frozenset(pair)
            if key in pairs:
                child.setdefault(key, v)
    assert set(child) == pairs
    return compress_chain([child[frozenset(pair)] for pair in zip(chain, chain[1:])])


def genealogy(site, ledger, n, old_ancestry, first_ancestry):
    kept = set()
    pending = [site]
    while pending:
        v = pending.pop()
        if v >= n and v not in kept:
            kept.add(v)
            pending.extend(ledger[v]["parents"])
    return {"knot": site, "old_ancestors": names(old_ancestry[site]),
            "first_layer_ancestors": [n + i for i in names(first_ancestry[site])],
            "births": [ledger[v] for v in sorted(kept)]}


def trace(spec, arm, occupied, stop_age):
    n = len(spec["sizes"])
    s, t = spec["roles"]["seams"]
    gap = t - s
    m = gap // 2
    far = t + 2 if arm == "1" else s - 2
    mark_roots = roots(spec)
    ring_knots = [set(row) for row in spec["roles"]["rings"]]
    old_ancestry = [1 << v for v in range(n)]
    first_ancestry = [0] * n
    data, ledger, records = {}, {}, {}
    chain, interior = [], []
    combo = passage = joined = None
    schedules = []
    source_occupation = set(occupied)
    the_generator = generate(spec, occupied, stop_age, CAPS)
    while True:
        try:
            age, frame = next(the_generator)
        except StopIteration as end:
            term = end.value
            break
        assert set(frame["occupied"]) == source_occupation
        if age:
            assert not frame["new_occupied"] and not frame["spent_occupied"]
            for v in frame["born"]:
                assert v == len(old_ancestry)
                parents = frame["parent_sets"][v]
                old_ancestry.append(reduce(or_, (old_ancestry[p] for p in parents), 0))
                first_ancestry.append(1 << (v - n) if age == 1 else reduce(or_, (first_ancestry[p] for p in parents), 0))
                ledger[v] = {"knot": v, "age": age, "parents": parents, "spent": frame["consumed"][v],
                             "fresh": frame["fresh"][v]}
            if age == 1:
                unary, chain, interior = first_groups(frame, s, t, arm)
                release = {str(q): [{**ledger[v]} for v in unary[q]] for q in sorted({s + 2, t - 2})}
                records["inward_released_unaries"] = release
                if chain:
                    origin = first_ancestry[chain[0]]
                    schedules.append(chain[:])
                    records["passage_source_unary"] = chain[0]
                if interior:
                    records["interior_first_layer_path"] = [ledger[v] for v in interior]
                    mark_bits = first_ancestry[interior[0]] | first_ancestry[interior[-1]]
                    sector = reduce(or_, (first_ancestry[v] for v in interior), 0)
            elif len(chain) > 1:
                chain = merge_chain(chain, frame)
                schedules.append(chain[:])
                if len(chain) == 1:
                    assert first_ancestry[chain[0]] & origin and old_ancestry[chain[0]] & (1 << far)
                    joined = age

            if schedules and passage is None:
                witness = next((v for v in frame["born"] if first_ancestry[v] & origin and old_ancestry[v] & (1 << far)), None)
                if witness is not None:
                    passage = {"age": age, "target_old_holder": far,
                               **genealogy(witness, ledger, n, old_ancestry, first_ancestry)}
            if interior:
                cohort = [v for v in frame["born"] if first_ancestry[v] & sector]
                assert len(cohort) == m + age - 1
                assert all(not (first_ancestry[v] & ~sector) and len(frame["fresh"][v]) == 2 for v in cohort)
                assert all(s < q < t for v in cohort for q in names(old_ancestry[v]))
                together = [v for v in cohort if first_ancestry[v] & mark_bits == mark_bits]
                assert len(together) == max(0, age - m + 1)
                if together and combo is None:
                    combo = {"age": age, "left_and_right_first_unaries": [interior[0], interior[-1]],
                             **genealogy(together[0], ledger, n, old_ancestry, first_ancestry)}
                records.setdefault("interior_path_layers", []).append(
                    {"age": age, "cohort_births": len(cohort), "combined_births": len(together), "all_fresh_counts_two": True})

        stars = frame["stars"]
        if age <= 8:
            g = incidence(stars)
            # All horizons are small and counts use only the displayed incidence.
            unique = {}
            for kind, subject in set(mark_roots.values()):
                unique[kind, subject] = view(g, subject, kind, len(stars), gap + 6, ring_knots,
                                             set(frame["born"]) if age else set(), source_occupation)
            local = {mark: unique[(kind, subject)] for mark, (kind, subject) in mark_roots.items()}
        else:
            local = {}
        data[age] = {"knots": frame["junction_count"], "distinctions": frame["distinction_count"],
                     "born": len(frame["born"]) if age else 0, "stage_sha256": digest(stars), "views": local,
                     "midpoint_first_children_parent_counts": sorted(len(ps) for ps in frame["parent_sets"].values()
                          if (s + t) // 2 in ps) if age == 1 else None,
                     "total_occupied": len(source_occupation), "occupied_beyond_the_original_ring_distinctions": 0}
    records["same_far_old_holder_from_released_unary"] = passage
    if combo is not None:
        records["earliest_combined_descendant"] = combo
    if schedules:
        records["passage_constructive_chain"] = schedules
        records["passage_merge_completed_by_layer"] = joined
    if interior:
        records["passage_excluded_both_directions_by_separated_first_layer_component"] = True
    return {"arm": arm, "original_values": sorted(source_occupation), "growth_termination": term,
            "frames": data, "lineage": records, "last_completed_age": max(data)}


def four_loads(spec, arms):
    common = sorted(set.intersection(*(set(row["frames"]) for row in arms.values())))
    focal = roots(spec)
    first_interaction = None
    first_noring_interaction = None
    first_midpoint_interaction = None
    no_count_structure = None
    counts = Counter()
    first_beyond = {}
    for age in common:
        raw = [arms[arm]["frames"][age] for arm in ("0", "1", "2", "3")]
        for label in focal:
            if not raw[0]["views"]:
                continue
            views = [row["views"][label] for row in raw]
            for r, values in enumerate(zip(*views, strict=True)):
                nk = [v["knots"] for v in values]
                nd = [v["distinctions"] for v in values]
                nonadd = nk[3] - nk[2] - nk[1] + nk[0]
                counts["four_arm_views"] += 1
                counts["nonzero_knot_interaction"] += nonadd != 0
                projected = [v["typed_shell_degree_counts"] for v in values]
                independent = all(not any(v["old_ring_seen"]) for v in values)
                if independent:
                    assert all(not v["occupied_distinctions"] for v in values)
                    counts["four_arm_views_without_old_ring_holders"] += 1
                witness = {"age": age, "root": label, "radius_incidence_hops": r, "knots_00_10_01_11": nk,
                           "distinctions_00_10_01_11": nd, "knot_interaction": nonadd,
                           "whole_stage_knots_00_10_01_11": [v["knots"] for v in raw],
                           "before_any_original_ring": independent}
                if nonadd and (first_interaction is None or (age, r) < first_interaction["order"]):
                    first_interaction = {"order": (age, r), **witness}
                if nonadd and independent and (first_noring_interaction is None or (age, r) < first_noring_interaction["order"]):
                    first_noring_interaction = {"order": (age, r), **witness}
                if nonadd and label == "midpoint" and first_midpoint_interaction is None:
                    first_midpoint_interaction = {"order": (age, r), **witness}
                if len(set(nk)) == 1 and any(p != projected[0] for p in projected[1:]):
                    if independent and (no_count_structure is None or (age, r) < no_count_structure["order"]):
                        no_count_structure = {"order": (age, r), **witness,
                                              "four_typed_shell_degree_profiles": projected}
                if label in ("beyond_left", "beyond_right", "far_left_holder", "far_right_holder"):
                    idx = 0 if "right" in label else 1
                    comparisons = ((0, 1), (2, 3)) if idx == 0 else ((0, 2), (1, 3))
                    for mode, (x, y) in zip(("other_quiet", "other_loaded"), comparisons, strict=True):
                        goal = (label, mode)
                        if values[x]["old_ring_seen"][idx] or values[y]["old_ring_seen"][idx]:
                            continue
                        if projected[x] != projected[y] and (goal not in first_beyond or (age, r) < first_beyond[goal]["order"]):
                            bins = [{tuple(row[:-1]): row[-1] for row in projected[i]} for i in (x, y)]
                            changes = [[*k, bins[0].get(k, 0), bins[1].get(k, 0)]
                                       for k in sorted(bins[0].keys() | bins[1].keys())
                                       if bins[0].get(k, 0) != bins[1].get(k, 0)]
                            first_beyond[goal] = {"order": (age, r), **witness, "other_ring": mode,
                                "arms_compared_in_00_10_01_11_order": [x, y],
                                "visible_occupied_marks_equal": values[x]["occupied_distinctions"] == values[y]["occupied_distinctions"],
                                "changed_birth_count_in_view": values[y]["born_knots"] - values[x]["born_knots"],
                                "typed_shell_degree_changes_before_after": changes}
    return {"common_completed_ages": common, "coverage": dict(counts), "first_knot_count_interaction": first_interaction,
            "first_midpoint_knot_count_interaction": first_midpoint_interaction,
            "first_interaction_without_old_ring_holders": first_noring_interaction,
            "equal_knot_count_but_different_rooted_shapes": no_count_structure,
            "first_beyond_shape_difference_before_donor_inclusion": list(first_beyond.values())}


def roster_controls(spec, arms):
    s, t = spec["roles"]["seams"]
    local = [arms[arm]["frames"][1]["midpoint_first_children_parent_counts"] for arm in ("0", "1", "2", "3")]
    if t - s == 4:
        assert local == [[2, 2], [1, 2], [1, 2], [1, 1]]
    else:
        assert local == [[2, 2]] * 4
    n = [arms[arm]["frames"][1]["born"] for arm in ("0", "1", "2", "3")]
    assert n[3] - n[2] - n[1] + n[0] == 0
    joined = arms["3"]["lineage"].get("earliest_combined_descendant")
    if arms["3"]["last_completed_age"] >= (t - s) // 2:
        assert joined["age"] == (t - s) // 2
    for arm in ("1", "2"):
        lineage = arms[arm]["lineage"]
        if arms[arm]["last_completed_age"] >= (t - s) // 2 + 1:
            assert lineage["same_far_old_holder_from_released_unary"]["age"] <= (t - s) // 2 + 1
    return {"first_birth_counts_00_10_01_11": n, "midpoint_child_parent_counts_00_10_01_11": local}


def check_local_renaming(spec, recorded):
    """Scramble one whole physical stage per arm and match the rooted boundary exactly."""
    control = []
    root = roots(spec)["midpoint"][1][0]
    for arm, occupied in loads(spec).items():
        stage = dict(generate(spec, occupied, 1, CAPS))[1]
        stars = stage["stars"]
        distinctions = sorted({d for row in stars for d in row})
        rng = Random(422)
        k = list(range(len(stars)))
        d = [17 + 3 * j for j in range(len(distinctions))]
        rng.shuffle(k)
        rng.shuffle(d)
        new_k = {old: idx for idx, old in enumerate(k)}
        new_d = dict(zip(distinctions, d, strict=True))
        renamed = tuple(tuple(new_d[x] for x in stars[v]) for v in k)
        recoded = view(incidence(renamed), (new_k[root],), "knot", len(stars), 3,
                       [{new_k[v] for v in row} for row in spec["roles"]["rings"]],
                       {new_k[v] for v in stage["born"]}, {new_d[x] for x in occupied})
        wanted = recorded["arms"][arm]["frames"][1]["views"]["midpoint"][:4]
        assert all({**old, "occupied_distinctions": sorted(new_d[x] for x in old["occupied_distinctions"])} == new
                   for old, new in zip(wanted, recoded, strict=True))
        control.append({"arm": arm, "radii": [0, 1, 2, 3]})
    return control


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=MAX_AGE)
    parser.add_argument("--out", type=Path, default=DATA)
    args = parser.parse_args()
    if not 1 <= args.through <= MAX_AGE:
        parser.error("--through must be within the registered ages 1 through 10")
    output = {}
    for spec in fixtures():
        s, t = spec["roles"]["seams"]
        assert t - s in INPUT["double_gaps"] and s % 2 == t % 2 == 0
        arms = {a: trace(spec, a, state, args.through) for a, state in sorted(loads(spec).items())}
        output[spec["id"]] = {"source": spec, "profile_roots": roots(spec), "local_view_radius_limit": t - s + 6,
                              "arms": arms, "controls": roster_controls(spec, arms), "four_load_comparison": four_loads(spec, arms)}
    result = {"aliases_for_loads": {"0": "neither", "1": "left", "2": "right", "3": "both"},
              "caps": CAPS, "maximum_requested_ancestry_age": args.through, "maximum_view_age": min(8, args.through),
              "renaming_controls_on_four_step_midpoint": check_local_renaming(output["T4"]["source"], output["T4"]), "cases": output}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as target:
        tmp = Path(target.name)
        json.dump(result, target, separators=(",", ":"))
        target.write("\n")
    tmp.replace(args.out)


if __name__ == "__main__":
    main()
