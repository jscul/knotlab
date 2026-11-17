"""Read-out of the third class (KEEP-REACH-20261117-001, the thread's own code, 2026-11-17): every kept draw of sample_keep.jsonl and
mutants_keep.jsonl that is alive at every depth, never forgets on all assignments (forget.py), and has no two-orbit bond from level 3
at some s. For each: forgetting read on the values states take (actual joints of an orbit and a descendant orbit r levels below, from
every level j >= jmin, j <= 16, stable depth; least r up to 10, None if none), from level 1 and from level 3; and, from level 3 at
s = 13..16 (past every preperiod seen), whether some top joint is non-product and whether its missing pairs are exposed. Writes
third_class.json."""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'exploratory'))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from third_detail import pair_states, exposed  # noqa: E402
from look_four import rectangular  # noqa: E402
from window_tree import WindowTree, level_states  # noqa: E402


def actual_forget(tree, jmin, levels=16, rmax=10):
    F = tree.feasible(20)
    r0 = next(r for r in range(19) if F[r] == F[r + 1])
    Fc = F[r0]
    st = level_states(tree, levels, [Fc] * (levels + 2))
    for r in range(1, rmax + 1):
        ok = True
        for j in range(jmin, levels + 1):
            for t, up in st[j]:
                fr = {(t, frozenset((x, x) for x in up))}
                for _ in range(r):
                    fr = {(tree.children[t2][ci][0], tree.step(t2, Fc, ci, J)) for t2, J in fr for ci in range(len(tree.children[t2]))}
                for c, J in fr:
                    Jf = frozenset((a, z) for a, z in J if z in Fc[c])
                    if Jf and not rectangular(Jf):
                        ok = False
        if ok:
            return r
    return None


rows = [json.loads(l) for l in open(HERE / 'sample_keep.jsonl')] + [json.loads(l) for l in open(HERE / 'mutants_keep.jsonl')]
third = [r for r in rows if r.get('small_orbits') and r.get('alive_every_depth') and r.get('r_all') is None and not r.get('timeout')
         and not r['two_orbit_every_s']]
out = {}
for r in third:
    tree = WindowTree(r['key'])
    seq = pair_states(tree, 3, 16)
    late = seq[12:]
    nonprod = sum(1 for joints in late for t1, t2, J in joints if J and not rectangular(J))
    hidden = 0
    for joints in late:
        for t1, t2, J in joints:
            if J and not rectangular(J):
                A = {a for a, _ in J}
                B = {z for _, z in J}
                ea, eb = exposed(A, tree.m[t1]), exposed(B, tree.m[t2])
                if not any(a in ea and z in eb for a in A for z in B if (a, z) not in J):
                    hidden += 1
    a1, a3 = actual_forget(tree, 1), actual_forget(tree, 3)
    kind = ('forgets on actual values' if a3 is not None else
            'top joints become products' if nonprod == 0 else
            'top joints stay non-product, dependence hidden' if hidden == nonprod else 'top joints non-product, some exposed')
    out[str(r['index'])] = dict(key=r['key'], actual_forget_from_1=a1, actual_forget_from_3=a3, late_top_nonproduct=nonprod,
                                late_top_hidden=hidden, kind=kind, two_orbit_first=r['two_orbit_first'])
    print(r['index'], kind, a1, a3, nonprod, hidden, flush=True)
tally = collections.Counter(v['kind'] for v in out.values())
json.dump(dict(third=out, tally=dict(tally)), open(HERE / 'third_class.json', 'w'), indent=1)
print(dict(tally))
