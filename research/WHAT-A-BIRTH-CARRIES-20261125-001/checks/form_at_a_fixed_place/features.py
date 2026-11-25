"""What in the second seed's form decides the class of the first seed's making?  For each study of form.py: is the
class (by what the first seed's descent makes, at the last round read by every form) a function of
  near   : how many knots the link knot shares a distinction with, and its own loose count;
  near+  : near, and the loose counts of those knots;
  near++ : near+, and how many further knots each of those shares with (the form to two steps from the link);
and how many classes there are among forms that agree on each of these."""
import json, sys, collections, itertools
sys.path.insert(0, '.')
def feats(name):
    shape, rest = name.split(':')
    at = 0
    if '@' in rest:
        rest, w = rest.split('@'); at = 1 if w == 'mid' else 0
    lo = tuple(int(x) for x in rest.split(','))
    n = len(lo)
    pairs = {'one': [], 'two': [(0, 1)], 'chain3': [(0, 1), (1, 2)], 'ring3': [(0, 1), (1, 2), (0, 2)], 'chain': [(i, i + 1) for i in range(n - 1)]}[shape]
    nb = collections.defaultdict(set)
    for a, b in pairs: nb[a].add(b); nb[b].add(a)
    near = (len(nb[at]), lo[at])
    nearp = near + (tuple(sorted(lo[j] for j in nb[at])),)
    nearpp = near + (tuple(sorted((lo[j], len(nb[j]) - 1, tuple(sorted(lo[k] for k in nb[j] if k != at))) for j in nb[at])),)
    return {'near': near, 'near+': nearp, 'near++': nearpp}
rows = [json.loads(l) for l in open(sys.argv[1])]
tot = collections.Counter(); deeper = []
for d in rows:
    if 'error' in d: continue
    n = d['forms still read, by round']; full = max(i for i, x in enumerate(n) if x == n[0])
    C = d['classes by what it makes'][full]
    forms = [f for f in C if f != '(none)']
    res = {}
    for key in ('near', 'near+', 'near++'):
        g = collections.defaultdict(set)
        for f in forms: g[feats(f)[key]].add(C[f])
        res[key] = all(len(v) == 1 for v in g.values())
    level = next((k for k in ('near', 'near+', 'near++') if res[k]), 'further than two steps')
    sp = d['spec']; tot[(str(sp['take']), level)] += 1
    if level == 'further than two steps': deeper.append((str(sp['take']), sp['ration'], sp['treatment'], sp['first'][0]))
print('studies by taking rule and by how much of the form decides the class:')
for k, v in sorted(tot.items()): print('  ', v, k)
print('decided by more than two steps from the link:', deeper)
