"""My own knot test on every structure part 8 tested; compare with part 8's projection and canonical verdicts."""
import collections
import json
import sys

sys.path.insert(0, 'CHECK_SCRATCH')
from mykt_np import test_structure

A = 'REPO_ROOT/artifacts/TWO-COUNTINGS-20261125-001A/TWO-COUNTINGS-20261125-001A-E001_two_countings/'


def parse(s):
    law, rest = s.split('(')
    return law, tuple(rest.rstrip(')').split(','))


d = json.load(open(A + 'part8_knots.json'))
disagree = []
canon = collections.Counter()
fails_by_label = collections.defaultdict(collections.Counter)
nstruct_fail = 0
out = []
for st in d['structures']:
    rules = [parse(x) for x in st['structure']]
    mine = test_structure(rules)
    if mine['n_states'] != st['n_states']:
        disagree.append(('states', st['labels'][0], mine['n_states'], st['n_states']))
    any_fail = False
    for a, b in zip(mine['rules'], st['knots']):
        assert a['rule'] == b['knot']
        if (a['whole'], a['K1'], a['K2'], a['K3'], a['own']) != (b['whole'], b['K1'], b['K2'], b['K3'], b['own']) or \
                a['induced'] != b['induced']:
            disagree.append((st['labels'][0], a['rule']))
        c = b.get('canonical')
        if isinstance(c, dict):
            canon['canonical run, agrees' if c.get('agrees with projection') else 'canonical run, DISAGREES/err'] += 1
        else:
            canon[str(c)] += 1
        if not a['whole']:
            any_fail = True
            for lab in st['labels']:
                fails_by_label[lab.split(':')[0]][a['rule']] += 1
    nstruct_fail += any_fail
    out.append({'labels': st['labels'], 'n_vars': mine['n_vars'], 'n_states': mine['n_states'],
                'fail': [a['rule'] + ':' + ''.join(k for k in ('K1', 'K2', 'K3') if not a[k]) for a in mine['rules']
                         if not a['whole']],
                'own_fail': [a['rule'] for a in mine['rules'] if not a['own']],
                'canon': [str(b.get('canonical'))[:40] for b in st['knots']]})
print('structures', len(d['structures']), 'disagreements with my test', len(disagree), disagree[:10])
print('structures with a failing rule', nstruct_fail)
print('canonical status of knots', dict(canon))
for lab, c in fails_by_label.items():
    print(lab, dict(c))
json.dump(out, open(sys.argv[1], 'w'))
