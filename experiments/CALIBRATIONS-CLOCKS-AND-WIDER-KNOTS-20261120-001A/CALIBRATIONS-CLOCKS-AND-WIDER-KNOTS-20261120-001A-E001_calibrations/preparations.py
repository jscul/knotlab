"""Finite word pairs, sequential signed products and normalized selective continuations."""
from collections import Counter
from fractions import Fraction as F
from study_io import allowed, failed, plus, write


def pm(x):
    return -1 if x.bit_count() % 2 else 1


def affected_pairs(support, change):
    keys = sorted({min(s, s ^ change) for s in support})
    return [[s for s in (k,k ^ change) if s in support] for k in keys]


def prepared(support, change, size):
    n = len(support)
    pairs = affected_pairs(support, change)
    m = sum(len(pair) for pair in pairs if len(pair) == 2)
    # Integer numerator of twice the conditional report expectation on each input word.
    conditional = {s: int((s ^ change) in support) for s in support}
    certain = []
    for read in range(1, 1 << size):
        values = {pm(s & read) for s in support}
        if len(values) != 1:
            continue
        r, = values
        before = sum(conditional[s] * pm(s & read) for s in support)
        after = sum(conditional[s] * pm((s ^ change) & read) for s in support)
        assert before == after == r*m
        certain.append([read,r,before,after])
    assert len(support) == sum(map(len,pairs))
    return dict(pairs=pairs,common_words=m,plus=plus(n,m),dephased_fresh_plus='1' if m == n else '1/2',
                retained_label_revealed_pair_plus='1' if m == n else '1/2',restarted_pair_average=plus(n,m),
                initially_certain_signed_products_denominator=n,products=certain)


def posterior(support, change, size, supports=None, law=None):
    n = len(support)
    m = sum((s ^ change) in support for s in support)
    states = range(1 << size)
    result = {}
    for a in (1,-1):
        v = [int(s in support) + a*int((s ^ change) in support) for s in states]
        norm = sum(i*i for i in v)
        assert norm == 2*(n + a*m)
        chance = F(norm,4*n)
        if not norm:
            result[str(a)] = dict(chance='0',posterior=None)
            continue
        forbidden = [s for s in states if v[s] and s not in support]
        leak = F(sum(v[s]**2 for s in forbidden),norm)
        assert leak == (F(n-m,2*(n+m)) if a == 1 else F(1,2))
        assert all(v[s ^ change] == a*v[s] for s in states)
        correction = [0]*len(v)
        for s in states:
            correction[s if s in support else s ^ change] += v[s]*v[s]
        # A full ordinary word read followed by a conditional corrective translation destroys phases.
        assert all(not correction[s] for s in states if s not in support)
        others = []
        for other in range(1, 1 << size):
            moment = F(sum(v[s]*v[s ^ other] for s in states),norm)
            branches = []
            for b in (1,-1):
                v2 = [v[s] + b*v[s ^ other] for s in states]
                mass = sum(value**2 for value in v2)
                joint = chance * F(mass,4*norm)
                assert joint == chance*(1+b*moment)/2
                leak_joint = chance*F(sum(v2[s]**2 for s in states if s not in support),4*norm)
                branches.append([str(joint),str(leak_joint)])
            others.append([other,branches])
        # On a full pair the positive input is a plus eigenvector. On a singleton
        # the allowed-subspace effect is half the identity, for either outcome.
        clipped_weights = [0 if s not in support else (2 if a==1 else 0) if (s ^ change) in support else 1 for s in states]
        assert sum(clipped_weights)==n+a*m
        result[str(a)] = dict(chance=str(chance),posterior=dict(amplitudes=v,squared_norm=norm,
            compressed_square_root_ordinary_numerators=clipped_weights,compressed_square_root_denominator=n+a*m,
            ordinary_numerators=[i*i for i in v],illegal_words=forbidden,illegal_mass=str(leak),
            illegal_rules=None if supports is None else [[s,failed(s,supports,law)] for s in forbidden],
            uniform_on_posterior_support=len({i*i for i in v if i})==1,
            unsigned_set_preparation_up_to_overall_sign=len({i for i in v if i})==1,
            repeated_sign=a,membership_followed_by_word_read_and_correction_numerators=correction,
            correction_restores_ordinary_uniform=all(correction[s]*n==norm for s in support),
            next_change_joint_and_joint_illegal=others))
    # After both the input sign and the membership/word correction are forgotten,
    # the original ordinary distribution must be recovered on every word.
    corrected=[sum(F(r['chance'])*F(r['posterior']['membership_followed_by_word_read_and_correction_numerators'][s],
                     r['posterior']['squared_norm']) for r in result.values() if r['posterior']) for s in states]
    assert all(p==F(int(s in support),n) for s,p in enumerate(corrected))
    assert sum(F(row['chance']) for row in result.values())==1
    assert sum(F(row['chance'])*F(row['posterior']['illegal_mass']) for row in result.values() if row['posterior'])==F(n-m,2*n)
    return result


def principles():
    rows=[]; totals=Counter()
    for size in (1,2,3):
        for pattern in range(1,1 << (1 << size)):
            support={s for s in range(1 << size) if pattern>>s & 1};totals['supports']+=1
            for t in range(1,1 << size):
                row=prepared(support,t,size);rows.append([size,pattern,t,row]);totals['supports_times_changes']+=1
                totals['occupied_pairs']+=len(row['pairs']);totals['initially_certain_reads']+=len(row['products'])
                totals['full_pairs']+=sum(len(p)==2 for p in row['pairs'])
                totals['singleton_pairs']+=sum(len(p)==1 for p in row['pairs'])
                totals['restart_changes_mean']+=row['dephased_fresh_plus']!=row['restarted_pair_average']
    # Full ordinary pair, then Z, the sign of X, then Z again. Compute the ordered
    # operator word separately from two actual sign instruments with the same fair middle report.
    signed_product=0; recorded={k:Counter() for k in ('actual_flip','selective_projector','allowed_stay')}
    for w in range(2):
        z=pm(w); signed_product+=z*pm(w^1)
        for a in (1,-1):
            recorded['actual_flip'][z*a*(-z)]+=F(1,4)
            recorded['allowed_stay'][z*a*z]+=F(1,4)
            for later in (1,-1):recorded['selective_projector'][z*a*later]+=F(1,8)
    assert signed_product==-2 and all(r[-1]==r[1]==F(1,2) for r in recorded.values())
    sandwich=dict(formal_ZXZ_expectation=str(F(signed_product,2)),
                  recorded_product_chances={k:{str(sign):str(p) for sign,p in r.items()} for k,r in recorded.items()},
                  ordinary_value_changes={'actual_flip':'1','selective_projector':'1/2','allowed_stay':'0'})
    write('principles.json.gz',dict(full_pair_then_ordinary_sandwich=sandwich,columns=['width','support_bitset','change_mask','audit'],totals=totals,cases=rows))
    return totals


def instruments():
    summaries=[];counts=Counter()
    for size in (1,2,3):
        for pattern in range(1,1 << (1 << size)):
            support={s for s in range(1 << size) if pattern>>s & 1}
            for t in range(1,1 << size):
                branches=posterior(support,t,size);summaries.append([size,pattern,t,branches]);counts['inputs']+=1
                for r in branches.values():
                    p=r['posterior']
                    if p is None:counts['zero_chance']+=1;continue
                    counts['positive_branches']+=1;counts['leaks']+=F(p['illegal_mass'])>0
                    counts['unequal_nonzero_magnitudes']+=not p['uniform_on_posterior_support']
                    counts['not_an_unsigned_set']+=not p['unsigned_set_preparation_up_to_overall_sign']
    write('posteriors.json.gz',dict(columns=['width','support_bitset','change_mask','outcomes'],totals=counts,cases=summaries))
    fixtures={}
    for label,knots in [('isolated',[[0,1,2]]),('sharing',[[0,1,2],[0,3,4]]),('split',[[0,1,2],[3,4,5]])]:
        for law in ('parity','nae'):
            support=allowed(knots,law);size=1+max(map(max,knots));each={}
            for t in range(1,1 << size):
                each[str(t)]=posterior(support,t,size,knots,law)
            fixtures[label+'/'+law]=dict(supports=knots,ordinary_words=sorted(support),changes=each)
    write('posteriors_named.json.gz',fixtures)
    return counts
