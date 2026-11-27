"""Replay the relay and chain counterexamples with an explicit demand lookahead."""

import argparse
from collections import Counter
from dataclasses import replace
import gzip
import json
from math import comb
from pathlib import Path

from core import build_core
from reader import _piece_terms, predict_core


HERE = Path(__file__).resolve().parent
LAWS = ("nae", "parity")
CASES = (
    ("relay", "cyc7_treeplus", "draw", 335, 24, "two overlapping round-one groups"),
    ("relay", "cyc6_uniform", "index", 13560, 24, "two overlapping blocks"),
    ("chains", "cyc7_treeplus", "draw", 109, 9, "cycled piece with one attached chain"),
    ("lookahead", "cyc7_treeplus", "draw", 116, 24, "unfinished core without chains"),
)


def grown_record(source, key, value, law):
    filename = HERE.parent / f"grown_{source}_{law}.jsonl.gz"
    with gzip.open(filename, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get(key) == value:
                return row
    raise ValueError(f"missing {key} {value} in {filename.name}")


def first_coded(read, rounds, law):
    """Apply the first relay gate and keep the set-based chains on unfinished cores."""
    if read.status != "in":
        return None, read.status
    relay_allowed = law == "nae" or len(read.pieces) > 1
    count0 = [Counter() for _ in range(rounds + 1)]
    count1 = [Counter() for _ in range(rounds + 1)]
    for piece in read.pieces:
        if piece.stop not in ("rank cap", "finished"):
            return None, piece.stop
        relay = not piece.cycle and not piece.chains and relay_allowed
        if relay:
            tips = [label for label, node in piece.nodes.items()
                    if node.points == piece.points and not node.children]
            if len(tips) != 1:
                return None, "not one last birth holding the whole piece"
            # Only the last rank is needed to locate the gated relay in these cases.
            if piece.ranks[max(piece.ranks)] != tuple(tips):
                raise ValueError("first-coded relay lies outside this audit's tip cases")
        for own, parents, first, long, multiplicity in _piece_terms(
            replace(piece, relay=relay), read.sizes, rounds, relay_allowed
        ):
            for t in range(first, rounds + 1 if long else first + 1):
                number = multiplicity * (comb(t - first + long - 1, long - 1) if long else 1)
                count0[t][own] += number
                count1[t][parents] += number
    rows = [
        {"n": sum(c0.values()),
         "sig0": sorted([list(sig), n] for sig, n in c0.items()),
         "sig1": sorted([[list(sig[:4]), [list(parent) for parent in sig[4]]], n]
                        for sig, n in c1.items())}
        for c0, c1 in zip(count0[1:], count1[1:])
    ]
    return rows, "predicted"


def signature_delta(predicted, observed, show_signatures):
    def counts(row, kind):
        return Counter({json.dumps(sig): count for sig, count in row[kind]})

    def excess(a, b, kind):
        extra = counts(a, kind) - counts(b, kind)
        result = {"births": extra.total()}
        if show_signatures:
            result["signatures"] = [[json.loads(sig), n] for sig, n in sorted(extra.items())]
        return result

    return {
        kind: {"prediction only": excess(predicted, observed, kind),
               "growth only": excess(observed, predicted, kind)}
        for kind in ("sig0", "sig1")
    }


def compare(result, grown, rounds, *, show_signatures=True):
    rows, status = result
    if rows is None:
        return {"status": status}
    observed = grown["rows"][:rounds]
    if grown["end"].startswith("closes"):
        observed += [{"n": 0, "sig0": [], "sig1": []}] * (rounds - len(observed))
    first = next((t for t, pair in enumerate(zip(rows, observed), 1) if pair[0] != pair[1]), None)
    outcome = {"status": status, "rounds compared": len(observed), "first differing round": first}
    if first is not None:
        p, g = rows[first - 1], observed[first - 1]
        outcome.update({"predicted births": p["n"], "grown births": g["n"],
                        "signature differences": signature_delta(p, g, show_signatures)})
    return outcome


def piece_summary(read, rounds):
    out = []
    for piece in read.pieces:
        tip_rank = max(piece.ranks)
        target_nodes = [piece.nodes[label] for label in piece.ranks.get(rounds + 1, ())]
        out.append({"cycle by count": piece.cycle, "chains": sum(piece.chains.values()),
                    "stop": piece.stop, "highest stored rank": tip_rank, "core births": piece.birth_count,
                    "chained-twin rank": piece.twin_rank,
                    "births at last read round": len(target_nodes),
                    "total core demand at last read round": sum(len(node.children) for node in target_nodes)})
    return out


def chain_copy_probe(read, grown, rounds, law):
    """Add the second occurrence on the birth whose two parents already hold the base."""
    piece, = read.pieces
    base, = piece.chains
    matches = []
    for label in piece.ranks[rounds + 1]:
        birth = piece.nodes[label]
        if len(birth.parents) != 2:
            continue
        left, right = (piece.nodes[parent] for parent in birth.parents)
        common = set(left.parents) & set(right.parents)
        if (base in left.points & right.points and common
                and all(base not in piece.nodes[prior].points for prior in common)):
            matches.append((label, left, right, common))
    if len(matches) != 1:
        raise ValueError("expected one birth with two distinct sources of the chain base")
    (label, left, right, common), = matches
    birth = piece.nodes[label]
    second_base = max(piece.points) + 1
    updated = replace(piece, points=piece.points | {second_base},
                      nodes={**piece.nodes, label: replace(birth, points=birth.points | {second_base})},
                      chains={**piece.chains, second_base: piece.chains[base]})
    return {
        "core children": len(birth.children),
        "chain base": base,
        "birth points": sorted(birth.points),
        "parent points": [sorted(left.points), sorted(right.points)],
        "common earlier parent points": [sorted(piece.nodes[prior].points) for prior in sorted(common)],
        "with second chain occurrence at that birth": compare(
            first_coded(replace(read, pieces=(updated,)), rounds, law), grown, rounds
        ),
    }


def audit(case, law, max_births=5000):
    mode, source, key, value, rounds, description = case
    grown = grown_record(source, key, value, law)
    with_demand = build_core(grown["stars"], law, max_rank=rounds + 2, max_births=max_births)
    record = {
        "case": mode, "source": source, key: value, "description": description, "law": law,
        "rounds requested": rounds, "growth end": grown["end"],
        "pieces with lookahead": piece_summary(with_demand, rounds),
        "frozen with lookahead": compare(predict_core(with_demand, rounds, law), grown, rounds),
        "first-coded with lookahead": compare(first_coded(with_demand, rounds, law), grown, rounds),
    }
    if mode != "relay":
        without_demand = build_core(grown["stars"], law, max_rank=rounds + 1, max_births=max_births)
        record.update({
            "pieces without lookahead": piece_summary(without_demand, rounds),
            "frozen without lookahead": compare(predict_core(without_demand, rounds, law), grown, rounds),
            "first-coded without lookahead": compare(
                first_coded(without_demand, rounds, law), grown, rounds, show_signatures=False
            ),
        })
    if mode == "chains":
        record["chain copy probe"] = chain_copy_probe(with_demand, grown, rounds, law)
        capped = build_core(grown["stars"], law, max_rank=25, max_births=max_births)
        record["core read toward size-rank 25"] = piece_summary(capped, rounds)
    return record


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pilot", action="store_true", help="run only the not-all-equal chained start")
    args = cli.parse_args()
    runs = [(CASES[2], "nae")] if args.pilot else [(case, law) for case in CASES for law in LAWS]
    print(json.dumps([audit(case, law) for case, law in runs], indent=2))


if __name__ == "__main__":
    main()
