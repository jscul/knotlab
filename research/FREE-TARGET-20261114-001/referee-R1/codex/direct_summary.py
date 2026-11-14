"""Consolidate retained direct-SAT records without promoting unfinished work."""
import hashlib
import json
from pathlib import Path
from direct_bonds import load_cases

OUT=Path(__file__).resolve().parent


def main():
    files=sorted(set(OUT.glob('direct_bonds*.jsonl'))|set(OUT.glob('direct_case*.jsonl'))|set(OUT.glob('direct_final*.jsonl')))
    raw=[]
    for p in files:
        for j,line in enumerate(p.read_text().splitlines(),1):
            x=json.loads(line);x['source_record']={'file':p.name,'line':j};raw.append(x)
    interrupted=json.loads((OUT/'direct_budget_interrupt.json').read_text())
    interrupted.update(key=load_cases(10)[interrupted['case']]['key'],minimum=None,
                       clauses=None,copies=None,targets=None,peak_rss_kb=0,
                       source_record={'file':'direct_budget_interrupt.json','line':1})
    raw.append(interrupted)
    cases=load_cases(10);by_family=[];points=[];mismatches=[]
    for idx,c in enumerate(cases):
        family={'case':idx,'key':c['key'],'r':c['r'],'S':c['preparation']['S'],
                'main':c['preparation']['n_defs']-1,'s_block_size':c['preparation']['s_block_size'],
                'L_path':c['L_path'][:5],'points':[]}
        family['unshifted_lower']=[2+s//c['r'] for s in range(1,6)]
        shift=int(family['main']!=family['S'])
        family['justified_lower']=[2+max(0,s-shift)//c['r'] for s in range(1,6)]
        for s in range(1,6):
            for h in (1,2):
                records=[r for r in raw if (r['case'],r['s'],r['h'])==(idx,s,h)]
                if not records:continue
                exact=[r for r in records if r['status']=='exact']
                mins={r['minimum'] for r in exact}
                if len(mins)>1:mismatches.append({'kind':'repeat_minimum_disagrees','case':idx,'s':s,'h':h,'values':sorted(mins)})
                r=exact[-1] if exact else records[-1]
                lower=max([z.get('proved_lower_bound',2) for z in records]+[2])
                p={k:r[k] for k in ['case','s','h','variables','clauses','copies','targets','status','minimum','source_record']}
                p['proved_lower_bound']=r['minimum'] if exact else lower
                p['claimed_lower_bound']=family['unshifted_lower'][s-1]
                p['justified_lower_bound']=family['justified_lower'][s-1]
                p['L_path']=family['L_path'][s-1]
                p['records_retained']=len(records)
                if not exact and lower>p['L_path']:
                    mismatches.append({'kind':'complete_exclusion_exceeds_path_upper_bound','point':p})
                if exact:
                    p.update(witness=r['witness'],witness_origins=r['witness_origins'],
                             forbidden_states=r.get('forbidden_states'),
                             one_deleted_all_shattered=r['one_deleted_all_shattered'],
                             below_claimed=r['minimum']<p['claimed_lower_bound'],
                             below_justified=r['minimum']<p['justified_lower_bound'],
                             above_path=r['minimum']>p['L_path'])
                    if p['below_claimed'] or p['below_justified'] or p['above_path'] or r['minimum']<lower:
                        mismatches.append({'kind':'bound_disagrees','point':p})
                family['points'].append(p);points.append(p)
        by_family.append(family)
    pairs=[]
    for f in by_family:
        for s in range(1,6):
            pp=[p for p in f['points'] if p['s']==s and p['status']=='exact']
            if len(pp)==2:
                pairs.append({'case':f['case'],'s':s,'h1':pp[0]['minimum'],'h2':pp[1]['minimum'],
                              'same':pp[0]['minimum']==pp[1]['minimum']})
    result={'meaning':'Exact minima only for members within each explicit all-copies cutoff; witnesses are whole-limit bonds. Halo agreement does not prove global minimum.',
            'cases':by_family,'raw_records':len(raw),'distinct_points':len(points),
            'exact_points':sum(p['status']=='exact' for p in points),
            'all_exact_equal_recorded_path':all(p['minimum']==p['L_path'] for p in points if p['status']=='exact'),
            'families_with_exact_points':len({p['case'] for p in points if p['status']=='exact'}),
            'complete_halo_pairs':pairs,'halo_pairs_all_agree':all(p['same'] for p in pairs),
            'mismatches':mismatches,'maximum_peak_rss_kb':max(r['peak_rss_kb'] for r in raw),
            'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (OUT/'direct_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['| Family | Block | r | Claimed lower, s=1..5 | L_path, s=1..5 | h=1 minima | h=2 minima |',
           '| --- | ---: | ---: | --- | --- | --- | --- |']
    def values(f,h):
        vals=[]
        for s in range(1,6):
            pp=[p for p in f['points'] if p['s']==s and p['h']==h]
            vals.append(str(pp[0]['minimum']) if pp and pp[0]['status']=='exact' else
                        ('I' if pp and pp[0]['status']=='interrupted_without_result' else ('T' if pp else '—')))
        return ', '.join(vals)
    for f in by_family:
        show=lambda a:', '.join(map(str,a))
        lines.append(f"| F{f['case']+1:02} | {f['s_block_size']} | {f['r']} | {show(f['unshifted_lower'])} | {show(f['L_path'])} | {values(f,1)} | {values(f,2)} |")
    lines+=['','T = unfinished at the point budget; I = explicitly interrupted without a result; — = not attempted. All are excluded from exact-value comparisons.',
            'F06 and F07 use a wrapper main; their proved lower bound uses s−1. Complete keys and partial lower-size exclusions are in direct_summary.json.','']
    (OUT/'direct_table.md').write_text('\n'.join(lines))
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','inputs','complete_halo_pairs']}))


if __name__=='__main__':main()
