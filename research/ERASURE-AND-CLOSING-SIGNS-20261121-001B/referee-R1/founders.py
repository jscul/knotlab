"""Regenerate the named sources, check their local rules, and audit the reported units."""

import argparse
from collections import Counter, deque
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb, log, sqrt
from pathlib import Path
from random import Random
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
TICKET = HERE.parent.name
ROOT = HERE.parents[2]
DATA = ROOT / 'artifacts' / TICKET / (TICKET + '-E001_closures')
DESIGN = ROOT / 'experiments' / TICKET / DATA.name
PANELS = dict(T=256, E=128, M=128, S=32)
RING_TYPES = [(m, p) for m in product((1, 2), repeat=5)
              for p in product((2, 3), repeat=5) if sum(p) > 10 and sum(m) + sum(p) <= 17]


def digest(file):
    return sha256(file.read_bytes()).hexdigest()


def check_record():
    review = json.loads((HERE.parent.with_name(TICKET[:-1]) / 'advisor_reviews.json').read_text())
    hashes = [digest(ROOT / row['file']) for row in review['studies']['B']['rounds']]
    assert hashes == [row['sha256'] for row in review['studies']['B']['rounds']]
    contract = json.loads((DESIGN / 'contract.json').read_text())
    replay = json.loads((DATA / 'replay_receipt.json').read_text())
    assert hashes[-1] == digest(HERE.parent / 'preregistration.md') == contract['public_inputs_sha256']
    assert hashes[-1] == replay['preregistration_sha256']
    assert digest(DESIGN / 'contract.json') == replay['contract_sha256']
    for name, recorded in replay['outputs_sha256'].items():
        assert digest(DATA / name) == recorded, name
    return dict(review_digests=hashes, output_digests=replay['outputs_sha256'])


def labelled_pairs(count, seq):
    degrees = Counter(seq)
    live = set(range(count))
    pairs = []
    for entry in seq:
        leaf = min(i for i in live if degrees[i] == 0)
        pairs.append(sorted((leaf, entry)))
        live.remove(leaf)
        degrees[entry] -= 1
    pairs.append(sorted(live))
    return sorted(pairs)


def next_founder(panel, rng):
    details = {}
    if panel == 'T':
        n = rng.randint(4, 8)
        seq = [rng.randrange(n) for _ in range(n - 2)]
        pairs = labelled_pairs(n, seq)
        extras = [int(rng.random() < 1/4) for _ in range(n)]
        occurrences = Counter(x for pair in pairs for x in pair)
        loose = [max(3 - occurrences[i], 0) + extras[i] for i in range(n)]
        meetings = [[i, j, 1] for i, j in pairs]
        details.update(prufer=seq, extra_private=extras, private_counts=loose, original_meetings=meetings)
    elif panel == 'S':
        n = 4
        loose = [1] * n
        meetings = [[i, j, 1 + (rng.random() < 1/8)] for i, j in combinations(range(n), 2)]
        details['original_meetings'] = meetings
    else:
        n = 5
        index = rng.randrange(len(RING_TYPES))
        counts, loose = RING_TYPES[index]
        meetings = [(i, (i + 1) % n, amount) for i, amount in enumerate(counts)]
        details.update(ring_index_zero_based=index, indexed_ring=[list(counts), list(loose)])

    rows = [[] for _ in range(n)]
    used = 0
    for i, j, count in meetings:
        names = range(used, used + count)
        rows[i].extend(names)
        rows[j].extend(names)
        used += count
    for i, count in enumerate(loose):
        rows[i].extend(range(used, used + count))
        used += count
    order = list(range(n))
    if panel == 'S':
        rng.shuffle(order)
    if panel == 'M':
        arities = [rng.randint(3, 4) for _ in range(2)]
        for count in arities:
            rows.append(list(range(used, used + count)))
            used += count
        details['companion_arities'] = arities
    permutation = list(range(used))
    rng.shuffle(permutation)
    if panel == 'M':
        parts = [0, 1, 2]
        rng.shuffle(parts)
        order = [i for part in parts for i in (range(5), (5,), (6,))[part]]
        details['component_order_to_original'] = parts
    details.update(before_permutation=rows, source_name_permutation=permutation,
                   source_holder_order_to_original=order,
                   source_rows=[sorted(permutation[x] for x in rows[i]) for i in order])
    return details


def nae_count(rows, width):
    # Inclusion-exclusion: insisting that the selected knots are constant
    # identifies all distinctions in each of them; every remaining class is free.
    total = 0
    for size in range(len(rows) + 1):
        for chosen in combinations(rows, size):
            classes = [1 << x for x in range(width)]
            for row in chosen:
                mask = sum(1 << x for x in row)
                merged = 0
                other = []
                for group in classes:
                    if group & mask:
                        merged |= group
                    else:
                        other.append(group)
                classes = other + [merged]
            total += (-1)**size * (1 << len(classes))
    return total


def parity_rank(rows):
    sums = {0}
    for row in rows:
        mask = sum(1 << x for x in row)
        sums |= {s ^ mask for s in sums}
    return len(sums).bit_length() - 1


def accepts(bits, law):
    return sum(bits) % 2 == 0 if law == 'parity' else len(set(bits)) > 1


def projection_checks(rows, law):
    holdings = [set(r) for r in rows]
    linked = [[i for i, other in enumerate(holdings) if i != h and own & other]
              for h, own in enumerate(holdings)]
    sizes = []
    for h, chosen in enumerate(rows):
        order = []
        seen = set()
        for start in [h, *range(len(rows))]:
            if start in seen:
                continue
            queue = deque([start])
            seen.add(start)
            while queue:
                i = queue.popleft()
                order.append(i)
                for j in linked[i]:
                    if j not in seen:
                        queue.append(j)
                        seen.add(j)
        # With a held local word, a tree supplies one previously set name per
        # subsequent knot; every other founder type has a private name per knot.
        local_words = [bits for bits in product((0, 1), repeat=len(chosen)) if accepts(bits, law)]
        witness = (1,) + (0,) * (len(chosen)-1) if law == 'parity' else (0,) * len(chosen)
        for bits in [*local_words, witness]:
            values = dict(zip(chosen, bits))
            for i in order[1:]:
                row = rows[i]
                free = sorted(holdings[i] - values.keys())
                assert free, (order, i)
                values.update(dict.fromkeys(free, 0))
                if not accepts([values[x] for x in row], law):
                    values[free[0]] = 1
            assert all(accepts([values[x] for x in row], law) for j, row in enumerate(rows) if j != h)
            assert tuple(values[x] for x in chosen) == bits
        sizes.append(len(local_words))
    return sizes


def binomial_interval(k, n):
    def lower(k):
        if k == 0:
            return 0.
        lo, hi = 0., 1.
        coefficients = [(i, comb(n, i)) for i in range(k, n + 1)]
        for _ in range(62):
            p = (lo + hi)/2
            upper_tail = sum(c * p**i * (1-p)**(n-i) for i, c in coefficients)
            if upper_tail < 0.025:
                lo = p
            else:
                hi = p
        return (lo + hi)/2
    return [lower(k), 1 - lower(n-k)]


def recount(draws, panel, law, compare_summary):
    n = len(draws)
    counts = Counter(dict(draws=n))
    by_age = Counter()
    distribution = Counter()
    for d in draws:
        history = d['laws'][law]
        assert not history['censored']
        previous = 0
        old_closed = set()
        found = []
        for cut in history['cuts']:
            counts['funded_steps'] += 1
            counts['births'] += len(cut['births'])
            closed = {tuple(c['holders']) for c in cut['components'] if not c['loose']}
            assert old_closed <= closed
            new = closed - old_closed
            assert {tuple(e['component_holders']) for e in cut['new_closing_components']} == new
            counts['newly_closed'] += len(new)
            counts['steps_with_previously_closed_components'] += int(bool(old_closed))
            counts['previously_closed_component_occurrences'] += len(old_closed)
            distribution[len(old_closed)] += 1
            by_age[cut['age'], len(new)] += 1
            assert cut['preceding_closed_pieces'] == previous
            previous = len(closed)
            old_closed = closed
            whole_closed = bool(closed) and len(closed) == len(cut['components'])
            assert cut['whole_closed'] == whole_closed
            counts['wholes_closed'] += int(whole_closed)
            found.extend(e['operator_positive'] for e in cut['new_closing_components'])
        counts['draws_closing'] += int(bool(found))
        counts['draws_admitting'] += int(any(found))
        counts['positive_components_read_from_archive'] += sum(found)
    intervals = {}
    archived = compare_summary['endpoints']['all_arities'] if compare_summary is not None else None
    for label, term in [('at_least_one_closure', 'draws_closing'), ('eligible_whole_closure', 'wholes_closed'),
                        ('at_least_one_admitting_closure', 'draws_admitting')]:
        if law == 'nae' and term == 'draws_admitting':
            continue
        intervals[term] = binomial_interval(counts[term], n)
        if archived:
            check = archived[label]
            assert [counts[term], n] == [check['numerator'], check['denominator']]
            assert all(abs(a-b) < 1e-9 for a,b in zip(intervals[term], check['95pct']))
    closed = counts['newly_closed']
    positive = counts['positive_components_read_from_archive']
    if law == 'parity' and closed:
        if panel == 'M':
            spread = 3 * sqrt(n * log(40)/2)
            interval = [max(0, (positive-spread)/closed), min(1, (positive+spread)/closed)]
        else:
            interval = binomial_interval(positive, closed)
        intervals['per_component_admission'] = interval
        if archived:
            assert all(abs(a-b) < 1e-9 for a,b in zip(interval, archived['per_component_admission']['95pct']))
    elif archived:
        assert archived['per_component_admission']['95pct'] is None
    return dict(counts=counts, previous_components_per_step=distribution, intervals=intervals,
                new_components_by_step={f'{age},{new}': freq for (age, new), freq in sorted(by_age.items())})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--per-panel', type=int, help='use only the first K original draws per weighting')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    start = perf_counter()
    record = check_record()
    assert len(RING_TYPES) == 40
    with gzip.open(DATA / 'panels_histories.json.gz', 'rt') as stream:
        history = json.load(stream)
    summary = json.loads((DATA / 'panels_summary.json').read_text())
    record['panels'] = {}
    for panel, size in PANELS.items():
        draws = sorted((x for x in history if x['panel'] == panel), key=lambda d: d['draw'])
        assert [d['draw'] for d in draws] == list(range(1, size+1))
        if args.per_panel:
            draws = draws[:args.per_panel]
        seed = sha256(f'{TICKET}|{panel}|physical-draws|20261121'.encode()).hexdigest()
        rng = Random(int(seed, 16))
        local = Counter()
        for archived in draws:
            d = next_founder(panel, rng)
            assert seed == archived['seed_sha256']
            for key, value in d.items():
                assert value == archived[key], (panel, archived['draw'],key)
            rows = d['source_rows']
            width = len(d['source_name_permutation'])
            for law in ('parity', 'nae'):
                count = 1 << (width-parity_rank(rows)) if law == 'parity' else nae_count(rows, width)
                sizes = projection_checks(rows, law)
                assert archived['laws'][law]['founder'] == dict(lawful=True, essential=True,
                                                                founder_words=count, projection_sizes=sizes)
                local[law + '_local_words_extended'] += sum(sizes)
                local[law + '_essential_rules_witnessed'] += len(rows)
        record['panels'][panel] = dict(regenerated_sources=len(draws), founder_checks=local)
        for law in ('parity','nae'):
            record['panels'][panel][law] = recount(draws, panel, law, summary[panel][law] if not args.per_panel else None)
    record['elapsed_seconds'] = perf_counter() - start
    record['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    path = Path(args.output)
    if path.parent.resolve() != HERE:
        parser.error('choose an output in the referee folder')
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(sum(r['regenerated_sources'] for r in record['panels'].values()), 'named sources,',
          round(record['elapsed_seconds'], 3), 'seconds,', record['peak_rss_kib'], 'KiB peak')


if __name__ == '__main__':
    main()
