"""Replay two sharp marked horizons and a short-cut stress control on serial parity junctions."""

from collections import Counter
from importlib import util
from itertools import combinations, product
import json
from pathlib import Path

PROOFS = Path(__file__).resolve().parents[2]
audit_path = next((PROOFS / "VARIABLE-OUTPUT-READER-20261118-001F").glob("*/audit.py"))
spec = util.spec_from_file_location("finite_interval_audit", audit_path)
audit = util.module_from_spec(spec)
spec.loader.exec_module(audit)


def open_box(maxima):
    """Names and directions are construction witnesses. The measurement ignores them."""
    sites = sorted((v for v in product(*(range(n + 1) for n in maxima)) if v != maxima),
                   key=lambda v: (sum(v), v))
    outputs = {}
    rows = []
    for index, site in enumerate(sites):
        taken = []
        for dim, value in enumerate(site):
            if value:
                older = list(site)
                older[dim] -= 1
                taken.append(outputs[tuple(older)][dim])
        outputs[site] = tuple(range(3 * index, 3 * index + 3))
        rows.append((*taken, *outputs[site]))
    parents = []
    for dim in range(3):
        parent = list(maxima)
        parent[dim] -= 1
        parents.append(tuple(parent))
    marks = tuple(outputs[v][i] for i, v in enumerate(parents))
    # Two distinct loose bits on the second holder, including its marked one.
    replacement = next(bit for bit in outputs[parents[1]] if bit not in marks)
    return rows, parents, marks, replacement


def fixed_test(rows, marks, replace):
    """Build every bond from a connected ordinary shore and its connected complement."""
    audit.replay_history(rows, tuple(range(len(rows))))
    legal = audit.permissions(rows)
    width = max(max(row) for row in rows) + 1
    exterior = len(rows)
    neighbors = [0] * (exterior + 1)
    owner = {}
    stars = [audit.mask(row) for row in rows]
    for site, row in enumerate(rows):
        for bit in row:
            owner.setdefault(bit, []).append(site)
    for sites in owner.values():
        left = sites[0]
        right = sites[1] if len(sites) == 2 else exterior
        neighbors[left] |= 1 << right
        neighbors[right] |= 1 << left

    def connected(side):
        live = side & -side
        seen = live
        while live:
            bit = live & -live
            new = neighbors[bit.bit_length() - 1] & side & ~seen
            seen |= new
            live = (live ^ bit) | new
        return seen == side

    scalar = [[width + 1] * width for _ in range(width)]
    bonds_by_size = [[] for _ in range(width + 1)]
    all_sites = (1 << (exterior + 1)) - 1
    last = 0
    cut = 0
    count = 0
    short_multi = []
    for index in range(1, 1 << exterior):
        side = index ^ (index >> 1)
        cut ^= stars[(side ^ last).bit_length() - 1]
        last = side
        if connected(side) and connected(all_sites ^ side):
            size = cut.bit_count()
            bonds_by_size[size].append(cut)
            count += 1
            if size <= 6 and side.bit_count() >= 3:
                short_multi.append((side, cut))
    pending = [((1 << width) - 1) ^ ((1 << (i + 1)) - 1) for i in range(width)]
    for size, bonds in enumerate(bonds_by_size):
        for support in bonds:
            for left in audit.active_bits(support):
                new = support & pending[left]
                for right in audit.active_bits(new):
                    scalar[left][right] = scalar[right][left] = size
                pending[left] ^= new
        if not any(pending):
            break
    assert not any(pending)
    original = tuple(sorted(marks))
    first = marks[0]
    rename = list(range(width))
    rename[first], rename[replace] = replace, first
    image = tuple(sorted(rename[v] for v in original))
    assert original in legal and image not in legal
    assert len(owner[replace]) == len(owner[marks[1]]) == 1 and owner[replace] == owner[marks[1]]
    changed = [(i, j, scalar[i][j], scalar[rename[i]][rename[j]]) for i, j in combinations(range(width), 2)
               if scalar[i][j] != scalar[rename[i]][rename[j]]]
    first_separating = min(min(a, b) for _, _, a, b in changed)
    assert short_multi == []
    histogram = Counter(scalar[i][j] for i, j in combinations(range(width), 2))
    return {
        "width": width, "sites": len(rows), "history": rows,
        "arity_counts": dict(sorted(Counter(map(len, rows)).items())),
        "legal_mark": original, "forbidden_image": image, "transposition": [first, replace],
        "legal_triples": len(legal), "number_of_bonds": count,
        "all_named_pairs_compared": width * (width - 1) // 2,
        "first_K_distinguishing_the_map": first_separating,
        "named_pairs_changed_in_full_table": len(changed),
        "marked_pair_K_before_after": [scalar[first][marks[1]], scalar[replace][marks[1]]],
        "short_bonds_with_three_or_more_sites": len(short_multi),
        "full_K_histogram": dict(sorted(histogram.items())),
    }


def main():
    report = {}
    for label, maxima, horizon in (("five_place_holders", (1, 1, 1), 5),
                                   ("six_place_holders", (2, 2, 1), 6)):
        rows, parents, marks, replace = open_box(maxima)
        result = fixed_test(rows, marks, replace)
        assert result["first_K_distinguishing_the_map"] == horizon
        result["chronological_coordinates_of_mark_holders"] = parents
        report[label] = result
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
