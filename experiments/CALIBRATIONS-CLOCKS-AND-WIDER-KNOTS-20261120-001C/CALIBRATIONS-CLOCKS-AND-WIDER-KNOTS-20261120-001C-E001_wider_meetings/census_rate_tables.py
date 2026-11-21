"""Measure then name the exact stage rate tables with ages withheld."""

from collections import Counter, defaultdict
from functools import cache
import gzip
from itertools import combinations
import json
from math import factorial, gcd, prod

from census_exact_rates import components, rate_plan
from census_stages import OUTPUT, mask_of, reduced, width
from census_rates import PairTable
from census_weighted import canonical_weighted
from model import nae_counts


def group_width(width, basis):
    classes = defaultdict(list)
    singleton = []
    for i in range(width):
        rest = 1 << i
        for row in basis:
            high = 1 << (row.bit_length() - 1)
            if rest & high:
                rest ^= row
        classes[rest].append(i)
    groups = []
    for group in classes.values():
        if len(group) == 1:
            singleton.extend(group)
        else:
            groups.append(((len(group), 0, 1), tuple(group)))
    if singleton:
        key = (len(singleton), 1, 2) if len(singleton) > 1 else (1, 0, 0)
        groups.append((key, tuple(singleton)))
    return sorted(groups)


def parity_table(rows):
    n = width(rows)
    basis = reduced(map(mask_of, rows))
    blocks = group_width(n, basis)
    signatures = tuple(signature for signature, _ in blocks)
    order = tuple(i for _, points in blocks for i in points)
    stabilizer = prod(factorial(len(points)) for _, points in blocks)
    stabilizer *= prod(factorial(c) for c in Counter(signatures).values())
    return PairTable((n, signatures, ((1, 2),) * (len(blocks) * (len(blocks) - 1) // 2)), order, stabilizer), basis


@cache
def read_component(local, youngest):
    if len(local) <= 13:
        return (*nae_counts(local), 0, 0)
    plan = rate_plan(local, youngest)
    largest = max(op.volume for op in plan.elimination.operations)
    if largest > 3 ** 12:
        raise ValueError(('tensor ceiling', largest, plan.work))
    return (*plan.measure(), largest, plan.work)


def nae_table(rows, youngest):
    widths = []
    factors = []
    local_rates = {}
    work = 0
    largest = 0
    for group, names in components(rows):
        compact = {name: i for i, name in enumerate(names)}
        local = tuple(tuple(compact[v] for v in rows[h]) for h in group)
        new = tuple(i for i, h in enumerate(group) if h in youngest)
        total, counts, peak, cost = read_component(local, new)
        widths.append(len(names))
        factors.append(total)
        local_rates.update({(names[i], names[j]): (count, total) for (i, j), count in counts.items()})
        work += cost
        largest = max(largest, peak)
    n = width(rows)
    total = prod(factors)
    counts = {}
    for pair in combinations(range(n), 2):
        if pair in local_rates:
            count, own = local_rates[pair]
            counts[pair] = count * (total // own)
        else:
            assert total % 2 == 0
            counts[pair] = total // 2
    return total, counts, (work, largest, widths)


def fingerprints(width, total, counts):
    profiles = [Counter() for _ in range(width)]
    rates = Counter()
    for (i, j), count in counts.items():
        d = gcd(count, total)
        key = (count // d, total // d)
        rates[key] += 1
        profiles[i][key] += 1
        profiles[j][key] += 1
    multiset = tuple(sorted(rates.items()))
    rows = tuple(sorted(tuple(sorted(counts.items())) for counts in profiles))
    return width, multiset, rows


def as_tuple(value):
    return tuple(map(as_tuple, value)) if isinstance(value, list) else value


def canonical_measurements(records, law):
    work, biggest = 0, 0
    groups = defaultdict(list)
    entries = []
    for source_index, source in enumerate(records):
        for stage in source['stages']:
            rows = tuple(map(tuple, stage['rows']))
            n = stage['width']
            item = {'source_index': source_index, 'age': stage['age'], 'width': n}
            if law == 'parity':
                table, basis = parity_table(rows)
                item['state_equations'] = basis
                item['allowed_states'] = 1 << (n - len(basis))
                item.update(table_key=table.key, table_order=table.order, table_automorphisms=table.automorphisms)
            else:
                try:
                    n_states, counts, resources = nae_table(rows, tuple(stage['youngest']))
                except ValueError as fault:
                    item['unresolved_rate_table'] = fault.args[0]
                else:
                    amount, peak, widths = resources
                    work += amount
                    biggest = max(biggest, peak)
                    groups[fingerprints(n, n_states, counts)].append((item, n_states, counts))
                    item.update(allowed_states=n_states, factor_widths=widths, contraction_work=amount,
                                largest_tensor=peak,
                                disagreement_counts=tuple(counts[p] for p in combinations(range(n), 2)))
            entries.append(item)
        if (source_index + 1) % 200 == 0:
            print(law, 'counted source', source_index + 1, flush=True)
    sorted_groups = sorted(groups.items(), key=lambda entry: (entry[0][0], len(entry[1])))
    for group_id, (signature, group) in enumerate(sorted_groups, start=1):
        for item, total, counts in group:
            table = canonical_weighted(item['width'], total, counts)
            item.update(table_key=table.key, table_order=table.order, table_automorphisms=table.automorphisms,
                        rate_fingerprint_group=group_id)
        if group_id % 200 == 0:
            print(law, 'canonical fingerprint group', group_id, 'width', signature[0], flush=True)
    return {'records': entries, 'contraction_work': work, 'largest_tensor': biggest,
            'rate_fingerprint_groups': len(groups),
            'rate_fingerprint_groups_with_repeated_cases': sum(len(group) > 1 for group in groups.values())}


def main():
    with gzip.open(OUTPUT / 'census_stages.json.gz', 'rt') as source:
        raw = json.load(source)
    output = {law: canonical_measurements(records, law) for law, records in raw.items()}
    (OUTPUT / 'census_rate_tables.json.gz').write_bytes(gzip.compress(json.dumps(output).encode(), mtime=0))
    print([(law, len(r['records']), r['contraction_work'], r['largest_tensor']) for law, r in output.items()])


if __name__ == '__main__':
    main()
