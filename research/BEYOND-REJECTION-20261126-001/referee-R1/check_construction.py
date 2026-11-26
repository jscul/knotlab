"""Independently reduce the archived ordinary construction to terminal counts."""
import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = next((ROOT / "artifacts/WHOLE-STAGE-SETTINGS-20261120-001C").glob("*/physical.json"))
BITS = (0, 1)
PAIRS = tuple(product(BITS, repeat=2))
WORDS = tuple(product(BITS, repeat=3))


def allowed(values, law):
    ones = sum(values)
    return ones % 2 == 0 if law == "parity" else 0 < ones < len(values)


def local_factor(rows, side, law):
    local = [s for k, s in rows.items() if k.startswith(side + ".")]
    terminals = sorted(x for x in rows[side + ".detector"] if x.startswith("terminal"))
    names = terminals + sorted(set().union(*local) - set(terminals))
    masks = [sum(1 << names.index(x) for x in s) for s in local]
    counts = Counter()
    for state in range(1 << len(names)):
        weights = [(m & state).bit_count() for m in masks]
        if law == "parity":
            ok = all(w % 2 == 0 for w in weights)
        else:
            ok = all(0 < w < m.bit_count() for w, m in zip(weights, masks))
        if ok:
            counts[tuple((state >> i) & 1 for i in range(3))] += 1
    return counts


def terminal_counts(rows, law):
    # Follow the actual terminal names of successive pairs in the receipt.
    following = {}
    for k, left in rows.items():
        if k.endswith(".left"):
            right = rows[k.removesuffix(".left") + ".right"]
            assert set(left[1:]) == set(right[1:]) and len(left[1:]) == 2
            following[left[0]] = right[0]
    one = [[sum(allowed((a, *mid), law) and allowed((b, *mid), law)
                for mid in PAIRS) for b in BITS] for a in BITS]
    destinations = []
    for i in range(3):
        name = f"terminal0.{i}"
        steps = 0
        while name in following:
            name = following[name]
            steps += 1
        assert steps == 8 and name.startswith("terminal8.")
        destinations.append(int(name.split(".")[-1]))
    transfer = [[1, 0], [0, 1]]
    for _ in range(8):
        transfer = [[sum(transfer[i][k] * one[k][j] for k in BITS)
                     for j in BITS] for i in BITS]
    left, right = (local_factor(rows, side, law) for side in ("A", "B"))
    counts = {}
    for a, b in product(WORDS, repeat=2):
        mass = left[a] * right[b]
        for i, dest in enumerate(destinations):
            mass *= transfer[a[i]][b[dest]]
        counts[a, b] = mass
    return destinations, one, counts


def check_type(receipt, uv, law):
    u, v = map(int, uv)
    old = receipt["old_supports"]
    dest, one, counts = terminal_counts(old, law)
    stored = receipt["laws"][law]
    assert dest == receipt["correspondence"]
    assert [[counts[a, b] for b in WORDS] for a in WORDS] == stored["old_terminal_weights"]["counts"]
    old_uses = Counter(name for support in old.values() for name in support)
    assert len(old) == 56 and len(old_uses) == 95
    pre_sizes = [len(receipt["pre_accessible"][s]["owned_distinctions"]) for s in ("A", "B")]
    assert pre_sizes == [22, 22]
    granted = 0
    for x, y in PAIRS:
        trial = stored["trials"][f"{x}{y}"]
        edited = old | trial["edited_supports"]
        uses = Counter(name for support in edited.values() for name in support)
        assert len(uses) == 97
        proposals = set()
        enough = True
        for s, prep, setting in (("A", u, x), ("B", v, y)):
            center = set(edited[f"{s}.center"])
            neighbors = [k for k, row in edited.items() if k != f"{s}.center" and center.intersection(row)]
            assert set(neighbors) == {f"{s}.address0", f"{s}.address1", f"{s}.detector"}
            proposals.update(tuple(sorted(pair)) for pair in combinations(neighbors, 2))
            for index in BITS:
                row = edited[f"{s}.address{index}"]
                loose = sum(uses[d] == 1 for d in row)
                assert loose == 2 - (index == prep) + (index == setting)
                enough &= loose >= 2
        recorded = trial["ordinary_round"]
        assert proposals == {tuple(sorted(p)) for p in recorded["proposed_groups"]}
        assert enough == ((x, y) == (u, v)) == (recorded["status"] == "extend")
        assert len(recorded["births"]) == 6 * enough
        for s in ("A", "B"):
            post = trial["post_accessible"][s]
            assert set(post["supports"]) >= set(receipt["pre_accessible"][s]["supports"])
            assert len(post["owned_distinctions"]) == (26 if enough else 23)
            assert len(post["owned_distinctions"][f"{s}.mark"]) == 1 + enough
        granted += enough
    return counts, {"destinations": dest, "one_pair_counts": one,
                    "positive_terminal_pairs": sum(c > 0 for c in counts.values()),
                    "old_assignments": sum(counts.values()), "funded_addresses": granted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="first law and preparation from the same run")
    args = parser.parse_args()
    start = perf_counter()
    data = json.loads(ARCHIVE.read_text())["modes"]["primary"]
    output = {}
    for law in (("parity",) if args.pilot else ("parity", "nae")):
        by_type = {}
        types = {}
        for uv in (("00",) if args.pilot else sorted(data)):
            by_type[uv], types[uv] = check_type(data[uv], uv, law)
        info = {"types": types}
        if not args.pilot:
            correlations = []
            for x, y in PAIRS:
                funded = by_type[f"{x}{y}"]
                disagreement = sum(n for (a, b), n in funded.items() if a[0] != b[0])
                correlations.append(1 - Fraction(disagreement, 2 * sum(funded.values())))
            info["uniform_old_correlations"] = list(map(str, correlations))
            info["uniform_old_CHSH"] = str(sum(correlations[:3]) - correlations[3])
        output[law] = info
    output["elapsed_seconds"] = round(perf_counter() - start, 6)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
