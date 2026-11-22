"""Check the two independently computed counts and the archived physical pairs."""
import gzip
import json
from pathlib import Path
from fractions import Fraction

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
leaf=HERE.name+'A'
output=ROOT/'artifacts'/leaf/(leaf+'-E001_sibling_event')
FIELDS={'available':'recorder_available','marked_event':'event_true','correct_bit':'correct_bit',
        'wrong_bit':'wrong_bit','silent':'silent','refused':'refused','false_event_indication':'false_event_indications',
        'true_event_indication':'true_event_indications'}


def verify():
    counts=json.loads((HERE/'independent_counts.json').read_text())
    main=json.loads((output/'results.json').read_text())['laws']
    with gzip.open(output/'paired_words.json.gz','rt') as f:
        raw=json.load(f)
    assert raw['bit_order']==list(range(16)) and raw['pair_order']==['intact','interrupted']
    checked={}
    for law,mine in counts.items():
        other=main[law]
        width=len(mine['legal_fresh_given_paid']['0'])
        compared=0
        for ours,theirs in [('all','all_original_launches'),('intact','paired_intact'),('interrupted','paired_interrupted_image')]:
            for u,row in mine['cohorts_per_original_paid_value'][ours].items():
                target=other['cohorts'][theirs]['by_u'][u]
                full=target['counts']
                for a,b in FIELDS.items():
                    assert row[a]==full[b],(law,ours,u,a)
                    compared+=1
                assert row['available']==full['enrolled']==full['first_cut_completed']
                assert full['missing_recorder']==full['invalid']==0
                assert target['F_fresh_word_support']==mine['legal_fresh_given_paid'][u]
        plus=other['cohorts']['paired_intact']['A_kernel_by_u_a_F']
        minus=other['cohorts']['paired_interrupted_image']['A_kernel_by_u_a_F']
        assert plus==minus
        observed=0
        for tag,kernel in plus.items():
            u,a,f=tag.split('|')
            assert f in mine['legal_fresh_given_paid'][u]
            possible_a=u if law=='parity' else str(1-int(u))
            if a!=possible_a:
                assert kernel=={'available_words':0,'bank_counts':{},'conditional_A_fresh_law':None}
                continue
            observed+=1
            assert set(kernel['conditional_A_fresh_law'])==set(mine['legal_fresh_given_paid'][a])
            assert all(Fraction(v)==Fraction(1,width) for v in kernel['conditional_A_fresh_law'].values())
        assert observed*width==mine['matched_F_A_strata']
        all_r=other['unselected_local_support']['A_full_word_to_true_bit_and_event_counts']
        for w,table in mine['full_A_by_u'].items():
            for u,mass in table.items():
                assert sum(n for key,n in all_r[w].items() if key.startswith(f'u={u},'))==mass
        rows={tuple(pair) for pair in raw['laws'][law]}
        assert len(rows)==len(raw['laws'][law])==mine['paired_launches']
        assert len({p for p,_ in rows})==len({q for _,q in rows})==len(rows)
        for p,q in rows:
            assert set(i for i in range(16) if p[i]!=q[i])=={2,3,10,11,12,13,14,15}
            assert p[1]==p[2]==p[3] and q[1]!=q[2]==q[3]
            assert p[4:7]==q[4:7] and p[7:10]==q[7:10]
            for w in (p,q):
                assert w[:4] in mine['canonical_local_law']['allowed']
                for i in range(4):
                    bank=w[4+3*i:7+3*i]
                    assert bank in mine['legal_fresh_given_paid'][w[i]]
        for u in '01':
            a=u if law=='parity' else str(1-int(u))
            f='011' if u=='0' else '100'
            for ar in [u*3,f]:
                b=str(1-int(a))
                v=str(1-int(u))
                assert (u+a*3+f+ar+u*6,u+a+b*2+f+ar+v*6) in rows
        checked[law]={'paired_complete_histories':len(rows),'cohort_count_cells':compared,
                      'matched_F_A_strata':mine['matched_F_A_strata'],'matched_numeric_witnesses_in_readable_report':4,
                      'unconditional_A_words_with_both_paid_values':len(all_r)}
    return checked


if __name__=='__main__':
    result=verify()
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)
