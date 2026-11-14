"""Structural holdout checks and explicit boundary/gap controls."""
import collections,gzip,itertools,json,time
import independent_rules as R
from validate_counterexample import keynorm,isomorphs_one
HERE=R.HERE;ROOT=R.ROOT


def run():
    started=time.monotonic()
    # All own distinctions are used; this is not only an unused-variable pad.
    raw=[[3,4,[['K',[3,5,6]],['K',[0,2,4]],['K',[0,1,3]],['K',[0,1,2]],['SELF',[4,5,1]]]]]
    witness=R.examine(raw); assert witness['A']['certified'] and witness['exact']['verdict']=='non-forgetting'
    defs,allG,G,size,calls,_=R.prepare(raw);witness['A_output_guard']=R.rule_A(size,calls,G,0,protect_F_outputs=True)
    assert not witness['A_output_guard']['certified']
    iso=isomorphs_one(raw);matches=[];key=R.canonical(raw);exactmatches=[]
    p=ROOT/'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
    with gzip.open(p,'rt') as f:
        for line in f:
            row=json.loads(line);defs=json.loads(row['key'])
            if row['key']==key:exactmatches.append(row['key'])
            if len(defs)==1 and defs[0][:2]==raw[0][:2] and keynorm(defs) in iso:matches.append(row['key'])
    assert not matches and not exactmatches
    # Second derivation: enumerate assignments directly, separate from SAT.
    pairs=set()
    for v in itertools.product((0,1),repeat=7):
        if all(len({v[j] for j in a})>1 for c,a in raw[0][2] if c=='K'):
            a=sum(v[j]<<j for j in range(3));args=raw[0][2][-1][1];b=sum(v[q]<<j for j,q in enumerate(args));pairs.add((a,b))
    independent_matrix=sum(1<<(8*a+b) for a,b in pairs)
    assert [hex(independent_matrix)]==witness['R_i']
    witness['structural_census_holdout']={'exact_key_matches':len(exactmatches),'isomorphic_matches':len(matches),
        'allowed_isomorphisms':'all 6 port and24 own-variable permutations, NAE argument order, and call order; SELF argument positions conjugated with port names',
        'all_own_distinctions_used':True,'independent_assignment_projection_matches':True}
    # N needs a nonempty consistent family. Complete triples on5 variables
    # are unsatisfiable; adding identity SELF remains within CALL_CAP12.
    dead=[[3,2,[['K',list(a)] for a in itertools.combinations(range(5),3)]+[['SELF',[0,1,2]]]]]
    dead_control=R.examine(dead);assert not dead_control['alive'] and dead_control['N']['cyclic'] and dead_control['exact']['r']==1
    # Every pair projection of a side relation must be full to permit peeling.
    pair_full=[]
    for mask in range(256):
        allowed={j for j in range(8) if (mask>>j)&1}
        direct=all({tuple((s>>j)&1 for j in range(3) if j!=drop) for s in allowed}==set(itertools.product((0,1),repeat=2)) for drop in range(3))
        assert direct==R.full_pairs(allowed);pair_full.append(direct)
    # For all2-state relations, composition with a product is a product.
    product=R.E.controls()
    result={'structurally_new_counterexample':witness,'Rule_N_empty_limit_exclusion_control':dead_control,
            'full_pair_projection_checks':256,'full_pair_relation_count':sum(pair_full),'algebra_controls':product,
            'seconds':time.monotonic()-started}
    (HERE/'structural_and_boundary_controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'structurally_new':True,'description':raw,'A':witness['A'],'N':witness['N'],'R_i':witness['R_i'],'exact':witness['exact'],
                      'isomorphic_census_matches':len(matches),'dead_domain_control_passed':True,'seconds':result['seconds']}))

if __name__=='__main__':run()
