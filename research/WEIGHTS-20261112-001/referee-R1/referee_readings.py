"""Referee WEIGHTS-R1: the W1 counts under three readings of the frozen stop, from the raw records: the prefix rule (the study's),
all completed samples, and the pause-time view (census.jsonl only, the dropped samples missing). Writes referee_readings.json."""
import json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
O = ROOT / 'artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts'
def wilson(k, n):
    z = 1.96; c = (k + z*z/2)/(n + z*z); h = z*math.sqrt(k*(n-k)/n + z*z/4)/(n + z*z); return [round(c-h, 4), round(c+h, 4)]
cen = {(r['beta'], r['sample']): r for r in map(json.loads, open(O/'census.jsonl')) if 'beta' in r}
dropped = [r for r in map(json.loads, open(O/'census.jsonl')) if 'beta' not in r]
res = {}
for l in open(O/'resume_census/results.jsonl'):
    x = json.loads(l)['result']; res[(x['beta'], x['sample'])] = x
done = {(c['beta'], c['sample'], c['r']) for c in json.load(open(ROOT/'research/WEIGHTS-20261112-001/completion.json')) if c['certified now']}
def tally(keys, recs):
    t = k = f = fc = o = 0; non = []
    for key in keys:
        for rr, v in recs[key]['by r'].items():
            if v['stratum'] != 'new kinds' or v['class'] != 'travels': continue
            t += 1; m = v.get('main', {}); e = v.get('enlarged') or {}
            if m.get('rank certified') == 2 or e.get('rank certified') == 2: k += 1
            elif m.get('rank forced') == 2 or e.get('rank forced') == 2:
                f += 1; c = (key[0], key[1], rr) in done; fc += c; non.append([key[1], rr, 'forced', c])
            else: o += 1; non.append([key[1], rr, 'one direction'])
    return {"travelling": t, "two certified": k, "forced": f, "completed": fc, "one direction": o,
            "two after completion": [k + fc, t, wilson(k + fc, t) if t else None], "non-two": non}
allrec = {**cen, **res}; out = {"dropped rows before the pause": len(dropped)}
for beta, stop in ((0, 101), (1, 55), (2, 89)):
    keys = sorted(k for k in allrec if k[0] == beta)
    out[beta] = {"prefix to %d" % stop: tally([k for k in keys if k[1] <= stop], allrec),
                 "all completed samples (%d)" % len(keys): tally(keys, allrec),
                 "pause view (census.jsonl only)": tally(sorted(k for k in cen if k[0] == beta), cen) if any(k[0] == beta for k in cen) else None,
                 "resumed sample indices at or below the stop that the pause view lacked": sorted(k[1] for k in res if k[0] == beta and k[1] <= stop and k not in cen)[:20]}
(Path(__file__).with_suffix('.json')).write_text(json.dumps(out, indent=1))
for beta in (0, 1, 2):
    for name, v in out[beta].items():
        if isinstance(v, dict): print(beta, name, {x: v[x] for x in ('travelling', 'two certified', 'forced', 'completed', 'one direction', 'two after completion')})
        else: print(beta, name, v)
