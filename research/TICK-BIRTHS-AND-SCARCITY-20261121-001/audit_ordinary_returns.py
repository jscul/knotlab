"""Independent finite-state read of the paid donor circuits in B281.

Construct the named source from the two prospective designs. A port is a spent
witness linking two actual donors. Its two numbers are counts of shared names,
one at each donor. Following the local order reads a subset of the ordinary
continuations. Both unrestricted controls retain all nonretracing choices in
their respective menus. This checker uses no experiment or investigator code.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from itertools import combinations, pairwise
from math import inf
from pathlib import Path
import argparse
import gzip
import json

PORTS = (1,5,13,21,29)
FULL = (2,3,11,16,19,23,26,27,34,38)
NEUTRAL = (2,3,10,11,16,17,23,24,26,27,34,35,38,39)
SIGNALS = [('B','A'),('B','A','c32'),('B','A','c32','c33'),
           ('B','A','c32','c33','c34'),('B','A','c32','c33','c34','S1')]


def original(kind, position):
    i = position % 40
    if i in PORTS:
        return 'p' if kind == 'c' else 'h'
    if kind == 'c' and i in (8,31):
        return 'A'
    if kind == 'c' and i in (9,30):
        return 'B'
    return f'{kind}{i}'


def charge(kind, index, direction, remark):
    first = original(kind,index)
    other = original(kind,index + direction)
    low = 3 if kind == 'c' or remark else 5
    if first in ('p','h'):
        sequence = (low,6,7,8,9,10,11,12,13,14)
        return sequence[2*PORTS.index(index % 40) + int(direction == 1)]
    if first == 'A':
        return {'c7':3,'B':30,'c32':31}[other]
    if first == 'B':
        return {'p':3,'A':30,'c10':31}[other]
    return low if direction == 1 else 4


def source(exchanges=(), remark=False, mixed=False, broken=False):
    rows = defaultdict(dict)

    def witness(left, right, a, b):
        if right in rows[left]:
            assert rows[left][right] == (a,b)
        rows[left][right] = (a,b)
        rows[right][left] = (b,a)

    for i in range(40):
        for k, other in (('c','u'), ('u','c')):
            destination = other if i in exchanges else k
            witness(original(k,i), original(destination,i+1),
                    charge(k,i,1,remark), charge(destination,i+1,-1,remark))
    witness('c36','u36',1,2)
    receiver = ['R0','R1','R2','R3','R0']
    for left,right in pairwise(receiver):
        if not broken or left != 'R1':
            witness(left,right,1,2)
    witness('c34','S1',1,6)
    witness('S2','B',1,7)
    if broken:
        witness('S1','R2',1,2)
        witness('R1','S2',1,2)
    else:
        witness('S1','S2',1,2)
    if mixed:
        witness('R0','X',1,9)
        witness('X','Y',1,8)
        witness('Y','c0',1,10)
    else:
        witness('R0','c0',1,9)
    return rows


def circuit(rows, v):
    return sorted((u for u,(a,b) in rows[v].items() if min(a,b) >= 3),
                  key=lambda u: rows[v][u][0])


def orbit(rows, direction):
    pair = ('c0','p')
    cycle = []
    visited = set()
    while pair not in visited:
        visited.add(pair)
        cycle.append(pair[0])
        prev,now = pair
        ports = circuit(rows,now)
        assert len(ports) == len({rows[now][u][0] for u in ports})
        pair = now, ports[(ports.index(prev)+direction) % len(ports)]
    assert pair == ('c0','p')
    return cycle


def marked(rows, role):
    return any(rows[role][u][0] == 3 for u in circuit(rows,role))


def family_limit(rows, cycle):
    good = [marked(rows,u) for u in cycle]
    if all(good):
        return inf
    current = limit = 0
    for flag in 2*good:
        current = current+1 if flag else 0
        limit = max(limit,current)
    return limit


def on_cycle(word, cycle):
    repeated = cycle * (2 + len(word)//len(cycle))
    return any(repeated[start:start+len(word)] == list(word)
               for start in range(len(cycle)))


def first_receipt(history,signal):
    for index in range(len(history)-len(signal)+1):
        portion=tuple(history[index:index+len(signal)])
        if portion == signal or portion == signal[::-1]:
            assert index > 0  # the delivering input keeps the full signal
            return index+len(signal), ('sender' if portion==signal else 'reversed')
    return None


def price(rows, word):
    return 2 + sum(len(rows[v])-2 for v in word)


def aligned_menu(rows, initial, first, last, circuit_only, match_path=None):
    """All turn counts with the *first* two registrations at these exact sizes."""
    if match_path:
        start_price = price(rows, initial)
        endpoints = {n:(match_path[n-2:n], price(rows, match_path[:n]))
                     for n in (first,last)}
        wanted_prior = max(i for i,r in enumerate(match_path[:first],1) if r=='p')
    else:
        start_price = 0
    paths = {(*initial[-2:],start_price, len(initial) if match_path else 0): Counter({0:1})}
    for size in range(len(initial)+1, last+1):
        new = defaultdict(Counter)
        for (previous,end,inside,prior),counts in paths.items():
            options = circuit(rows,end) if circuit_only else rows[end]
            for choice in options:
                if choice in (previous,'R0'):
                    continue
                a = (end,choice)
                b = (previous,end,choice)
                match1 = a in (SIGNALS[0],SIGNALS[0][::-1])
                match2 = b in (SIGNALS[1],SIGNALS[1][::-1])
                if size <= first and match1 != (size == first):
                    continue
                if match2 != (size == last):
                    continue
                grant = inside + len(rows[choice]) - 2 if match_path else 0
                latest = size if match_path and size <= first and choice=='p' else prior
                if match_path:
                    # Each allowed role has at least two neighbors, so the
                    # grant is nondecreasing along every permitted history.
                    next_boundary = first if size <= first else last
                    if grant > endpoints[next_boundary][1]:
                        continue
                    if size in endpoints and ([end,choice],grant) != endpoints[size]:
                        continue
                    if size == first and latest != wanted_prior:
                        continue
                    # Once both endpoints agree, matching the child grant
                    # also matches the two deletion-parent grants.
                increment = int(first < size and choice=='p')
                for turn,number in counts.items():
                    new[(*a,grant,latest)][turn+increment] += number
        paths = new
    total = Counter()
    for counts in paths.values():
        total.update(counts)
    return dict(sorted(total.items()))


def audit(name,changes,remark,mixed,broken):
    rows = source(changes, remark, mixed, broken)
    root = ['R0','X','Y'] if mixed else ['R0']
    third = orbit(rows,1)
    for direction in (1,-1):
        cycle = orbit(rows,direction)
        history = root + cycle*3
        events = [first_receipt(history,w) for w in SIGNALS]
        if broken:
            assert 'S2' not in rows['S1']
        counts = None
        if events[0] and events[1]:
            a,b = events[0][0],events[1][0]
            places = [n for n in range(a+1,b+1) if history[n-1]=='p']
            payers = []
            mixed_payers = []
            for size in places:
                outside = history[1:size]
                payers.append(all(marked(rows,v) for v in outside)
                              and (on_cycle(outside,third) or on_cycle(outside[::-1],third)))
                mixed_payers.append(outside[:4]==['X','Y','c0','p']
                                    and all(marked(rows,v) for v in outside[2:])
                                    and on_cycle(outside[2:],third))
            grants = [[price(rows,hist) for hist in (history[:n-1],history[1:n],history[:n])]
                      for n in (a,b)]
            readings = [aligned_menu(rows,root+['c0','p'],a,b,flag) for flag in (True,False)]
            matched = [aligned_menu(rows,root+['c0','p'],a,b,flag,history) for flag in (True,False)]
            counts = (places, sum(payers), grants, readings, sum(mixed_payers), matched)
        yield {'case':name,'direction':direction,'cycle':len(cycle),'limit':family_limit(rows,third),
               'p_per_orbit':cycle.count('p'),'receipts':events,'turns_and_grants':counts}


CASES = [('fast_lasting',(),False,False,False),('slow_finite',FULL,False,False,False),
         ('fast_finite',NEUTRAL,False,False,False),('slow_lasting',FULL,True,False,False),
         ('mixed_lasting',(),False,True,False),('mixed_finite',FULL,False,True,False),
         ('break_lasting',(),False,False,True),('break_finite',FULL,False,False,True)]


def physical_source(record, expected, shortage):
    stars = record['original_stars']
    named = {i:r for r,i in record['live_roles'].items()}
    owners = defaultdict(set)
    for knot, holdings in enumerate(stars):
        for slot in holdings:
            owners[slot].add(knot)
    loose = {n:next(iter(js)) for n,js in owners.items() if len(js)==1}
    assert set(loose.values()) == set(named)
    actual = defaultdict(dict)
    for witness,holdings in enumerate(stars):
        if witness in named:
            continue
        partners = Counter()
        for slot in holdings:
            (other,) = owners[slot]-{witness}
            partners[named[other]] += 1
        (a,na),(b,nb) = partners.items()
        assert b not in actual[a]
        actual[a][b],actual[b][a] = (na,nb),(nb,na)
    assert actual == expected
    supply = Counter(loose.values())
    deficit = {named[j]:len(actual[named[j]])-supply[j] for j in named
               if len(actual[named[j]]) != supply[j]}
    assert deficit == ({'p':1} if shortage else {})

    births = 0
    for law in ('nae','parity'):
        words = {j:(r,) for j,r in named.items()}
        used = set(owners)
        available = loose
        previous = list(words)
        for depth,cut in enumerate(record['laws'][law]['cuts'],1):
            if shortage:
                assert not cut['births'] and cut['shortages']
                continue
            if depth == 1:
                expected_pairs = {frozenset([j,k]) for j,k in combinations(previous,2)
                                  if named[k] in actual[named[j]]}
            else:
                expected_pairs = {frozenset([j,k]) for j,k in combinations(previous,2)
                                  if set(words[j]) & set(words[k])}
            remaining = available.copy()
            future = {}
            previous = []
            for birth in cut['births']:
                left,right = birth['parents']
                expected_pairs.remove(frozenset((left,right)))
                inputs = birth['consumed_names']
                assert {remaining.pop(slot) for slot in inputs} == {left,right}
                if depth == 1:
                    w = named[left],named[right]
                else:
                    x,y = map(set,(words[left],words[right]))
                    w = tuple(next(iter(group)) for group in (x-y,x&y,y-x))
                fresh = set(birth['fresh_names'])
                assert len(fresh)==birth['grant']==price(actual,w)
                assert not fresh.intersection(used)
                used.update(fresh)
                child = birth['holder']
                future.update({n:child for n in fresh})
                words[child] = w
                previous.append(child)
                births += 1
            assert not remaining and not expected_pairs
            available = future
    return births


def check_archive():
    home = Path(__file__).resolve().parent
    leaf = home.name + 'A'
    path = home.parents[1] / 'artifacts' / leaf / (leaf+'-E001_tick_births') / 'clock.json.gz'
    with gzip.open(path,'rt') as src:
        cases = json.load(src)['cases']
    with gzip.open(path.with_name('physical.json.gz'),'rt') as src:
        sources = {row['case']:row for row in json.load(src)['cases']}
    comparisons = intervals = distinct_histories = births = 0
    for case in CASES:
        name,changes,remark,mixed,broken = case
        archive_key = ('prefix_'+('slow_finite' if changes else 'fast_lasting') if mixed
                       else 'sender_cut_'+('slow_finite' if changes else 'fast_lasting') if broken
                       else name)
        given = cases[archive_key]
        assert given['funded'] and given['sender_continues'] == (not broken)
        rows = source(changes,remark,mixed,broken)
        births += physical_source(sources[archive_key],rows,False)
        for actual in audit(*case):
            tip = given['forward' if actual['direction']==1 else 'reverse']
            assert orbit(rows,actual['direction']) == tip['orbit']
            ceiling = given['families']['pure_maximum']
            assert actual['limit'] == (inf if ceiling is None else ceiling)
            for n,e in enumerate(actual['receipts'],1):
                other = tip['pulses'][f'W{n}']
                assert e == (None if other is None else (other['size'],other['orientation']))
                comparisons += 1
            if actual['turns_and_grants'] is None:
                assert tip['interval'] is None
                continue
            turns,pure,grants,menus,mixed_payers,matched = actual['turns_and_grants']
            assert tip['interval']['turns'] == turns
            tick_events = [e for e in given['events'] if e['tick'] and e['size'] in turns]
            assert sum(e['payer']['current_pure'] for e in tick_events) == pure
            assert sum(e['payer']['current_mixed_prefix_third'] for e in tick_events) == mixed_payers
            for n,grant in enumerate(grants,1):
                pay = tip['pulses'][f'W{n}']['payment']
                assert grant == [pay[k] for k in ('inside_grant','outside_grant','child_grant')]
            for key,menu in zip(('circuit','whole_ordinary'),menus,strict=True):
                observed = given['unrestricted_matched_end_ranks'][key]['counts']
                archived = {int(k):v for k,v in observed.items()}
                assert menu == archived, (archive_key,key,menu,archived)
                distinct_histories += sum(menu.values())
            for key,menu in zip(('circuit','whole_ordinary'),matched,strict=True):
                observed = given['unrestricted_with_matched_initial_phase_ends_and_prices'][key]['counts']
                assert menu == {int(k):v for k,v in observed.items()}
            intervals += 1
    assert not cases['shortage_fast_lasting']['funded']
    assert cases['shortage_fast_lasting']['receiving_time'] is None
    births += physical_source(sources['shortage_fast_lasting'],source(),True)
    print(f'All nine literal original holdings and {births} individual first- and '
          'second-cut payments reproduced across the two laws.')
    print(f'{comparisons} first signal readings across 16 directed receivers; '
          f'{intervals} finite intervals, their payers, endpoint grants and both '
          f'unrestricted history counts agree ({distinct_histories} counted across menus).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    if parser.parse_args().check:
        check_archive()
        raise SystemExit
    for case in CASES:
        for row in audit(*case):
            print(row)

