"""Can a splitting whole choice use a pair unavailable at birth?

Force that pair, merge its distinctions into one group and solve the remaining
linear equations. Branch only on pairs that would make a group meet a knot
twice. A branch includes the pair or forbids it, exhausting both possibilities.
"""
import argparse
import json
from pathlib import Path

from split_search import ReaderSearch, split_choices

HERE = Path(__file__).resolve().parent


def witness_with_pair(row, required, strict=False):
    pairs = list(map(tuple, row['pairs']))
    n = len(pairs)
    incidence = [sum(1 << u for u,k in enumerate(row['supports']) if d in k)
                 for d in range(1 + max(max(k) for k in row['supports']))]
    columns = [sum(((eq >> j) & 1) << k for k, eq in enumerate([row['cost'], *row['checks']]))
               for j in range(n)]
    calls = 0
    def consider(allowed, needed, groups, fixed):
        nonlocal calls
        calls += 1
        which = {d:g for g in groups for d in g}
        seen = {}
        for g in set(which.values()):
            seen[g] = sum(incidence[d] for d in g)
        def compatible(a,b):
            l, r = which[a], which[b]
            return l == r or (not (seen[l] & seen[r]) and (not strict or len(l | r) == 2))
        allowed = [j for j in allowed if compatible(*pairs[j])]
        piv = {}
        syndrome = needed
        solution = 0
        for j in allowed:
            col = columns[j]
            mask = 1 << j
            while col:
                h = col.bit_length()
                if h not in piv:
                    piv[h] = col, mask
                    break
                vec, how = piv[h]
                col ^= vec
                mask ^= how
            # Keep a short prefix solution where possible.
            while syndrome and syndrome.bit_length() in piv:
                vec, how = piv[syndrome.bit_length()]
                syndrome ^= vec
                solution ^= how
            if not syndrome:
                break
        if syndrome:
            return None
        links = {d:which[d] for d in which}
        used = []
        for j in allowed:
            if not (solution & (1<<j)):
                continue
            a,b = pairs[j]
            l,r = links[a],links[b]
            if l != r:
                if seen[l] & seen[r] or (strict and len(l | r) > 2):
                    break
                merged = l | r
                seen[merged] = seen[l] | seen[r]
                for d in merged:
                    links[d] = merged
            used.append(j)
        else:
            return tuple(fixed) + tuple(used)
        # The pair conflicting in this completion must be accepted or refused.
        a,b = pairs[j]
        l,r = which[a],which[b]
        assert l != r
        left = [i for i in allowed if i != j]
        joined = (groups - {l,r}) | {l | r}
        result = consider(left, needed ^ columns[j], joined, [*fixed,j])
        return result if result is not None else consider(left,needed,groups,fixed)
    forced = pairs.index(required)
    a,b = required
    groups = frozenset([frozenset(required), *(frozenset([d]) for d in range(len(incidence)) if d not in (a,b))])
    result = consider([j for j in range(n) if j != forced], 1 ^ columns[forced], groups,[forced])
    if result is None:
        return None,calls
    mask = sum(1 << j for j in result)
    assert not any((mask & r).bit_count()%2 for r in row['checks'])
    assert (mask & row['cost']).bit_count()%2
    parts = []
    failure = [pairs[j] for j in result]
    for a,b in failure:
        merged = {a,b}
        keep = []
        for part in parts:
            if merged & part:
                merged.update(part)
            else:
                keep.append(part)
        parts = [*keep, merged]
    assert all(len(set(k) & part)<=1 for k in row['supports'] for part in parts)
    assert not strict or all(len(p)==2 for p in parts)
    return {'failing_pairs':sorted(failure), 'readers':sorted(sorted(p) for p in parts)}, calls


def main(limit):
    data = {(r['population'],r['key']):r for r in map(json.loads,(HERE/'rebuilt_inputs.jsonl').open())}
    selected = [r['start'] for r in map(json.loads,(HERE.parent/'results.jsonl').open())
                if r['closing round'] > 1 and r['general']]
    details = []
    for key in selected[:limit]:
        full = data['whole',key]
        added = set(map(tuple,full['pairs']))-set(map(tuple,data['birth',key]['pairs']))
        item = dict(census_start=key, extra_pairs=len(added))
        for field, strict in [('new_split', False), ('new_strict_split', True)]:
            calls = 0
            for pair in sorted(added):
                result, num = witness_with_pair(full, pair, strict)
                calls += num
                if result:
                    break
            item[field] = result
            item[field + '_extra_pair'] = pair if result else None
            item[field + '_branches'] = calls
        # Independent cross-check: the birth family embeds in the whole family.
        # Count each labelled odd failure set once across all compatible readers.
        counts = {}
        for mode in ('birth', 'whole'):
            code = data[mode, key]
            search = ReaderSearch(code['supports'],code['pairs'])
            try:
                counts[mode] = split_choices(search)
            finally:
                search.free_data.cache_clear()
        for field, name in [('odd_choices_with_a_split','new_split'),('strict_odd_choices','new_strict_split')]:
            total = counts['whole'][field] - counts['birth'][field]
            assert total >= 0 and bool(total) == bool(item[name])
            item[name + '_labelled_choice_counts'] = {mode:r[field] for mode,r in counts.items()}
        details.append(item)
    summary = {'scope':'later starts with a split; stop at first extra split per start',
               'starts':len(details),'starts_with_new_choice':sum(bool(r['new_split']) for r in details),
               'starts_with_new_strict_choice':sum(bool(r['new_strict_split']) for r in details),
               'rows':details}
    for name in ['new_split','new_strict_split']:
        summary[name + '_total_labelled_extra_words'] = sum(
            r[name + '_labelled_choice_counts']['whole'] - r[name + '_labelled_choice_counts']['birth']
            for r in details)
    if limit is None:
        (HERE/'whole_extension.json').write_text(json.dumps(summary,indent=1)+'\n')
    print(summary['starts'], summary['starts_with_new_choice'], summary['starts_with_new_strict_choice'])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int)
    main(parser.parse_args().limit)
