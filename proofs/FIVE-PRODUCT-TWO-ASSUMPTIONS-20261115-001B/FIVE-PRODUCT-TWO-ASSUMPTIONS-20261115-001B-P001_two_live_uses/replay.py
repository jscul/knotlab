"""Verify the exact raw premise of each citation, price operations, and record the sources of both assumptions."""
from collections import Counter
from itertools import takewhile

from programs import original


class ProofError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ProofError(message)


def raw(premises):
    cell = original.WORLD
    for row in premises:
        cell &= original.equation(*row)
    return cell


def replay(tree, cell, sides, charges, lemma=None, uses=None, ancestry=None, path=(), origins=None):
    require(isinstance(tree, list) and tree, 'malformed proof tree')
    tag = tree[0]
    charges[tag] += 1
    if ancestry is not None:
        ancestry[path] = cell
    if origins is None:
        origins = {}

    def advance(child, after, operation, branch):
        acquired = dict(origins)
        if lemma is not None:
            for mask, bit in lemma['premise']:
                eq = original.equation(mask, bit)
                if not cell <= eq and after <= eq:
                    acquired[str(mask)] = operation
        return replay(child, after, sides, charges, lemma, uses, ancestry, path+(branch,), acquired)

    if tag in ('R', 'P'):
        after = original.span(cell & sides[tag])
        if len(tree) == 1:
            require(not after, 'evaluator has surviving rows at a claimed closure')
        else:
            require(len(tree) == 2 and after, 'invalid evaluator continuation')
            charges['ordinary_child_references'] += 1
            advance(tree[1], after, 'rich check' if tag == 'R' else 'plain check', tag)
        return
    if tag == 'Q':
        require(len(tree) == 4, 'invalid question')
        yes = cell & original.equation(tree[1], 1)
        no = cell-yes
        require(no and yes, 'question must divide the current raw case')
        charges['ordinary_child_references'] += 2
        advance(tree[2], no, f'question {tree[1]}=0', 0)
        advance(tree[3], yes, f'question {tree[1]}=1', 1)
        return
    require(tag == 'L' and len(tree) == 2 and lemma is not None, 'undefined or circular citation')
    for mask, bit in lemma['premise']:
        require(cell <= original.equation(mask,bit), f'raw premise {mask}={bit} unestablished')
    lit = original.equation(*lemma['conclusion'])
    before = original.fixed(cell)
    after = original.fixed(cell & lit)
    require(before - lit and after, 'use must remove a fixed point and leave a live continuation')
    uses.append({'path':list(path), 'raw':len(cell), 'premises_acquired_by':dict(origins),
                 'fixed_before':len(before), 'fixed_excluded':len(before-lit), 'fixed_after':len(after)})
    charges['ordinary_child_references'] += 1
    advance(tree[1], cell & lit, 'citation', 'L')


def inspect(proof, charge=1):
    require(set(proof) == {'premise','conclusion','body','root'}, 'malformed declaration')
    sides = original.sources(charge)
    guard = raw(proof['premise'])
    literal = original.equation(*proof['conclusion'])
    train, main = Counter(), Counter()
    replay(proof['body'], guard-literal, sides, train)
    uses, ancestry = [], {}
    replay(proof['root'], original.WORLD, sides, main, proof, uses, ancestry)
    require(uses, 'stored deduction has no use')
    total = train+main
    common = None
    if len(uses)>1:
        paths = [u['path'] for u in uses]
        prefix = tuple(bits[0] for bits in takewhile(lambda b: len(set(b))==1, zip(*paths)))
        common = {'path':list(prefix), 'raw':len(ancestry[prefix]),
                  'established_masks':[m for m,b in proof['premise'] if ancestry[prefix]<=original.equation(m,b)]}
    return {'training':original.weight(train),'main':original.weight(main),'total':original.weight(total),
            'charges':dict(sorted(total.items())), 'uses':uses, 'common_ancestor':common}


def expanded(proof):
    # Discharge and every citation split on x0. The raw checker has already established both guard equations.
    # The literal tree is identical after erasing the redundant v premise from the declaration.
    one_premise = dict(proof, premise=proof['premise'][0])
    ordinary = original.expand(one_premise)
    return original.inspect(ordinary)['cost']
