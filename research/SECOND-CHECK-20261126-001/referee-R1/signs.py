"""Check the two readings on the rebuilt equations and on the supplied weightings."""
import argparse
import json
from itertools import combinations
from pathlib import Path
from rebuild import independent, kernel, loose, mask, parity, places, syndrome, union

HERE = Path(__file__).resolve().parent


def words(generators):
    values = [0]
    for generator in generators:
        values += [x ^ generator for x in values]
    return values


def local_change(stage, label):
    """Use one old shared distinction, both of its holders and one child of each."""
    for old in places(label):
        holders = [row for row in stage if row & (1 << old)]
        if len(holders) != 2:
            continue
        first, second = holders
        for a in stage:
            if a in holders or not a & first:
                continue
            for b in stage:
                if b in holders or a == b or not b & second:
                    continue
                ids = list(places(first | second | a | b))
                for selected in combinations(ids, 5):
                    move = mask(selected)
                    if (move & (1 << old) and not syndrome(move, stage)
                        and parity(move, label) and move & loose(stage)):
                        return move, [stage.index(row) for row in (first, second, a, b)]
    raise ValueError("no witness in four holders")


def autocorrelation(weighting, change):
    return sum(a*weighting.get(x ^ change, 0) for x, a in weighting.items())


def split_tables(n, allowed, label):
    """Numerators of supplied expectations, contracted on the literal allowed words."""
    old = (1 << n)-1
    states = words(allowed)
    total = len(states)
    tables = {}
    for sign in ((1, -1) if label is not None else (1,)):
        weighting = {x: (sign if label is not None and parity(x, label) else 1) for x in states}
        correlations = [autocorrelation(weighting, t) for t in range(1 << n)]
        observed = set()
        for part in range(1, old):
            moments = correlations[part], correlations[old ^ part], correlations[old]
            assert moments == (0, 0, sign*total)
            # Multiply the joint probabilities by four. Order is ++, +-, -+, --.
            scaled = tuple((total+a*moments[0]+b*moments[1]+a*b*moments[2])//total
                           for a in (1, -1) for b in (1, -1))
            assert scaled == ((2, 0, 0, 2) if sign == 1 else (0, 2, 2, 0))
            observed.add(scaled)
        tables[sign] = dict(ordered_splits=old-1, four_times_probabilities=list(observed.pop()))
    return tables


def read_case(n, record):
    result = {}
    old = (1 << n)-1
    for setting in ("free", "pinned"):
        case = record[setting]
        stage = [mask(r) for r in case["grown_places"]]
        moves = [mask(r) for r in case["moves"]]
        pins = [1 << i for i in places(loose(stage))] if setting == "pinned" else []
        equations = stage+pins
        allowed = kernel(equations, case["width"])
        together = case["width"]-len(independent(equations+moves))
        row = dict(allowed_states=2**len(allowed), both_value_laws_states=2**together)
        label = mask(case["least_label"]) if case["distances"] else None
        if setting == "pinned":
            row["split_reads"] = split_tables(n, allowed, label)
            row["old_shared_value_rank"] = len(independent(x & old for x in allowed))
            if label is not None:
                least = [x for x in words(allowed) if parity(x, label)
                         and x.bit_count() == case["distances"][1]]
                assert old in least
                avoids_old = [x for x in least if not (x & old)]
                row.update(least_change_count=len(least), least_avoiding_old=len(avoids_old))
                if avoids_old:
                    row["change_avoiding_old_example"] = list(places(avoids_old[0]))
        else:
            assert not syndrome(old, moves) and any(parity(old, g) for g in allowed)
            t, holders = local_change(stage, old)
            row.update(change=list(places(t)), holders=holders,
                       ordinary_old_ring_label=list(places(old)))
            class_labels = (x for x in words(kernel(moves, case["width"]))
                            if x.bit_count() == case["distances"][0] and parity(x, t))
            least = sorted(class_labels)
            only_loose = [x for x in least if not (x & ~loose(stage))]
            row.update(least_label_count=len(least), least_entirely_loose=len(only_loose))
            if only_loose:
                row["loose_label_example"] = list(places(only_loose[0]))
            assert old in least and label in least
            # The free five-knot case is also small enough for a literal sum.
            if n == 5:
                states = words(allowed)
                row["change_numerators"] = [autocorrelation(
                    {x: sign if parity(x, old) else 1 for x in states}, t) for sign in (1, -1)]
                assert row["change_numerators"] == [len(states), -len(states)]
        result[setting] = row
        print(n, setting, row)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sizes", nargs="+", type=int, choices=range(5, 9))
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    data = json.loads((HERE/"rings.json").read_text())
    result = {n: read_case(n, data[str(n)]) for n in args.sizes}
    if args.output:
        args.output.write_text(json.dumps(result, indent=1)+"\n")


if __name__ == "__main__":
    main()
