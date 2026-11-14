"""Independent finite-support closure for the first eight simple growers.

No per-call relation, semigroup or Lemma G is used. These eight systems are
unions of NAE-on-consecutive-triples chains, meeting only at main's ports.
Two omitted consecutive chain variables separate the projected constraints.
This gives a support-cardinality radius and makes the direct SAT minima global.
"""
import json
from grow_core import HERE, ROOT, READS, read, usual, limits, flatten, Solver


def separator(blank_count):
    n = blank_count + 4
    clauses = []
    for j in range(n - 2):
        clauses.extend(([j + 1, j + 2, j + 3], [-(j + 1), -(j + 2), -(j + 3)]))
    boundary = [0, 1, n - 2, n - 1]
    verdicts = []
    with Solver(name='glucose42', bootstrap_with=clauses) as sat:
        for state in range(16):
            cube = [v + 1 if (state >> j) & 1 else -(v + 1) for j, v in enumerate(boundary)]
            verdicts.append(sat.solve(assumptions=cube))
    return verdicts


def main():
    family_rows = json.loads(read(HERE / 'grow_sample.json'))[:8]
    measurements = [json.loads(line) for line in read(HERE / 'grow_results.jsonl').splitlines()]
    halo = {(r['case'], r['depth']): r for r in
            (json.loads(line) for line in read(HERE / 'grow_halo6.jsonl').splitlines())}
    assert all(separator(2))
    assert not all(separator(1)), 'one missing variable must fail to separate'
    certified = []
    shapes = []
    for index, row in enumerate(family_rows):
        recs = [r for r in measurements if r['case'] == index]
        assert len(recs) == 6
        S = recs[0]['S']
        defs = usual(json.loads(row['key']))
        G, _ = limits(defs)
        recursive_types = {i for i, d in enumerate(defs)
                           if any(c == 'SELF' for c, a in d[2])}
        other_recursive_own = {i: flatten(defs, i)[0] - defs[i][0]
                               for i in recursive_types - {S}}
        assert not any(other_recursive_own.values())
        size, body = flatten(defs, S)
        assert size == 4 and defs[S][0] == 3
        steps = [args for c, args in body if c == S]
        constraints = [(c, args) for c, args in body if c != S]
        assert len(steps) == 1 and constraints
        supports = []
        for c, args in constraints:
            if c != 'K':
                assert defs[c][0] == 3 and flatten(defs, c)[0] == 3
                assert G[c] == {1, 2, 3, 4, 5, 6}
            assert len(set(args)) == 3 and 3 in args
            supports.append(frozenset(args))
        assert len(set(supports)) == 1
        live = sorted(supports[0] - {3})
        step = steps[0]
        new_at = [j for j in live if step[j] == 3]
        old = [step[j] for j in live if step[j] != 3]
        assert len(new_at) == len(old) == 1 and old[0] == new_at[0]
        assert G[S] == set(range(8))
        if row['wrapper']:
            main_size, main_body = flatten(defs, len(defs) - 1)
            assert main_size == defs[-1][0], 'wrapper introduces no own members'
            assert all(c == 'K' or c == S for c, a in main_body)
            assert all(len({a[j] for j in live}) == 2 for c, a in main_body if c == S)
        shapes.append({'case': index, 'sha': row['key_sha256'][:12], 'S': S,
                       'live': live, 'own': 3, 'next_arguments': list(step),
                       'one_consecutive_triple_chain_per_entry': True,
                       'other_recursive_own_counts': other_recursive_own,
                       'all_other_recursive_definitions_have_no_own':
                           not any(other_recursive_own.values())})
        for rec in recs:
            assert rec['status'] == 'exact'
            B = rec['minimum']
            # A root-containing bond of size k has at most k-1 own members.
            # Before its deepest own member, two consecutive omitted members
            # would separate it from the roots, contradicting minimality.
            # Own indices start at chain index 2. Therefore deepest index
            # M <= 2(k-1)+1 = 2k-1; absolute depth <= 2k-3+wrapper.
            # Any bond smaller than B is thus wholly inside this radius:
            radius = 2 * B - 5 + int(row['wrapper'])
            assert rec['cutoff'] >= radius
            assert halo[(index, rec['depth'])]['minimum'] == B
            certified.append({'case': index, 'sha': rec['sha'], 'depth': rec['depth'],
                              'global_minimum': B, 'finite_prefix_cutoff': rec['cutoff'],
                              'all_smaller_bonds_depth_radius': radius,
                              'claimed_bound': rec['claimed_bound'],
                              'claimed_bound_holds': B >= rec['claimed_bound'],
                              'uses_lemma_G': False, 'uses_per_call_relation_code': False})
    result = {'families': 8, 'global_exact_depth_cases': len(certified),
              'two_blank_separator_16_assignments': separator(2),
              'one_blank_negative_control_16_assignments': separator(1),
              'shapes': shapes, 'rows': certified, 'inputs': READS}
    (HERE / 'grow_global_exact.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('shapes', 'rows', 'inputs')}))


if __name__ == '__main__':
    main()
