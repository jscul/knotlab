"""tally.py census_checks.jsonl rings2.jsonl: the class map's checks (README.md): by stage and choice of move, the
structures with two or more classes, the part a change avoiding the loose distinctions can exchange, whether the class
can be read inside one knot, and whether one round keeps the old classes."""
import sys, json, collections
c = collections.Counter()
for p in sys.argv[1:]:
    for l in open(p):
        r = json.loads(l)
        for when in ('start', 'after one round'):
            a = r[when]
            if not isinstance(a, dict): c[(p, when, 'no round')] += 1; continue
            for choice in ('shortest through each distinction', 'shortest overall'):
                v = a[choice]; k = (p, when, choice)
                c[k + ('read',)] += 1
                if v['classes'] > 1:
                    c[k + ('two or more classes',)] += 1
                    full = v['dim (S0+H)/H'] == v['dim S/H']
                    c[k + ('every class pair exchanged avoiding loose' if full else 'some class fixed by loose values',)] += 1
                    if choice.startswith('shortest through'):
                        c[k + ('class read inside one knot',)] += v['the class read inside one knot']
        if 'old classes kept by the grown moves' in r and r['start']['shortest through each distinction']['classes'] > 1:
            c[(p, 'kept into the next stage', r['old classes kept by the grown moves'])] += 1
for k, v in sorted(c.items(), key=str): print(k, v)
