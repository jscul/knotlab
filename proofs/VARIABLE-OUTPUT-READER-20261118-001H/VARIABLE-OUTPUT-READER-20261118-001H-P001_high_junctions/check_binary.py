"""Replay the binary two-output obstruction to recognizing a six-place junction."""

from importlib import util
from itertools import combinations
import json
from pathlib import Path

PROOFS = Path(__file__).resolve().parents[2]


def module(name, ticket, file):
    path = next((PROOFS / ticket).glob("*/" + file))
    spec = util.spec_from_file_location(name, path)
    result = util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


oracle = module("preceding_high_audit", "VARIABLE-OUTPUT-READER-20261118-001F", "audit.py")
reader = module("short_support_deduction", "VARIABLE-OUTPUT-READER-20261118-001D", "check_scalar_span.py")


def construct():
    rows = [(0, 1, 2)]
    available = [[0, 1, 2]]
    width = 3

    def add(parents, fresh_count=3):
        nonlocal width
        taken = tuple(available[p].pop(0) for p in parents)
        fresh = list(range(width, width + fresh_count))
        width += fresh_count
        rows.append((*taken, *fresh))
        available.append(fresh.copy())
        return len(rows) - 1

    first = [add((0,)) for _ in range(3)]
    second = [add(parents) for parents in combinations(first, 2)]
    u = add(second)
    outputs = tuple(available[u])
    p, q = add((u,)), add((u,))
    w = add((p, q), 2)
    outside = available[w][0]
    add((u, w))
    yield "as_constructed", rows.copy(), u, outputs, outside, width
    # Close a second pair on two of the seed's children inside the original block.
    # The new terminal holder supplies a legal triple without removing the obstruction at u.
    add(first[:2])
    yield "one_more_join_with_a_legal_triple", rows.copy(), u, outputs, outside, width


def run():
    result = []
    for label, rows, u, outputs, outside, width in construct():
        oracle.replay_history(rows, tuple(range(len(rows))))
        scalar, number_of_bonds = oracle.scalar_minima(rows, width)
        table = {(i,j):scalar[i][j] for i,j in combinations(range(width),2)}
        observed = reader.compare_truth(label, width, rows, table)
        assert all(table[tuple(sorted((x,outside)))] <= 5 for x in outputs)
        sources = {}
        for a,b in combinations(rows[u],2):
            if table[a,b] != 5:
                continue
            close = [other for other in range(width) if other not in rows[u]
                     and scalar[a][other] <= 5 and scalar[b][other] <= 5]
            if not close:
                sources[f"{a},{b}"] = "only sites in the true six-place star are close to both"
        menu = sorted(oracle.permissions(rows))
        result.append({"fixture": label, "history": rows, "width": width, "six_place_site": rows[u],
                       "three_outputs": outputs, "outside_bit": outside,
                       "K_from_outputs_to_outside": [1+scalar[x][outside] for x in outputs],
                       "other_forcing_pairs_on_the_same_star": list(sources), "legal_triples": len(menu),
                       "one_legal_triple": menu[0] if menu else None,
                       "bonds_counted": number_of_bonds, "table_only_inference": observed})
    return result


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
