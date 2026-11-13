#!/home/jscul/p-vs-np-contact-first/.venv/bin/python
"""R1 joining/hash sample, using only the lead's fresh pattern reconstruction.

The joining calculation below does not call that module's joining helper:
it constructs explicit suffix partitions from binary strings.
"""

import collections
import gzip
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path


ROOT = Path('/home/jscul/p-vs-np-contact-first')
OUT = ROOT / 'research/ADDR-KNOTS-20261113-001/referee-R1/codex'
KEYS = ROOT / ('artifacts/ADDR-KNOTS-20261113-001A/'
               'ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz')
CLASSES = ('finitary', 'bounded', 'polynomial', 'exponential')


def load_fresh_patterns():
    path = OUT / 'fresh_patterns.py'
    specification = importlib.util.spec_from_file_location('r1_fresh_patterns', path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def suffix_partitions(level, suffix_length):
    assert 1 <= suffix_length <= level
    partitions = collections.defaultdict(set)
    for address in range(1 << level):
        spelling = format(address, f'0{level}b')
        partitions[spelling[-suffix_length:]].add(address)
    return dict(partitions)


def joining_by_membership(triples, level, suffix_length):
    partitions = suffix_partitions(level, suffix_length)
    crossing = 0
    for triple in triples:
        represented = sum(any(address in members for address in triple)
                          for members in partitions.values())
        crossing += int(represented > 1)
    return crossing


def own_fingerprint(patterns):
    """Independent byte construction: signed little-endian 64-bit integers."""
    digest = hashlib.sha1()
    for level, triples in enumerate(patterns, 1):
        digest.update(level.to_bytes(8, 'little', signed=True))
        digest.update(len(triples).to_bytes(8, 'little', signed=True))
        for triple in triples:
            for address in triple:
                digest.update(address.to_bytes(8, 'little', signed=True))
    return digest.hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def controls(module):
    triples = [(0, 1, 2), (0, 2, 4), (0, 4, 8), (1, 3, 5)]
    j1 = joining_by_membership(triples, 4, 1)
    j2 = joining_by_membership(triples, 4, 2)
    assert (j1, j2) == (1, 3)
    assert joining_by_membership([], 4, 1) == 0
    suffix_join = joining_by_membership([(0, 4, 8)], 4, 1)
    prefix_partition = {format(x, '04b')[0] for x in (0, 4, 8)}
    wrong_prefix_join = int(len(prefix_partition) > 1)
    assert suffix_join == 0 and wrong_prefix_join == 1
    sample_patterns = [[], [(0, 1, 2)]]
    own_hash = own_fingerprint(sample_patterns)
    assert own_hash == module.fingerprint(sample_patterns)
    return dict(literal_pattern=triples, level=4, k1_expected=1, k1_computed=j1,
                k2_expected=3, k2_computed=j2,
                empty_join_count=0,
                wrong_prefix_cut_detected=dict(triple=[0, 4, 8],
                                               correct_suffix_join=suffix_join,
                                               wrong_prefix_join=wrong_prefix_join),
                independent_hash_bytes_match_fresh_module=True,
                all_passed=True)


def choose_keys(activity):
    selected, globally_used_patterns = [], set()
    for cls in CLASSES:
        group = sorted((sample for sample in activity['samples']
                        if sample['recorded']['rel_class'] == cls),
                       key=lambda sample: sample['selection_hash'])
        chosen = []
        for s in sorted({sample['key'][0] for sample in group}):
            candidates = [sample for sample in group if sample['key'][0] == s
                          and sample['pattern_hash'] not in globally_used_patterns]
            if candidates:
                chosen.append(candidates[0])
                globally_used_patterns.add(candidates[0]['pattern_hash'])
        # Remaining slots favour a larger placement list, with the existing
        # fixed SHA-256 order as a tie break. No reconstructed result is used.
        for sample in sorted(group, key=lambda sample:
                             (-len(sample['key'][4]), sample['selection_hash'])):
            if len(chosen) == 5:
                break
            if sample['pattern_hash'] not in globally_used_patterns:
                chosen.append(sample)
                globally_used_patterns.add(sample['pattern_hash'])
        assert len(chosen) == 5
        assert all(sample['recorded']['fate'] != 'F0' for sample in chosen)
        selected.extend(sample['key_id'] for sample in chosen)
    assert len(selected) == 20 and len(globally_used_patterns) == 20
    wanted = set(selected)
    records = {}
    with gzip.open(KEYS, 'rt') as stream:
        for line in stream:
            record = json.loads(line)
            if record['key_id'] in wanted:
                assert record['key_id'] not in records
                records[record['key_id']] = record
    assert wanted == set(records)
    return [records[key_id] for key_id in selected]


def main():
    started = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    module = load_fresh_patterns()
    control_result = controls(module)
    activity_path = OUT / 'relative_activity.json'
    activity = json.loads(activity_path.read_text())
    selected = choose_keys(activity)
    samples = []
    for record in selected:
        sample_started = time.monotonic()
        patterns = [module.pattern(record['key'], level) for level in range(1, 13)]
        assert any(patterns)
        for level, triples in enumerate(patterns, 1):
            assert triples == sorted(set(triples))
            assert all(len(set(triple)) == 3 and tuple(sorted(triple)) == tuple(triple)
                       and all(0 <= address < (1 << level) for address in triple)
                       for triple in triples)
        knots = [len(triples) for triples in patterns]
        k1 = [joining_by_membership(triples, level, 1)
              for level, triples in enumerate(patterns, 1)]
        k2 = [None if level < 2 else joining_by_membership(triples, level, 2)
              for level, triples in enumerate(patterns, 1)]
        digest = own_fingerprint(patterns)
        result = dict(
            key_id=record['key_id'], key=record['key'],
            rel_class=record['rel_class'], rel_degree=record['rel_degree'],
            fate=record['fate'],
            recorded=dict(knots_n=record['knots_n'], join_n=record['join_n'],
                          pattern_hash=record['pattern_hash']),
            reconstructed=dict(knots_n=knots, join_k1_n=k1, join_k2_n=k2,
                               pattern_hash=digest),
            counts_match=knots == record['knots_n'],
            join_k1_match=k1 == record['join_n'],
            pattern_hash_match=digest == record['pattern_hash'],
            wall_seconds=time.monotonic() - sample_started)
        samples.append(result)
        print(json.dumps(dict(progress=len(samples), rel_class=record['rel_class'],
                              key_id=record['key_id'], counts_match=result['counts_match'],
                              join_k1_match=result['join_k1_match'],
                              pattern_hash_match=result['pattern_hash_match'])), flush=True)
    summary = dict(
        sampled_keys=len(samples),
        nonempty_keys=sum(sample['fate'] != 'F0' for sample in samples),
        distinct_pattern_hashes=len({sample['recorded']['pattern_hash'] for sample in samples}),
        samples_per_class=dict(collections.Counter(sample['rel_class'] for sample in samples)),
        levels_checked=len(samples) * 12,
        knot_count_mismatches=sum(not sample['counts_match'] for sample in samples),
        k1_join_mismatches=sum(not sample['join_k1_match'] for sample in samples),
        pattern_hash_mismatches=sum(not sample['pattern_hash_match'] for sample in samples))
    result = dict(
        identity='ADDR-KNOTS-20261113-001 referee R1 joining/hash sample',
        branch='code_analysis', evidence_stage='independent_referee_sample',
        method=dict(reconstruction='lead fresh_patterns.py, fresh code from frozen spec',
                    joining='explicit suffix partitions from binary strings; membership counts',
                    fingerprint='fresh signed little-endian integer byte construction',
                    selection='five per class from revised activity sample; globally unique hashes; '
                              'cover state counts then favour large placement lists',
                    k2='reported diagnostic only; no stored comparison',
                    no_SAT_solve=True),
        sources=dict(keys_path=str(KEYS.relative_to(ROOT)), keys_sha256=sha256_file(KEYS),
                     activity_json_sha256=sha256_file(activity_path),
                     fresh_patterns_sha256=sha256_file(OUT / 'fresh_patterns.py'),
                     script_sha256=sha256_file(Path(__file__))),
        controls=control_result, samples=samples, summary=summary,
        resources=dict(wall_seconds=time.monotonic() - started,
                       peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                       address_space_cap_bytes=2 * 1024**3, child_processes=0),
        limitations=['Sample only, not a complete census audit.',
                     'Pattern reconstruction is shared with the lead; joining and hash bytes are separate.',
                     'No all-level survival or native-emergence conclusion.'])
    (OUT / 'joining_check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(summary=summary, resources=result['resources']), sort_keys=True))


if __name__ == '__main__':
    main()
