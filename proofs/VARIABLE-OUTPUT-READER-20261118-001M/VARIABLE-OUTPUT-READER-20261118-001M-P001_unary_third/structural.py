"""Check the large five-shore lemma on early and late third-unary histories."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1]


def bitmask(bits):
    return sum(1 << bit for bit in bits)


def incidence(rows):
    holders = {}
    for site, row in enumerate(rows):
        for bit in row:
            holders.setdefault(bit, []).append(site)
    adjacent = [set() for _ in rows]
    for sites in holders.values():
        if len(sites) == 2:
            a, b = sites
            adjacent[a].add(b)
            adjacent[b].add(a)
        else:
            assert len(sites) == 1
    return holders, adjacent


def legal(rows, marks):
    holders, adjacent = incidence(rows)
    if any(len(holders[bit]) != 1 for bit in marks):
        return False
    sites = [holders[bit][0] for bit in marks]
    return (len(set(sites)) == len(sites)
            and all(adjacent[a] & adjacent[b] for a, b in combinations(sites, 2))
            and (len(sites) < 3 or not set.intersection(*(adjacent[site] for site in sites))))


def adjoin(rows, marks, outputs):
    assert legal(rows, marks)
    first = 1 + max(bit for row in rows for bit in row)
    return [*rows, [*marks, *range(first, first + outputs)]]


def binary_fork(rows):
    holders, _ = incidence(rows)
    loose = sorted(bit for bit, sites in holders.items() if len(sites) == 1)
    moves = [bits for bits in combinations(loose, 2) if legal(rows, bits)]
    first, second = next((a, b) for a, b in combinations(moves, 2) if set(a).isdisjoint(b))
    return adjoin(adjoin(rows, first, 2), second, 2)


def check(rows, name):
    holders, _ = incidence(rows)
    stars = [bitmask(row) for row in rows]
    inputs = [tuple(bit for bit in row if holders[bit][0] != site) for site, row in enumerate(rows)]
    unaries = [i for i, ins in enumerate(inputs) if len(ins) == 1]
    caps = [i for i, ins in enumerate(inputs) if len(ins) == 3]
    assert len(unaries) == 3 and set(unaries[:2]) == {1, 2}
    assert all(legal(rows[:i], inputs[i]) for i in range(1, len(rows)))
    short_shores = {}
    shore = cut = 0
    for index in range(1, 1 << len(stars)):
        changed = index & -index
        shore ^= changed
        cut ^= stars[changed.bit_length() - 1]
        if shore.bit_count() < 3:
            continue
        assert cut.bit_count() >= 5
        if cut.bit_count() == 5:
            short_shores[shore] = cut
            assert shore & 1 and (shore & bitmask(unaries)).bit_count() >= 2
            for edge, sides in holders.items():
                if cut & (1 << edge):
                    assert shore & (1 << sides[0])
    assert all(a | b in short_shores for a, b in combinations(short_shores, 2))
    exposed = 0
    for cut in short_shores.values():
        exposed |= cut
    clean = {}
    for site in caps:
        choices = [edge for edge in inputs[site] if not exposed & (1 << edge) and holders[edge][0] != 0]
        assert choices
        clean[site] = choices
    return {'name': name, 'width': len(holders), 'sites': len(rows), 'shrinks': len(caps),
            'nonempty_shores_checked': (1 << len(rows)) - 1, 'large_five_shores': len(short_shores),
            'incomparable_large_five_pairs': sum((a & b) not in (a, b) for a, b in combinations(short_shores, 2)),
            'protected_nonseed_inputs_per_shrinking_site': clean, 'junction_supports': rows}


def main():
    first, = (PROOFS / 'VARIABLE-OUTPUT-READER-20261118-001J').glob('*/frontier.json')
    second, = (PROOFS / 'VARIABLE-OUTPUT-READER-20261118-001K').glob('*/alternate.json')
    original = json.loads(first.read_bytes())['closure']['first_histories_by_shrinking_joins']['2']
    later = binary_fork(adjoin(original, (21, 24), 2))
    loose = [bit for bit, sites in incidence(later)[0].items() if len(sites) == 1]
    late_unary = adjoin(later, (min(loose),), 3)
    positive = json.loads(second.read_bytes())['unary_third']['first_positive_state_at_or_above_threshold']
    third = positive['junction_supports']
    fourth = adjoin(third, positive['legal_mark'], 2)
    controls = [check(late_unary, 'late unary after a pair of independent binary additions'),
                check(third, 'early unary with a positive triple after three shrinks'),
                check(fourth, 'the fourth shrink'), check(binary_fork(fourth), 'two binary additions after four shrinks')]
    assert any(item['incomparable_large_five_pairs'] for item in controls)
    print(json.dumps({'prior_sources': {str(p.relative_to(PROOFS)): sha256(p.read_bytes()).hexdigest()
                                       for p in (first, second)}, 'controls': controls}, indent=2))


if __name__ == '__main__':
    main()
