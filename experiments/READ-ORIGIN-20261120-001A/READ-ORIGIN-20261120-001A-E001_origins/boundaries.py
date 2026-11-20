"""Read all compatible complete-boundary origins from physical unit holdings."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
from random import Random
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = "SERIAL-REPAIRS-20261120-001A"
ORDINARY = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / PREV / (PREV + "-E001_repairs")))
sys.path.insert(0, str(ROOT / "experiments" / ORDINARY / (ORDINARY + "-E001_ordinary")))
from end_operator import from_stars, step
from outside import rank_of
from pysat.solvers import Minisat22

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "boundaries.json"
LAWS = ("parity", "nae")


def source(n, links, opens):
    stars = {i: [] for i in range(n)}
    bit = 0
    for a, b in links:
        stars[a].append(bit)
        stars[b].append(bit)
        bit += 1
    for i, count in enumerate(opens):
        stars[i].extend(range(bit, bit + count))
        bit += count
    return {v: tuple(s) for v, s in stars.items()}


def ownership(stars):
    holders = defaultdict(list)
    for v, star in stars.items():
        for d in star:
            holders[d].append(v)
    assert all(1 <= len(v) <= 2 for v in holders.values())
    return holders


def ordinary(stars, law):
    ids = sorted(stars)
    result = step(from_stars([stars[i] for i in ids]), law)
    if result.status != "extend":
        return result.status, []
    return "extend", [(tuple(ids[k] for k in parents), output)
                      for parents, output in zip(result.parents, result.fresh, strict=True)]


def write_layer(stars, law, choose=None):
    status, events = ordinary(stars, law)
    assert status == "extend" and events
    if choose is not None:
        events = choose(events)
    owners = ownership(stars)
    supplies = {v: sorted(d for d in star if len(owners[d]) == 1)
                for v, star in stars.items()}
    built = stars.copy()
    next_bit = max(owners, default=-1) + 1
    for parents, output in events:
        inputs = [supplies[p].pop(0) for p in parents]
        built[max(built) + 1] = tuple(inputs + list(range(next_bit, next_bit + output)))
        next_bit += output
    return built


def law_gate(stars, law, checked):
    token = law, tuple(stars.items())
    if token in checked:
        return checked[token]
    try:
        from_stars(tuple(stars.values()))
    except ValueError:
        checked[token] = False
        return False
    if any(len(row) < 3 for row in stars.values()):
        allowed = False
    elif law == "parity":
        masks = [sum(1 << d for d in row) for row in stars.values()]
        rank = rank_of(masks)
        allowed = all(rank - rank_of([w & ~mask for w in masks]) == 1 for mask in masks)
    else:
        clauses = [[sign * (d + 1) for d in row] for row in stars.values() for sign in (-1, 1)]
        with Minisat22(bootstrap_with=clauses) as solver:
            allowed = all(solver.solve(assumptions=[(d + 1) * (1 if state >> i & 1 else -1)
                                                    for i, d in enumerate(row)])
                          for row in stars.values() for state in range(1, (1 << len(row)) - 1))
    checked[token] = allowed
    return allowed


def preceding(stars, law, checked):
    owners = ownership(stars)
    live = {v[0] for v in owners.values() if len(v) == 1}
    if live:
        trials = [live]
    elif law == "parity":
        trials = [{v} for v in stars]
    else:
        trials = []
    for gone in trials:
        old = {v: s for v, s in stars.items() if v not in gone}
        if not old or not law_gate(old, law, checked):
            continue
        old_owners = ownership(old)
        actual = Counter()
        for child in gone:
            inherited = [d for d in stars[child] if d in old_owners]
            child_fresh = [d for d in stars[child] if d not in old_owners]
            # Fresh positions are unspent at this boundary. Incoming positions
            # were loose at distinct old parents before this whole cohort.
            if any(len(owners[d]) != 1 for d in child_fresh) or any(
                    len(old_owners[d]) != 1 for d in inherited):
                break
            parents = tuple(sorted(old_owners[d][0] for d in inherited))
            if not parents or len(set(parents)) != len(parents):
                break
            actual[parents, len(child_fresh)] += 1
        else:
            status, expected = ordinary(old, law)
            if status == "extend" and Counter(expected) == actual:
                yield old


def possible_boundary_origins(current, law, checked):
    all_roots = set()

    def walk(stars):
        members = frozenset(stars)
        if members in all_roots or not law_gate(stars, law, checked):
            return
        all_roots.add(members)
        for pred in preceding(stars, law, checked):
            walk(pred)

    walk(current)
    return all_roots


def recode(stars, seed):
    rng = Random(seed)
    names = list(stars)
    bits = list(ownership(stars))
    perm_knots, perm_bits = names.copy(), bits.copy()
    rng.shuffle(perm_knots)
    rng.shuffle(perm_bits)
    km = dict(zip(names, perm_knots, strict=True))
    bm = dict(zip(bits, perm_bits, strict=True))
    return {km[k]: tuple(bm[d] for d in star) for k, star in stars.items()}, km


def stage_size(stars):
    return len(stars), len(ownership(stars))


def ring_panel(rounds=20):
    first = source(5, [(i, (i + 1) % 5) for i in range(5)], [2] * 5)
    panels = {}
    for law in LAWS:
        stars = first
        checked = {}
        results = []
        expected_origins = set()
        for t in range(rounds + 1):
            expected_origins.add(frozenset(stars))
            assert stage_size(stars) == (5 * (t + 1), 10 * t + 15)
            assert possible_boundary_origins(stars, law, checked) == expected_origins
            renamed, km = recode(stars, 20261120831 + t)
            if t in (0, 1, 5, rounds):
                assert possible_boundary_origins(renamed, law, {}) == {
                    frozenset(km[k] for k in s) for s in expected_origins}
            status, menu = ordinary(stars, law)
            assert status == "extend" and len(menu) == 5
            assert all(len(parents) == fresh == 2 for parents, fresh in menu)
            results.append({"age": t, "knots": len(stars), "distinctions": len(ownership(stars)),
                            "compatible_origins": len(expected_origins),
                            "fixed_length_bits": (len(expected_origins) - 1).bit_length()})
            if t < rounds:
                stars = write_layer(stars, law)
        panels[law] = results
    return panels


def last_event_panel():
    initial = source(1, [], [3])
    panel = {}
    for law in LAWS:
        stars = initial
        for _ in range(3):
            stars = write_layer(stars, law)
        checked = {}
        assert law_gate(stars, law, checked)
        forms = possible_boundary_origins(stars, law, checked)
        by_size = Counter(map(len, forms))
        expected = {1: 8, 4: 8, 7: 8, 8: 1} if law == "parity" else {1: 1, 4: 1, 7: 1, 8: 1}
        assert by_size == expected
        status, _ = ordinary(stars, law)
        assert status == ("closed" if law == "parity" else "extend")
        panel[law] = {"size": stage_size(stars), "next_status": status, "labeled_origins": len(forms),
                      "by_original_knot_count": sorted(by_size.items()), "literal_sources_checked": len(checked)}
        if law == "parity":
            assert possible_boundary_origins(stars, "nae", {}) == {frozenset(stars)}
    return panel


def one_bit_at_every_knot_count():
    out = []
    for k in range(2, 13):
        n = k - 1
        stars = source(n, [(i, i + 1) for i in range(n - 1)], [4] + [3] * (n - 1))
        checked = {}
        for law in LAWS:
            assert law_gate(stars, law, checked)
            _, plan = ordinary(stars, law)
            fixed = [h for parents, h in plan if parents == (0,)]
            assert len(fixed) >= 2 and set(fixed) == {3}
            current = write_layer(stars, law, lambda _: [((0,), 3)])
            assert law_gate(current, law, checked)
            _, resumed = ordinary(current, law)
            new = [h for parents, h in resumed if parents == (0,)]
            assert new and set(new) == {2}
            assert stage_size(current) == (k, 4 * k - 1)
        out.append({"knots": k, "distinctions": 4 * k - 1, "true_cost": 3, "restart_cost": 2})
    return out


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    result = {"complete_ring": ring_panel(), "closed_boundary": last_event_panel(),
              "ambiguous_at_each_knot_count": one_bit_at_every_knot_count()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["closed_boundary"])


if __name__ == "__main__":
    main()
