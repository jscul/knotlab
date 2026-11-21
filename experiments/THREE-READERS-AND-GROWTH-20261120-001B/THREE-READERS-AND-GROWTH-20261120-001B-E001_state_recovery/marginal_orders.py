"""Read complete tables of at most p named distinctions from allowed words."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
OLD = 'READS-HOLDERS-SOURCES-20261120-001B'
sys.path.insert(0, str(ROOT / 'experiments' / OLD / (OLD + '-E001_irredundant')))
from controls import allowed, deletions, lawful, mask_of, width


def local_table(words, support):
    counts = Counter(sum(((w >> i) & 1) << j for j, i in enumerate(support)) for w in words)
    return tuple(counts[k] for k in range(1 << len(support)))


def table_comparison(rows, alternative, law):
    n = width(rows)
    assert width(alternative) == n
    for one in (rows, alternative):
        assert lawful(one, law) and all(deletions(one, law)[0])
    words, other = (allowed(one, law) for one in (rows, alternative))
    assert len(words) == len(other) and set(words) != set(other)
    maximum = max(map(len, (*rows, *alternative)))
    orders = {}
    for r in range(1, maximum + 1):
        marginal_differences, support_differences = [], []
        for group in combinations(range(n), r):
            u, v = local_table(words, group), local_table(other, group)
            if u != v:
                marginal_differences.append((group, u, v))
            if tuple(bool(i) for i in u) != tuple(bool(i) for i in v):
                support_differences.append((group, u, v))
        orders[str(r)] = {
            'groups': len(tuple(combinations(range(n), r))),
            'different_probability_tables': len(marginal_differences),
            'different_support_tables': len(support_differences),
            'example_probability_difference': next(iter(marginal_differences), None),
            'example_support_difference': next(iter(support_differences), None),
        }
    return {'law': law, 'presentations': [rows, alternative], 'width': n, 'states_each': len(words),
            'words_only_in_first_and_only_in_second': [min(set(words)-set(other)),min(set(other)-set(words))],
            'orders': orders}


def monochromatic_from_even_moments(words, indices):
    # For signs in {-1,1}, the monochromatic indicator is the sum of even
    # products divided by 2^(q-1). No symmetry hypothesis on weights is used.
    total = 0
    for r in range(0, len(indices) + 1, 2):
        for sub in combinations(indices, r):
            m = mask_of(sub)
            total += sum(1 if (w & m).bit_count() % 2 == 0 else -1 for w in words)
    return Fraction(total, (1 << (len(indices)-1)) * len(words))


def main():
    a = ((0,1,2,3),(0,4,5,6),(1,4,5,7),(2,3,6,7))
    swap = {1:6,6:1}
    b = tuple(tuple(swap.get(i,i) for i in row) for row in a)
    older = table_comparison(a, b, 'nae')
    assert [older['orders'][str(r)]['different_probability_tables'] == 0 for r in range(1,5)] == [True,True,True,False]
    controls = []
    for p in (4,5):
        a = (tuple(range(p)), (0,*range(p,2*p-1)))
        swap = {1:p,p:1}
        b = tuple(tuple(swap.get(i,i) for i in row) for row in a)
        for law in ('nae','parity'):
            ctl = table_comparison(a,b,law)
            for r in range(1,p):
                assert ctl['orders'][str(r)]['different_support_tables'] == 0
                if law=='parity':
                    assert ctl['orders'][str(r)]['different_probability_tables'] == 0
            assert ctl['orders'][str(p)]['different_support_tables'] > 0
            controls.append(ctl)
        words = allowed(a,'nae')
        named = list(range(2*p-1))
        tests = 0
        for q in range(3,p+1):
            for sub in combinations(named,q):
                m=mask_of(sub)
                actual = Fraction(sum((w&m) in (0,m) for w in words),len(words))
                assert actual == monochromatic_from_even_moments(words,sub)
                tests+=1
        controls[-2]['monochromatic_identity_tests']=tests
    result = {'eight_name_strict_lower_bound':older,'two_holders_with_one_meeting':controls,
              'ordering':'local words listed by their low-order chosen name first, integer codes ascending',
              'NAE_exact_orders':{'p4':{'full_probability':4,'support_only':4},'p5':{'full_probability':4,'support_only':5}},
              'parity_exact_orders':{'p4':{'full_probability':4,'support_only':4},'p5':{'full_probability':5,'support_only':5}}}
    (OUT/'marginal_orders.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
