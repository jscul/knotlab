"""tally.py: rings_out.jsonl.gz against preregistration.md."""
import json, collections, gzip
from pathlib import Path
rows = [json.loads(l) for l in gzip.open(Path(__file__).resolve().parent / 'rings_out.jsonl.gz', 'rt')]
c = collections.Counter(); notes = []
for r in rows:
    fam, t = r['family'][:40], r['round']
    if 'end' in r: notes.append((fam, t, 'end', r['end'])); continue
    for k, v in r.items():
        if not isinstance(v, dict): continue
        trip = (v['e, middle unread'], v['e, middle changes'], v['e, middle values'])
        if k.startswith('readers') and 'against' not in k:
            loose_fam = 'one loose' in r['family']
            want = (0, 1, 0)
            if loose_fam and t == 0 and k.endswith('rings 0 and 1'): want = (0, 0, 0)
            c[('1 pairs', 'separated')] += v['separated']; c[('1 pairs', 'rows')] += 1
            c[('1 pairs', 'as predicted')] += trip == want; c[('1 pairs', 'identities agree')] += v['identities agree']
            if trip != want: notes.append((fam, t, k, trip, 'wanted', want))
            if 'e, only the link distinction read for its change' in v:
                c[('2 link only', 'rows')] += 1; c[('2 link only', 'e = 1')] += v['e, only the link distinction read for its change'] == 1
                if v['e, only the link distinction read for its change'] != 1: notes.append((fam, t, k, 'link only', v['e, only the link distinction read for its change']))
        elif k.startswith('control'):
            want = (1, 1, 1) if t == 0 else (0, 1, 0)
            c[('3 control', 'rows')] += 1; c[('3 control', 'as predicted')] += trip == want
            if trip != want: notes.append((fam, t, 'control', trip, 'wanted', want))
        elif 'against' in k:
            c[('4 two rings against one', 'rows')] += 1
            if t == 0:
                ok = trip == (0, 2, 0) and v.get('square', {}) and v['square']['cells certain'] == 9 and v['square']['rows and columns commute on A']
                c[('4 two rings against one, round 0', 'rows')] += 1; c[('4 two rings against one, round 0', 'as predicted')] += bool(ok)
                if not ok: notes.append((fam, t, k, trip, v.get('square')))
            else:
                notes.append((fam, t, k, trip, v.get('square')))
for k in sorted(c): print(json.dumps({' / '.join(k): c[k]}))
for n in notes: print(json.dumps(n))
