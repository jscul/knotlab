"""Read the frozen predictions concerning the main runs and the all-pairs swap."""
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from c_opportunities import ART, HERE, ID, ROOT, RUNS, id_pair, rows

def recount(limit=None):
    starts = json.loads((ROOT / "research" / (ID+"C") / "starts_c.json").read_text())["starts"]
    import random
    order = random.Random("C|order").sample(range(len(starts)), len(starts))
    common = {starts[i]["id"] for i in [i for i in order if not starts[i]["set_aside_parity"]][:500]}
    by_stratum = defaultdict(Counter)
    pairs_common = defaultdict(dict)
    state = defaultdict(Counter)
    failures, cases, members, cases_by_round = Counter(), Counter(), Counter(), Counter()
    cases_by_run = defaultdict(Counter)
    previous = {}
    origins = []
    for run in RUNS:
        for r in rows(run,limit):
            law = r['law']
            ration, treatment, keep, take, kl, wt = law.split('/')
            key = (run,ration,treatment,r.get('n_start'))
            if 'error' in r:
                state[run]["unread"] += 1
                continue
            n = r['n_start']
            stage = by_stratum[key]
            stage["n"] += 1
            has_pair = any(kept for _,kept,_ in r['pair_rounds'].values())
            stage["growths with pairs"] += has_pair
            d = state[run]
            d['growths'] += 1
            d['pairs'] += len(r['pairs'])
            d['met pairs'] += sum(p['meet'] is not None for p in r['pairs'])
            d['rounds above the cap'] += len(r['more_than_eight'])
            if run in ('R1a','R1b','R2') and r['start'] in common:
                pairs_common[wt][(r['start'],law.rsplit('/',1)[0])] = has_pair
            kt = r['knot_test']
            d['growths with failing knots'] += bool(kt['n_fails'])
            d['verdicts'] += kt['verdicts']
            for f in kt['fails']: failures[(run,f['kind'])] += 1
            if 'nae_last_round_ties' in r:
                d['tie checks'] += 1
                d['made tie classes'] += r['nae_last_round_ties']['classes_with_a_made_distinction']
            for c in r['cases']:
                reading = c['reading']
                cases[(run,reading)] += 1
                cases_by_run[run][reading] += 1
                if run in RUNS[:5]:
                    if ration == 'FLOOR1' and reading in ('form','both'):
                        members[(treatment, c['y_loose_max'])] += 1
                    if reading=='vA' and ration=='FLOOR1' and treatment=='CANCEL-OFFSHOOT':
                        d["earlier values reading in predicted laws"] += 1
                    cases_by_round[(run,c['s'])] += 1
            if run in ('R1a','R1b') and n <= 4:
                previous[r["seed"]] = {id_pair(r,p): p for p in r["pairs"]}
            if run == 'R6':
                for c in r['cases']:
                    if c['reading']!='form' or not c['first_stage']['passes_at_100']:
                        continue
                    k = id_pair(r,c)
                    orig = previous.get(r['seed'])
                    init = orig and orig.get(k)
                    origins.append(dict(start=r['start'],first=c['X'],second=c['Y'],round=c['s'],
                                        growth_in_main_run=orig is not None,
                                        pair_previously_read=init is not None,
                                        form_previously_met=init is not None and 'form' in init['after']))
    pc1bad, pc2bad, no_data = [],[],[]
    for (run,ra,tr,n),d in sorted(by_stratum.items()):
        if run not in ('R1a','R1c'): continue
        v=d['growths with pairs']/d['n']
        low,high = ((.2,.55) if n==5 else (.25,.65)) if (ra,tr)==('FLOOR1','CANCEL-OFFSHOOT') else (0,.1)
        if not low<=v<=high: pc1bad.append([run,ra,tr,n,d['growths with pairs'],d['n']])
    for run in ('R1b','R1d'):
        for ra,tr in sorted(set((r,t) for run2,r,t,n in by_stratum if run2==run)):
            small=sum((by_stratum.get((run,ra,tr,n),Counter()) for n in (3,4)),Counter())
            if not small['n']:
                no_data.append([run,ra,tr])
            elif small['growths with pairs']/small['n']<.2:
                pc2bad.append([run,ra,tr,small['growths with pairs'],small['n']])
    shared=set(pairs_common['T1']) & set(pairs_common['T2'])
    def items(counter):
        return [list(k)+[v] for k,v in sorted(counter.items())]
    return {"growths":state,"first_stage_case_rows":cases_by_run,
            "PC1 outside range by size":pc1bad,"PC2 below one fifth on three and four knots":pc2bad,
            "PC2 cells without growths":no_data,"PC6 max loose per member of second form":items(members),
            "failing knots":items(failures),"case reading rounds":items(cases_by_round),
            "holder comparison for the 500 starts":
                {wt:{"read":len(v),"pair":sum(v.values()),"common_read":len(shared),
                     "pair_on_common_read":sum(v[k] for k in shared)} for wt,v in pairs_common.items()},
            "origin of all-pairs claimed positives":origins}
if __name__=="__main__":
    pilot = "--pilot" in sys.argv
    t=time.monotonic()
    result=recount(40 if pilot else None)
    if not pilot:
        (HERE/"c_predictions.json").write_text(json.dumps(result, indent=2)+"\n")
    print(round(time.monotonic()-t,3),"seconds")
