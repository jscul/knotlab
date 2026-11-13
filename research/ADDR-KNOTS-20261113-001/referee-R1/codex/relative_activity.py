#!/home/jscul/p-vs-np-contact-first/.venv/bin/python
"""Fresh R1 relative-activity audit; standard library only, no producer imports.

Read authority: codex_spec.md and its addendum, preregistration.md, and the
retained keys.jsonl.gz.  All writes are restricted to this script's directory.
Products are written left to right and act right to left.  A signed item
(q, -1) denotes the inverse of the state map q.
"""

import argparse
import collections
import gzip
import hashlib
import json
import resource
import time
from pathlib import Path


ROOT = Path('/home/jscul/p-vs-np-contact-first')
OUT = ROOT / 'research/ADDR-KNOTS-20261113-001/referee-R1/codex'
KEYS = ROOT / ('artifacts/ADDR-KNOTS-20261113-001A/'
               'ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz')
CLASSES = ('finitary', 'bounded', 'polynomial', 'exponential')
SELECTION_SALT = 'ADDR-KNOTS-R1-relative-activity-v1'


def words(s):
    return [()] + [(q,) for q in range(s)] + [
        (q, r) for q in range(s) for r in range(s)]


def build_product(sw, d0, d1, start, *, wrong_inverse=False):
    """Close signed tuples under sections, keeping both input-labelled arcs."""
    states = [tuple(start)]
    index = {states[0]: 0}
    swaps, children = [], []
    for state in states:
        root = 0
        for q, sign in state:
            root ^= sw[q]
        swaps.append(root)
        successors = []
        for first in (0, 1):
            bit = first
            section = [None] * len(state)
            for pos in range(len(state) - 1, -1, -1):
                q, sign = state[pos]
                image = bit ^ sw[q]
                branch = bit if sign == 1 or wrong_inverse else image
                section[pos] = ((d0 if branch == 0 else d1)[q], sign)
                bit = image
            section = tuple(section)
            if section not in index:
                index[section] = len(states)
                states.append(section)
            successors.append(index[section])
        children.append(tuple(successors))
    return states, swaps, children


def nonidentity_by_predecessors(swaps, children):
    """Exactly the states that can reach an output swap."""
    predecessors = [[] for _ in swaps]
    for q, pair in enumerate(children):
        for r in pair:
            predecessors[r].append(q)
    nonidentity = {q for q, bit in enumerate(swaps) if bit}
    queue = collections.deque(sorted(nonidentity))
    while queue:
        for q in predecessors[queue.popleft()]:
            if q not in nonidentity:
                nonidentity.add(q)
                queue.append(q)
    return nonidentity


def nonidentity_by_refinement(swaps, children):
    """Separate finite-behaviour refinement, without predecessor propagation."""
    agrees_with_identity = [True] * len(swaps)
    iterations = 0
    while True:
        next_agreement = [
            bit == 0 and agrees_with_identity[pair[0]]
            and agrees_with_identity[pair[1]]
            for bit, pair in zip(swaps, children)]
        iterations += 1
        if agrees_with_identity == next_agreement:
            break
        agrees_with_identity = next_agreement
    return {q for q, same in enumerate(agrees_with_identity) if not same}, iterations


def classify_graph(swaps, children, *, keep_identity=False,
                   count_parallel=True):
    """SCC criterion, with deliberately incorrect options for negative controls."""
    active = (set(range(len(swaps))) if keep_identity
              else nonidentity_by_predecessors(swaps, children))
    if not active:
        return dict(activity_class='finitary', degree=None,
                    reachable_states=len(swaps), nonidentity_states=0,
                    scc_count=0, cyclic_scc_count=0, longest_cyclic_chain=0,
                    component_histogram=[], exponential_certificate=None)
    adjacency = {q: tuple(r for r in children[q] if r in active)
                 for q in active}
    reverse = {q: [] for q in active}
    for q, targets in adjacency.items():
        for r in targets:
            reverse[r].append(q)

    # Iterative Kosaraju: neither recursion depth nor a graph package is used.
    visited, finish = set(), []
    for root in sorted(active):
        if root in visited:
            continue
        visited.add(root)
        stack = [(root, 0)]
        while stack:
            q, next_index = stack[-1]
            if next_index == len(adjacency[q]):
                finish.append(q)
                stack.pop()
                continue
            stack[-1] = (q, next_index + 1)
            r = adjacency[q][next_index]
            if r not in visited:
                visited.add(r)
                stack.append((r, 0))
    component_of, components = {}, []
    for root in reversed(finish):
        if root in component_of:
            continue
        cid = len(components)
        members, stack = [], [root]
        component_of[root] = cid
        while stack:
            q = stack.pop()
            members.append(q)
            for r in reverse[q]:
                if r not in component_of:
                    component_of[r] = cid
                    stack.append(r)
        components.append(sorted(members))

    internal = [0] * len(components)
    dag = [set() for _ in components]
    for q, targets in adjacency.items():
        cid = component_of[q]
        for r in (targets if count_parallel else set(targets)):
            rid = component_of[r]
            if cid == rid:
                internal[cid] += 1
            else:
                dag[cid].add(rid)
    cyclic = [n > 0 for n in internal]
    histogram = collections.Counter(
        (len(group), internal[cid], cyclic[cid])
        for cid, group in enumerate(components))
    branching = next((cid for cid, group in enumerate(components)
                      if cyclic[cid] and internal[cid] > len(group)), None)
    indegree = [0] * len(components)
    for targets in dag:
        for rid in targets:
            indegree[rid] += 1
    queue = collections.deque(q for q, value in enumerate(indegree) if not value)
    chain = [int(value) for value in cyclic]
    removed = 0
    while queue:
        cid = queue.popleft()
        removed += 1
        for rid in dag[cid]:
            chain[rid] = max(chain[rid], chain[cid] + int(cyclic[rid]))
            indegree[rid] -= 1
            if indegree[rid] == 0:
                queue.append(rid)
    assert removed == len(components)
    longest = max(chain, default=0)
    if branching is not None:
        cls, degree = 'exponential', None
    elif longest == 0:
        cls, degree = 'finitary', None
    elif longest == 1:
        cls, degree = 'bounded', 0
    else:
        cls, degree = 'polynomial', longest - 1
    certificate = None
    if branching is not None:
        certificate = dict(vertices=len(components[branching]),
                           internal_arcs=internal[branching],
                           state_numbers=components[branching])
    return dict(activity_class=cls, degree=degree,
                reachable_states=len(swaps), nonidentity_states=len(active),
                scc_count=len(components), cyclic_scc_count=sum(cyclic),
                longest_cyclic_chain=longest,
                component_histogram=[dict(vertices=k[0], internal_arcs=k[1],
                                          cyclic=k[2], count=v)
                                     for k, v in sorted(histogram.items())],
                exponential_certificate=certificate)


def section_counts(children, active, level=160):
    """Exact integer path counts, including multiplicity of equal successors."""
    counts = [0] * len(children)
    counts[0] = 1
    values = [int(0 in active)]
    for _ in range(level):
        next_counts = [0] * len(children)
        for count, pair in zip(counts, children):
            next_counts[pair[0]] += count
            next_counts[pair[1]] += count
        counts = next_counts
        values.append(sum(counts[q] for q in active))
    return values


def empirical_class(values):
    """The spec's finite-160-level discriminator; this is not the SCC result."""
    if values[160] == 0:
        return 'finitary'
    if values[80] > 0 and values[160] >= 1000 * values[80]:
        return 'exponential'
    if max(values[81:161]) <= max(values[1:81]):
        return 'bounded'
    return 'polynomial'


def graph_action(swaps, children, x, level):
    q, image = 0, 0
    for pos in range(level - 1, -1, -1):
        bit = (x >> pos) & 1
        image = (image << 1) | (bit ^ swaps[q])
        q = children[q][bit]
    return image


def direct_state_action(sw, d0, d1, q, x, level):
    """Raw positive-state action, independent of the product transition table."""
    if level == 0:
        return 0
    first = x >> (level - 1)
    rest = x & ((1 << (level - 1)) - 1)
    out = first ^ sw[q]
    next_state = d0[q] if first == 0 else d1[q]
    return ((out << (level - 1)) |
            direct_state_action(sw, d0, d1, next_state, rest, level - 1))


def positive_word_permutation(sw, d0, d1, word, level):
    image = list(range(1 << level))
    for q in reversed(word):
        image = [direct_state_action(sw, d0, d1, q, x, level) for x in image]
    return image


def invert_permutation(permutation):
    inverse = [None] * len(permutation)
    for source, target in enumerate(permutation):
        assert inverse[target] is None
        inverse[target] = source
    return inverse


def relative_product(source_word, target_word):
    return tuple((q, 1) for q in target_word) + tuple(
        (q, -1) for q in reversed(source_word))


def class_rank(cls, degree):
    return (CLASSES.index(cls), degree if degree is not None else -1)


def numeric_summary(values):
    selected = (0, 1, 2, 3, 4, 8, 16, 40, 80, 120, 160)
    return dict(theta={str(n): values[n] for n in selected},
                max_1_80=max(values[1:81]), max_81_160=max(values[81:161]),
                finite_160_class=empirical_class(values))


def control_suite():
    # Each listed automaton is a standalone mathematical control, not a record.
    # All descendants of state 0 in each table are reachable from that state.
    controls = [
        ('identity_with_two_parallel_self_arcs', [0], [(0, 0)],
         'finitary', None, lambda n: 0),
        ('root_swap_only', [1, 0], [(1, 1), (1, 1)],
         'finitary', None, lambda n: int(n == 0)),
        ('bounded_adding_machine', [1, 0], [(1, 0), (1, 1)],
         'bounded', 0, lambda n: 1),
        ('linear_activity', [0, 1, 0], [(0, 1), (2, 1), (2, 2)],
         'polynomial', 1, lambda n: n + 1),
        ('quadratic_activity', [0, 0, 1, 0],
         [(0, 1), (1, 2), (3, 2), (3, 3)],
         'polynomial', 2, lambda n: 1 + n + n * (n - 1) // 2),
        ('exponential_parallel_arcs', [1], [(0, 0)],
         'exponential', None, lambda n: 2 ** n),
    ]
    results = []
    for name, sw, children, expected_class, degree, count_formula in controls:
        exact = classify_graph(sw, children)
        active, iterations = nonidentity_by_refinement(sw, children)
        assert active == nonidentity_by_predecessors(sw, children)
        values = section_counts(children, active)
        assert (exact['activity_class'], exact['degree']) == (expected_class, degree)
        assert all(value == count_formula(n) for n, value in enumerate(values))
        assert empirical_class(values) == expected_class
        results.append(dict(name=name, expected_class=expected_class,
                            expected_degree=degree, exact=exact,
                            identity_refinement_iterations=iterations,
                            analytic_count_match_all_levels_0_160=True,
                            **numeric_summary(values)))

    identity_mutant = classify_graph([0], [(0, 0)], keep_identity=True)
    parallel_mutant = classify_graph([1], [(0, 0)], count_parallel=False)
    assert identity_mutant['activity_class'] == 'exponential'
    assert parallel_mutant['activity_class'] == 'bounded'

    # Raw states: identity, one root swap, adding machine.  The latter two
    # do not commute, and the adding machine's inverse branches must differ.
    sw, d0, d1 = [0, 1, 1], [0, 0, 0], [0, 0, 2]
    level = 5
    p = positive_word_permutation(sw, d0, d1, (2,), level)
    inverse = invert_permutation(p)
    _, psw, pc = build_product(sw, d0, d1, ((2, -1),))
    assert [graph_action(psw, pc, x, level) for x in range(1 << level)] == inverse
    _, badsw, badc = build_product(sw, d0, d1, ((2, -1),), wrong_inverse=True)
    wrong_inverse_count = sum(graph_action(badsw, badc, x, level) != inverse[x]
                              for x in range(1 << level))
    assert wrong_inverse_count > 0
    a, b = (2,), (1,)
    ap = positive_word_permutation(sw, d0, d1, a, level)
    bp = positive_word_permutation(sw, d0, d1, b, level)
    ai = invert_permutation(ap)
    expected_relative = [bp[ai[x]] for x in range(1 << level)]
    wrong_order = [ai[bp[x]] for x in range(1 << level)]
    wrong_order_count = sum(x != y for x, y in zip(expected_relative, wrong_order))
    assert wrong_order_count > 0
    _, rsw, rc = build_product(sw, d0, d1, relative_product(a, b))
    assert [graph_action(rsw, rc, x, level) for x in range(1 << level)] == expected_relative
    cancellation = []
    for start in (((2, 1), (2, -1)), ((2, -1), (2, 1))):
        _, csw, cc = build_product(sw, d0, d1, start)
        exact = classify_graph(csw, cc)
        values = section_counts(cc, nonidentity_by_predecessors(csw, cc))
        assert exact['nonidentity_states'] == 0 and not any(values)
        cancellation.append(dict(product=start, exact=exact, theta_all_zero=True))
    return dict(positive_activity_controls=results,
                negative_controls=dict(
                    identity_not_removed_class=identity_mutant['activity_class'],
                    duplicate_arcs_collapsed_class=parallel_mutant['activity_class'],
                    wrong_inverse_branch_action_mismatches_at_level5=wrong_inverse_count,
                    wrong_relative_order_action_mismatches_at_level5=wrong_order_count),
                cancellation_controls=cancellation, all_passed=True)


def load_metadata():
    groups = {cls: [] for cls in CLASSES}
    line_count = 0
    with gzip.open(KEYS, 'rt') as stream:
        for line in stream:
            record = json.loads(line)
            line_count += 1
            item = {name: record[name] for name in
                    ('key', 'key_id', 'pattern_hash', 'rel_class', 'rel_degree', 'letter_class',
                     'letter_degree', 'fate', 'flags')}
            item['selection_hash'] = hashlib.sha256(
                (SELECTION_SALT + ':' + item['key_id']).encode()).hexdigest()
            groups[item['rel_class']].append(item)
    return groups, line_count


def choose_samples(group, count):
    """Cover every observed s, placement count, and degree, then joint cells.

    Within each selection step use only source metadata and the fixed SHA-256
    tie break, never results of this audit.  The selected cells are deterministic.
    """
    group = sorted((item for item in group if item['fate'] != 'F0'),
                   key=lambda item: item['selection_hash'])
    chosen = []
    chosen_patterns = set()
    targets = [('s', value) for value in sorted({x['key'][0] for x in group})]
    targets += [('placements', value) for value in
                sorted({len(x['key'][4]) for x in group})]
    targets += [('degree', value) for value in
                sorted({x['rel_degree'] for x in group if x['rel_degree'] is not None})]

    def feature(item, kind):
        if kind == 's':
            return item['key'][0]
        if kind == 'placements':
            return len(item['key'][4])
        return item['rel_degree']

    for kind, value in targets:
        if len(chosen) == count:
            break
        if any(feature(item, kind) == value for item in chosen):
            continue
        candidates = [item for item in group if feature(item, kind) == value
                      and item['pattern_hash'] not in chosen_patterns]
        if not candidates:
            continue
        chosen.append(candidates[0])
        chosen_patterns.add(candidates[0]['pattern_hash'])
    cells = {(x['key'][0], len(x['key'][4]), x['rel_degree']) for x in chosen}
    for item in group:
        if len(chosen) == count:
            break
        cell = (item['key'][0], len(item['key'][4]), item['rel_degree'])
        if item['pattern_hash'] not in chosen_patterns and cell not in cells:
            chosen.append(item)
            chosen_patterns.add(item['pattern_hash'])
            cells.add(cell)
    for item in group:
        if len(chosen) == count:
            break
        if item['pattern_hash'] not in chosen_patterns:
            chosen.append(item)
            chosen_patterns.add(item['pattern_hash'])
    return chosen


def check_record(item):
    started = time.monotonic()
    s, sw, d0, d1, placements = item['key']
    ws = words(s)
    used = sorted({word_index for placement in placements for word_index in placement})
    permutations = {(n, idx): positive_word_permutation(sw, d0, d1, ws[idx], n)
                    for n in range(9) for idx in used}
    inverses = {key: invert_permutation(value) for key, value in permutations.items()}
    products, occurrences = {}, []
    action_mismatches = []
    for placement_number, placement in enumerate(placements):
        for source in placement:
            for target in placement:
                if source == target:
                    continue
                start = relative_product(ws[source], ws[target])
                if start not in products:
                    states, psw, children = build_product(sw, d0, d1, start)
                    exact = classify_graph(psw, children)
                    active, refinement_iterations = nonidentity_by_refinement(psw, children)
                    assert active == nonidentity_by_predecessors(psw, children)
                    values = section_counts(children, active)
                    enumeration_count = 0
                    for n in range(9):
                        endpoint_count = 0
                        for address in range(1 << n):
                            expected = permutations[n, target][inverses[n, source][address]]
                            got = graph_action(psw, children, address, n)
                            if got != expected:
                                action_mismatches.append(dict(
                                    placement=placement_number, source=source,
                                    target=target, level=n, address=address,
                                    expected=expected, got=got))
                            q = 0
                            for pos in range(n - 1, -1, -1):
                                q = children[q][(address >> pos) & 1]
                            endpoint_count += int(q in active)
                            enumeration_count += 1
                        assert endpoint_count == values[n]
                    products[start] = dict(
                        product=[list(pair) for pair in start], exact=exact,
                        identity_refinement_iterations=refinement_iterations,
                        identity_algorithms_agree=True,
                        action_and_section_enumeration_addresses=enumeration_count,
                        counted_sections_match_enumeration_levels_0_8=True,
                        **numeric_summary(values))
                occurrences.append(dict(placement=placement_number,
                                        source_word_index=source,
                                        target_word_index=target,
                                        product_index=list(products).index(start)))
    results = list(products.values())
    winner = max(range(len(results)), key=lambda j: class_rank(
        results[j]['exact']['activity_class'], results[j]['exact']['degree']))
    calculated = results[winner]['exact']
    exact_match = ((calculated['activity_class'], calculated['degree']) ==
                   (item['rel_class'], item['rel_degree']))

    # Secondary letter class uses every positive map appearing in a placement,
    # and is kept separate from the primary relative-product classification.
    letters = sorted({q for idx in used for q in ws[idx]})
    letter_classes = []
    for q in letters:
        _, lsw, lc = build_product(sw, d0, d1, ((q, 1),))
        letter_classes.append(classify_graph(lsw, lc))
    letter_winner = max(letter_classes, key=lambda result: class_rank(
        result['activity_class'], result['degree']))
    letter_match = ((letter_winner['activity_class'], letter_winner['degree']) ==
                    (item['letter_class'], item['letter_degree']))
    empirical_disagreements = [j for j, result in enumerate(results)
                              if result['finite_160_class'] !=
                              result['exact']['activity_class']]
    return dict(key_id=item['key_id'], key=item['key'], pattern_hash=item['pattern_hash'],
                selection_hash=item['selection_hash'],
                recorded=dict(rel_class=item['rel_class'], rel_degree=item['rel_degree'],
                              letter_class=item['letter_class'],
                              letter_degree=item['letter_degree'],
                              fate=item['fate'], flags=item['flags']),
                computed_rel_class=calculated['activity_class'],
                computed_rel_degree=calculated['degree'],
                relative_class_and_degree_match=exact_match,
                computed_letter_class=letter_winner['activity_class'],
                computed_letter_degree=letter_winner['degree'],
                letter_class_and_degree_match=letter_match,
                winning_product_index=winner, relative_occurrences=occurrences,
                products=results, action_mismatches=action_mismatches,
                empirical_160_disagreement_product_indices=empirical_disagreements,
                wall_seconds=time.monotonic() - started)


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_notes(result):
    summary = result['summary']
    coverage_lines = []
    for cls, entry in result['sampling']['coverage'].items():
        coverage_lines.append(
            f"| {cls} | {entry['sample_count']} | {entry['s']} | "
            f"{entry['placement_counts']} | {entry['recorded_degrees']} |")
    text = f'''# R1: independent relative activity audit

{summary['sampled_keys']} retained descriptions representing distinct nonempty
(pattern hash, relative class) units were checked: 20 from each recorded class
when run with the default arguments. Relative class and degree mismatches:
**{summary['relative_class_degree_mismatches']}**. Action mismatches:
**{summary['action_mismatches']}**. Secondary letter class and degree mismatches:
**{summary['letter_class_degree_mismatches']}**.

## Interface and independence

This is a code-analysis referee check of the exact relative-product activity
labels in the retained key records. This fresh standard-library script imports
no producer or recheck code. Inputs are `codex_spec.md`, its addendum,
`preregistration.md`, and the retained `keys.jsonl.gz`; the supplied proof note
and report were read for claim context. Forbidden producer and recheck paths
were not opened. No network was used. Writes for this lane are the three owned
relative activity files in this directory. The deterministic sample excludes
F0 and is stratified by recorded class; it tests labels and is not an estimate
of population accuracy.

| Recorded class | Keys | State counts s | Distinct placement counts | Degrees |
| --- | ---: | --- | --- | --- |
{chr(10).join(coverage_lines)}

Selection prioritizes available s, placement counts, and polynomial degrees
before adding unrepresented joint cells, with SHA-256 tie breaks using the
salt in the JSON, while never selecting a pattern twice within a class. The
table gives actual coverage: finitary placement counts 6, 7, and 9 are not in
the sample. Finitary placement counts 4, 6, 7, and 9 collectively have only
three distinct nonempty patterns in the retained population, so covering all
of those counts conflicts with the distinct-pattern requirement. Selection
does not use this checker's computed outcomes. The final selection replaces
an initial 80-description feasibility pass that allowed empty and repeated
patterns; only the revised 80-unit sample is used for this retained result.

## Exact procedure and controls

For each sampled key, every ordered pair in every distinct placement is checked.
The fresh product is `target * inverse(source)`, acting right to left; inverse
sections follow the original input recovered from the output letter. Reachable
signed tuples are closed under both letters. A state is removed exactly when
it cannot reach an output swap. A separate finite-behaviour refinement agrees
on every removed state. Iterative Kosaraju components retain both arcs when
the two letter successors coincide. An internally branching cyclic component
gives exponential activity; otherwise the largest number of cyclic components
on a component path gives degree one less, with no cyclic component finitary.

Known controls pass for identity, a root-only swap, an adding machine with
bounded activity, degree-one and degree-two polynomial activity, and a map
with exponential activity. Their exact section counts match analytic formulas
at every level 0 through 160. Both orders of a map times its inverse reduce
behaviourally to identity. Deliberately retaining identity components or
collapsing parallel arcs produces the wrong classifications, as expected.
Deliberately using the wrong inverse section or reversing a noncommuting
relative composition causes action mismatches. Control details are in JSON.

There are {summary['unique_products']} distinct signed product tuples within
the sampled keys, representing {summary['relative_pair_occurrences']} ordered
placement pairs. Each is compared on every address at levels 0 through 8
against raw positive-state actions composed with an explicitly inverted
finite permutation. Counted nonidentity sections are also compared with
explicit address enumeration through level 8. This amounts to
{summary['action_address_comparisons']} action/address comparisons.

## Validation gap and finite-level limitation

The specification's **V-rel** gate validates finite actions of relative maps;
it does not compare their activity classifications. **V-act-class** applies
the finite-level count discriminator to the original state maps with all maps
included, not to inverse products. Thus the named gates do not directly
validate the primary relative-class labels. This audit independently checks
that primary classification on its stated sample.

The empirical discriminator at level 160 disagrees with the exact component
class on {summary['finite160_product_class_disagreements']} sampled products.
Finite agreement of action or activity counts cannot by itself establish an
asymptotic class: product automata can have more states, longer transients, and
slower growth than the original letter automata. Here the primary result is
the full finite product-automaton component calculation; level-160 counts are
an additional diagnostic, not the source of the class or degree. Polynomial
degree is checked by the component calculation, not by the empirical rule.

## Scope, replay, and resources

This checks only the sampled keys' activity and finite actions. It supplies no
all-level survival conclusion and no native-emergence conclusion. No SAT or
summary-bootstrap computation was repeated. A label-based stratified sample
cannot detect every possible error elsewhere in the retained population.

Replay from the repository root:

```sh
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/ADDR-KNOTS-20261113-001/referee-R1/codex/relative_activity.py
```

The process used a 2 GiB address-space cap and no child processes. Measured
wall time: {result['resources']['wall_seconds']:.3f} seconds; peak resident
memory: {result['resources']['peak_rss_mib']:.3f} MiB. Input and script hashes
are retained in JSON. The stop boundary is {summary['sampled_keys']} sampled
keys, with no extrapolation to unchecked records.
'''
    (OUT / 'relative_activity_notes.md').write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--per-class', type=int, default=20)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.per_class <= 20
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    started = time.monotonic()
    controls = control_suite()
    if args.controls_only:
        print(json.dumps(controls, sort_keys=True))
        return
    groups, total = load_metadata()
    coverage, samples = {}, []
    for cls in CLASSES:
        chosen = choose_samples(groups[cls], args.per_class)
        assert len(chosen) == args.per_class
        assert len({x['pattern_hash'] for x in chosen}) == len(chosen)
        assert all(x['fate'] != 'F0' for x in chosen)
        coverage[cls] = dict(sample_count=len(chosen),
                             s=sorted({x['key'][0] for x in chosen}),
                             placement_counts=sorted({len(x['key'][4]) for x in chosen}),
                             recorded_degrees=sorted(
                                 {x['rel_degree'] for x in chosen},
                                 key=lambda x: -1 if x is None else x))
        for item in chosen:
            result = check_record(item)
            samples.append(result)
            if len(samples) % args.per_class == 0 or not result['relative_class_and_degree_match']:
                print(json.dumps(dict(progress=len(samples),
                                      key_id=result['key_id'],
                                      recorded_class=cls,
                                      computed_class=result['computed_rel_class'],
                                      computed_degree=result['computed_rel_degree'],
                                      match=result['relative_class_and_degree_match'],
                                      products=len(result['products']),
                                      wall_seconds=result['wall_seconds'])), flush=True)
    summary = dict(
        sampled_keys=len(samples),
        distinct_pattern_class_units=len({(x['pattern_hash'], x['recorded']['rel_class'])
                                          for x in samples}),
        nonempty_sample_keys=sum(x['recorded']['fate'] != 'F0' for x in samples),
        relative_class_degree_mismatches=sum(not x['relative_class_and_degree_match']
                                            for x in samples),
        letter_class_degree_mismatches=sum(not x['letter_class_and_degree_match']
                                          for x in samples),
        action_mismatches=sum(len(x['action_mismatches']) for x in samples),
        unique_products=sum(len(x['products']) for x in samples),
        relative_pair_occurrences=sum(len(x['relative_occurrences']) for x in samples),
        action_address_comparisons=sum(
            product['action_and_section_enumeration_addresses']
            for x in samples for product in x['products']),
        finite160_product_class_disagreements=sum(
            len(x['empirical_160_disagreement_product_indices']) for x in samples))
    result = dict(
        identity='ADDR-KNOTS-20261113-001 referee R1 relative-activity sample',
        branch='code_analysis', evidence_stage='independent_referee_sample',
        scientific_scope='relative activity labels, not NAE satisfiability',
        sources=dict(keys_path=str(KEYS.relative_to(ROOT)), keys_sha256=file_sha256(KEYS),
                     script_sha256=file_sha256(Path(__file__))),
        sampling=dict(salt=SELECTION_SALT, per_recorded_class=args.per_class,
                      exclude_F0=True, unique_unit=['pattern_hash', 'rel_class'],
                      retained_key_count=total,
                      population_class_counts={cls: len(rows) for cls, rows in groups.items()},
                      eligible_nonempty_pattern_class_units={
                          cls: len({row['pattern_hash'] for row in rows if row['fate'] != 'F0'})
                          for cls, rows in groups.items()},
                      coverage=coverage),
        controls=controls, samples=samples, summary=summary,
        resources=dict(wall_seconds=time.monotonic() - started,
                       peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                       address_space_cap_bytes=2 * 1024**3,
                       child_processes=0))
    (OUT / 'relative_activity.json').write_text(json.dumps(result, indent=2) + '\n')
    write_notes(result)
    print(json.dumps(dict(summary=summary, resources=result['resources']), sort_keys=True))


if __name__ == '__main__':
    main()
