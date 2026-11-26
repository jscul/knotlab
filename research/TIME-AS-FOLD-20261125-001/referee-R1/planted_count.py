"""An artificial positive control for the frozen count reading. Its birth law is supplied.

Two start knots hold {0,1,2,3} and {2,3,4}. In the first round they make,
respectively, two clock members and one second-part member. At alternate rounds the
clock's two members make a single member, which makes two again. The second part's
single member makes a successor in the first round of each period. In the second
round of the period it makes a successor only if it is joinable with the clock's
single member. Which births occur and what they receive are supplied for this
control. Each birth also receives a permanently barred distinction of its own.
The reader below gets only birth records, holdings and barrings.

The two single members take different shared distinctions. A third knot made in
the first round of the period holds both and witnesses joinability. In the
start-only control each single member takes one of the two distinctions shared
by the start, and the third knot takes neither. No growth or reading module is
imported. Only the archived final Boolean expression is separately checked below.
"""
import argparse
import ast
import hashlib
import itertools
import json
import resource
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

BASE = ((0, 1, 2, 3), (2, 3, 4))
END = 15


@dataclass(frozen=True)
class Birth:
    round: int
    parents: tuple
    inputs: tuple
    fresh: tuple
    shared_inputs: tuple

    @property
    def places(self):
        return self.inputs + self.fresh


def components(items, sets):
    parts = [{item} for item in items]
    for group in sets:
        joined = [part for part in parts if part & group]
        if joined:
            parts = [part for part in parts if part not in joined] + [set.union(*joined)]
    return tuple(sorted(tuple(sorted(part)) for part in parts))


class History:
    def __init__(self, stars):
        self.births = [Birth(0, (), tuple(star), (), ()) for star in stars]
        self.next_distinction = 1 + max(itertools.chain.from_iterable(stars))
        self.barred = {}
        self.rosters = {}
        self.end = 0

    def add(self, t, parents, inputs, fresh_count, barred=False):
        before = self.roster(t - 1)
        inputs = tuple(sorted(set(inputs)))
        shared = tuple(d for d in inputs if len(before['holders'][d]) > 1)
        fresh = tuple(range(self.next_distinction, self.next_distinction + fresh_count + 1))
        self.next_distinction += len(fresh)
        self.barred[fresh[-1]] = t
        if barred:
            self.barred.update(dict.fromkeys(fresh, t))
        self.births.append(Birth(t, tuple(parents), inputs, fresh, shared))
        return len(self.births) - 1

    def roster(self, t):
        if t in self.rosters:
            return self.rosters[t]
        holders = defaultdict(set)
        for n, birth in enumerate(self.births):
            if birth.round > t:
                break
            for d in birth.places:
                holders[d].add(n)
        usable = defaultdict(list)
        barred = Counter()
        meets = defaultdict(set)
        for d, owners in holders.items():
            if len(owners) == 1:
                n, = owners
                if self.barred.get(d, END + 1) <= t:
                    barred[n] += 1
                else:
                    usable[n].append(d)
            else:
                for n in owners:
                    meets[n].update(owners - {n})
        members = set(usable)
        witnesses = {n: members & others for n, others in meets.items() if len(members & others) >= 2}
        self.rosters[t] = dict(holders=holders, usable={n: sorted(ds) for n, ds in usable.items()},
                               barred=barred, witnesses=witnesses, parts=components(members, witnesses.values()))
        return self.rosters[t]

    def bar(self, t, knots):
        loose = self.roster(t)['usable']
        for n in knots:
            self.barred.update(dict.fromkeys(loose.get(n, ()), t))
        self.rosters.pop(t, None)

    def descendants(self, t, part):
        result = set(part)
        for n, birth in enumerate(self.births):
            if birth.round > t and result.intersection(birth.parents):
                result.add(n)
        return result


def grow(stars, variant, *, bar=None, mask=None, end=END):
    """Apply a bar to usable distinctions; apply a mask to the joinability decision."""
    h = History(stars)
    y_start = next(i for i, star in enumerate(stars) if len(star) == 4)
    x_start = 1 - y_start
    sy, sx = set(stars[y_start]), set(stars[x_start])
    y_loose, x_loose = sorted(sy - sx), sorted(sx - sy)
    if variant == 'start-only':
        y_shared, x_shared = sorted(sy & sx)
    else:
        y_shared, x_shared = y_loose[0], x_loose[0]
    y_tick = [h.add(1, (y_start,), (d,), 2) for d in y_loose]
    x_tick = h.add(1, (x_start,), x_loose, 2)
    y_single = x_single = None
    misses = 0
    for t in range(2, end + 1):
        if bar and t - 1 == bar[0]:
            h.bar(t - 1, bar[1])
        R = h.roster(t - 1)
        loose = R['usable']
        if t % 2 == 0:
            y_single = None
            if y_tick and all(n in loose for n in y_tick):
                y_single = h.add(t, y_tick, [loose[n][0] for n in y_tick] + [y_shared], 2)
                inputs = [loose[n][1] for n in y_tick]
                if variant != 'start-only':
                    inputs.extend((y_shared, x_shared))
                h.add(t, y_tick, inputs, 1, barred=True)
            x_single = None
            if x_tick in loose and variant == 'delay-two-periods' and misses == 2:
                h.bar(t, (x_tick,))
            elif x_tick in loose:
                x_single = h.add(t, (x_tick,), loose[x_tick] + [x_shared], 1)
        else:
            y_tick = []
            if y_single in loose:
                y_tick = [h.add(t, (y_single,), (d,), 2) for d in loose[y_single]]
            x_tick = None
            if x_single in loose:
                joined = any({x_single, y_single} <= members for members in R['witnesses'].values())
                if mask and t > mask[0]:
                    xs = h.descendants(mask[0], mask[1])
                    ys = h.descendants(mask[0], mask[2])
                    if x_single in xs and y_single in ys and variant != 'ignores-mask':
                        joined = False
                # The two delay controls supply finite memory of missed joins.
                one_extra = variant == 'unequal-offset' and t % 4 == 3 and misses == 0
                if not joined:
                    misses += 1
                if joined or variant in ('keeps-making', 'delay-two-periods') or one_extra:
                    x_tick = h.add(t, (x_single,), loose[x_single], 2)
                else:
                    h.bar(t, (x_single,))
        h.end = t
    return h


def same_part(H, s, P, t, Q):
    if len(P) != len(Q):
        return False
    def reading(at, order):
        roster = H.roster(at)
        members = set(order)
        counts = tuple((len(roster['usable'][n]), roster['barred'][n]) for n in order)
        sets = {frozenset(order.index(n) for n in held & members)
                for held in roster['witnesses'].values() if len(held & members) >= 2}
        return counts, {m for m in sets if not any(m < other for other in sets)}
    target = reading(s, P)
    return any(reading(t, perm) == target for perm in itertools.permutations(Q))


def first_returns(H, s, part):
    chain = [(s, part)]
    copies = given_off = 0
    while s < H.end:
        descendants = H.descendants(s, part)
        for t in range(s + 1, H.end + 1):
            parts = H.roster(t)['parts']
            hits = [q for q in parts if set(q) <= descendants and any(H.births[n].round > s for n in q)
                    and same_part(H, s, part, t, q)]
            if hits:
                copies += len(hits) - 1
                given_off += sum(bool(descendants & set(q)) for q in parts if q not in hits)
                s, part = t, min(hits)
                chain.append((s, part))
                break
        else:
            break
    return chain, copies, given_off


def second_parts(H, s, P):
    roster = H.roster(s)
    parts = roster['parts']
    sharing = [{i for i, q in enumerate(parts) if owners & set(q)} for owners in roster['holders'].values()]
    cls = next(c for c in components(range(len(parts)), sharing) if parts.index(P) in c)
    return [q for i, q in enumerate(parts) if i not in cls and any(H.births[n].round > 0 for n in q)][:8]


def trace(H, s, X):
    """Course per round as in the frozen paired test, including order-preserving renaming."""
    side = H.descendants(s, X)
    new = [n for n in sorted(side) if H.births[n].round > s]
    knots = {n: ('new', i) for i, n in enumerate(new)}
    distinctions = {d: ('fresh', i) for i, d in enumerate(sorted(d for n in new for d in H.births[n].fresh))}
    existing = H.roster(s)['holders']
    def kn(n):
        return ('old', n) if H.births[n].round <= s else knots.get(n, ('other',))
    def dn(d):
        return ('old', d) if d in existing else distinctions.get(d, ('other',))
    result = {}
    for t in range(s + 1, H.end + 1):
        roster = H.roster(t)
        made = []
        for n in new:
            b = H.births[n]
            if b.round == t and set(b.parents) <= side:
                barred = sum(H.barred.get(d) == t for d in b.fresh)
                made.append((kn(n), 'join' if len(b.parents) > 1 else 'offshoot',
                             tuple(sorted(map(kn, b.parents))), tuple(sorted(map(dn, b.inputs))),
                             tuple(sorted(map(dn, b.shared_inputs))), len(b.fresh), len(b.fresh) - barred, barred))
        members = sorted((kn(n), len(ds), roster['barred'][n]) for n, ds in roster['usable'].items() if n in side)
        sets = {frozenset(kn(n) for n in held & side)
                for held in roster['witnesses'].values() if len(held & side) >= 2}
        maximal = {m for m in sets if not any(m < other for other in sets)}
        result[t] = (made, members, maximal)
    return result


def own_and_joint(H, s, X, Y):
    xs, ys = H.descendants(s, X), H.descendants(s, Y)
    own, joint = Counter(), Counter()
    for b in H.births:
        if b.round > s and xs.intersection(b.parents):
            (joint if ys.intersection(b.parents) else own)[b.round] += 1
    return own, joint


def parity_check(H):
    """Exact local projection of the joint parity relation by eliminating other distinctions."""
    rows = [sum(1 << d for d in b.places) for b in H.births]
    def rank(vectors):
        pivots = {}
        for x in vectors:
            while x:
                i = x.bit_length()
                if i not in pivots:
                    pivots[i] = x
                    break
                x ^= pivots[i]
        return len(pivots)
    total = rank(rows)
    # Each full row supplies one constraint on its own distinctions. Exactly one
    # makes the projection precisely its full even-parity relation. Removing later
    # rows widens that projection while retaining the knot's own row.
    return [n for n, row in enumerate(rows)
            if row.bit_count() < 3 or total - rank(x & ~row for x in rows) != 1]


def made_meeting(H, tb, stop, Xs, Ys):
    for t in range(tb, stop):
        witnesses = []
        for n, group in H.roster(t)['witnesses'].items():
            if any(x != y for x in group & Xs for y in group & Ys):
                witnesses.append(n)
        if witnesses:
            return sorted({('made' if H.births[n].round > 0 else 'start') for n in witnesses})
    return []


def count(own, a, b):
    return sum(own[t] for t in range(a + 1, b + 1))


def read_controls(stars, variant, *, short=False):
    A = grow(stars, variant)
    found = []
    for s in range(A.end):
        for Y in A.roster(s)['parts']:
            if len(Y) >= 2:
                chain, copies, off = first_returns(A, s, Y)
                periods = [b[0] - a[0] for a, b in itertools.pairwise(chain[:5])]
                if len(periods) == 4 and len(set(periods)) == 1:
                    found.extend((chain, copies, off, X) for X in second_parts(A, s, Y))
        if found:
            break
    assert len(found) == 1
    chain, copies, off, X = found[0]
    assert copies == off == 0     # B' is A, Ball is B
    s, Y = chain[0]
    p = chain[1][0] - s
    Xs = A.descendants(s, X)
    ta = trace(A, s, X)
    ownA, jointA = own_and_joint(A, s, X, Y)
    periods = [count(ownA, a[0], b[0]) for a, b in itertools.pairwise(chain[:5])]
    joint_periods = [count(jointA, a[0], b[0]) for a, b in itertools.pairwise(chain[:5])]
    histories = [A, grow(stars, variant, bar=(s, X))]
    bars = []
    for r, (tb, yr) in enumerate(chain[1:4], 1):
        actual_bar = set(yr) - Xs
        B = grow(stars, variant, bar=(tb, actual_bar), end=tb + 1 if short and r == 2 else END)
        at_bar = {n for n in Xs if A.births[n].round <= tb}
        M = grow(stars, variant, mask=(tb, at_bar, yr), end=tb + 4*p)
        histories.extend((B, M))
        trB, trM = trace(B, s, X), trace(M, s, X)
        ownB, jointB = own_and_joint(B, s, X, Y)
        hi2, hi4 = min(B.end, tb + 2*p), min(B.end, tb + 4*p)
        first = next((t for t in range(tb + 1, hi4 + 1) if ta[t] != trB[t]), None)
        masked = [all(trB[t] == trM[t] for t in range(tb + 1, hi + 1)) for hi in (hi2, hi4)]
        lag = next((l for l in range(2*p + 1) if tb + l + 2*p <= min(B.end, A.end)
                    and count(ownB, tb+l, B.end) == 0
                    and all(count(ownA, tb+l+i*p, tb+l+(i+1)*p) > 0 for i in (0, 1))), None)
        provenance = made_meeting(A, tb, first, Xs, A.descendants(tb, yr)) if first else []
        bars.append(dict(tick=r, round=tb, B_end=B.end, A_end=A.end,
                         diff=first, mask_equals_B_through_2=masked[0], mask_equals_B_through_4=masked[1],
                         late_own=count(ownB, tb+2*p, B.end), lag=lag, e=count(ownB, tb, B.end),
                         total_own=count(ownB,s,B.end), joint_after=count(jointB,tb,B.end), meeting=provenance))
    constant = len(set(periods)) == 1 and periods[0] > 0
    c_core = constant and len({b['e'] for b in bars}) == 1 and all(
        b['lag'] is not None and min(b['A_end'], b['B_end']) >= b['round'] + 4*p
        and b['mask_equals_B_through_4'] for b in bars)
    ciii = 'holds'
    if any(b['diff'] is None or b['diff'] > b['round'] + 2*p
           or not b['mask_equals_B_through_2'] for b in bars):
        ciii = 'undecided'
    if any(min(b['A_end'], b['B_end']) >= b['round'] + 2*p
           and (b['diff'] is None or b['diff'] > b['round'] + 2*p) for b in bars):
        ciii = 'fails'
    bad = [parity_check(h) for h in histories]
    c_known_failure = not constant or any(b['late_own'] > 0 for b in bars)
    if c_known_failure:
        c_status = 'fails'
    elif c_core and all('made' in b['meeting'] for b in bars) and not any(bad):
        c_status = 'holds before numbering'
    else:
        # TD 4.6 has only two explicit decided failures. Missing positive
        # conditions belong here; a known start-only meeting cannot fulfil C.3.
        c_status = 'undecided under TD 4.6'
    recovered = [(b['total_own'] - b['e']) // periods[0] for b in bars] if c_core else None
    return dict(first_round=s, ticks=[v[0] for v in chain[1:]], Y_size=len(Y), X_size=len(X),
                copies=copies, given_off=off, own=periods, joint=joint_periods, bars=bars,
                C_count_and_mask=c_core, C_3_made_witness=all('made' in b['meeting'] for b in bars), C_with_provenance=c_status, C_iii=ciii, recovered_ticks=recovered,
                minimum_places=min(len(b.places) for h in histories for b in h.births),
                invalid_knot_indices=bad, knots_in_histories=[len(h.births) for h in histories])



def compare_archived_gate(examples):
    # Match the source first. Execute only the exact, checked Boolean expression
    # against the independently constructed bar records, never the author's reader.
    root = Path(__file__).resolve().parents[3]
    code_path, = root.glob('experiments/TIME-AS-FOLD-20261125-001A/*/tf_tests.py')
    source = code_path.read_text()
    function, = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'verdicts']
    assignment, = [n for n in ast.walk(function) if isinstance(n, ast.Assign)
                   and any(isinstance(v, ast.Name) and v.id == 'ok' for v in n.targets)]
    expression = assignment.value
    expected = ('len(run_bars) == 3 and all(b.get("grown_4_periods") and b.get("lag") is not None '
                'and b.get("M_equals_B_4") for b in run_bars) and len(es) == 1')
    assert ast.dump(expression) == ast.dump(ast.parse(expected, mode='eval').body)
    code = compile(ast.Expression(expression), str(code_path), 'eval')
    results = {}
    for name, row in examples.items():
        p = row['ticks'][0] - row['first_round']
        bars = [dict(grown_4_periods=min(b['A_end'], b['B_end']) >= b['round'] + 4*p,
                     lag=b['lag'], M_equals_B_4=b['diff'] is not None and b['mask_equals_B_through_4'])
                for b in row['bars']]
        values = dict(run_bars=bars, es={b['e'] for b in row['bars']})
        enters = (len(set(row['own'])) == 1 and row['own'][0] > 0
                  and all(b['late_own'] == 0 for b in row['bars']))
        matches = eval(code, {'__builtins__': {'all': all, 'len': len}}, values)
        results[name] = dict(reaches_positive_branch=enters, archived_preliminary_hold=enters and matches,
                             frozen_made_witness_each_bar=row['C_3_made_witness'])
    return dict(file=str(code_path.relative_to(root)), sha256=hashlib.sha256(source.encode()).hexdigest(),
                line=assignment.lineno, checked_expression=ast.get_source_segment(source, expression), examples=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=240)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    start = time.monotonic()
    numbers = itertools.product(itertools.permutations(range(5)), ((0, 1), (1, 0)))
    totals = Counter()
    named_starts = set()
    example = None
    for numbers_d, numbers_k in itertools.islice(numbers, args.limit):
        label = {old: new for new, old in enumerate(numbers_d)}
        stars = tuple(tuple(sorted(label[d] for d in BASE[k])) for k in numbers_k)
        named_starts.add(stars)
        row = read_controls(stars, 'made')
        assert row['C_with_provenance'] == 'holds before numbering', row
        assert row['C_iii'] == 'holds' and row['recovered_ticks'] == [1, 2, 3], row
        totals['numberings'] += 1
        totals['A_B_M_and_X_barred_histories'] += len(row['knots_in_histories'])
        totals['knots_checked_in_final_relations'] += sum(row['knots_in_histories'])
        if example is None:
            example = row
    positive_seconds = time.monotonic() - start
    variants = {k: read_controls(BASE, k) for k in ('start-only', 'keeps-making', 'ignores-mask',
                                                      'delay-two-periods', 'unequal-offset')}
    variants['short second bar'] = read_controls(BASE, 'made', short=True)
    assert variants['start-only']['C_count_and_mask'] and variants['start-only']['C_iii'] == 'holds'
    assert all(b['meeting'] == ['start'] for b in variants['start-only']['bars'])
    assert variants['start-only']['C_with_provenance'] == 'undecided under TD 4.6'
    assert variants['keeps-making']['C_with_provenance'] == variants['keeps-making']['C_iii'] == 'fails'
    assert all(variants[k]['C_with_provenance'] == 'undecided under TD 4.6'
               and variants[k]['C_iii'] == 'undecided' for k in ('ignores-mask', 'short second bar'))
    assert variants['delay-two-periods']['C_with_provenance'] == 'holds before numbering'
    assert variants['delay-two-periods']['C_iii'] == 'fails'
    assert [b['e'] for b in variants['unequal-offset']['bars']] == [1, 3, 1]
    assert variants['unequal-offset']['C_with_provenance'] == 'undecided under TD 4.6'
    assert variants['unequal-offset']['C_iii'] == 'holds'
    # A child of a mixed parent qualifies as joint by the frozen parent test.
    mixed = grow(BASE, 'made', end=1)
    Y, = [part for part in mixed.roster(1)['parts'] if len(part) == 2]
    X, = second_parts(mixed, 1, Y)
    loose = mixed.roster(1)['usable']
    mixed.add(2, X, (loose[X[0]][0],), 1)
    child = mixed.add(2, (X[0], Y[0]), (loose[X[0]][1], loose[Y[0]][0]), 1)
    mixed.add(3, (child,), mixed.roster(2)['usable'][child], 1)
    pure, joint = own_and_joint(mixed, 1, X, Y)
    assert pure == {2: 1} and joint == {2: 1, 3: 1}
    archived = compare_archived_gate(dict(positive=example, **variants))
    for label in ('positive', 'start-only', 'delay-two-periods'):
        assert archived['examples'][label]['archived_preliminary_hold']
    output = dict(archived_source_gate=archived, supplied='Two-phase birth rule and start, outside the census. Parts, first returns, own births, '
                           'barred and masked histories, meeting witnesses and parity projections are read from the records.',
                  start=BASE, settings=dict(through_round=END, workers=1, maximum_GiB=2),
                  totals=totals, distinct_named_starts=len(named_starts), positive_example=example,
                  controls_on_original_numbering=variants,
                  mixed_parent_control=dict(own_by_round=pure, joint_by_round=joint),
                  positive_seconds=round(positive_seconds, 3), elapsed_seconds=round(time.monotonic()-start, 3),
                  peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if args.output:
        args.output.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({k: output[k] for k in ('totals','distinct_named_starts','positive_seconds','elapsed_seconds','peak_RSS_KiB')}))


if __name__ == '__main__':
    main()
