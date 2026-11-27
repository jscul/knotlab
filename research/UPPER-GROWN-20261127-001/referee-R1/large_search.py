"""Search all disjoint signed boxes using the complete small-law certificates."""
import argparse
from collections import defaultdict
from functools import cache
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

from large_cores import clauses, mask_of, members

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH / 'NAE-LAYER-20261127-001' / 'referee-R1'))
from growth_rule import advance, supports_of


def candidates(supports, certificates):
    names = sorted(set().union(*map(set, supports)))
    knot_masks = list(map(mask_of, supports))
    ids = {}
    signed = []

    @cache
    def possible(part, value):
        masks = [part]
        if value and part.bit_count() == 2:
            masks.extend(part | 1 << x for x in names if not (part >> x) & 1)
        keep = []
        for m in masks:
            if any(m & k == m for k in knot_masks):
                continue
            key = (m, value)
            if key not in ids:
                ids[key] = len(signed)
                signed.append(key)
            keep.append((ids[key], m))
        return keep

    triples = set()
    for ((a, va), (b, vb), (c, vc)) in certificates:
        for i, ma in possible(a, va):
            for j, mb in possible(b, vb):
                if ma & mb:
                    continue
                ab = ma | mb
                for k, mc in possible(c, vc):
                    if not (ab & mc):
                        triples.add(tuple(sorted((i, j, k))))
    return triples, signed


def directions(triples, n):
    sides = {}
    for a, b, c in triples:
        ab, ac, bc = a*n+b, a*n+c, b*n+c
        sides[ab] = sides.get(ab, 0) | (1 << c)
        sides[ac] = sides.get(ac, 0) | (1 << b)
        sides[bc] = sides.get(bc, 0) | (1 << a)
    return sides


def refine(triples, signed):
    n = len(signed)
    union = (1 << n) - 1
    containing = defaultdict(int)
    for i, (m, v) in enumerate(signed):
        for x in members(m):
            containing[x] |= 1 << i
    disjoint = []
    for m, v in signed:
        allowed = union
        for x in members(m):
            allowed &= ~containing[x]
        disjoint.append(allowed)
    counts = [len(triples)]
    while triples:
        sides = directions(triples, n)
        kept = [(a, b, c) for a, b, c in triples
                if sides[a*n+b] & disjoint[c] and sides[a*n+c] & disjoint[b]
                and sides[b*n+c] & disjoint[a]]
        if len(kept) == len(triples):
            break
        triples = kept
        counts.append(len(triples))
    return triples, disjoint, counts


def structural_boxes(triples, signed, disjoint):
    """Given surviving clauses, extend the least signed reading of a box."""
    sides = directions(triples, len(signed))
    links = defaultdict(set)
    for a, b, c in triples:
        links[a].add((b, c))
        links[b].add((a, c))
        links[c].add((a, b))
    for a in sorted(links):
        by_pair = defaultdict(list)
        for b, c in links[a]:
            if a < b and a < c:
                also = sides[b*len(signed)+c] & disjoint[a] & ~((1 << (a+1)) - 1)
                for partner in members(also):
                    by_pair[partner].append((b, c))
        for aa, common in by_pair.items():
            if len(common) < 4:
                continue
            others = defaultdict(int)
            for b, c in common:
                others[b] |= 1 << c
                others[c] |= 1 << b
            for b in sorted(others):
                amask = others[b]
                if amask.bit_count() < 2:
                    continue
                for bb in others:
                    if bb <= b or not disjoint[b] >> bb & 1:
                        continue
                    # b is the smallest of the other four readings.
                    cs = others[bb] & amask & ~((1 << (b+1)) - 1)
                    for c in members(cs):
                        for cc in members(cs & disjoint[c] & ~((1 << (c+1)) - 1)):
                            yield (a, aa, b, bb, c, cc)


def stage_list():
    starts = json.loads((RESEARCH / 'FORBID-EDITS-20261126-001' / 'starts.json').read_text())
    stages = []
    for f in sorted((HERE.parent / 'out').glob('census_*.jsonl')):
        for raw in f.read_text().splitlines():
            row = json.loads(raw)
            idx = int(row['start'].split()[1])
            if not any(step['search'] == 'local' for step in row['rounds']):
                continue
            stage = supports_of(starts[idx])
            for step in row['rounds']:
                if step['round']:
                    growth = advance(stage)
                    assert growth.status == 'funded'
                    stage = growth.supports
                assert (len(stage),len(set().union(*map(set, stage)))) == (step['knots'],step['distinctions'])
                if step['search'] == 'local':
                    stages.append((idx, step['round'], len(starts[idx][2]), stage))
    return sorted(stages)


def screen(supports):
    cert, stats = clauses(supports)
    triples, signed = candidates(supports, cert)
    rem, disj, counts = refine(triples, signed)
    stats.update({'partial word certificates': len(cert), 'signed readings':len(signed),
                  'signed triples before and after disjoint alternatives':counts})
    return rem, signed, disj, stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--first', type=int, default=0)
    parser.add_argument('--count', type=int)
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    roster = stage_list()
    selected = roster[options.first:options.first+options.count if options.count is not None else None]
    rows = []
    for idx, round_no, n_start, stage in selected:
        start = perf_counter()
        trimmed, signed, disjoint, stats = screen(stage)
        boxes = list(structural_boxes(trimmed, signed, disjoint))
        rows.append(dict(start=idx, round=round_no, knots=len(stage),
                         distinctions=len(set().union(*map(set,stage))),**stats,
                         structural_boxes=len(boxes),
                         seconds=round(perf_counter()-start,5)))
        if boxes:
            rows[-1]['first structural box'] = [[list(members(signed[u][0])), signed[u][1]] for u in boxes[0]]
        if options.output:
            options.output.write_text(json.dumps({'rows':rows,'peak_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2)+'\n')
        else:
            print(json.dumps(rows[-1]),flush=True)


if __name__ == '__main__':
    main()
