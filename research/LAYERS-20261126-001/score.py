"""score.py OUT.json frozen_census.jsonl frozen_heldout.jsonl: the frozen predictions (README, "Frozen") tallied."""
import sys, json, collections


def main(out, paths):
    T = collections.Counter(); breaks = []; towers = []
    for p in paths:
        S = 'census' if 'census' in p else 'held out'
        for l in open(p):
            x = json.loads(l)
            if 'error' in x: T[(S, 'error')] += 1; breaks.append([S, x['index'], x['error']]); continue
            if not x['grows']: T[(S, 'does not grow: ' + x.get('end', ''))] += 1; continue
            if x['in the conditions']:
                ok = x['classes'] == x['predicted classes'] and x['each piece parity a label']
                T[(S, 'P1: in the conditions', 'holds' if ok else 'breaks')] += 1
                if not ok: breaks.append([S, x['index'], x['classes'], x['predicted classes'], x['each piece parity a label']])
            else:
                why = ('an old knot keeps a loose distinction' if x['an old knot keeps a loose distinction'] else '') + \
                      (' / three knots pairwise share' if x['three knots pairwise share'] else '')
                T[(S, 'P2: outside the conditions (%s)' % why.strip(' /'), '%d classes' % x['classes'])] += 1
            if x['classes'] >= 4:
                r = x.get('labels read knot by knot')
                T[(S, 'P3: four or more classes', 'read knot by knot' if r else 'not read knot by knot')] += 1
                if not r: towers.append([S, x['index'], x['classes']])
    res = {'tally': {' / '.join(k): v for k, v in sorted(T.items())}, 'P1 breaks': breaks, 'candidate tower steps': towers}
    json.dump(res, open(out, 'w'), indent=1); print(json.dumps(res, indent=1)[:4000])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
