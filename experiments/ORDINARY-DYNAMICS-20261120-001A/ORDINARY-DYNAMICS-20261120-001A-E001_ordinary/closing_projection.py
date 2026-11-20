"""Read the root-star comparison directly from all allowed physical assignments."""
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
TRIPLE = (10, 11, 12)


def literal_stars(extra):
    hub = (0, 1, 2, 9) if extra else (0, 1, 2)
    original = [hub, (0, 3, 4), (1, 5, 6), (2, 7, 8)]
    # The three children of the three ungathered pairs around the same holder.
    first = [(3, 5, 10), (6, 7, 11), (8, 4, 12)]
    if extra:
        first.append((9, 13, 14))
    return original, first


def local_words(arity, law):
    if law == "parity":
        return {word for word in product((0, 1), repeat=arity) if sum(word) % 2 == 0}
    return {word for word in product((0, 1), repeat=arity) if 0 < sum(word) < arity}


def projections(stars, query, law):
    names = sorted(set().union(*(set(row) for row in stars)))
    index = {p: i for i, p in enumerate(names)}
    masks = [sum(1 << index[p] for p in row) for row in stars]
    actual = set()
    projected = [set() for _ in stars]
    count = 0
    for word in range(1 << len(names)):
        if law == "parity":
            permitted = all((word & mask).bit_count() % 2 == 0 for mask in masks)
        else:
            permitted = all(0 < word & mask < mask for mask in masks)
        if not permitted:
            continue
        count += 1
        actual.add(tuple((word >> index[p]) & 1 for p in query))
        for i, row in enumerate(stars):
            projected[i].add(tuple((word >> index[p]) & 1 for p in row))
    for row, words in zip(stars, projected):
        assert words == local_words(len(row), law)
        for omit in range(len(row)):
            assert len({w[:omit]+w[omit+1:] for w in words}) == 2 ** (len(row)-1)
    return count, sorted("".join(map(str, w)) for w in actual)


def main():
    rows = []
    for extra in (False, True):
        original, first = literal_stars(extra)
        for law in ("parity", "not-all-equal"):
            source_count, _ = projections(original, (), law)
            stage_count, visible = projections(original+first, TRIPLE, law)
            implied = all(tuple(map(int, w)) in local_words(3, law) for w in visible)
            assert implied == (law == "parity" and not extra)
            # All three input slots are spent by one real ternary child.
            # No other newborn shares its parents, hence the next group demand is zero.
            fresh = 0 if implied else 1
            recoded = {m: 37-2*m for row in original+first for m in row}
            moved = [tuple(recoded[m] for m in row) for row in reversed(original+first)]
            assert projections(moved, tuple(recoded[m] for m in TRIPLE), law) == (stage_count, visible)
            rows.append(dict(added=extra,law=law,source_assignments=source_count,stage_assignments=stage_count,
                             triple_projection=visible,triple_implied=implied,central_fresh=fresh,
                             source_and_reached_stars_have_full_knots=True))
    output = dict(control="same unlabelled first three pairs; directly enumerate the whole physical source and first stage",
                  source="one hub and three two-loose leaves; exactly one extra loose at hub in paired source",
                  pair_children=[list(x) for x in literal_stars(False)[1]],rows=rows)
    (OUT/"closing_projection.json").write_text(json.dumps(output,indent=2)+"\n")
    for row in rows:
        print(row["added"],row["law"],row["source_assignments"],row["stage_assignments"],row["triple_projection"],row["central_fresh"])

if __name__ == "__main__":
    main()
