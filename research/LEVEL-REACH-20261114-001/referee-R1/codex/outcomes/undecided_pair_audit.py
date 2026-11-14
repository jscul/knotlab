"""Independent cross-pair bounds and bounded size-three search on four keys.

The parent's sample_plan was frozen before this extension. All four gaps are
checked for cross-level pair bonds. Only gap4 receives a fresh size-three
search, in ascending a,b,c order, with a 30-second per-key search ceiling.
"""
from __future__ import annotations
import gzip
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
REF = OUT.parent
sys.path.insert(0, str(REF))
from fresh_pattern import build
from fresh_search import levels
from pysat.solvers import Solver

N = 9
NVARS = (1 << (N+1))-1
TRIPLE_SECONDS = 30
START = time.monotonic()


def assumptions(support, values):
    return [(v+1) if b else -(v+1) for v,b in zip(support,values)]


class Checked:
    def __init__(self, knots):
        self.knots = knots
        self.clauses = [[v+1 for v in knot] for knot in knots] + [[-(v+1) for v in knot] for knot in knots]
        self.solver = Solver(name='glucose4', bootstrap_with=self.clauses)
        self.models = {}
        self.states = []
        self.columns = [0]*NVARS
        self.calls = 0
        self.unsat = []

    def solve(self, support=(), values=(), deadline=None):
        self.calls += 1
        units = assumptions(support,values)
        end = min(time.monotonic()+60, deadline) if deadline else time.monotonic()+60
        while True:
            self.solver.conf_budget(20000)
            answer = self.solver.solve_limited(assumptions=units)
            if answer is not None:
                break
            if time.monotonic() > end:
                raise TimeoutError('SAT conflict-slice deadline')
        if not answer:
            self.unsat.append(units)
            return False,None
        positive = [v-1 for v in self.solver.get_model() if 0<v<=NVARS]
        model = sum(1<<v for v in positive)
        assert all(bool(model>>v&1)==bool(b) for v,b in zip(support,values))
        if model not in self.models:
            assert all(any(model>>v&1 for v in knot) and not all(model>>v&1 for v in knot) for knot in self.knots)
            index = len(self.states)
            self.models[model] = index
            self.states.append(model.to_bytes((NVARS+7)//8,'little').hex())
            for v in positive:
                self.columns[v] |= 1<<index
        return True,self.models[model]

    def support_check(self,support,forbidden,deadline=None):
        sat,_ = self.solve(support,forbidden,deadline)
        projection_states = []
        for dropped in support:
            subset = [v for v in support if v!=dropped]
            states=[]
            for values in itertools.product((0,1),repeat=len(subset)):
                full,index=self.solve(subset,values,deadline)
                states.append({'values':values,'satisfiable':full,'state_index':index})
            projection_states.append({'support':subset,'assignments':states})
        return {'support':support,'forbidden_assignment':forbidden,'nonfull':not sat,
                'maximal_projections_full':all(x['satisfiable'] for p in projection_states for x in p['assignments']),
                'proper_projection_states':projection_states}


def triple_search(checked,A,B):
    start=time.monotonic();end=start+TRIPLE_SECONDS
    trials=0;missing=0;nonminimal=0
    bad_pairs=set()
    try:
        for a in A:
            for b in B:
                for c in range(NVARS):
                    if c==a or c==b or any(frozenset(p) in bad_pairs for p in ((a,b),(a,c),(b,c))):
                        continue
                    trials+=1
                    if time.monotonic()>end:
                        raise TimeoutError('size-three search ceiling')
                    for bv,cv in itertools.product((0,1),repeat=2):
                        allbits=(1<<len(checked.states))-1
                        present=(allbits^checked.columns[a])
                        present&=checked.columns[b] if bv else allbits^checked.columns[b]
                        present&=checked.columns[c] if cv else allbits^checked.columns[c]
                        if present:
                            continue
                        missing+=1
                        satisfiable,_=checked.solve([a,b,c],[0,bv,cv],end)
                        if satisfiable:
                            continue
                        candidate=checked.support_check([a,b,c],[0,bv,cv],end)
                        if candidate['maximal_projections_full']:
                            return {'status':'found','L':3,'candidate':candidate,'seconds':time.monotonic()-start,
                                    'triple_support_trials':trials,'missing_assignment_queries':missing,'nonminimal_candidates':nonminimal}
                        nonminimal+=1
                        for projection in candidate['proper_projection_states']:
                            if not all(x['satisfiable'] for x in projection['assignments']):
                                bad_pairs.add(frozenset(projection['support']))
        return {'status':'exhausted','lower_bound':4,'seconds':time.monotonic()-start,
                'triple_support_trials':trials,'missing_assignment_queries':missing,'nonminimal_candidates':nonminimal}
    except TimeoutError as error:
        return {'status':'undecided','reason':str(error),'seconds':time.monotonic()-start,
                'triple_support_trials':trials,'missing_assignment_queries':missing,'nonminimal_candidates':nonminimal}


plan_path=REF/'sample_plan.json'
selected=[item for item in json.loads(plan_path.read_text())['sample'] if item['stratum']=='undecided']
raw={}
with gzip.open(ROOT/'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/results.jsonl.gz','rt') as handle:
    for line in handle:
        outer=json.loads(line)
        if outer['case'] in {item['case'] for item in selected}:
            raw[outer['case']]=outer['result']
result={'N':N,'k0':3,'selection':'four frozen undecided sample_plan entries','sample_plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        'triple_search':{'gap':4,'seconds_per_key':TRIPLE_SECONDS,'order':'ascending a,b,c; first a fixed0 by NAE complement symmetry'},
        'method':'fresh Glucose4 NAE CNF; explicit state checks; exhaustive crosspair00/01; bounded model-filtered triples',
        'limitations':['No full profile is resolved unless every gap has matching bounds.','Fresh size-three candidates are checked, not inherited from the study.','A timed-out triple search supplies no absence result.','Solver UNSAT results have no emitted LRAT proof in this audit.'],
        'cases':[]}
for item in selected:
    start=time.monotonic();record=raw[item['case']]
    assert record['key']==item['key']
    checked=Checked(build(item['key'],N))
    case={'case':item['case'],'key':item['key'],'reported_profile':item['study'],'queries':[]}
    try:
        alive,state=checked.solve();assert alive
        case['alive_state_index']=state
        for gap,entry in enumerate(record['levels'],1):
            A,B=levels(3,gap)
            pairs=[];forbidden=[]
            for a in A:
                for b in B:
                    states=[]
                    for values in ((0,0),(0,1)):
                        satisfiable,index=checked.solve([a,b],values)
                        states.append(index)
                        if not satisfiable:
                            forbidden.append({'support':[a,b],'forbidden_assignment':values})
                    pairs.append({'support':[a,b],'state_indices_for00_01':states})
            query={'s':gap,'reported_L':entry['L_N'],'cross_pairs':len(pairs),'assignments_queried':2*len(pairs),
                   'pair_projection_states':pairs,'forbidden_pairs':forbidden,'lower_bound':2 if forbidden else 3}
            if forbidden:
                candidate=checked.support_check(forbidden[0]['support'],forbidden[0]['forbidden_assignment'])
                query['candidate']=candidate
                query['upper_bound']=2 if candidate['nonfull'] and candidate['maximal_projections_full'] else None
            elif type(entry['L_N'])is int:
                candidate=checked.support_check(entry['anywhere']['bond'],entry['anywhere']['forbidden_assignment'])
                query['reported_candidate_checked']=candidate
                query['upper_bound']=entry['L_N'] if candidate['nonfull'] and candidate['maximal_projections_full'] else None
            else:
                query['upper_bound']=None
            if gap==4 and query['upper_bound'] is None:
                query['size_three_search']=triple_search(checked,A,B)
                if query['size_three_search']['status']=='found':
                    query['upper_bound']=3
                elif query['size_three_search']['status']=='exhausted':
                    query['lower_bound']=4
            query['exact']=query['upper_bound'] is not None and query['upper_bound']==query['lower_bound']
            case['queries'].append(query)
        case['status']='ok'
    except TimeoutError as error:
        case['status']='undecided';case['reason']=str(error)
    finally:
        case['SAT_queries']=checked.calls;case['checked_distinct_states']=len(checked.states)
        case['seconds']=time.monotonic()-start
        path=OUT/f"undecided_states_{item['case']}.json.gz"
        with gzip.open(path,'wt')as handle:
            json.dump({'encoding':'little-endian hex bitv=idv','states':checked.states,'unsat_assumptions':checked.unsat},handle)
        case['states_file']=path.name
        checked.solver.delete()
    result['cases'].append(case)
    print(json.dumps({'case':item['case'],'seconds':case['seconds'],'bounds':[[q['lower_bound'],q['upper_bound']]for q in case['queries']],
                      's4_scan':case['queries'][-1].get('size_three_search',{}).get('status')if case['queries']else None}),flush=True)
result['seconds']=time.monotonic()-START
result['peak_rss_MB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
(OUT/'undecided_pair_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'seconds':result['seconds'],'peak_rss_MB':result['peak_rss_MB']}),flush=True)
