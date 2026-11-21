"""Necessary tests for the one-unary alternative at each weighting, using pair input only."""
from fractions import Fraction
from itertools import combinations, product
from math import lcm
import json
from newest_families import OUT, read_table


def dump(value):
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(type(value).__name__)


def constant(c, names):
    pairs = [c[min(i,j),max(i,j)] for i,j in combinations(names, 2)]
    if len(names) == 2:
        return (1 + sum(pairs)) / 2
    if len(names) == 3:
        return (1 + sum(pairs)) / 4
    raise ValueError('Only two- and three-name constant probabilities are determined here.')


def required_word_divisor(c, names):
    divisor = 1
    for group in combinations(names, 3):
        for complement in product((-1,1),repeat=2):
            signs = (1, *complement)
            prob = (1 + sum(signs[i]*signs[j]*c[group[i],group[j]]
                            for i,j in combinations(range(3),2))) / 8
            divisor = lcm(divisor, prob.denominator)
    return divisor


def analyze_unary(weight):
    n, rates = read_table(OUT / f'target_{weight}.json')
    table = dict(zip(combinations(range(n), 2), (1 - 2*r for r in rates), strict=True))
    signed = lambda i, j: Fraction(1) if i == j else table[min(i,j), max(i,j)]
    # The sole candidate newest unary, if chosen, would remove 29 and 30 and expose 8.
    old = sorted(set(range(n)) - {29,30})
    q = -min(signed(8,z) for z in old if z != 8)
    companions = sorted(z for z in old if z!=8 and signed(8,z)==-q)
    assert companions == [3,5,6,7]
    proper = {str(group):constant(table,group) for count in (2,3) for group in combinations(companions,count)}
    assert min(proper.values()) > q
    residual = [x for x in old if x!=8]
    rows = []
    for y in companions:
        lookup = {z:(signed(y,z)-signed(8,z))/(1+q) for z in residual if z!=y}
        minimum = min(lookup.values()); tied=sorted(z for z,v in lookup.items() if v==minimum)
        proper_mass = {str(t):constant(table,t)/(1+q) for k in (2,3) if k<len(tied) for t in combinations(tied,k)}
        whole_lower = constant(table,tied)/(1+q) if len(tied) in (2,3) else None
        rows.append(dict(loose=y,minimum=minimum,tied=tied,proper_constant_lower_bounds=proper_mass,
                         whole_constant_lower_bound=whole_lower,proper_support_impossible=min(proper_mass.values(),default=1)>-minimum,
                         whole_support_excluded=whole_lower is not None and whole_lower > -minimum))
    divisor=required_word_divisor(table,old)
    older_input_deductions=[]
    for name in companions:
        low=min(signed(name,z) for z in residual if z!=name)
        minimizers=[z for z in residual if z!=name and signed(name,z)==low]
        possible_companions=sorted(set(minimizers)-set(companions))
        older_input_deductions.append(dict(input=name,minimum=low,tied=minimizers,
                                           possible_separate_companions=possible_companions))
    if weight=='inherited':
        witness=next(item for item in rows if item['loose']==5)
        assert witness['whole_support_excluded']
        x=next(item for item in older_input_deductions if item['input']==3)
        assert len(x['possible_separate_companions']) < 2
        status='Earlier stage as a uniform source and all positive earlier ages excluded.'
        max_after_rows = None
    else:
        assert all(item['proper_support_impossible'] and not item['whole_support_excluded'] for item in rows)
        forced=[{8,*companions},*[{item['loose'],*item['tied']} for item in rows]]
        assert all(len(forced[0]&s)==1 for s in forced[1:])
        assert all(not (p&q) for p,q in combinations(forced[1:],2))
        unused=len(set(old)-set.union(*forced))
        from math import prod
        max_after_rows=(2**len(forced[0])-2)*prod(2**(len(s)-1)-1 for s in forced[1:])*2**unused
        assert max_after_rows==362880000 and max_after_rows//divisor==1
        status='Uniform competitor requires the five specified earlier holders and the unique listed word count. Existence or exclusion of that last uniform branch is unresolved.'
    return dict(weight=weight,older_width=len(old),alternative_child=[8,29,30],sole_old_loose=8,
                previous_constant_probability=q,previous_companions=companions,proper_probabilities=proper,
                earlier_uniform_word_divisor=divisor,erased_rows=rows,earlier_inherited_restriction=older_input_deductions if weight=='inherited' else None,
                upper_words_given_mandatory_rows=max_after_rows,verdict=status)


def main():
    records={measure:analyze_unary(measure) for measure in ('inherited','uniform')}
    (OUT/'sole_unary.json').write_text(json.dumps(records,indent=2,default=dump)+'\n')
    print({k:(v['previous_constant_probability'],v['earlier_uniform_word_divisor'],v['upper_words_given_mandatory_rows']) for k,v in records.items()})


if __name__=='__main__':
    main()
