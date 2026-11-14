"""Build compact referee inventories and verify saved numerical evidence."""
import collections,gzip,hashlib,itertools,json,time
from pathlib import Path
from lasso_certify import DP,INF,OUT,read_rows,transport

def loadlines(name):
    p=OUT/name
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:
        for line in f:yield json.loads(line)

def stripped(name,omit):return {r['key']:{k:v for k,v in r.items() if k not in omit} for r in loadlines(name)}

def finite_value(v):return v if v<INF else None

def plain_layers(row,depth=5):
    dp=DP(json.loads(row['key']),16)
    layer={}
    for e in range(len(dp.main.calls)):
        for v,c in dp.start(e).items():layer[v]=min(layer.get(v,INF),c)
    fixed=dp.start(0);minimum=[];first=[]
    for s in range(1,depth+1):
        minimum.append(finite_value(dp.value(layer)));first.append(finite_value(dp.value(fixed)))
        nl={}
        for i in range(len(dp.mid.calls)):
            for v,c in dp.step(layer,i).items():nl[v]=min(nl.get(v,INF),c)
        layer=nl;fixed=dp.step(fixed,0)
    return dict(key=row['key'],minimum=minimum,fixed_first=first,unequal_depths=[i+1 for i,(a,b) in enumerate(zip(minimum,first)) if a!=b])

def main():
    rows=read_rows();lassos=stripped('lasso_results.jsonl',{'vector'});mins=stripped('min_path_results.jsonl.gz',{'vector'});autos=stripped('lasso_automaton_results.jsonl.gz',{'graph','certificate'})
    for l in lassos.values():l['certificate_source']='lasso_results.jsonl'
    for name in ['lasso_improvements.json','lasso_higher_cap.json']:
        if (OUT/name).exists():
            for result in json.loads((OUT/name).read_text()):
                if result.get('certificate'):
                    c={k:v for k,v in result['certificate'].items() if k!='vector'}
                    lassos[result['key']].update(c)
                    lassos[result['key']]['certificate_source']=name
    assert len(lassos)==204 and len(mins)==204
    for r in mins.values():assert not r.get('mismatches')
    inventory=[];late_mismatches=[];censored_cells=0
    for key,l in lassos.items():
        row=rows[key];m=mins[key];a=autos.get(key)
        lc=bool(l.get('certified'));mc=bool(m.get('certified_uncarried_bounded'))
        if m.get('complete'):
            for field,trace in [('L_path',m['plain']),('L_path_uncarried',m['uncarried'])]:
                for s,expected in enumerate(row.get(field,[]),1):
                    j=s-1 if s<=len(trace) else m['repeat_from_depth']-1+(s-m['repeat_from_depth'])%m['period']
                    got=trace[j];wanted=expected if expected<=m['cap'] else None
                    censored_cells+=1
                    if got!=wanted:late_mismatches.append(dict(key=key,depth=s,field=field,referee=got,row=wanted))
        if row['class_path_uncarried']=='bounded':assert lc or mc
        entry=dict(key=key,row_order=l['row_order'],mixed_path_needed=bool(row.get('mixed_path_needed')),row_mixed_flag=row.get('mixed_path_needed'),row_uncarried_class=row.get('class_path_uncarried'),single_lasso_certified=lc,per_depth_uncarried_certified=lc or mc,per_depth_bound=m.get('eventual_uncarried_bound') if mc else l.get('eventual_bound') if lc else None,certificate_source=l['certificate_source'])
        if lc:
            for k in ['entry','prefix','period','repeat_from_depth','repeat_at_depth','eventual_bound','all_depths_have_bond','all_depth_bound','residue_values','top_port_masks','cap','vector_states']:
                entry[k]=l[k]
        else:
            entry['lasso_search_reason']=l.get('reason')
            entry['no_lasso_at_cap7']=bool(a and a.get('complete') and not a.get('safe_cycle'))
        if row['class_path_uncarried']=='none at any depth':
            dp=DP(json.loads(key),7)
            masks={sum(1<<j for j,v in enumerate(a) if v<dp.main.k) for a in dp.main.calls}
            todo=list(masks)
            for T in todo:
                for aa in dp.mid.calls:
                    U=transport(T,aa)
                    if U not in masks:masks.add(U);todo.append(U)
            assert 0 not in masks
            entry['no_uncarried_path_port_mask_obstruction']=sorted(masks)
        inventory.append(entry)
    assert not late_mismatches,late_mismatches[:2]
    inventory.sort(key=lambda x:x['row_order'])
    (OUT/'family_certificates.json').write_text(json.dumps(inventory,indent=2)+'\n')
    # A repeated argument within ONE SELF triple; this is separate from duplicate
    # calls, which are possible in the random archive.
    defs=[[3,2,[['K',[0,1,3]],['K',[0,3,4]],['SELF',[3,3,0]],['SELF',[3,4,1]]]]]
    dp=DP(defs,10);synthetic=[]
    for s in range(1,4):
        vals=[]
        for path in itertools.product(range(2),repeat=s):
            vec=dp.start(path[0])
            for i in path[1:]:vec=dp.step(vec,i)
            vals.append(dict(path=list(path),value=finite_value(dp.value(vec))))
        synthetic.append(dict(depth=s,paths=vals,minimum=min(v['value'] for v in vals)))
    expected=[[3,4],[3,4,4,5],[3,4,4,5,4,5,5,6]]
    assert [[p['value'] for p in r['paths']] for r in synthetic]==expected
    eq=[plain_layers(r) for r in rows.values() if r.get('first_ray_class')=='grows' and r.get('symmetry_equivalence_class_count')==1]
    assert len(eq)==4 and all(r['unequal_depths'] for r in eq)
    supplemental=dict(repeated_within_SELF=dict(definitions=defs,greatest_fixed_points=dp.rels,depths=synthetic,direct_enumeration_expected=expected,agrees=True),equivalent_calls_counterexamples=eq)
    (OUT/'supplemental_checks.json').write_text(json.dumps(supplemental,indent=2)+'\n')
    summary=dict(total_families=len(inventory),original_uncarried_classes=dict(collections.Counter(x['row_uncarried_class'] for x in inventory)),single_lasso_certificates=sum(x['single_lasso_certified'] for x in inventory),strict_all_positive_depth_lassos=sum(x.get('all_depths_have_bond',False) for x in inventory),mixed_total=sum(x['mixed_path_needed'] for x in inventory),mixed_lassos=sum(x['mixed_path_needed'] and x['single_lasso_certified'] for x in inventory),eventual_lasso_bounds=dict(collections.Counter(x['eventual_bound'] for x in inventory if x['single_lasso_certified'])),new_uncarried_certificates=[x['key'] for x in inventory if x['single_lasso_certified'] and x['row_uncarried_class']!='bounded'],per_depth_combined_certificates=sum(x['per_depth_uncarried_certified'] for x in inventory),per_depth_vector_repeats=sum(x.get('complete',False) for x in mins.values()),per_depth_directly_certified=sum(x.get('certified_uncarried_bounded',False) for x in mins.values()),per_depth_bounds=dict(collections.Counter(x['per_depth_bound'] for x in inventory if x['per_depth_uncarried_certified'])),censored_depth_cells_compared=censored_cells,censored_mismatches=late_mismatches,finite_cap_automata_complete=sum(x.get('complete',False) for x in autos.values()),finite_cap_automata_no_safe_cycle=sum(x.get('complete',False) and not x.get('safe_cycle') for x in autos.values()),finite_cap_negative_is_not_all_cap_negative=True,unfound_single_lasso_keys=[x['key'] for x in inventory if not x['single_lasso_certified']],lassos_with_missing_prefix=[dict(key=x['key'],main_minimum_prefix=rows[x['key']]['L_path'][:5],lasso_values=lassos[x['key']]['values']) for x in inventory if x['single_lasso_certified'] and not x['all_depths_have_bond']])
    (OUT/'recomputation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['unfound_single_lasso_keys','new_uncarried_certificates','lassos_with_missing_prefix']}))

if __name__=='__main__':main()
