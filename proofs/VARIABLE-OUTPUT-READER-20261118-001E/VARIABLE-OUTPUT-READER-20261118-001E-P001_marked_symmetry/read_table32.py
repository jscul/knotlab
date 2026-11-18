"""Replay the anonymous three-parent reader for the specified width-32 table."""

from itertools import combinations
import json
from random import Random

from check_32_realizations import PRIOR, WIDTH, graphic, physical_verdicts, short


def eligible_triples(distinctions, distances):
    """Apply the table-specific predicate to every unordered triple."""
    return {
        frozenset(triple) for triple in combinations(distinctions, 3)
        if all(distances[frozenset(pair)] == 6 for pair in combinations(triple, 2))
    }


def run():
    source = json.loads((PRIOR / "active_part.json").read_text())["completions"][0]
    stars = source["junction_supports"]
    table = short.bridge.scalar_table(graphic.cut_supports(short.bridge, stars), WIDTH)
    expected = {frozenset(triple) for triple in physical_verdicts(stars)}
    names = list(range(WIDTH))
    observed = {frozenset(pair): value for pair, value in table.items()}
    accepted = eligible_triples(names, observed)
    candidates = {a for triple in accepted for a in triple}
    assert len(candidates) == 6 and len(accepted) == 8 and accepted == expected
    four_neighbors = {
        a for a in names
        if sum(observed[frozenset((a, b))] == 4 for b in names if b != a) == 4
    }
    assert candidates == four_neighbors
    partners = {a: {b for b in candidates if b != a
                    and observed[frozenset((a, b))] == 3} for a in candidates}
    assert all(len(pair) == 1 for pair in partners.values())
    assert all(observed[frozenset((a, b))] == 6 for a, b in combinations(candidates, 2)
               if b not in partners[a])
    wrong = frozenset((26, 27, 28))
    assert wrong.issubset(candidates) and wrong not in accepted
    altered = dict(observed)
    altered[frozenset((26, 27))] = 6
    assert wrong in eligible_triples(names, altered) and wrong not in expected
    shuffled = list(names)
    Random(19404).shuffle(shuffled)
    alternative = {frozenset(shuffled[a] for a in pair): value
                   for pair, value in observed.items()}
    shuffled_accepted = eligible_triples(list(reversed(shuffled)), alternative)
    assert shuffled_accepted == {frozenset(shuffled[a] for a in group) for group in accepted}
    print(f"{len(candidates)} candidates, {len(accepted)} legal triples, "
          "zero mismatches from their three pair distances alone.")


if __name__ == "__main__":
    run()
