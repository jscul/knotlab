"""Independent checks using literal allowed states and the predecessor's unchanged joins."""

from collections import Counter
from itertools import combinations, product
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PREVIOUS = "CUBIC-FROM-A-KNOT-20261117-001"
GROWTH = ROOT / "proofs" / PREVIOUS / (PREVIOUS + "-P001_local_growth") / "check.py"


def mask(bits):
    return sum(1 << bit for bit in bits)


def members(value):
    return [bit for bit in range(value.bit_length()) if value >> bit & 1]


def fixture(inputs, old):
    """Replay the given loose-bit choices and retain bit identities."""
    stars = [(0, 1, 2)]
    before = {"0": ("p0", "p1", "p2")}
    for j, ports in enumerate(inputs, 1):
        fresh = (3*j, 3*j+1, 3*j+2)
        chosen_names = tuple(f"p{bit}" for bit in ports)
        fresh_names = tuple(f"p{bit}" for bit in fresh)
        assert old["legal_local_move"](before, chosen_names, fresh_names)
        stars.append((*ports, *fresh))
        before[str(j)] = (*chosen_names, *fresh_names)
    return stars, before


def literal_bonds(stars):
    """Project the truth table directly onto every subset of its twelve bits."""
    n = 3 * len(stars)
    masks = [mask(star) for star in stars]
    allowed = [row for row in range(1 << n)
               if all((row & check).bit_count() % 2 == 0 for check in masks)]
    free = {0}
    bonds = set()
    for kept in range(1, 1 << n):
        if len({row & kept for row in allowed}) == 1 << kept.bit_count():
            free.add(kept)
        elif kept.bit_count() >= 3 and all(kept ^ (1 << i) in free for i in members(kept)):
            bonds.add(kept)
    return bonds, len(allowed)


def short_bonds_from_stars(stars):
    """The claimed classification, checked against an independent enumeration."""
    stars = [mask(star) for star in stars]
    pairs = {a ^ b for a, b in combinations(stars, 2)
             if a & b and (a ^ b).bit_count() <= 6}
    return set(stars) | pairs


def canonical_knot_check(stars, kept):
    """Encode the whole fixture, then let knotlab forget the omitted bits."""
    clauses = []
    for star in stars:
        for row in product((0, 1), repeat=len(star)):
            if sum(row) % 2 == 1:
                clauses.append(" ".join(("~" if value else "") + f"p{bit}"
                                        for bit, value in zip(star, row)))
    observe = sorted(kept)
    witnesses = sorted(set(range(3 * len(stars))) - set(kept))
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
            "--loops", *(f"p{i}" for i in observe[:-1]), "--contact", f"p{observe[-1]}",
            "--witnesses", *(f"p{i}" for i in witnesses), "--json"]
    env = {**os.environ, "PYTHONPATH": str(ROOT / "tools")}
    report = json.loads(subprocess.check_output(args, cwd=ROOT, env=env, text=True))
    return {"K1": report["binding"], "K2": report["invisible_in_parts"],
            "K3": report["coexistence"], "knot": report["is_knot"],
            "projected_states": len(report["allowed"])}


def four_junctions(old):
    examples = {"three_children": [(0,), (1,), (2,)],
                "chain": [(0,), (3,), (6,)],
                "seed_next_to_five": [(0,), (3,), (1, 6)]}
    expected = {"three_children": (3, 3, 0), "chain": (5, 2, 0),
                "seed_next_to_five": (4, 2, 0)}
    output = {}
    for name, inputs in examples.items():
        stars, presentation = fixture(inputs, old)
        bonds, count = literal_bonds(stars)
        assert count == 256
        assert {b for b in bonds if b.bit_count() <= 6} == short_bonds_from_stars(stars)
        groups, _ = old["parent_groups"](presentation)
        sizes = Counter(map(len, groups))
        assert tuple(sizes[n] for n in (1, 2, 3)) == expected[name]
        distances = {}
        for a, b in combinations(range(12), 2):
            pair = mask([a, b])
            distances[a, b] = min(c.bit_count()-1 for c in bonds if c & pair == pair)
        output[name] = {"allowed_states": count, "distinct_bonds": len(bonds),
                        "next_group_sizes_1_2_3": expected[name],
                        "distance_histogram": dict(sorted(Counter(distances.values()).items()))}
        if name == "seed_next_to_five":
            # Bits 2 and 9 are each loose at opposite ends of the same shared bit.
            assert distances[2, 9] == 5 and all(not {2, 9} <= set(star) for star in stars)
            supports = {"seed": set(stars[0]), "four": set(stars[1]), "five": set(stars[3]),
                        "sum_of_seed_and_five": set(stars[0]) ^ set(stars[3]),
                        "nonminimal_union": set(stars[0]) | set(stars[3])}
            reports = {key: canonical_knot_check(stars, kept) for key, kept in supports.items()}
            assert all(reports[key]["knot"] for key in list(supports)[:-1])
            assert reports["nonminimal_union"]["K1"] and not reports["nonminimal_union"]["K2"]
            output[name]["canonical"] = reports
            output[name]["false_adjacency_distance"] = distances[2, 9]
    return output


def attached_cube_control():
    helper = runpy.run_path(str(GROWTH.with_name("cut_control.py")))
    _, rows, _ = helper["seed_to_cube"]()
    triples = []
    for triple in combinations(range(8), 3):
        marginal = {tuple(row[i] for i in triple) for row in rows}
        if len(marginal) < 8 and all(
            len({(row[i], row[j]) for row in rows}) == 4 for i, j in combinations(triple, 2)
        ):
            triples.append(triple)
    covered = {pair for triple in triples for pair in combinations(triple, 2)}
    assert len(covered) == 28 and len(rows) == 8
    return {"old_bits": 8, "old_rows": len(rows), "old_pairs_at_bond_distance_two": len(covered),
            "old_bits_in_one_first_threshold_clique": 8, "largest_designated_star": 6}


def complete_round(old, recover):
    current = old["grow_parallel"](3)[0][-1]
    bits = sorted({bit for star in current.values() for bit in star})
    index = {bit: i for i, bit in enumerate(bits)}
    stars = [[index[b] for b in star] for star in current.values()]
    checks = [mask(star) for star in stars]
    # Gray order visits every combination of the 20 equations, including the empty one.
    small = set()
    value = 0
    for step in range(1, 1 << len(stars)):
        toggled = (step & -step).bit_length() - 1
        value ^= checks[toggled]
        if value.bit_count() <= 6:
            small.add(value)
    assert small == short_bonds_from_stars(stars)
    assert all(not any(other != s and other & s == other for other in small) for s in small)
    # 6 is simply the common symbol for every distance larger than 5.
    table = {pair: 6 for pair in combinations(bits, 2)}
    for support in small:
        kept = [bits[i] for i in members(support)]
        for pair in combinations(kept, 2):
            table[pair] = min(table[pair], len(kept) - 1)
    recovered = recover(table)
    assert recovered == {frozenset(star) for star in current.values()}
    groups = old["parent_groups"](current)[0]
    next_sizes = [sum(len(group) == size for group in groups) for size in (1, 2, 3)]
    assert next_sizes == [3, 9, 3]
    return {"junctions": len(stars), "distinctions": len(bits), "combinations": 1 << len(stars),
            "exact_stars_from_truncated_table": len(recovered),
            "minimal_short_supports_by_size": dict(sorted(Counter(s.bit_count() for s in small).items())),
            "next_group_sizes_1_2_3": next_sizes}


if __name__ == "__main__":
    predecessor = runpy.run_path(str(GROWTH))
    reader = runpy.run_path(str(Path(__file__).with_name("check_rearrangements.py")))["recover_stars"]
    print(json.dumps({"four_junctions": four_junctions(predecessor),
                      "complete_round_three": complete_round(predecessor, reader),
                      "nonlinear_attachment_control": attached_cube_control()}, indent=2))
