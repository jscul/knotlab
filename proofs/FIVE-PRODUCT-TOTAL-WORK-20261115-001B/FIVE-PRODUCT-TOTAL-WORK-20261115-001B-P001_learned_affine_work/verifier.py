"""Replay the named proof, its ordinary expansion and a common-ancestor rewrite on raw sets."""
from collections import Counter
from functools import cache
from itertools import takewhile


WORLD = frozenset(range(512))


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def equation(mask, bit):
    ensure(type(mask) is int and 0 < mask < 512 and type(bit) is int and bit in (0, 1),
           'equation must test a displayed nonconstant parity')
    return frozenset(p for p in WORLD if (p & mask).bit_count() % 2 == bit)


@cache
def sources(charge):
    ensure(charge in (0, 1), 'invalid charge')
    rich, plain = set(), set()
    for p in WORLD:
        x0, x1, x2, x3, x4, x5, s, u, v = ((p >> i) & 1 for i in range(9))
        correct = (x0*x1, x2*(x1 ^ x3), x4*(x3 ^ x5))
        displayed = (u, v, s ^ u ^ v)
        if displayed == correct:
            rich.add(p)
        if sum(a != b for a, b in zip(correct, displayed)) % 2 == charge:
            plain.add(p)
    return {'R': frozenset(rich), 'P': frozenset(plain)}


@cache
def span(points):
    if not points:
        return frozenset()
    origin = min(points)
    basis = {}
    for p in points:
        row = p ^ origin
        while row:
            pivot = row.bit_length()-1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    space = {origin}
    for row in basis.values():
        space |= {a ^ row for a in space}
    return frozenset(space)


@cache
def fixed(raw, charge=1):
    sides = sources(charge)
    while raw:
        joint = span(raw & sides['R']) & span(raw & sides['P'])
        if joint == raw:
            return raw
        raw = joint
    return raw


def weight(counts):
    return sum(counts[k] for k in ('R', 'P', 'Q', 'L'))


def inspect(proof, charge=1, require_live=True, retained=None):
    ensure(set(proof) in ({'root'}, {'root', 'premise', 'conclusion', 'body'}), 'incomplete named declaration')
    banked = 'body' in proof
    sides = sources(charge)
    if retained is not None:
        ensure(not banked, 'filtered table replay takes an ordinary proof')
        sides = {tag: rows & retained for tag, rows in sides.items()}
    guard = equation(*proof['premise']) if banked else None
    literal = equation(*proof['conclusion']) if banked else None
    uses, ancestry = [], {}

    def run(tree, cell, counts, path, in_body):
        ensure(isinstance(tree, list) and tree and isinstance(tree[0], str), 'malformed proof node')
        tag = tree[0]
        counts[tag] += 1
        if not in_body:
            ancestry[path] = cell
        if tag in ('R', 'P'):
            after = span(cell & sides[tag])
            if len(tree) == 1:
                ensure(not after, 'evaluator accepted a state at a claimed empty leaf')
                return
            ensure(len(tree) == 2 and after, 'malformed evaluator continuation')
            counts['structural_children'] += 1
            return run(tree[1], after, counts, path + ('check',), in_body)
        if tag == 'Q':
            ensure(len(tree) == 4, 'malformed affine question')
            ones = equation(tree[1], 1)
            yes, no = cell & ones, cell - ones
            ensure(yes and no, 'query does not divide its raw affine guard')
            counts['structural_children'] += 2
            run(tree[2], no, counts, path + (0,), in_body)
            run(tree[3], yes, counts, path + (1,), in_body)
            return
        ensure(tag == 'L' and len(tree) == 2 and banked and not in_body, 'undefined or circular lemma citation')
        ensure(cell <= guard, 'raw current assumptions do not establish the named guard')
        after = cell & literal
        f, af = fixed(cell, charge), fixed(after, charge)
        if require_live:
            ensure(af and f-literal, 'lemma has no live continuation or excludes no fixed point')
        uses.append({'path': list(path), 'before': len(f), 'excluded': len(f-literal), 'after': len(af),
                     'raw': len(cell)})
        counts['structural_children'] += 1
        run(tree[1], after, counts, path + ('use',), False)

    body_counts, main_counts = Counter(), Counter()
    if banked:
        run(proof['body'], guard - literal, body_counts, (), True)
    run(proof['root'], WORLD, main_counts, (), False)
    ensure(bool(uses) == banked, 'unreachable lemma declaration')
    lca = None
    if len(uses) >= 2:
        paths = [x['path'] for x in uses]
        same = takewhile(lambda entries: len(set(entries)) == 1, zip(*paths))
        prefix = tuple(entries[0] for entries in same)
        region = ancestry[prefix]
        lca = {'path': list(prefix), 'raw': len(region), 'raw_outside_premise': len(region - guard),
               'fixed_outside_premise': len(fixed(region, charge) - guard)}
    total = body_counts + main_counts
    return {'cost': weight(total), 'counts': dict(sorted(total.items())), 'lemma_cost': weight(body_counts),
            'main_cost': weight(main_counts), 'uses': uses, 'common_ancestor': lca,
            'textual_expansion_cost': weight(main_counts) + len(uses)*weight(body_counts)}


def specialize(tree, cell, proof, charge=1):
    """Make a legal ordinary tree after restriction; prune constant questions and redundant hulls."""
    tag = tree[0]
    sides = sources(charge)
    if tag in ('R', 'P'):
        after = span(cell & sides[tag])
        if not after:
            return [tag]
        ensure(len(tree) == 2, 'strengthened terminal acquired a witness')
        child = specialize(tree[1], after, proof, charge)
        return child if after == cell else [tag, child]
    if tag == 'L':
        guard = equation(*proof['premise'])
        ensure(cell <= guard, 'cannot specialize a citation outside its guard')
        mask, bit = proof['conclusion']
        yes, no = (tree[1], proof['body']) if bit else (proof['body'], tree[1])
        return specialize(['Q', mask, no, yes], cell, proof, charge)
    ensure(tag == 'Q', 'unsupported specialization node')
    yes = cell & equation(tree[1], 1)
    no = cell - yes
    if not yes:
        return specialize(tree[2], no, proof, charge)
    if not no:
        return specialize(tree[3], yes, proof, charge)
    return ['Q', tree[1], specialize(tree[2], no, proof, charge), specialize(tree[3], yes, proof, charge)]


def expand(proof):
    return {'root': specialize(proof['root'], WORLD, proof)}


def hoist(proof):
    info = inspect(proof)
    lca = info['common_ancestor']
    ensure(lca is not None and lca['raw_outside_premise'] == 0, 'common ancestor does not establish the lemma guard')
    location = tuple(lca['path'])
    mask, bit = proof['conclusion']

    def rewrite(tree, here):
        if here == location:
            no, yes = (tree, proof['body']) if bit == 0 else (proof['body'], tree)
            return ['Q', mask, no, yes]
        if location[:len(here)] != here:
            return tree
        if tree[0] == 'Q':
            return ['Q', tree[1], rewrite(tree[2], here+(0,)), rewrite(tree[3], here+(1,))]
        ensure(tree[0] in ('P', 'R') and len(tree) == 2, 'unexpected path to common ancestor')
        return [tree[0], rewrite(tree[1], here+('check',))]
    return {'root': specialize(rewrite(proof['root'], ()), WORLD, proof)}
