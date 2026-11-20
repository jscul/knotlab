"""Verify the central study comparisons and replay the two rational brackets."""
from collections import deque
from fractions import Fraction
from math import prod
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def read_json(name):
    return json.loads((DATA/name).read_text())


def shortest(start, finish, onward):
    seen = {start}
    todo = deque([(start, 0)])
    while todo:
        point, steps = todo.popleft()
        if point == finish:
            return steps
        for other in onward[point]:
            if other not in seen:
                todo.append((other, steps+1))
                seen.add(other)
    raise ValueError('no return to the selected branch')


def check_rate(case, certificate, scale):
    # Use ordered simple neighbourhoods of the supplied source.
    neighbours = [set() for _ in case['sizes']]
    for v,w in case['meetings']:
        neighbours[v].add(w)
        neighbours[w].add(v)
    blocks = [sorted(row) for row in neighbours if len(row) >= 2]
    ports = [(v,b) for b,block in enumerate(blocks) for v in block]
    onward = {(v,b):[(w,c) for c,block in enumerate(blocks) if c != b and v in block
                     for w in block if w != v] for v,b in ports}
    loose = [size-len(row) for size,row in zip(case['sizes'],neighbours)]
    spare = [loose[v]-sum(len(row)-1 for row in blocks if v in row) for v in range(len(loose))]

    def equation(port, z, values):
        v,_ = port
        factor = (1+z/(1-z)**max(0,3-loose[v]))**spare[v]
        return 1+z*factor*prod(values[q] for q in onward[port])

    upper = certificate['upper_certificate']
    z = 1/Fraction(upper['x'])
    values = dict(zip(ports, [Fraction(v, scale) for v in upper['positive_supersolution_scaled_in_port_order']], strict=True))
    assert all(equation(p,z,values) <= values[p] for p in ports)

    lower = certificate['lower_certificate']
    z = 1/Fraction(lower['x'])
    root, left, right = map(tuple, lower['ports'])
    assert left != right and left in onward[root] and right in onward[root]
    exponent = 1+shortest(left,root,onward)+shortest(right,root,onward)
    assert exponent == lower['power']
    bound = 1/z**exponent
    cap = Fraction(int(scale*bound)+2, scale)
    values = dict.fromkeys(ports, Fraction(1))
    for _ in range(lower['iterations']):
        values = {p:min(cap,Fraction(int(scale*equation(p,z,values)),scale)) for p in ports}
    assert values[root] == Fraction(lower['lower_ordinate_scaled'],scale) > bound


def main():
    inputs = {c['id']:c for c in json.loads((HERE/'inputs.json').read_text())['cases']}
    certs = read_json('fate_rate_bounds.json')
    for name, cert in certs['cases'].items():
        check_rate(inputs[name], cert, certs['scale'])
    physical = read_json('stages.json')['cases']
    coverage = {name:len(o['stages']) for name,o in physical.items()}
    assert sum(coverage.values()) == read_json('recognition.json')['verified_stages'] == 160
    source = read_json('source_bonds.json')['matrices']
    first = read_json('bond_first.json')
    for row in first['records']:
        name = row['case']
        if row['age'] == 0 and name in source:
            for i,anchor in enumerate(row['path']):
                assert anchor['path_bond_distances'] == source[name][i]
    ring = read_json('ring_distance_dp.json')['cases']
    for name, expected in [('T4',(31,19,27)),('T8',(39,27,35))]:
        for age in range(3):
            frame = physical[name]['stages'][str(age)]
            entry = ring[name]['ages'][str(age)]
            assert entry['status']=='exact'
            for tier, witness in entry['readings'].items():
                value = expected[0] if age == 0 else expected[1 if tier == 'all_exclusive' else 2]
                assert witness['bond_distance'] == value
                support = set()
                for knot in witness['shore']:
                    support.symmetric_difference_update(frame['stars'][knot])
                assert support == set(witness['bond']) and len(support)==value+1
    singles = read_json('fate_series.json')['cases']
    for name, size, last in [('T4',4,89),('T8',6,4)]:
        counts = singles[name]['both_exclusive_by_age']
        assert counts.index(4) == size-1 and counts[size-1] == 4
        for age in range(6):
            stages = [physical[k]['stages'][str(age)] for k in (name,'J1','B')]
            full, one, path = (len(frame['live']) for frame in stages)
            assert counts[age] == full - 2*one + path
        assert counts[5] == last
        d = int(name[1:])
        assert singles[name]['physical_growing_separation_by_age'][:6] == [d+2]+[d+2*t for t in range(1,6)]
    for entry in first['comparisons']:
        if entry['case'] == 'J1' and entry['reference'] == 'B':
            age = entry['age']
            assert entry['full_balls']['5']['0']['mean_signed_delta'] == str((-7,-17)[age])
            assert entry['restricted_balls']['5']['0']['mean_signed_delta'] == '-3'
    print('Replayed both rational rate brackets, 840 marked source pairs, all case cutoffs, both interaction onsets, 18 exact two-ring bond witnesses and the first two near-attachment profiles.')


if __name__ == '__main__':
    main()
