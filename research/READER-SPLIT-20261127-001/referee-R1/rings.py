"""Test every possible length against the actual holdings; retain one shortest construction."""
import json
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def ring_data(row):
    knots = row['supports']
    copies = {}
    near = [set() for k in knots]
    for a, b in combinations(range(len(knots)), 2):
        meeting = set(knots[a]) & set(knots[b])
        if meeting:
            copies[a,b] = copies[b,a] = sorted(meeting)
            near[a].add(b)
            near[b].add(a)
    four = any(all(b in near[a] for a,b in combinations(f,2))
               for f in combinations(range(len(knots)),4))
    pairs = {tuple(p): 1 << i for i,p in enumerate(row['pairs'])}
    max_degree = max(map(len, near))
    def find_one(n):
        for h, others in enumerate(near):
            for knots_used in combinations(sorted(others), n):
                for tail in permutations(knots_used[1:]):
                    if tail[-1] < tail[0]:
                        continue
                    cycle = (knots_used[0], *tail)
                    if any(cycle[(i+1)%n] not in near[k] for i,k in enumerate(cycle)):
                        continue
                    chosen = []
                    m = (n-1)//2
                    for i,k in enumerate(cycle):
                        across = copies[cycle[(i+m)%n],cycle[(i+m+1)%n]]
                        options = (tuple(sorted(p)) for p in product(copies[h,k], across))
                        pair = next((p for p in options if p in pairs), None)
                        if pair is None:
                            break
                        chosen.append(pair)
                    if len(chosen) == n:
                        mask = sum(pairs[p] for p in chosen)
                        assert len(set(d for p in chosen for d in p)) == 2*n
                        assert not any((c & mask).bit_count()%2 for c in row['checks'])
                        assert (row['cost'] & mask).bit_count()%2 == 1
                        return dict(common_knot=h,ring=cycle,readers=chosen)
        return None
    rings = {}
    for n in range(3, max_degree + 1, 2):
        witness = find_one(n)
        if witness is not None:
            rings[n] = witness
    return four, max_degree, rings


def main():
    study = HERE.parent
    birth = {r['start']:r for r in map(json.loads,(study/'results.jsonl').open())}
    types = {r['type']:r for r in map(json.loads,(study/'census_types.jsonl').open())}
    fixtures = json.loads((study/'fixtures.json').read_text())
    depth = Counter()
    by = defaultdict(Counter)
    all_lengths = defaultdict(Counter)
    diffuse = []
    examples = {}
    ring_rows = []
    for row in map(json.loads,(HERE/'rebuilt_inputs.jsonl').open()):
        pop, key = row['population'],row['key']
        four,degree,rings = ring_data(row)
        n = min(rings,default=None)
        certificate = rings.get(n)
        all_lengths[pop][str(sorted(rings))] += 1
        by[pop][str(n)] += 1
        depth[pop] = max(depth[pop], degree)
        archive = {'birth':birth,'type':types,'fixture':fixtures}.get(pop,{}).get(key)
        if archive:
            assert archive['four mutually meeting knots'] == four
            assert archive['four meeting with decidable pairings'] == (n == 3)
            assert archive['shortest odd ring around a knot'] == n
        ring_rows.append(dict(population=pop,key=key,four=four,length=n,witness=certificate,all_lengths=sorted(rings)))
        if pop == 'birth':
            if max(map(len,row['supports'])) <= 3:
                diffuse.append(dict(key=key,knots=len(row['supports']),length=n))
            if n is None and archive['strict']:
                examples.setdefault(archive['fewest strict readers'],
                                    dict(census_start=key,supports=row['supports'],readers=archive['strict readers']))
    with (HERE/'ring_rows.jsonl').open('w') as target:
        for r in ring_rows:
            print(json.dumps(r,separators=(',',':')),file=target)
    data = dict(weighting='one vote per census start, separately one per finished type',
                shortest=by, combinations_of_lengths=all_lengths, maximum_distinct_knots_met=depth, at_most_three=diffuse,
                recorded_examples_without_an_odd_ring=examples)
    (HERE/'rings.json').write_text(json.dumps(data,indent=2)+'\n')
    print(dict(by), dict(depth))


if __name__ == '__main__':
    main()
