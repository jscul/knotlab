"""Enumerate all locally enabled orders for the registered two sends and controls."""
from collections import Counter
from dataclasses import asdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import os
import subprocess
import sys

from receiver import explore, full_tables
from substrate import (HERE, LAWS, OUT, ROOT, allowed, build, common_word, extend, grow, local_prefix,
                       mask, read, recoding, transform)


def serialized(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n').encode()


def digest(obj):
    return sha256(serialized(obj)).hexdigest()


def canonical_check(law):
    keys = ('l', 'r', 'k')
    bad = [row for row in product((0, 1), repeat=3) if not allowed(sum(row), 3, law)]
    cnf = ';'.join(' '.join(('~' if v else '') + k for k, v in zip(keys, row)) for row in bad)
    result = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf,
                             '--loops', 'l', 'r', '--contact', 'k', '--json'],
                            env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')}, capture_output=True,
                            text=True, check=True)
    report = json.loads(result.stdout)
    assert report['binding'] and report['loss_on_erasure'] and report['coexistence'] and report['is_knot']
    return {'cnf': cnf, 'report': report}


def main():
    starts = tuple(build(x) for x in (False, True))
    originals = tuple(x[0] for x in starts)
    edited_holders = [i for i, (l, r) in enumerate(zip(*originals)) if set(l) != set(r)]
    before, after = [x[1] for x in starts]
    assert edited_holders == sorted(d.witness for d in before)
    for old, new, other in zip(before, after, reversed(before), strict=True):
        assert old.receiver == new.receiver and old.witness == new.witness
        assert old.receipt == new.receipt and old.memory == new.memory
        assert other.source == new.source and other.donor_bundle == new.donor_bundle
        assert not set(old.donor_bundle).intersection(new.donor_bundle)
    record = {'schema': 'two-sends-v1', 'design': ['689b59f94e7ca3bf981e28b324939eb50a620a9b0310b87f6d6a1c5017abd7ed',
                                                   'cb403c343a44684e47f08ff5c0ee980db9e85e72824fa5e37b98e0e187e8bb7f'],
              'originals': {}, 'laws': {}, 'all_physical_orders': []}
    summary = {'laws': {}, 'source_code_sha256': {p.name: sha256(p.read_bytes()).hexdigest()
                                               for p in (HERE / f for f in ('run.py','receiver.py','substrate.py'))}}
    for crossed, (source, devices, source_p, edits) in enumerate(starts):
        record['originals'][crossed] = {'stars': source, 'devices_in_c8_u8_order': [asdict(d) for d in devices],
                                         'source_p': source_p, 'edits': edits}
    for law in LAWS:
        law_row = record['laws'][law] = {'canonical_three': canonical_check(law), 'boards': {}, 'words': {}}
        growth = [grow(original, law) for original in originals]
        conditions = Counter()
        cells = 0
        tables = {}
        grouping = {}
        for orient in (False, True):
            word0 = common_word(originals, [d.orient(orient) for d in starts[0][1]], law)
            prefixes = []
            for crossed, ((original, devices, p, _), (stages, cuts, knot_checks)) in enumerate(zip(starts, growth)):
                canonical = tuple(d.orient(orient) for d in devices)
                stars = stages[-1]
                initial = extend(word0, cuts, law)
                assert all(allowed((initial & mask(row)).bit_count(), len(row), law) for row in stars)
                assert (initial ^ word0) & mask(sorted(set().union(*map(set, original)))) == 0
                prefix = [local_prefix(stages, initial, d) for d in canonical]
                prefixes.append(prefix)
                names_of_source = sorted(set().union(*(set(row) for row in original)))
                assert names_of_source == list(range(len(names_of_source)))
                full = full_tables(stars, canonical, law)
                assert [x['arity'] for x in full] == [12, 14]
                tables[str(crossed)] = [{k: x[k] for k in ('arity', 'possible', 'allowed')} for x in full]
                if not orient:
                    law_row['boards'][crossed] = {'cuts': cuts, 'newborn_stars': stars[len(original):],
                                                  'original_law_checks': knot_checks, 'recodings': {}}
                law_row['words'][f'{crossed}-{int(orient)}'] = {'complete_original': hex(word0),
                        'complete_after_two_cuts': hex(initial), 'whole_receiver_local_prefixes': prefix,
                        'exhaustive_relay_checks': full}
                for naming in ('original', 'reverse', 'shuffle'):
                    remapped, hmap, dmap = recoding(stars, naming)
                    local_devices = tuple(d.rename(hmap, dmap) for d in canonical)
                    relabelled = transform(initial, dmap)
                    if not orient:
                        law_row['boards'][crossed]['recodings'][naming] = {'old_holder_to_new': hmap,
                                                                          'old_distinction_to_new': dmap}
                    for conditional in ((True,) if crossed else (True, False)):
                        key = 'interrupted' if crossed else ('intact' if conditional else 'read_disabled')
                        for offer in (1, 2):
                            cell = explore(remapped, local_devices, hmap[p], offer, conditional, relabelled)(law)
                            codes = cell['memory_decoded']
                            expected = [1,1]
                            if conditional:
                                expected[crossed] = offer
                            assert codes == expected == cell['history_decoded']
                            assert cell['final_receipt_bank'] == ['001', '001']
                            comparable = {k: cell[k] for k in ('complete_orders', 'states', 'receiver_transcripts',
                                                                  'memory_decoded', 'incoming_changes', 'own_acknowledgments')}
                            group_key = (key, offer)
                            if group_key in grouping:
                                assert grouping[group_key] == comparable
                            grouping[group_key] = comparable
                            cells += 1
                            conditions[key] += cell['complete_orders']
                            record['all_physical_orders'].append({'law': law, 'condition': key, 'offer': offer,
                                  'receiver': 'c8', 'other': 'u8', 'reversed_bank': orient, 'naming': naming,
                                  'common_initial_before_name_transport': hex(initial), **cell})
            assert prefixes[0] == prefixes[1]
        summary['laws'][law] = {'growth': [[len(c['births']) for c in row[1]] for row in growth],
             'registered_cells_with_recodings': cells, 'orders_by_condition_with_recodings': dict(conditions),
             'canonical_cells': [{'condition': label,'offer': offer, **d} for (label,offer),d in grouping.items()],
             'foreground_full_tables': tables, 'identical_whole_receiver_prefixes': True,
             'canonical_knot_check': law_row['canonical_three']['report']['is_knot']}
    for cond in ('intact', 'interrupted', 'read_disabled'):
        for offer in (1,2):
            pairs = [[x for x in s['canonical_cells'] if x['condition'] == cond and x['offer'] == offer][0]
                      for s in summary['laws'].values()]
            assert pairs[0] == pairs[1]
    raw = OUT / 'sends.json.gz'
    raw.write_bytes(gzip.compress(serialized(record), compresslevel=9, mtime=0))
    summary['data_sha256'] = sha256(raw.read_bytes()).hexdigest()
    (OUT / 'summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'data_sha256': summary['data_sha256'], 'orders': {
        law: row['orders_by_condition_with_recodings'] for law,row in summary['laws'].items()}}))


if __name__ == '__main__':
    main()
