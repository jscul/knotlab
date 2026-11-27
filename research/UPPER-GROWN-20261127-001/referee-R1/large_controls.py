"""Check the disjoint certificates on exhaustive controls and held-out starts."""
import argparse
from itertools import combinations, permutations, product
import json
from pathlib import Path
from time import perf_counter

from pysat.solvers import Solver

from large_search import HERE, RESEARCH, advance, candidates, clauses, mask_of, members, refine, screen, stage_list, structural_boxes


def flags(groups, states):
    masks = []
    for g in groups:
        support = mask_of(g)
        mask = 0
        for i, s in enumerate(states):
            if (s & support) in (0, support):
                mask |= 1 << i
        masks.append(mask)
    return masks


def direct_control(supports):
    """Exhaust the source truth table, including determination on every knot."""
    n = 1 + max(x for g in supports for x in g)
    knot_masks = list(map(mask_of, supports))
    states = [s for s in range(1 << n) if all((s & k) not in (0,k) for k in knot_masks)]
    everything = (1 << len(states)) - 1
    all_carriers = [c for k in (2,3) for c in combinations(range(n),k)]
    columns = flags(all_carriers, states)
    eligible = []
    for c, e in zip(all_carriers, columns):
        if not e or e == everything:
            continue
        for k in knot_masks:
            by_fix = {}
            for i, s in enumerate(states):
                val = (e >> i) & 1
                if by_fix.setdefault(s & k, val) != val:
                    break
            else:
                break
        else:
            eligible.append((mask_of(c), e))
    certificates, _ = clauses(supports)
    signed_triples, names = candidates(supports, certificates)
    produced = {tuple(sorted(names[i] for i in t)) for t in signed_triples}
    by_mask = {mask_of(c):e for c,e in zip(all_carriers,columns)}
    for T in produced:
        cell = everything
        for g, v in T:
            cell &= by_mask[g] if v else everything ^ by_mask[g]
        assert not cell, T

    full_bonds = 0
    multiclauses = 0
    missing = []
    for (a, ra), (b, rb), (c, rc) in combinations(eligible, 3):
        if a & b or a & c or b & c:
            continue
        absent = []
        for signs in product(range(2),repeat=3):
            cell = everything
            for column,v in zip((ra,rb,rc),signs):
                cell &= column if v else everything ^ column
            if not cell:
                absent.append(signs)
        if len(absent) == 1:
            full_bonds += 1
            key = tuple(sorted(zip((a,b,c),absent[0])))
            if key not in produced:
                missing.append(key)
        elif len(absent) > 1 and all(len({tuple(w[k] for k in keep) for w in product(range(2),repeat=3)
                                          if w not in absent}) == 4 for keep in combinations(range(3),2)):
            multiclauses += 1
    assert not missing, missing[:1]
    return {'knots':len(supports),'distinctions':n,'allowed states':len(states),
            'unread carriers':len(eligible),'eligible one-word bonds':full_bonds,
            'additional multiword bonds':multiclauses,
            'necessary signed triples':len(produced),'false absences':0,
            'eligible one-word bonds omitted':0}


def planted():
    """All eight choices survive; omitting any one eliminates the box."""
    controls=[]
    for values in ((1,1,1,1,1,1),(0,1,0,0,1,1)):
        names=[(7 << (3*i),v) for i,v in enumerate(values)]
        triples=set(product((0,1),(2,3),(4,5)))
        def count(edges):
            kept, d, _ = refine(edges,names)
            return len(list(structural_boxes(kept,names,d)))
        assert count(triples) == 1
        after = [count(triples-{t}) for t in sorted(triples)]
        assert not any(after)
        controls.append({'signed readings':values,'boxes before erasure':1,'boxes after each erasure':after})
    return controls


def opposite_triples(triples, names):
    """Try all matches between two entirely disjoint clauses, then test the other six."""
    keys=set(triples)
    clauses_by_mask=[(t,names[t[0]][0] | names[t[1]][0] | names[t[2]][0]) for t in sorted(keys)]
    boxes=set()
    pairs=0
    for i,(a,ma) in enumerate(clauses_by_mask):
        for b,mb in clauses_by_mask[:i]:
            if ma & mb:
                continue
            pairs+=1
            for aligned in permutations(b):
                groups=tuple(zip(a,aligned))
                if all(tuple(sorted(t)) in keys for t in product(*groups)):
                    boxes.add(tuple(sorted(tuple(sorted(pair)) for pair in groups)))
    return pairs,len(boxes)


def witness(pilot):
    original=json.loads((RESEARCH/'RING-BOND-20261127-001'/'referee-R1'/'layer_witness.json').read_text())
    stage=tuple(map(tuple,original['source_knots_not_all_equal']))
    named=original['lower_carriers_in_A0_A1_B0_B1_C0_C1_order']
    target={tuple(sorted((mask_of(named[i]),1) for i in item))
            for item in product((0,1),(2,3),(4,5))}
    certs=set()
    found=0
    for item in original['first_bonds']:
        supports=tuple(stage[i] for i in item['source_laws_whose_separate_deletion_restores_111'])
        raw,_=clauses(supports)
        edges,names=candidates(stage,raw)
        full={tuple(sorted(names[i] for i in edge)) for edge in edges}
        expected=tuple(sorted((mask_of(named[i]),1) for i in item['readings']))
        assert expected in full
        found+=1
        certs.update(raw)
    # Work on the named readings to check this particular planted box and all
    # eight separate deletions, without conflating it with other choices.
    edges,names=candidates(stage,certs)
    ids={s:i for i,s in enumerate(names)}
    target_ids={tuple(sorted(ids[e] for e in triple)) for triple in target}
    assert target_ids <= edges
    def box_count(triples):
        kept,d,_=refine(triples,names)
        return len(list(structural_boxes(kept,names,d)))
    assert box_count(target_ids) == 1 and not any(box_count(target_ids-{e}) for e in target_ids)
    result={'known lower words recovered from their source laws':found,
            'named box recovered':1,'individual lower-clause erasures destroying it':8,
            'lower words with disconnected source laws':sum(not b['those_laws_connected_by_shared_distinctions']
                                                               for b in original['first_bonds']),
            'lower words needing at least one padded carrier':sum(any(b['carrier_members_outside_those_laws'])
                                                               for b in original['first_bonds'])}
    # This second control chooses small source subsets directly, without
    # looking at which subsets supplied the eight archived first bonds.
    all_partial=set()
    for subset in combinations(stage[:6] if pilot else stage,3):
        all_partial.update(clauses(subset)[0])
    edges,names=candidates(stage,all_partial)
    kept,d,counts=refine(edges,names)
    positives=list(structural_boxes(kept,names,d))
    opposite,independent_count=opposite_triples(kept,names)
    assert len(positives)==independent_count
    if not pilot:
        assert independent_count >= 1
    result['all source subsets of at most three laws in the indicated prefix']={
        'prefix of source knots':6 if pilot else 12,'signed triples before and after pruning':counts,
        'disjoint opposite pairs of triples':opposite,'boxes from first join':len(positives),
        'boxes from opposite-triple join':independent_count}
    return result


def second_join(pilot):
    archive=json.loads((HERE/'large_stages.json').read_text())['rows']
    counts='signed triples before and after disjoint alternatives'
    roster={(i,r):s for i,r,_,s in stage_list()}
    selected=[row for row in archive if row[counts][-1]]
    if pilot:
        selected=selected[:1]
    results=[]
    for row in selected:
        kept,names,_,stats=screen(roster[row['start'],row['round']])
        assert stats[counts]==row[counts]
        opposite,boxes=opposite_triples(kept,names)
        assert boxes==row['structural_boxes']
        results.append({'start':row['start'],'round':row['round'],'retained triples':len(kept),
                        'disjoint opposite pairs of triples':opposite,'boxes':boxes})
    return results


class ActualStage:
    """Two copies of the raw constraints for independent allowed-state checks."""
    def __init__(self, supports):
        self.supports = supports
        self.n = max(x for k in supports for x in k)+1
        self.next = 2*self.n + 1
        self.sat = Solver()
        for offset in (0,self.n):
            for row in supports:
                lit=[offset+1+x for x in row]
                self.sat.add_clause(lit)
                self.sat.add_clause([-i for i in lit])
        self.same=[]
        for i in range(self.n):
            u=self.fresh()
            x,y=i+1,i+1+self.n
            self.sat.add_clause([-u,-x,y])
            self.sat.add_clause([-u,x,-y])
            self.same.append(u)
        self.reads = {}
        self.unread = {}

    def fresh(self):
        u=self.next
        self.next+=1
        return u

    def agreement(self, mask, copy=0):
        if (mask,copy) not in self.reads:
            xs=[1+x+self.n*copy for x in members(mask)]
            u=self.fresh()
            # The two constant words force agreement; every differing value
            # guarantees disagreement. No evaluation-order assumption is used.
            self.sat.add_clause([u,*xs])
            self.sat.add_clause([u,*(-x for x in xs)])
            for x in xs[1:]:
                self.sat.add_clause([-u,-xs[0],x])
                self.sat.add_clause([-u,xs[0],-x])
            self.reads[mask,copy]=u
        return self.reads[mask,copy]

    def is_unread(self, m):
        if m not in self.unread:
            r,t=self.agreement(m),self.agreement(m,1)
            self.unread[m]=all(self.sat.solve(assumptions=[-r,t,*[self.same[x] for x in k]])
                               for k in self.supports)
        return self.unread[m]

    def one_clause(self, edge):
        raw, signs=zip(*edge)
        if not all(self.is_unread(m) for m in raw):
            return False
        rs=[self.agreement(m) for m in raw]
        missing=[]
        for word in product(range(2),repeat=3):
            if not self.sat.solve(assumptions=[r if v else -r for r,v in zip(rs,word)]):
                missing.append(word)
        return missing==[signs]


def opportunity(pilot):
    result=[]
    roster={(i,r):s for i,r,_,s in stage_list()}
    for idx,r,original_count in ((32,2,6),(2547,1,0)):
        stage=roster[idx,r]
        partial,_=clauses(stage)
        edges,signed=candidates(stage,partial)
        reader=ActualStage(stage)
        certified=[]
        seen=set()
        inspected=0
        # A deterministic prefix suffices to test the archive's threshold.
        for edge in sorted(edges):
            word=tuple(signed[i] for i in edge)
            inspected+=1
            if reader.one_clause(word):
                carrier_ids=tuple(sorted(m for m,_ in word))
                assert carrier_ids not in seen
                seen.add(carrier_ids)
                certified.append([[list(members(m)),v] for m,v in word])
            if len(certified)==(1 if pilot else 8):
                break
        assert len(certified)==(1 if pilot else 8), (idx,len(certified))
        reader.sat.delete()
        result.append({'start':idx,'round':r,'distinctions':reader.n,
                       'source knots':len(stage),'archived local bonds':original_count,
                       'signed candidates inspected':inspected,
                       'whole-stage eligible bonds verified':len(certified),
                       'carriers and their single forbidden word':certified})
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    p.add_argument('--output',required=True,type=Path)
    opts=p.parse_args()
    start=perf_counter()
    ring=((0,1,3),(1,2,4),(2,0,5))
    one=advance(ring).supports
    two=advance(one).supports
    cases=[('source three-knot ring',ring),('first grown round of the ring',one),
           ('second grown round of the ring',two),
           ('closed four-knot source with repeated shared distinctions',
            ((0,1,4),(0,1,5),(2,3,4),(2,3,5))),
           ('two disconnected three-place laws',((0,1,2),(3,4,5)))]
    results={'exhaustive small systems':{name:direct_control(s) for name,s in cases[:1 if opts.pilot else None]},
             'unsigned and signed synthetic control':planted(),
             'closed twelve-knot source':witness(opts.pilot),
             'opposite-triple recheck on each stage with surviving candidates':second_join(opts.pilot),
             'the two large stages below eight archived local bonds':opportunity(opts.pilot)}
    results['seconds']=perf_counter()-start
    opts.output.write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    main()
