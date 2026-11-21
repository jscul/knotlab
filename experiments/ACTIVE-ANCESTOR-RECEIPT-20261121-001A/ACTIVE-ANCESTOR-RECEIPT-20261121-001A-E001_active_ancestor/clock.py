"""Complete ordinary and third-qualified receiving histories on the twelve frozen starts."""
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, pairwise
from pathlib import Path
import gzip
import json
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PREVIOUS = 'SHARED-DONOR-AND-SIGN-RESPONSE-20261121-001A'
spec = spec_from_file_location('settled_shared_donor', ROOT / 'experiments' / PREVIOUS /
                               (PREVIOUS + '-E001_shared_donor') / 'clock.py')
shared = module_from_spec(spec)
spec.loader.exec_module(shared)
prior = shared.prior
old = prior.old
SIZES = (32, 48, 64, 80)
READERS = ('ordinary', 'binary', 'third_qualified')


@dataclass(frozen=True)
class Case:
    d: int
    setup: str
    switch: str

    @property
    def name(self):
        return f'{self.d}_{self.setup}_{self.switch}'


def cases():
    return tuple(Case(d, setup, switch)
                 for d, setup, switches in ((32, 'main', ('none', 'full', 'near', 'far')),
                                            (32, 'sym', ('none', 'full')),
                                            (32, 'one', ('none', 'full')),
                                            (64, 'main', ('none', 'full')),
                                            (32, 'ss', ('none', 'full')))
                 for switch in switches)


class Middle:
    def __init__(self, case):
        d = case.d
        graph = nx.Graph()
        for zone in ('R', 'S'):
            neutral, named = old.base(zone)
            for word in (neutral, *named):
                graph.add_edges_from(pairwise((*word, word[0])))
        graph.add_edges_from((('Rr1', 'Sb2'), ('Rb2', 'a'), ('b', 'Sb2')))
        graph.add_edges_from(pairwise(('a', *(f'p{i}' for i in range(1, d+14)), 'b')))
        graph.add_edge('a', 'c0')
        if case.setup != 'one':
            graph.add_edge(f'c{d}', 'b')
        positions = tuple(k*d//4 for k in (1, 3, 5, 7))
        cuts = {'none': (), 'near': positions[:2], 'far': positions[2:], 'full': positions}[case.switch]
        self.c_nodes = {f'c{i}' for i in range(2*d+1)}
        self.mixed_nodes = self.c_nodes | {f'u{i}' for i in range(2*d+1)}
        self.steps = nx.DiGraph()
        for i in range(2*d+1):
            j = (i+1) % (2*d+1)
            for a, b in (('c', 'u'), ('u', 'c')):
                tail, head = f'{a}{i}', f'{b if i in cuts else a}{j}'
                self.steps.add_edge(tail, head)
                graph.add_edge(tail, head)
        graph.add_edge(f'c{3*d//2}', f'u{3*d//2}')
        if case.setup != 'sym':
            graph.add_edge(f'c{3*d//2+2}', 'z0')
            graph.add_edges_from(pairwise(('z0', 'z1', 'z2', 'z3', 'z0')))
        self.spine = graph.copy()
        self.cells = {}
        if case.setup == 'ss':
            for i, w in ((26, 'w1'), (27, 'w2')):
                triple = frozenset((f'c{i}', f'c{i+1}', w))
                for u, v in combinations(triple, 2):
                    graph.add_edge(u, v)
                    self.cells[frozenset((u, v))] = (triple, 'S')
        self.graph = graph
        self.supply = dict(graph.degree())
        self.blocks = {v: set() for v in graph}
        for a, b in graph.edges:
            pair = frozenset((a, b))
            block = self.cells.get(pair, (pair, 'ordinary'))
            self.blocks[a].add(block)
            self.blocks[b].add(block)
        assert nx.is_connected(graph) and min(self.supply.values()) >= 2
        assert all(self.steps.in_degree(v) == self.steps.out_degree(v) == 1 for v in self.mixed_nodes)

    def authorized_steps(self, mixed=False, forbid_extra=False):
        nodes = self.mixed_nodes if mixed else self.c_nodes
        arcs = self.steps.subgraph(nodes).copy()
        if forbid_extra:
            arcs.remove_edges_from([(u, v) for u, v in arcs.edges if frozenset((u, v)) in self.cells])
        return arcs

    def eligible(self, binary):
        g = self.spine.copy()
        if binary:
            g.remove_edges_from([tuple(pair) for pair in self.cells])
        g.remove_nodes_from([v for v in g if v.startswith('R') and v != 'Rb2'])
        return g


def lifetime(arcs):
    comp = [arcs.subgraph(s) for s in nx.weakly_connected_components(arcs)]
    circuits = [sorted(c) for c in comp if all(c.in_degree(v) == c.out_degree(v) == 1 for v in c)]
    runs = []
    for c in comp:
        heads = [v for v in c if c.in_degree(v) == 0]
        if not heads:
            continue
        start, = heads
        path = [start]
        while c.out_degree(path[-1]):
            nxt, = c.successors(path[-1]); path.append(nxt)
        assert len(path) == len(c)
        runs.append(path)
    return {'unbounded':bool(circuits),'circuits':sorted(circuits),'finite_runs':sorted(runs),
            'maximum':None if circuits else max(map(len,runs))}


@cache
def tables(signal):
    return old.prefix_next(signal), old.prefix_next(signal[::-1])


def all_first(middle, m, reader, ceiling):
    """Minimum accepted first-completion histories in the finite nonretracing intake automaton."""
    qualified = reader == 'third_qualified'
    if qualified and ceiling is not None and m > ceiling:
        return [], {'exhaustion':'global third ceiling', 'ceiling':ceiling,'states':0}
    graph = middle.eligible(reader == 'binary')
    ct = middle.authorized_steps().to_undirected()
    signal = old.send(m//16)
    fw, rv = tables(signal)
    # previous and current donor, capped c-suffix (m is absorbing attainment), two prefix states
    start = ('Rb2', 'a', 0, 0, 0)
    distance = {start:3}; pred = defaultdict(list); todo = deque([start]); ends = []
    best = None
    while todo:
        current = todo.popleft()
        previous, last, suffix, f, r = current
        level = distance[current]
        if best is not None and level >= best:
            continue
        for v in sorted(graph[last]):
            if v == previous or v.startswith('R'):
                continue
            run = 0
            if qualified:
                if suffix == m:
                    run = m
                elif ct.has_edge(last, v):
                    run = min(m, suffix+1)
                elif v in middle.c_nodes:
                    run = 1
            dest = (last, v, run, fw.get((f,v),0), rv.get((r,v),0))
            if dest not in distance:
                distance[dest] = level+1
                if m in dest[3:]:
                    if not qualified or run == m:
                        best = level+1; ends.append(dest)
                    # Any extension would already contain the same complete W in its inside parent.
                else:
                    todo.append(dest)
            if distance[dest] == level+1:
                pred[dest].append(current)
    def backwards(state):
        if state == start:
            yield ('Rt','Rb2','a')
        else:
            for ancestor in pred[state]:
                for word in backwards(ancestor):
                    yield (*word,state[1])
    words = sorted({word for end in ends for word in backwards(end)})
    assert not words or all(len(word)==best for word in words)
    return words, {'exhaustion':'all states' if best is None else 'complete first accepting breadth',
                   'states':len(distance),'first_right_size':best,'end_states':len(ends)}


def ancestral_intervals(word,m,arcs,cells):
    allowed = arcs.to_undirected()
    spans=[]; i=0
    while i<len(word):
        if word[i] not in arcs:
            i+=1;continue
        j=i+1
        while j<len(word) and allowed.has_edge(word[j-1],word[j]):
            j+=1
        spans.append([i,j]); i=j
    positions=[[a,a+m] for i,j in spans for a in range(i,j-m+1)]
    distinct={prior.index(prior.units(word[i:j],cells)) for i,j in positions}
    return {'maximal_runs':spans,'size_m_positions':positions,'distinct':len(distinct)}


def price(middle,word):
    return shared.actual_price(word,middle.blocks,middle.supply)


def read_receipt(middle,m,right):
    signal=old.send(m//16)
    word=(*old.left(len(right)),'Rb1',*right)
    incoming,internal=word[1:],word[:-1]
    tiles=prior.units(word,middle.cells)
    assert m//16 in old.intrinsic_decodes(word,[internal,incoming])
    assert m//16 in old.intrinsic_decodes(word[::-1],[incoming[::-1],internal[::-1]])
    assert not old.intrinsic_decodes(word,[internal]) and not old.intrinsic_decodes(word,[internal,incoming,internal])
    assert all(a!=b for a,b in pairwise(tiles))
    reading=prior.trace_receiver(word,m,middle.cells,middle.supply,middle.graph)
    beg,end=reading['launch_slice']
    assert len({old.canonical(w) for w in prior.frame_orientations(tiles)})==1
    parts=(signal,signal[:-1],signal[1:],word[beg:end],internal,incoming,word)
    grants={field:price(middle,w) for field,w in zip(shared.PRICE_FIELDS,parts,strict=True)}
    assert grants == reading['price_vector']
    sham=tuple('Sb0' if v=='Sb1' else v for v in word)
    assert old.intrinsic_decodes(sham,[sham[:-1],sham[1:]])==[]
    assert all(price(middle,x)==price(middle,y) for x,y in zip((word,internal,incoming),(sham,sham[:-1],sham[1:]),strict=True))
    actual=[]
    for i,g in enumerate(prior.units(incoming,middle.cells)):
        if len(g)==3:actual.append([i,sorted(g)])
    att={name:ancestral_intervals(incoming,m,middle.authorized_steps(mixed,no_extra),middle.cells)
         for name,mixed,no_extra in (('third',False,False),('third_no_extra',False,True),('untyped_continuing',True,False))}
    return {'right':right,'size':len(word),'age':len(word)-1,'delay':len(word)-m,
            'turns_origin':reading['ticks_from_origin'],'turns_since_send':reading['ticks_after_send'],
            'tick_sizes':reading['tick_sizes'],'seven_grants':grants,'own_launch_slice':[beg,end],
            'complete_signal_in_outside':old.factors(incoming,signal),'complete_signal_in_inside':old.factors(internal,signal),
            'actual_blocks_with_extra_in_outside':actual,'ancestors':att,
            'complete_receiver_readings':reading['anchored_readings_at_receipt'],
            'internal_chain_slice_digest':sha256(json.dumps(reading['lineage_slices_and_readings']).encode()).hexdigest(),
            'neutral_sham_signal_registered':False,'neutral_sham_three_terminal_grants':[price(middle,y) for y in (sham[:-1],sham[1:],sham)]}


def solve(case):
    middle=Middle(case)
    lives={name:lifetime(middle.authorized_steps(mix,no)) for name,mix,no in (
        ('third',False,False),('third_no_extra',False,True),('untyped_continuing',True,False))}
    assert lives['untyped_continuing']['unbounded'] and len(lives['untyped_continuing']['circuits'])==2
    receipts={};rows=[]
    for reader in READERS:
        for m in SIZES:
            words,search=all_first(middle,m,reader,lives['third']['maximum'])
            ids=[]
            for word in words:
                sig=sha256(json.dumps((m,word)).encode()).hexdigest()[:20]
                if sig not in receipts:
                    receipts[sig]=read_receipt(middle,m,word)
                rr=receipts[sig];ids.append(sig)
                assert reader!='binary' or not rr['actual_blocks_with_extra_in_outside']
                assert reader!='third_qualified' or rr['ancestors']['third']['distinct']>0
            rows.append({'reader':reader,'m':m,'first_members':ids,'search':search})
    return {'case':case.name,'lifetimes':lives,'candidate_pairs':sorted(sorted(p) for p in middle.graph.edges),
            'ordinary_groups':sorted({tuple(sorted(shared_group[0])) for vals in middle.blocks.values() for shared_group in vals}),
            'rows':rows,'receipts':receipts}


def main():
    output={'case_labels':[c.name for c in cases()],'laws':['parity','not-all-equal'],
            'fields':list(shared.PRICE_FIELDS),'cases':[solve(c) for c in cases()]}
    OUTPUT.mkdir(parents=True,exist_ok=True)
    data=json.dumps(output,sort_keys=True,separators=(',',':')).encode()+b'\n'
    (OUTPUT/'receipts.json.gz').write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
    for c in output['cases']:
        vec={r:[] for r in READERS}
        for row in c['rows']:
            rec=[c['receipts'][i] for i in row['first_members']]
            vec[row['reader']].append((row['m'],rec[0]['delay'] if rec else None,len(rec)))
        print(c['case'],vec,flush=True)


if __name__=='__main__':
    main()
