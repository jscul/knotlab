"""Take each currently legal triple one step further at the earlier width-46 example."""

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLDER = HERE.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001L" / "VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third"
SPEC = spec_from_file_location("earlier_continuation", OLDER / "continuation.py")
previous = module_from_spec(SPEC)
SPEC.loader.exec_module(previous)


def joined_table(old_table, rows, original_sites, width):
    local, _ = previous.previous.wired_table(rows[original_sites:])
    numbers = []
    for x, y in combinations(range(width), 2):
        if y < 28:
            k = old_table[x, y]
        elif x == 23 or x >= 28:
            k = local[x, y]
        else:
            k = old_table[tuple(sorted((x, 23)))] + local[23, y] - 2
        numbers.append(k - 1)
    return numbers


def run():
    record = json.loads((OLDER / "continuation.json").read_text())
    source = record["full_law_identity_equal_with_legal_triples"]
    roots = previous.original()
    old_tables = [previous.entries(rows, dual_check=True) for rows in roots]
    states = list(roots)
    for inputs, outputs in source["inputs_and_output_counts"]:
        states = [previous.extend(rows, inputs, outputs) for rows in states]
    triples = [tuple(g) for g in source["legal_triples"]]
    assert len(triples) == 8 and all(sorted(previous.menu(rows, 3)) == triples for rows in states)
    results = []
    for group, fresh in product(triples, (2, 3)):
        grown = [previous.extend(rows, group, fresh) for rows in states]
        width = 46 + fresh
        tabs = [joined_table(old, rows, len(base), width)
                for old, rows, base in zip(old_tables, grown, roots, strict=True)]
        assert tabs[0] == tabs[1] and previous.matches_transport(*grown)
        checked_whole = 0
        if group == triples[0]:
            for rows, table in zip(grown, tabs, strict=True):
                direct = previous.entries(rows)
                assert [direct[k] - 1 for k in sorted(direct)] == table
                checked_whole += 1
        menus = [previous.menu(rows, 3) for rows in grown]
        assert menus[0] == menus[1]
        results.append(dict(mark=group, new=fresh, width=width, equal_entries=len(tabs[0]),
                            table_sha256=sha256(bytes(tabs[0])).hexdigest(), next_triples=menus[0],
                            independently_measured_whole_tables=checked_whole))
    return dict(source_sha256=sha256((OLDER / "continuation.json").read_bytes()).hexdigest(),
                method="Original tables by the wired-graph and parity-span methods. All later entries by the proved single-distinction attachment law and a direct local bond calculation.",
                choices=results)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
