"""reflect.py: the link offered at the stop (intuition-links): does the far site turn the pass back exactly when it is
short?  For the switch receiver under the cap of three at d = 3, and each of the 48 senders of the jam study: the
rounds in which the sender's site knot is short, beside the round the receiver switches (switch_runs of the
short-again study).  An intuition, not evidence."""
import sys, os, json, gzip, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import receivers
jam, bench, eng = receivers.jam, receivers.bench, receivers.eng
S = jam.starts() + [('stub', None, None)]
receivers.register()
sw = {}
for l in gzip.open(os.path.join(HERE, '..', 'SHORT-AGAIN-20261126-001', 'switch_runs.jsonl.gz'), 'rt'):
    r = json.loads(l)
    if r.get('law') == ['CAP-3', 'CANCEL-WAIT'] and r.get('join') == 'meeting' and r.get('A') == 'g7:122@0' and r.get('d') == 3:
        sw[r['B']] = r['leaves first way']
out = []
for name, stars, site in S:
    st, ro, _ = jam.changed('g7:122@0', name, 3, None, 'meeting')
    k = ro.index('B') + (0 if name == 'stub' else bench.SITE[name])
    law = jam.law_of('CAP-3', 'CANCEL-WAIT'); T = eng.from_stars(st); G = eng.Guard(100); rounds = []
    for rnd in range(1, 6):
        rec = eng.play_round(T, law, G)
        if k in rec['members']: rounds.append([rnd, rec['owe'][k] - rec['h'][k]])
    out.append({'B': name, 'switch round': sw.get(name), 'site: round and owe less holds while a member': rounds})
    print('%-10s switch %-4s site %s' % (name, sw.get(name), rounds))
json.dump(out, open(os.path.join(HERE, 'reflect.json'), 'w'), indent=0)
