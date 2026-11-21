"""All labelled six-knots/seven-meeting founders from direct subsets and tree-edit histories."""
from collections import Counter
from itertools import combinations, permutations, product
from math import comb, factorial
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT/'artifacts'/HERE.parent.name/HERE.name
ONE = 'KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B'
sys.path.insert(0,str(ROOT/'experiments'/ONE/(ONE+'-E001_meetings')))
from cycle_counts import labelled_trees
from source_mechanisms import initial_read
from representatives import source_rows
from end_operator import from_stars, neighbors, step

PAIRS = tuple(combinations(range(6),2))
FLAGS = tuple(product((0,1),repeat=6))
RENAMINGS = tuple(permutations(range(6)))


def is_connected(edges):
    groups = [{x} for x in range(6)]
    for a,b in edges:
        first, second = groups[a],groups[b]
        if first is not second:
            merged = first | second
            for v in merged:
                groups[v] = merged
    return len(groups[0]) == 6


def renumber_pairs(edges, mapping):
    return tuple(sorted(tuple(sorted((mapping[a],mapping[b]))) for a,b in edges))


def renumber_flags(flags, mapping):
    changed = [0]*6
    for a,b in enumerate(mapping):
        changed[b] = flags[a]
    return tuple(changed)


def inverse(mapping):
    return tuple(mapping.index(i) for i in range(6))


def shape_id(pairs):
    return '-'.join(str(a)+str(b) for a,b in pairs)


class Catalog:
    def __init__(self):
        self.patterns = tuple(q for q in combinations(PAIRS,7) if is_connected(q))
        self.transports = {}
        self.decorations = {}
        self.types = {}
        self.trees = tuple(labelled_trees(6))
        self.all_edit_origins = [tuple(sorted(tree.union(edits))) for tree in self.trees
                                 for edits in combinations(sorted(set(PAIRS)-tree),2)]
        origin_counts = Counter(self.all_edit_origins)
        assert set(self.patterns)==set(origin_counts)
        for edges in self.patterns:
            if edges in self.transports:
                continue
            sym = []
            for perm in RENAMINGS:
                named = renumber_pairs(edges,perm)
                assert named >= edges
                if named not in self.transports:
                    self.transports[named] = edges,inverse(perm)
                if named == edges:
                    sym.append(perm)
            tau = sum(is_connected(t) for t in combinations(edges,5))
            assert tau == origin_counts[edges]
            for flags in FLAGS:
                if (edges,flags) in self.decorations:
                    continue
                images = Counter(renumber_flags(flags,perm) for perm in sym)
                assert min(images)==flags
                key = shape_id(edges)+'_'+''.join(map(str,flags))
                for f in images:
                    self.decorations[edges,f]=key
                auto = images[flags]
                assert len(images)*auto == len(sym)
                names = factorial(6)//auto
                self.types[key] = {'edges':edges,'flags':flags,'labelled':names,'histories':names*tau,'tau':tau,
                                   'aut':auto,'k':sum(flags),'mass_distinct':names*3**(6-sum(flags)),
                                   'mass_histories':names*tau*3**(6-sum(flags))}
        # Visit every labelled final seven-pair pattern and every label-specific flag.
        encoded = {edges:[self.classify(edges,f) for f in FLAGS] for edges in self.patterns}
        actual = Counter()
        for v in encoded.values():
            actual.update(v)
        # Revisit every literal tree, added pair, and flag, with its origin multiplicity.
        origins = Counter()
        for edges in self.all_edit_origins:
            origins.update(encoded[edges])
            rep,_ = self.transports[edges]
            assert origin_counts[edges] == origin_counts[rep]
        assert actual == {k:v['labelled'] for k,v in self.types.items()}
        assert origins == {k:v['histories'] for k,v in self.types.items()}
        for k in range(7):
            selected = [v for v in self.types.values() if v['k']==k]
            assert sum(v['labelled'] for v in selected) == len(self.patterns)*comb(6,k)
            assert sum(v['histories'] for v in selected) == len(self.all_edit_origins)*comb(6,k)
        assert len(self.all_edit_origins) == 6**4*comb(10,2)
        assert sum(v['mass_distinct'] for v in self.types.values()) == len(self.patterns)*4**6
        assert sum(v['mass_histories'] for v in self.types.values()) == len(self.all_edit_origins)*4**6

    def classify(self,edges,flags):
        edges=tuple(sorted(tuple(sorted(e)) for e in edges))
        rep,perm=self.transports[edges]
        return self.decorations[rep,renumber_flags(flags,perm)]


def components_of(end):
    graph=neighbors(end)
    groups=[]
    left=set(graph)
    while left:
        group=[min(left)]
        left.remove(group[0])
        for h in group:
            found=sorted(graph[h] & left)
            left.difference_update(found)
            group.extend(found)
        groups.append(tuple(sorted(group)))
    return tuple(sorted(groups))


def cuts(rows,law):
    end=from_stars(rows)
    trace=[]
    sizes=[len(components_of(end))]
    state=[end]
    for age in range(1,5):
        turn=step(end,law)
        if turn.status=='stall':
            return 'stalled',trace,sizes,state
        assert turn.status=='extend'
        trace.append(turn)
        end=turn.end
        state.append(end)
        sizes.append(len(components_of(end)))
        if not end.opens:
            return 'closed',trace,sizes,state
    return 'open',trace,sizes,state


def scan():
    catalog=Catalog()
    print('patterns, classes',len(catalog.patterns),len(catalog.types),flush=True)
    groups=Counter()
    survivors=[]
    for key,v in catalog.types.items():
        initial=initial_read(6,v['edges'],v['flags'])
        rows=source_rows(6,v['edges'],v['flags'])
        law,trace,sizes,ends=cuts(rows,'parity')
        assert bool(initial['shortages']) == (law=='stalled')
        assert len(initial['live_components']) == sizes[0]
        groups[(law,sizes[0],sizes[-1])]+=1
        if law=='closed' or (law=='open' and sizes[-1]==1):
            survivors.append((key,law,[len(c.parents) for c in trace],[sum(c.fresh) for c in trace],sizes, [len(row) for row in rows]))
    print('cells',groups)
    for s in survivors: print('finding',s)
    OUT.mkdir(parents=True,exist_ok=True)
    audit={'all_seven_subsets':comb(15,7),'connected_labelled_holdings':len(catalog.patterns),
           'unlabelled_shapes':len({v['edges'] for v in catalog.types.values()}),'decorated_classes':len(catalog.types),
           'prufer_trees':len(catalog.trees),'tree_two_edit_histories':len(catalog.all_edit_origins),
           'decorated_labels':len(catalog.patterns)*64,'decorated_histories':len(catalog.all_edit_origins)*64,'classes':catalog.types}
    (OUT/'labelled_orbits.json').write_text(json.dumps(audit,separators=(',',':'),sort_keys=True)+'\n')


if __name__=='__main__':
    scan()
