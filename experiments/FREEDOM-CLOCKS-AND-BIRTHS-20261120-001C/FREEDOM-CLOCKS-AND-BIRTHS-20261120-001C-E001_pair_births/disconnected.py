"""Secondary exhaustive global-update census for two sources sharing no name."""
from fractions import Fraction
import gzip
from itertools import combinations, combinations_with_replacement
import json
from math import comb, factorial, prod
import sys

from census_reached import (LAWS, OUTPUT, ROOT, TableClass, canonical_pair_table,
                            count_pairs, counts_at_bound, from_archive, mask_of,
                            minima, relation_supports, width)
from census_incidence import automorphisms, incidence_family
from class_coverage import classify as has_tree_of_ternary_parts
from tree_reading import read_definition
from controls import deletions, lawful
from model import ownership, reduced, spanned

engine = 'NAE-GROWTH-20261119-001B'
sys.path.insert(0, str(ROOT / 'experiments' / engine / (engine + '-E001_nae')))
import naelib


def frozen(value):
    return tuple(map(frozen, value)) if isinstance(value, list) else value


def rows_of(stage):
    return tuple(tuple(row) for row in stage.bits_of)


def physical_parts(rows):
    parts = []
    remaining = list(map(set, rows))
    while remaining:
        selected = [remaining.pop()]
        names = selected[0].copy()
        while True:
            meeting = [r for r in remaining if names & r]
            if not meeting:
                break
            names.update(*meeting)
            selected.extend(meeting)
            remaining = [r for r in remaining if r not in meeting]
        parts.append((sorted(names), selected))
    return parts


def advance(stage, law):
    old = len(stage.bits_of)
    rule = naelib.nae_rule if law == 'nae' else naelib.parity_rule
    outcome = stage.step(rule(naelib.F.fewest), None)
    if outcome is None:
        return 'stall', ()
    if outcome['new'] == 0:
        return 'closed', ()
    assert outcome['new'] == len(stage.bits_of) - old
    births = []
    for i in range(old, len(stage.bits_of)):
        consumed = stage.bits_of[i][:stage.parents[i]]
        old_parents = tuple(next(j for j in stage.owner[x] if j != i) for x in consumed)
        births.append((old_parents, stage.fresh[i]))
    return 'births', tuple(births)


def first_two(rows, law):
    stage = naelib.S.from_junctions(rows)
    first = advance(stage, law)
    reached = rows_of(stage)
    if first[0] != 'births':
        return first, reached, (first[0], ())
    return first, reached, advance(stage, law)


def verify_factorization(rows, law, total, counts):
    parts = physical_parts(rows)
    assert len(parts) == 2
    factors = []
    covered = []
    for names, holdings in parts:
        position = {name: i for i, name in enumerate(names)}
        local = tuple(tuple(sorted(position[x] for x in r)) for r in holdings)
        local_total, local_counts = count_pairs(local, law)
        for (i, j), pair_count in local_counts.items():
            assert Fraction(pair_count, local_total) == Fraction(counts[names[i], names[j]], total)
        marginal = dict.fromkeys(names, Fraction(1, 2))
        if law == 'parity':
            basis = reduced(map(mask_of, local))
            marginal = {x: Fraction(0) if spanned(1 << i, basis) else Fraction(1, 2)
                        for i, x in enumerate(names)}
        else:
            # A closed component here cannot be the six-name ambiguous pair:
            # it is an unchanged initial component of size at most five.
            loose = any(len(v) == 1 for v in ownership(local).values())
            assert loose or len(names) < 6
            assert lawful(local, law) and all(deletions(local, law)[0])
            covered.append(has_tree_of_ternary_parts(local)['covered'])
            if covered[-1]:
                assert read_definition(local, True)['recovered_exact_relation']
        factors.append((names, local_total, marginal))
    assert prod(f[1] for f in factors) == total
    a, b = factors
    for i in a[0]:
        for j in b[0]:
            p, q = a[2][i], b[2][j]
            assert Fraction(counts[tuple(sorted((i, j)))], total) == p*(1-q) + (1-p)*q
    if covered and all(covered):
        nonzero = [(i, j) for (i, j), m in counts.items() if 2*m != total]
        observed_parts = physical_parts([(i,) for i in range(width(rows))] + nonzero)
        assert sorted(p[0] for p in observed_parts) == sorted(p[0] for p in parts)
    return {'all_parts_in_proved_class': all(covered) if covered else None,
            'factor_widths': [len(x[0]) for x in factors],
            'factor_state_counts': [x[1] for x in factors],
            'cross_pairs_checked': len(a[0])*len(b[0]),
            'forced_individual_bits': sum(p == 0 for x in factors for p in x[2].values())}


def union_case(left, right, law):
    a, x, m = left
    b, y, k = right
    n = a+b
    rows = x + tuple(tuple(i+a for i in r) for r in y)
    mult = comb(n, a)*m*k // (2 if left == right else 1)
    family = incidence_family(n, tuple(map(mask_of, rows)))
    assert mult*automorphisms(family) == factorial(n)
    assert lawful(rows, law) and all(all(v) for v in deletions(rows, law))
    first, reached, later = first_two(rows, law)
    separate = [first_two(z, law) for z in (x, y)]
    parts = [[(v[0][0], len(v[0][1])), (v[2][0], len(v[2][1]))] for v in separate]
    result = {'law':law, 'source_width':n, 'source_rows':rows,
              'source_parts':(x,y), 'labelled_source_multiplicity':mult,
              'first_status':first[0], 'separate_first_and_second':parts,
              'separate_first_sum_matches':len(first[1]) == sum(p[0][1] for p in parts)}
    if first[0] == 'births':
        size = width(reached)
        total, counts = count_pairs(reached, law)
        factor_check = verify_factorization(reached, law, total, counts)
        profile = canonical_pair_table(size, total, counts)
        result.update(first_birth_count=len(first[1]), first_births=first[1],
                      stage_width=size, stage_rows=reached, next_status=later[0],
                      next_birth_count=len(later[1]), next_births=later[1], total_words=total,
                      table_key=profile.key, table_order=profile.order,
                      table_automorphisms=profile.automorphisms,
                      pair_counts=tuple(counts[i,j] for i,j in combinations(range(size),2)),
                      separate_next_sum_matches=len(later[1]) == sum(p[1][1] for p in parts),
                      factor_check=factor_check)
    return result


def classify(records):
    tables = {}
    for source in records:
        if source['first_status'] != 'births':
            continue
        key = source['table_key']
        size = source['stage_width']
        table = tables.setdefault(key, TableClass(source['table_automorphisms'], size))
        state, state_order = table.states.identify(size, relation_supports(source['stage_rows'], source['law']))
        physical, physical_order = table.presentations.identify(size, tuple(map(mask_of, source['stage_rows'])))
        assert table.automorphisms % state_order == 0 and state_order % physical_order == 0
        source.update(state_type_within_table=state, state_automorphisms=state_order,
                      physical_type_within_table=physical, physical_automorphisms=physical_order)
        table.sources.append(source)
    return tables


def main():
    initial = from_archive()
    with gzip.open(OUTPUT/'census_cases.json.gz','rt') as data:
        original = json.load(data)
    out = {}
    for law in LAWS:
        small = [s for s in initial[law] if s[0] <= 5]
        secondary = [union_case(a,b,law) for a,b in combinations_with_replacement(small,2)
                     if a[0]+b[0] <= 8]
        primary = [{k:frozen(v) for k,v in r.items()} for r in original[law]]
        alone = counts_at_bound(8, secondary, classify(secondary))
        pooled = primary+secondary
        tables = classify(pooled)
        global_counts = {n:counts_at_bound(n, pooled, tables) for n in range(3,9)}
        limits = minima(law, tables)
        joined = [(t,k) for k,t in tables.items() if any('source_parts' in s for s in t.sources)
                  and any('source_parts' not in s for s in t.sources)]
        summary = {'disconnected_alone':alone, 'combined_through_source_width':global_counts,
                   'pooled_minima':limits, 'reached_tables_shared_across_scopes':len(joined),
                   'shared_tables_with_different_counts':sum(len({s['next_birth_count'] for s in t.sources})>1
                                                             for t,k in joined),
                   'separate_first_sum_disagreements':sum(not s['separate_first_sum_matches'] for s in secondary),
                   'separate_next_sum_disagreements':sum(not s['separate_next_sum_matches'] for s in secondary
                                                          if s['first_status']=='births'),
                   'total_cross_pairs_verified':sum(s['factor_check']['cross_pairs_checked'] for s in secondary
                                                    if s['first_status']=='births'),
                   'disconnected_reached_widths':sorted({s['stage_width'] for s in secondary if s['first_status']=='births'}),
                   'cases':secondary}
        if law == 'nae':
            summary['disconnected_covered_by_class_proof'] = sum(
                s['factor_check']['all_parts_in_proved_class'] for s in secondary if s['first_status']=='births')
        out[law] = summary
        print(law, 'component types',len(secondary),'funding',alone['source_types_by_first_outcome'],
              'pooled next count ambiguities',global_counts[8]['reached_tables_and_relations']['table_types_with_birth_count_ambiguity'],
              'minima', {k:v['minimum_order'] for k,v in limits.items()},flush=True)
    (OUTPUT/'disconnected.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    main()
