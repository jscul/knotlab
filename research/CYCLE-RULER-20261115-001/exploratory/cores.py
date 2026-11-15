"""Exploratory: for the six small breaking cases (RULER-LEVEL's tree_plus_within, seed 7), the first s with L(s) < s + 2 at N = 6, top
level 1: the bond found, its forbidden assignment's smallest core of knots (deletion-minimal), each core knot's kind (tree or within)."""
import sys, json, re, os, shutil, collections
import numpy as np
from pysat.solvers import Cadical195
C = 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'
sys.path.insert(0, C)
import job
from pattern import pattern
log = open('research/RULER-LEVEL-20261114-001/exploratory/tree_plus_within.log').read()
bad = json.loads(log.split('counterexamples ')[1])
def lvl(i): return (int(i) + 1).bit_length() - 1
def name(i): n = lvl(i); return format(i - ((1 << n) - 1), f'0{n}b') if n else 'e'
wd = 'research/CYCLE-RULER-20261115-001/exploratory/work'
for b in bad:
    key = b['key']; shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd); job.BUDGET = 60
    r = job.compute(key, wd, N=6, k0=1, S=3, histograms=False)
    P = [tuple(int(x) for x in k) for k in pattern(key, 6)]
    for l in r['levels']:
        if isinstance(l['L_N'], int) and l['L_N'] < l['s'] + 2:
            bond = l['anywhere'].get('bond') or l['anywhere'].get('support') or []
            break
    else:
        print('no shortened level found', b['L']); continue
    print('== L', b['L'], 'first short s', l['s'], 'L', l['L_N'], 'bond', [name(x) for x in bond] if bond else l['anywhere'].keys())
    if not bond: continue
    # forbidden assignments on the bond: find one and its minimal core
    S = Cadical195(); off = 1 << 16
    for j, (a, bb, c) in enumerate(P):
        S.add_clause([-(off + j), a + 1, bb + 1, c + 1]); S.add_clause([-(off + j), -a - 1, -bb - 1, -c - 1])
    import itertools
    for vals in itertools.product((0, 1), repeat=len(bond)):
        lits = [(x + 1) if v else -(x + 1) for x, v in zip(bond, vals)]
        if not S.solve(assumptions=lits + [off + j for j in range(len(P))]):
            core = sorted(x - off for x in S.get_core() if x >= off)
            i = 0
            while i < len(core):
                t = core[:i] + core[i + 1:]
                if S.solve(assumptions=lits + [off + j for j in t]): i += 1
                else: core = sorted(x - off for x in S.get_core() if x >= off)
            print('   forbidden', dict(zip([name(x) for x in bond], vals)), 'core', len(core), 'knots:')
            for j in core:
                k = P[j]; kind = 'within' if len({lvl(x) for x in k}) == 1 else 'tree/join'
                print('      ', kind, [name(x) for x in k])
            break
shutil.rmtree(wd, ignore_errors=True)
