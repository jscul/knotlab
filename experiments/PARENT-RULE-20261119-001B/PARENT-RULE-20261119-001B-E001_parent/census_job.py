"""Shared-runner job for PARENT-RULE-20261119-001B-E001, part C (the census).  Every census start regrown in complete rounds under
the cheapest counts, rounds 0 to 8, every stage of at most 40 junctions:
- L: at every stage of round >= 1, violations of backed pairs (P1), backed by a closed junction (P1+), live junctions never meet
  (P2); peeling the stage gives the census's previous stage exactly; the peel depth is at least the round (open stages);
- R: rigidity, on every stage of round >= 1 with at most 14 junctions (full tables by bonds) and on every meet-once stage of 15 to
  40 junctions (tables read to distance 8, exact_table_v2): the table's isomorphisms onto itself, taken on twin classes (cap 2,000),
  and how many do not carry the equation space onto itself;
- Q: on every open stage of round >= 1 with at most 14 junctions, the full table against the previous stage's on the previous
  stage's distinctions: equal, smaller, larger.
Round-0 stages (the starts) are counted for the base rates only.  Shards of 100 starts in the census's order."""
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / 'experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
sys.setrecursionlimit(100000)
sys.path.insert(0, str(CENSUS))
sys.path.insert(0, str(HERE))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('census_job_parent', CENSUS / 'job.py')
CJ = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = CJ
_spec.loader.exec_module(CJ)
import exact_table_v2 as X  # noqa: E402
import plib as L  # noqa: E402
S, F, A = CJ.S, CJ.F, CJ.A
SHARD = 100
HI = 40
FULL = 14
HPOOL = 8
CAP = 2000
_ARR = None


def setup(params):
    global _ARR
    _ARR = CJ.load()


def cases():
    data = _ARR if _ARR is not None else CJ.load()
    for s in range(0, len(data), SHARD):
        yield f'census-{s // SHARD:04d}', {'lo': s, 'hi': min(len(data), s + SHARD)}


def rigid(stars, tab):
    n = bad = 0
    for lift, ok in L.carriers(stars, stars, tab, tab, CAP):
        if lift == 'cap':
            return {'renamings': n, 'not_carrying': bad, 'capped': True}
        n += 1
        if not ok:
            bad += 1
            return {'renamings': n, 'not_carrying': bad, 'capped': False, 'stopped_at_first': True}
    return {'renamings': n, 'not_carrying': bad, 'capped': False}


def run(case_id, p):
    data = _ARR if _ARR is not None else CJ.load()
    c = Counter()
    examples = []
    for i in range(p['lo'], p['hi']):
        key = data[i]
        P = S.from_junctions(A.stars_of(key))
        prev, prev_tab = None, None
        for r in range(CJ.RMAX + 1):
            stars = [frozenset(b) for b in P.bits_of]
            n = len(stars)
            if n > HI:
                break
            ms = L.max_shared(stars)
            once = 'once' if ms < 2 else 'two'
            pr = L.props(stars)
            open_ = pr['stratum'] != 'closed'
            if r == 0:
                c['start'] += 1
                c[f'start_{pr["stratum"]}'] += 1
                c['start_P1_ok'] += pr['P1'] == 0
                c['start_P1+P2_ok'] += pr['P1+'] == 0 and pr['P2'] == 0
            else:
                c['stage'] += 1
                c[f'stage_{once}'] += 1
                c[f'stage_{pr["stratum"]}'] += 1
                for k in ('P1', 'P1+', 'P2'):
                    if pr[k]:
                        c[f'viol_{k}'] += 1
                        if len(examples) < 5:
                            examples.append({'index': i, 'round': r, 'violation': k, 'stars': [sorted(s) for s in stars]})
                # an open stage peels to the previous stage; a closed one is the previous stage plus its closing junction
                peeled = L.peel(stars) if open_ else stars[:-1]
                if peeled != prev:
                    c['peel_not_previous'] += 1
                if open_:
                    d = L.depth(stars)
                    c['open_stage'] += 1
                    if d < r:
                        c['depth_below_round'] += 1
                        if len(examples) < 5:
                            examples.append({'index': i, 'round': r, 'violation': 'depth', 'depth': d,
                                             'stars': [sorted(s) for s in stars]})
            tab = None
            if n <= FULL:
                tab, _ = L.table(stars)
            if r >= 1 and tab is not None:
                g = rigid(stars, tab)
                oc = 'open' if open_ else 'closed'
                c[f'R_full_{once}_{oc}_stages'] += 1
                c[f'R_full_{once}_{oc}_capped'] += g['capped']
                c[f'R_full_{once}_{oc}_not_rigid'] += g['not_carrying'] > 0
                if g['not_carrying'] and len(examples) < 10:
                    examples.append({'index': i, 'round': r, 'violation': f'not_rigid_{oc}', 'stars': [sorted(s) for s in stars]})
                if open_ and prev_tab is not None:
                    q = Counter()
                    for pair, dprev in prev_tab.items():
                        dnow = tab.get(pair)
                        if dprev == 'none' and dnow == 'none':
                            q['equal'] += 1
                        elif dprev == 'none':
                            q['smaller'] += 1
                        elif dnow == 'none':
                            q['larger'] += 1
                        else:
                            q['equal' if dnow == dprev else ('smaller' if dnow < dprev else 'larger')] += 1
                    for k, v in q.items():
                        c[f'Q_{once}_{k}'] += v
                    c[f'Q_{once}_stages'] += 1
                    c[f'Q_{once}_stages_all_equal'] += q['smaller'] == 0 and q['larger'] == 0
            elif r >= 1 and once == 'once' and n >= 15:
                pooled = X.exact_table(stars, HPOOL)
                g = rigid(stars, pooled)
                oc = 'open' if open_ else 'closed'
                c[f'R_pooled_once_{oc}_stages'] += 1
                c[f'R_pooled_once_{oc}_capped'] += g['capped']
                c[f'R_pooled_once_{oc}_not_carrying'] += g['not_carrying'] > 0
            prev, prev_tab = stars, tab
            if r == CJ.RMAX:
                break
            res = P.step(S.gf2(F.fewest), None)
            if res is None or res['new'] == 0:
                break
    return {'counts': dict(c), 'examples': examples}
