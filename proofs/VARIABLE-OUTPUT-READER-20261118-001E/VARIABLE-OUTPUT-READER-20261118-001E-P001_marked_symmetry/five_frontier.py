"""Test the change from a five-bit frontier to a permanently ineligible four-bit one."""

from itertools import combinations

from check_32_realizations import short
from targeted_countermodel import ROOT, adjoin, ambiguity, continuation


HISTORY = (
    ((0,), 3), ((1,), 3), ((0, 2), 3), ((1, 3), 2), ((2, 4), 2),
    ((3, 5), 2), ((0, 6), 2), ((5, 7), 2), ((2, 8), 2),
    ((1, 7, 9), 2), ((4, 8, 10), 2), ((3, 9, 11), 2),
)


def run():
    gluing = continuation.load(ROOT, *continuation.SOURCES[-1])
    sites = ((0, 1, 2),)
    for parents, fresh in HISTORY:
        sites, _ = adjoin(gluing, sites, parents, fresh)
    gluing.replay(sites)
    holders, _ = gluing.incidence(sites)
    frontier = tuple(sorted(bit for bit, group in holders.items() if len(group) == 1))
    cuts = continuation.cut_supports(gluing, sites)
    assert len(holders) == 30 and frontier == (17, 25, 27, 28, 29)
    assert short.as_mask(frontier) in cuts
    distances = gluing.scalar_table(cuts, len(holders))
    assert all(distances[pair] == 4 for pair in combinations(frontier, 2))
    actual = set(ambiguity.triples(gluing, sites))
    assert actual == {frozenset((17, 25, z)) for z in (28, 29)}
    forced, extra, _ = short.infer(distances, len(holders))
    assert not extra and len(forced).bit_length() - 1 == 13
    assert forced == short.span(short.as_mask(star) for star in sites)
    after, _ = adjoin(gluing, sites, (6, 10, 12), 2)
    gluing.replay(after)
    after_holders, _ = gluing.incidence(after)
    after_loose = {bit for bit, owners in after_holders.items() if len(owners) == 1}
    assert after_loose == {27, 29, 30, 31} and not ambiguity.triples(gluing, after)
    print("Width 30: all ten frontier pairs have distance 4, two of ten triples legal, "
          "the full distance table forces all 13 parity generators.")
    print("Width 32 after the three-parent join: four-bit frontier, no legal triple.")


if __name__ == "__main__":
    run()
