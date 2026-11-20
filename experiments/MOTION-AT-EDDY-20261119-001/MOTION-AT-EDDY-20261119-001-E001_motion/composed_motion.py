"""Use the registered return pairing as the domain of the one-state update."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import json
import random

from b_updates import PathGuard, PHASES, bits, mask
from motion_stage import growth_engine, support_neighbors
from nearness import ReturnRule, co_knotted_pairs

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2]/'artifacts'/HERE.parent.name/HERE.name


class PairedReader:
    def __init__(self, nearness):
        # Only the unweighted distance-one relation is supplied to the reader.
        self.rule = ReturnRule(nearness)
        self.stage = self.rule.stage
        selected = {}
        for v,row in self.rule.graph.items():
            for u,w in combinations(sorted(row),2):
                if self.rule.exits((u,v)) == {w} and self.rule.exits((w,v)) == {u}:
                    q = self.rule.packet((u,v,w))
                    selected[q] = (u,v,w)
        self.quads = sorted(selected, key=lambda q:tuple(sorted(q)))
        self.ports = [selected[q] for q in self.quads]
        self.sites = {frozenset(triple):i for i,triple in enumerate(self.ports)}
        self.masks = [mask(q) for q in self.quads]
        self.private = [mask(bit for bit in q if set(self.stage.owners[bit])-self.rule.source)
                        for q in self.quads]
        assert all(p.bit_count()==2 for p in self.private)
        graph = support_neighbors(self.quads)
        assert all(len(row)<=2 for row in graph)
        self.guard = PathGuard(graph)
        literal = set(self.stage.ordinary_quads())
        assert set(self.quads) <= literal

    def encode(self, occupied):
        value = 0
        for q in occupied: value ^= self.masks[q]
        return value

    def decode(self, value):
        occupied = inconsistent = 0
        for i,p in enumerate(self.private):
            seen = value & p
            if seen == p: occupied |= 1<<i
            elif seen: inconsistent |= 1<<i
        return occupied,inconsistent

    @lru_cache(maxsize=None)
    def next_state(self,value):
        actions = self.guard.fire(*self.decode(value))
        assert len(actions)<=1, 'an isolated-packet schedule branched'
        if not actions:return None
        following = value ^ self.masks[actions[0]]
        assert (value^following).bit_count()==4 and self.stage.allowed_change(bits(following))
        return following


def launch_series(reader, path_ids, seams):
    # These old source names serve ONLY as an external judge for launch and scoring.
    path = {j:reader.sites.get(frozenset(path_ids[j-1:j+2]))
            for j in range(1,len(path_ids)-1)}
    summary = Counter()
    across = Counter()
    extremal = []
    sample = []
    for direction in [1,-1]:
        for start in path:
            def positions(s, phase):
                return [s+direction*i for i in phase]
            pos = positions(start,PHASES[0])
            if any(path.get(j) is None for j in range(min(pos),max(pos)+1)):continue
            state = reader.encode(path[j] for j in pos)
            assert state.bit_count()==10
            event = 0
            completed = [start]
            while True:
                after = reader.next_state(state)
                if after is None: break
                state = after
                event += 1
                units, phase = divmod(event,4)
                anchor = start+direction*units
                physical = positions(anchor,PHASES[phase])
                assert all(path.get(j) is not None for j in physical)
                assert state == reader.encode(path[j] for j in physical)
                if phase==0:
                    completed.append(anchor)
                    assert state.bit_count()==10
                assert event <= 4*len(path_ids)+4
            seen = [s for s in seams if min(completed)<s<max(completed)]
            across[tuple(seen)]+=1
            summary[direction]+=1
            if len(completed)-1>=2:summary['at_least_two']+=1
            row = dict(start=start,direction=direction,events=event,completed_shifts=len(completed)-1,
                       last_full_anchor=completed[-1],crossed=seen)
            extremal.append(row)
            if start in (1,len(path_ids)-2):sample.append(row)
    def format_crossing(k): return ','.join(map(str,k)) or 'none'
    return {'launches':{'positive':summary[1],'negative':summary[-1]},
            'at_least_two_shifts':summary['at_least_two'],
            'crossed_by_full_anchor':{format_crossing(k):v for k,v in across.items()},
            'outermost_launches':sample,
            'longest':max(extremal,key=lambda r:r['events']),
            'distinct_full_binary_states_evaluated':reader.next_state.cache_info().currsize}


def run(spec, relabel=False):
    growth=growth_engine()
    stage = growth.grow_case(spec,1,{'junctions':2048,'distinctions':8192})
    assert stage['qualification']['canonical'] and stage['qualification']['DOUBLE_IDENT']['in_class']
    source = growth.import_file('motion_holdout_source', Path(growth.__file__).with_name('fate_series.py')).Source(spec)
    source_map = [{'cycle_rank':part['rank'],'endless_chains':part['rays'],'points':len(part['point_ids'])}
                  for part in source.pieces()]
    stars = [list(row) for row in stage['stages']['1']['stars']]
    srcstars = list(stars[:len(spec['sizes'])])
    if relabel:
        rng=random.Random(2327)
        names=sorted(set().union(*map(set,stars))); perm=names.copy();rng.shuffle(perm)
        trans=dict(zip(names,perm,strict=True))
        srcstars=[[trans[e] for e in row] for row in srcstars]
        stars=[[trans[e] for e in row] for row in stars]; rng.shuffle(stars)
    reader=PairedReader(co_knotted_pairs(stars))
    names={frozenset(row):j for j,row in enumerate(reader.rule.stars)}
    role=spec['roles'];path_ids=[names[frozenset(srcstars[j])] for j in role['background']]
    result=launch_series(reader,path_ids,role['seams'])
    reader.next_state.cache_clear()
    return {'source_junctions':len(spec['sizes']),'total_junctions':len(stars),
            'distinctions':len(reader.stage.owners),'source_map':source_map,
            'all_ordinary_quads':len(reader.stage.ordinary_quads()),'paired_quads':len(reader.quads),
            'arbitrary_renaming':relabel,**result}


def main():
    report={}
    for spec in json.loads((HERE/'holdout.json').read_text())['cases']:
        row=run(spec)
        renamed=run(spec,True)
        assert {k:v for k,v in row.items() if k!='arbitrary_renaming'}=={k:v for k,v in renamed.items() if k!='arbitrary_renaming'}
        row['arbitrary_renaming']=True
        report[spec['id']]=row
    (DATA/'composed_motion.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,r in report.items():print(name,r['launches'],r['outermost_launches'],r['crossed_by_full_anchor'])


if __name__=='__main__':main()
