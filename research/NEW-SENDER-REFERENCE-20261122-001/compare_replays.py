"""Compare the independent count-based and mark-based calculations under their common masks."""
from fractions import Fraction
from itertools import product
import json
import audit_by_count as audit
from two_private import allowed, check_relation
from pathlib import Path

HERE = Path(__file__).resolve().parent
g = HERE.name
MAIN = next((HERE.parents[1]/'artifacts'/(g+'A')).glob('*/results.json'))


def compare():
    main = json.loads(MAIN.read_text())['laws']
    independent = json.loads((HERE/'by_count.json').read_text())
    aliases={'blind':'deterministic_refusal','pair_swap':'fixed_pair_swap','random_unlike':'random_unlike',
             'cross_pair':'outsider_equalize','subset_writer':'outsider_desire','address_writer':'addressed_desire'}
    counters={'cohorts':0,'payment_probabilities':0,'decoder_scores':0,'certificate_masses':0}
    for law, groups in independent.items():
        sample=main[law]
        assert groups['all']['private_bank_mixed']==sample['full_bank_mixed_launch_mass']
        assert groups['all']['designated_pair_mixed']==sample['pair_mixed_launch_mass']
        cases=[(groups['all']['cases'][c],sample['policy_scores'][long]) for c,long in aliases.items()]
        cases+= [(groups[cohort]['cases']['ready_pair'],sample['conditional_controls'][named])
                 for cohort,named in [('all','previous_ready_01'),('H_zero_background','previous_ready_01_and_H_zero_background')]]
        for left,right in cases:
            assert left['population']==right['launch_mass']
            counters['cohorts']+=1
            for j,p in enumerate(left['paid_one']):
                assert p==right['arm_events'][str(j)]['conditional_on_cohort'].get('paid_one','0')
                counters['payment_probabilities']+=1
            for read in ('fresh_only','fresh_plus_h'):
                assert left[read]['accuracy']==right['masked_decoding'][read]['best_guess']
                counters['decoder_scores']+=1
                assert Fraction(left[read]['certifying_mass'])==Fraction(right['masked_decoding'][read]['certainty_mass'])
                counters['certificate_masses']+=1
        source=audit.previous.source_data()
        births,_,_,_,_,h,k,grow,hname,q,_,_,_=audit.previous.reconstruct(source,law)
        old=dict(zip(source['original_name_order'],map(int,source['common_original_words'][law]),strict=True))
        paid,_=audit.previous.distribution(law,births,old,(hname,q),{})
        assert set(paid)==set(product((0,1),repeat=2)) and min(paid.values())>0
        k_support={tuple(map(int,word.replace('|',''))) for word,v in sample['launch_joint_K_inherited_and_bank'].items() if Fraction(v)>0}
        g_support={inputs+fresh for inputs in paid for fresh in product((0,1),repeat=len(grow.fresh)) if allowed(law,inputs+fresh)}
        law_relations={}
        for name,observed in [('K',k_support),('G',g_support)]:
            width=len(next(iter(observed)))
            checked=check_relation(law,width)
            assert {tuple(map(int,word)) for word in checked['allowed']}==observed
            law_relations[name]={'arity':width,'allowed_joint_words':len(observed),'source':'finite ordinary','K1':checked['binding'],'K2':checked['loss_on_erasure'],'K3':checked['coexistence']}
        counters.setdefault('canonical_relations',{})[law]=law_relations
    return counters


if __name__=='__main__':
    counts=compare()
    (HERE/'numeric_verification.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(counts)
