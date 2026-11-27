"""witness_nodes.py: the node reading on the referee's constructed counterexamples (post hoc: the starts are the
referee's, built against the graded order). Each case is grown 6 rounds; a step over 120 s is reported as not run."""
import json, sys, signal
sys.path.insert(0, '../LOOK-ALIKE-20261126-001')
import order, late, score, alike

class Late(Exception): pass
def alarm(*a): raise Late()
signal.signal(signal.SIGALRM, alarm)

cases = []
for fn in ('referee-R1/obstruction_nae.jsonl', 'referee-R1/small_nae.jsonl'):
    x = json.loads(open(fn).readline()); cases.append((fn.split('/')[-1].replace('_nae.jsonl', ''), x['stars']))
for l in open('referee-R1/challenge_anchor.jsonl'):
    x = json.loads(l)
    if 'stars' in x: cases.append(('challenge anchor ' + str(x.get('case')), x['stars']))
for name, stars in cases:
    for law in ('nae', 'parity'):
        r = {'witness': name, 'law': law}
        try:
            signal.alarm(120); g = alike.grow(stars, rounds=6, knot_law=law); signal.alarm(0)
            r.update({'rounds grown': len(g['rows']), 'end': g['end']})
        except Late:
            r['growth'] = 'not run (over 120 s)'; print(json.dumps(r), flush=True); continue
        for key, f in (('graded order', lambda: late.predict(stars, 6, law, general=True)),
                       ('node reading', lambda: order.predict_nodes(stars, 6, law, groups=True))):
            try:
                signal.alarm(120); P, why = f(); signal.alarm(0)
                r[key] = score.compare(P, g) if P is not None else 'not predicted: ' + why
            except Late:
                r[key] = 'not run (over 120 s)'
            except Exception as e:
                signal.alarm(0); r[key] = 'error ' + repr(e)[:80]
        print(json.dumps(r), flush=True)
