"""Replay the overlap formula, arbitrary attachments and actual funded growth."""
from fractions import Fraction
from itertools import combinations
import json
from math import comb
from random import Random

from local_parts import (OUT, count_pairs, decode, load_catalogue, measured_pairs,
                         member, nae_separator, width)
from disconnected import first_two
from model import allowed, literal_counts


def supports(p,q,k):
    return (tuple(range(p)),tuple(range(k))+tuple(range(p,p+q-k)))


def closed_form(rows):
    left,right=map(set,rows)
    n=len(left|right)
    a,b=len(left-right),len(right-left)
    z=(1<<n)-(1<<(a+1))-(1<<(b+1))+2
    signed={(i,j):2-((1<<(b+1)) if i in left and j in left else 0)
                    -((1<<(a+1)) if i in right and j in right else 0)
            for i,j in combinations(range(n),2)}
    return z,signed


def verify_recovery(rows,library):
    total,counts=count_pairs(rows,'nae')
    guessed=decode(width(rows),total,counts,library)
    assert nae_separator(rows,guessed) is None and nae_separator(guessed,rows) is None
    return {'width':width(rows),'words':total,'decoded_rows':guessed,'same_words':True,
            'membership':member(rows,library)}


def main():
    library=load_catalogue()
    out={'requested':[],'arities':[],'attachment_controls':[]}
    prescribed=[(4,4,3),(4,4,2),(4,5,3),(4,5,2)]
    rng=Random(30819681)
    for p,q,k in prescribed+[(3,4,2),(3,3,2),(5,6,4),(7,8,2),(8,12,7),(13,13,12)]:
        rows=supports(p,q,k)
        n=width(rows)
        total,signed=closed_form(rows)
        direct,counts=count_pairs(rows,'nae')
        assert direct==total and all(signed[pair]==total-2*counts[pair] for pair in signed)
        if n<=13:
            assert (total,counts)==literal_counts(allowed(rows,'nae'),n)
        g,_,_=measured_pairs(n,total,counts)
        assert g.number_of_edges()==comb(n,2)
        assert verify_recovery(rows,{})['same_words']
        perm=list(range(n));rng.shuffle(perm)
        renamed=tuple(tuple(perm[i] for i in r) for r in rows)
        assert verify_recovery(renamed,{})['same_words']
        assert verify_recovery(rows,library)['same_words']
        if (p,q,k) in prescribed:
            item={'p':p,'q':q,'overlap':k,'initial_rows':rows,'initial_width':n,
                  'NAE_total':total,'bare_reduced_correlations':sorted({str(Fraction(s,total)) for s in signed.values()})}
            for law in ('nae','parity'):
                step,reached,later=first_two(rows,law)
                z,rates=count_pairs(rows,law)
                assert step[0]==later[0]=='births'
                record={'words':z,'pair_disagreements':{f'{i},{j}':str(Fraction(v,z)) for (i,j),v in rates.items()},
                        'first_birth_count':len(step[1]),'first_births':step[1],
                        'first_reached_rows':reached,'first_reached_width':width(reached),
                        'next_count':len(later[1]),'next_births':later[1]}
                if law=='nae':
                    record['analytic_decoder']=verify_recovery(reached,{})
                    record['finite_library_decoder']=verify_recovery(reached,library)
                item[law]=record
            out['requested'].append(item)
        out['arities'].append({'p':p,'q':q,'overlap':k,'names':n,'word_count':total,
                               'strict_product_pairs':g.number_of_edges(),'renamed_recovery':True})
    # Combine a ternary part with a repeated meeting, two wider repeated
    # parts and one single-name join, erasing all root and part labels.
    base=list(supports(4,5,2))
    joined=tuple(base+[(2,7,8),(7,9,10),(8,9,10),(3,11,12,13),(11,12,13,14)])
    disjoint=joined+((15,16,17,18),(15,16,19,20))
    for rows in (joined,disjoint):
        assert member(rows,library)['analytic']
        out['attachment_controls'].append(verify_recovery(rows,{}))
    for p,q in ((3,4),(4,5),(7,9)):
        rows=supports(p,q,1);total,signed=closed_form(rows)
        c=lambda a,b: Fraction(signed[tuple(sorted((a,b)))],total)
        assert c(1,p)==c(1,0)*c(0,p)
    (OUT/'blocks_control.json').write_text(json.dumps(out,indent=2)+'\n')
    print('four seeds, ten repeated blocks, two compound stages and three single-name controls passed')


if __name__=='__main__':
    main()
