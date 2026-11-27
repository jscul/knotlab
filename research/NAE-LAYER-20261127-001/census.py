"""census.py OUT.jsonl: the advisor's census-wide predictions under not-all-equal (README.md, "Frozen").  NAE-LAYER-20261127-001.

On every census start, under not-all-equal: (C1) the allowed states are connected by single-distinction changes (one
class under single changes); (C2) no pair of distinctions is tied (every pair takes all four values); (C3) the loose
distinctions show 2^m - 2 patterns when the start is tree-shaped (its knots and shared distinctions form no cycle, and
no two knots share two distinctions) and 2^m otherwise, m the number of loose distinctions.  (C4) On the first 500
census starts that grow a round, the stage's loose distinctions show all 2^m patterns after it (by a solver call per
pattern).  For comparison under parity: (C3') the loose patterns number 2^(m - 1) on every start with loose
distinctions."""
import sys, json, collections, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import t7 as T
forbid = T.forbid


def tree_shaped(S):
    h = forbid.holders(S); pairs = collections.Counter()
    for x, v in h.items():
        if len(v) == 2: pairs[tuple(sorted(v))] += 1
    if any(c > 1 for c in pairs.values()): return False
    parent = list(range(len(S)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in pairs:
        if find(a) == find(b): return False
        parent[find(a)] = find(b)
    return True


def parity_patterns(S):
    names = sorted({x for r in S for x in r}); idx = {x: i for i, x in enumerate(names)}; lo = T.loose_of(S)
    masks = [sum(1 << idx[x] for x in r) for r in S]
    sol = [s for s in range(1 << len(names)) if all(bin(s & m).count('1') % 2 == 0 for m in masks)]
    return len({tuple((s >> idx[x]) & 1 for x in lo) for s in sol})


if __name__ == '__main__':
    out = sys.argv[1]; tally = collections.Counter(); grown = 0
    with open(out, 'w') as f:
        for i, s in enumerate(forbid.census()):
            S = forbid.supports_of(s); names, idx, sol = T.states(S); lo = T.loose_of(S); m = len(lo)
            sset = set(sol)
            # C1: connected under single flips
            seen = {sol[0]} if sol else set(); stack = list(seen)
            while stack:
                u = stack.pop()
                for j in range(len(names)):
                    v = u ^ (1 << j)
                    if v in sset and v not in seen: seen.add(v); stack.append(v)
            c1 = len(seen) == len(sol)
            c2 = all(len({((s >> a) & 1, (s >> b) & 1) for s in sol}) == 4 for a, b in itertools.combinations(range(len(names)), 2))
            pats = len({tuple((s >> idx[x]) & 1 for x in lo) for s in sol})
            tree = tree_shaped(S); pred = (2 ** m - 2) if tree else 2 ** m
            rec = {'start': 'census %d' % i, 'C1': c1, 'C2': c2, 'loose': m, 'tree-shaped': tree, 'C3 patterns': pats, 'C3 predicted': pred,
                   "C3' parity patterns": parity_patterns(S) if m else None}
            if grown < 500:
                st, status, births = forbid.grown(S, 'nae', 'ordinary')
                if status == 'funded' and len(T.loose_of(st)) <= 14:
                    n, of = T.patterns_sat(st); rec['C4 after one round'] = [n, of]; grown += 1
            tally['starts'] += 1; tally['C1 fails'] += not c1; tally['C2 fails'] += not c2
            if m: tally['C3 fails'] += pats != pred; tally["C3' fails"] += rec["C3' parity patterns"] != 2 ** (m - 1)
            if 'C4 after one round' in rec: tally['C4 read'] += 1; tally['C4 fails'] += rec['C4 after one round'][0] != rec['C4 after one round'][1]
            f.write(json.dumps(rec) + '\n'); f.flush()
        f.write(json.dumps({'tally': dict(tally)}) + '\n')
    print(dict(tally))
