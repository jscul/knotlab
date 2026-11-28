"""Reconstruct pair decisions and signs from the archived growth engine and finished holdings."""
import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH / 'MOST-FAILING-20261127-001/referee-R1'))
import rebuild  # Previous referee's growth-history driver and its archived start roster.


def owners(supports):
    result = {}
    for k, knot in enumerate(supports):
        for d in knot:
            result.setdefault(d, []).append(k)
    return result


def independent(rows):
    pivots = {}
    for row in rows:
        while row:
            top = row.bit_length()
            if top not in pivots:
                pivots[top] = row
                break
            row ^= pivots[top]
    return len(pivots)


def system(stages, whole=False):
    supports = stages[-1]
    holders = owners(supports)
    assert all(len(v) == 2 for v in holders.values())
    snapshots = [owners(s) for s in stages]
    first = {d: next(t for t, h in enumerate(snapshots) if d in h) for d in holders}
    pairs = []
    for a, b in combinations(sorted(holders), 2):
        if set(holders[a]) & set(holders[b]):
            continue
        ha = snapshots[max(first[a], first[b])]
        if whole or len(ha[a]) == 2 or len(ha[b]) == 2:
            pairs.append((a, b))
    checks = []
    for u, v in combinations(range(len(supports)), 2):
        checks.append(sum(1 << i for i, (a, b) in enumerate(pairs)
                          if (a in supports[u] and b in supports[v])
                          or (a in supports[v] and b in supports[u])))
    cost = 0
    for i, (a, b) in enumerate(pairs):
        first_a, last_a = holders[a]
        if sum(first_a < k < last_a for k in holders[b]) == 1:
            cost |= 1 << i
    rank = independent(checks)
    return dict(supports=supports, pairs=pairs, checks=checks, cost=cost,
                dimension=len(pairs)-rank, odd=independent([*checks, cost]) != rank)


def supports_from_meetings(ends):
    return tuple(tuple(d for d, h in enumerate(ends) if k in h)
                 for k in range(1 + max(max(p) for p in ends)))


def fixtures():
    for name, knots in [
        ("ring of three's closure", ((0,1,2), (1,3,4), (3,0,5))),
        ("ring of five's closure, grown", ((0,1,2,3,7), (0,4,8), (1,4,5), (2,5,6), (3,6,9))),
        ("closure F, grown", ((0,1,2), (0,3,4), (1,3,5), (2,4,6))),
    ]:
        closed, stages = rebuild.history(knots)
        assert closed == "closed"
        yield name, stages
    for n, word in [(4,"four"),(5,"five")]:
        meetings = [(0,i+1) for i in range(n)] + [(i+1,(i+1)%n+1) for i in range(n)]
        yield f"ring of {word}'s closure", [supports_from_meetings(meetings)]
    joined = [(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(0,3),(1,4),(2,5)]
    yield "two rings of three joined knot to knot", [supports_from_meetings(joined)]
    yield "three knots each meeting each of three others", [supports_from_meetings([(a,b) for a in range(3) for b in range(3,6)])]


def main(limit=None):
    starts = rebuild.core.read_starts()
    prior = {}
    for row in map(json.loads, (Path(rebuild.__file__).parent / 'codes.jsonl').open()):
        if 'start' in row or 'type' in row:
            key = ('birth', row['start']) if 'start' in row else ('type', row['type'])
            prior[key] = row
    if limit is not None:
        starts = starts[:limit]
    counts = Counter()
    outputs = []
    checked = set()
    def add(population, key, stages, data):
        item = dict(population=population, key=key, round=len(stages)-1, **data)
        if population in ('birth', 'type'):
            previous = prior[population, key]
            for field in ('supports', 'pairs', 'checks', 'cost', 'dimension'):
                assert json.dumps(item[field]) == json.dumps(previous[field]), (population, key, field)
            checked.add((population,key))
        outputs.append(item)
    for key, start in enumerate(starts):
        status, stages = rebuild.history(start)
        t = len(stages)-1
        counts['initially closed' if status == 'closed' and not t else status] += 1
        if status != 'closed' or t == 0:
            continue
        local = system(stages)
        if local['odd']:
            add('birth', key, stages, local)
        full = system(stages, whole=True) if t > 1 else local
        if full['odd']:
            counts['whole odd'] += 1
            if t > 1:
                add('whole', key, stages, full)
    if limit is not None:
        print(len(starts), dict(counts), len(outputs))
        return
    for key, pattern in enumerate(json.loads(rebuild.CENSUS.read_text())):
        stages = [supports_from_meetings(pattern['sharing'])]
        add('type', key, stages, system(stages, whole=True))
    for key, stages in fixtures():
        add('fixture', key, stages, system(stages))
    assert checked == set(prior)
    archived = {r['start'] for r in map(json.loads, (HERE.parent/'results.jsonl').open())}
    losses = {r['start'] for r in map(json.loads, (HERE.parent/'whole_only.jsonl').open())}
    birth = {r['key'] for r in outputs if r['population'] == 'birth'}
    later = {r['key'] for r in outputs if r['population'] == 'whole'}
    assert archived == birth and later - birth == losses
    with (HERE/'rebuilt_inputs.jsonl').open('w') as out:
        for r in outputs:
            print(json.dumps(r,separators=(',',':')), file=out)
    summary = dict(weighting='one vote per census start, separately one vote per finished type',
                   starts=len(starts), outcomes=counts, agrees_with_prior_codes=len(checked),
                   populations=Counter(r['population'] for r in outputs),
                   later_only_whole_odd=sorted(losses))
    (HERE/'population.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    main(parser.parse_args().limit)
