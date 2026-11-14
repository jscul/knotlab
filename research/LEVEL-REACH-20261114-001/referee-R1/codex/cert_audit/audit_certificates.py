"""Independent finite-certificate audit; no study source is read or imported."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DATA = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach'
CERTS = ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex/certificates'
OLD = ROOT / 'research/ADDR-KNOTS-20261113-001/referee-R1/codex'
SEED = 'LEVEL-REACH-R1-independent-certificate-sample-v1'


def old_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, OLD / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fresh = old_module('old_referee_patterns', 'fresh_patterns.py')
rup = old_module('old_referee_rup', 'check_rup.py')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def profile(r):
    if r.get('flags', {}).get('no_join'):
        return 'no join'
    if r.get('union', {}).get('verdict') == 'dead':
        return 'dead'
    values = [x.get('L_N') for x in r.get('levels', [])]
    if 'none' in values:
        return 'no bond'
    if 'undecided' in values or len(values) != 4 or any(x is None for x in values):
        return 'undecided'
    if values == [3, 4, 5, 6]:
        return 'chained'
    if len(set(values)) == 1 and isinstance(values[0], int):
        return 'direct'
    return 'other'


def claims(level):
    for context in ('anywhere', 'target_restricted'):
        if context in level:
            yield context, level[context]
    for row in level.get('per_target', []):
        yield f'per_target:{row["b"]}', row


def certificate_reference(claim):
    return claim.get('certificate', {}).get('refutation')


def make_inventory_and_selection():
    candidates = defaultdict(list)
    outcomes = Counter()
    count = Counter()
    missing = []
    bad = []
    references = {}
    over_ten = []
    raw = hashlib.sha256()
    seen = set()
    targeted = []
    with gzip.open(DATA / 'results.jsonl.gz', 'rb') as f:
        for line in f:
            raw.update(line)
            row = json.loads(line)
            count['records'] += 1
            if row['case'] in seen:
                bad.append({'case': row['case'], 'issue': 'duplicate key record'})
            seen.add(row['case'])
            if row.get('status') != 'ok':
                bad.append({'case': row['case'], 'issue': 'non-ok record'})
                continue
            r = row['result']
            group = profile(r)
            outcomes[group] += 1
            for level in r.get('levels', []):
                s = level['s']
                a = level.get('anywhere', {})
                if ((row['case'].startswith('58480a08') and s in (1, 2, 3)) or
                        (row['case'].startswith('e1fc9d92') and s == 1)):
                    targeted.append({'case': row['case'], 's': s, 'L': a.get('L'),
                                     'stratum': group, 'selection_reason': 'lead-requested below-target support'})
                if isinstance(a.get('L'), int):
                    candidates[group].append({'case': row['case'], 's': s, 'L': a['L'],
                                              'rank': digest(f'{SEED}/{row["case"]}/{s}'.encode())})
                for context, claim in claims(level):
                    loc = {'case': row['case'], 's': s, 'context': context}
                    if claim.get('L') == '> 10':
                        over_ten.append({**loc, 'optimality_proved': claim.get('optimality_proved'),
                                         'search': claim.get('search')})
                    if not isinstance(claim.get('L'), int):
                        continue
                    count['numeric_bond_claims'] += 1
                    count[f'numeric_{context.split(":")[0]}'] += 1
                    cert = claim.get('certificate', {})
                    count['recorded_state_pool_entries'] += len(cert.get('state_pool', []))
                    count['recorded_state_references'] += sum(len(x.get('state_indices', [])) for x in cert.get('maximal_proper', []))
                    ref = certificate_reference(claim)
                    if not ref or not ref.get('kept_as'):
                        missing.append({**loc, 'issue': 'no retained proof reference'})
                        continue
                    name = ref['kept_as']
                    signature = (ref.get('cnf_sha256'), ref.get('proof_sha256'), ref.get('proof_bytes'))
                    if name in references and references[name] != signature:
                        bad.append({**loc, 'issue': 'inconsistent metadata for retained name', 'name': name})
                    references[name] = signature
                    for ext in ('.cnf.gz', '.lrat.gz'):
                        if not (CERTS / (name + ext)).is_file():
                            missing.append({**loc, 'issue': 'missing file', 'file': name + ext})
                    if cert.get('assignments_checked') != sum(len(x.get('state_indices', [])) for x in cert.get('maximal_proper', [])):
                        bad.append({**loc, 'issue': 'assignment count differs from indices'})
    selection = []
    availability = {}
    for group in ('chained', 'direct', 'other', 'undecided'):
        available = sorted(candidates[group], key=lambda x: x['rank'])
        availability[group] = {'numeric_cells': len(available), 'keys': len({x['case'] for x in available})}
        used = set()
        picked = []
        for s in (1, 2, 3, 4):
            match = next((x for x in available if x['s'] == s and x['case'] not in used), None)
            if match:
                picked.append(match)
                used.add(match['case'])
        for x in available:
            if len(picked) >= 4:
                break
            if x['case'] not in used:
                picked.append(x)
                used.add(x['case'])
        selection.extend({**x, 'stratum': group} for x in picked)
    selected_ids = {(x['case'], x['s']) for x in selection}
    selection.extend(x for x in targeted if (x['case'], x['s']) not in selected_ids)
    expected = json.loads((DATA / 'raw_hashes.json').read_text())['registered/results.jsonl']
    inv = {'counts': dict(count), 'outcomes': dict(outcomes), 'unique_numeric_certificate_pairs': len(references),
           'missing': missing, 'inconsistent': bad, 'over_ten_claims': over_ten,
           'raw_results_uncompressed_sha256': raw.hexdigest(), 'raw_hash_matches_record': raw.hexdigest() == expected,
           'results_gzip_sha256': file_digest(DATA / 'results.jsonl.gz'), 'sampling_availability': availability}
    save('inventory.json', inv)
    save('selection.json', {'seed': SEED, 'unit': '(key,s), all nested numeric claims', 'selection': selection})
    return inv, selection


def rebuild(key, N):
    """Only old independent actions are reused; term placement is fresh here."""
    catalog = fresh.words(key[0])
    needed = {t for placement in key[4] for t in placement}
    triples = set()
    for n in range(N + 1):
        maps = fresh.state_actions(key, n)
        images = {}
        for t in needed:
            word, suffix = catalog[t // 3], t % 3
            values = list(range(1 << n))
            for q in reversed(word):
                values = [maps[q][x] for x in values]
            depth = n + bool(suffix)
            if depth > N:
                continue
            if suffix:
                values = [(x << 1) | (suffix - 1) for x in values]
            images[t] = [(1 << depth) - 1 + x for x in values]
        for placement in key[4]:
            if not all(t in images for t in placement):
                continue
            for image in zip(*(images[t] for t in placement)):
                if len(set(image)) == 3:
                    triples.add(tuple(sorted(image)))
    return sorted(triples)


def read_cnf(data):
    clauses, pending = [], []
    nvars = expected = None
    for line in data.decode().splitlines():
        text = line.strip()
        if not text or text.startswith('c'):
            continue
        if text.startswith('p'):
            if nvars is not None:
                raise ValueError('duplicate CNF header')
            p, kind, n, m = text.split()
            if p != 'p' or kind != 'cnf':
                raise ValueError('invalid CNF header')
            nvars, expected = int(n), int(m)
            continue
        for v in map(int, text.split()):
            if not v:
                clauses.append(pending)
                pending = []
            else:
                pending.append(v)
    if nvars is None or pending or len(clauses) != expected:
        raise ValueError('malformed CNF or clause count')
    if any(abs(v) > nvars for c in clauses for v in c):
        raise ValueError('CNF variable outside declared range')
    return nvars, clauses


def clause_counter(clauses):
    return Counter(tuple(sorted(c)) for c in clauses)


def hint_free_lrat(original, nvars, lines):
    checker = rup.RUPChecker(original, nvars)
    additions = deletions = ignored_hints = negative_hints = 0
    empty_line = None
    seen_ids = set(range(1, len(original) + 1))
    for line_number, raw_line in enumerate(lines, 1):
        tokens = raw_line.strip().split()
        if not tokens or tokens[0] == 'c':
            continue
        try:
            cid = int(tokens[0])
            if cid <= 0:
                raise ValueError('nonpositive line id')
            if len(tokens) > 1 and tokens[1] == 'd':
                ids = list(map(int, tokens[2:]))
                if not ids or ids[-1] != 0 or any(x <= 0 for x in ids[:-1]):
                    raise ValueError('malformed deletion')
                deletions += 1
                continue  # Retaining previously proved clauses is sound.
            if cid in seen_ids:
                raise ValueError('duplicate clause id')
            nums = list(map(int, tokens[1:]))
            split = nums.index(0)
            clause, hints = nums[:split], nums[split + 1:]
            if not hints or hints[-1] != 0 or 0 in hints[:-1]:
                raise ValueError('malformed hint terminator')
            if any(abs(v) > nvars for v in clause):
                raise ValueError('new variable')
        except (ValueError, IndexError) as exc:
            return {'valid': False, 'line': line_number, 'reason': str(exc)}
        if not checker.contradiction([-v for v in clause]):
            return {'valid': False, 'line': line_number, 'reason': 'addition is not RUP',
                    'additions': additions, 'ignored_deletions': deletions}
        checker.add(clause)
        seen_ids.add(cid)
        additions += 1
        ignored_hints += len(hints) - 1
        negative_hints += sum(x < 0 for x in hints[:-1])
        if not clause and empty_line is None:
            empty_line = line_number
    return {'valid': empty_line is not None, 'reason': None if empty_line else 'no derived empty clause',
            'additions': additions, 'ignored_deletions': deletions, 'ignored_hints': ignored_hints,
            'negative_hints': negative_hints, 'empty_clause_line': empty_line}


def decode_state(text, nvars):
    data = bytes.fromhex(text)
    if len(data) != (nvars + 7) // 8:
        raise ValueError('state encoding has wrong length')
    value = int.from_bytes(data, 'little')
    if value >> nvars:
        raise ValueError('nonzero padding bits')
    return value


def first_violated(mask, triple_masks):
    for i, m in enumerate(triple_masks):
        value = mask & m
        if value == 0 or value == m:
            return {'triple_index': i, 'polarity': 'positive' if value == 0 else 'negative'}
    return None


def check_claim(claim, context, triples, nvars, k0, s, state_cache):
    started = time.monotonic()
    errors = []
    support = claim.get('bond', [])
    assignment = claim.get('forbidden_assignment', [])
    L = claim['L']
    if len(support) != L or len(set(support)) != L or any(type(v) is not int or v < 0 or v >= nvars for v in support):
        errors.append('invalid bond support')
    if len(assignment) != L or any(type(v) is not int or v not in (0, 1) for v in assignment):
        errors.append('invalid forbidden assignment')
    A = set(range((1 << k0) - 1, (1 << (k0 + 1)) - 1))
    B = set(range((1 << (k0 + s)) - 1, (1 << (k0 + s + 1)) - 1))
    if not A.intersection(support) or not B.intersection(support):
        errors.append('support misses top or target level')
    if context.startswith('per_target:') and int(context.split(':')[1]) not in support:
        errors.append('support misses named target')
    if context == 'target_restricted' and any(v >= (1 << (k0 + s + 1)) - 1 for v in support):
        errors.append('restricted support below target')
    cert = claim.get('certificate', {})
    ref = cert.get('refutation', {})
    name = ref.get('kept_as')
    answer = {'context': context, 'L': L, 'bond': support, 'forbidden_assignment': assignment,
              'recorded_optimality_proved': claim.get('optimality_proved'), 'certificate_name': name,
              'errors': errors}
    if errors:
        return answer
    cnf_path, proof_path = CERTS / f'{name}.cnf.gz', CERTS / f'{name}.lrat.gz'
    cnf_data, proof_data = gzip.decompress(cnf_path.read_bytes()), gzip.decompress(proof_path.read_bytes())
    count, stored = read_cnf(cnf_data)
    original = fresh.cnf(triples)
    units = [[(v + 1) if b else -(v + 1)] for v, b in zip(support, assignment)]
    expected = original + units
    counter_expected, counter_stored = clause_counter(expected), clause_counter(stored)
    answer.update(cnf_uncompressed_sha256=digest(cnf_data), proof_uncompressed_sha256=digest(proof_data),
                  cnf_gzip_sha256=file_digest(cnf_path), proof_gzip_sha256=file_digest(proof_path),
                  cnf_clause_count=len(stored), rebuilt_clause_count=len(expected),
                  clause_multiset_equal=counter_expected == counter_stored,
                  clause_set_equal=set(counter_expected) == set(counter_stored),
                  cnf_digest_matches_record=digest(cnf_data) == ref.get('cnf_sha256') == name,
                  proof_digest_matches_record=digest(proof_data) == ref.get('proof_sha256'),
                  proof_bytes_match_record=len(proof_data) == ref.get('proof_bytes'))
    for key in ('clause_multiset_equal', 'cnf_digest_matches_record', 'proof_digest_matches_record', 'proof_bytes_match_record'):
        if not answer[key]:
            errors.append(key + ' failed')
    if count != nvars:
        errors.append('CNF variable count mismatch')
    # Use the independently reconstructed clauses, never a mismatching stored CNF.
    answer['rup'] = hint_free_lrat(expected, nvars, proof_data.decode().splitlines())
    if not answer['rup']['valid']:
        errors.append('hint-free RUP refutation failed')
    triple_masks = [sum(1 << v for v in triple) for triple in triples]
    pools = cert.get('state_pool', [])
    masks = []
    for index, text in enumerate(pools):
        try:
            mask = decode_state(text, nvars)
            masks.append(mask)
            if text not in state_cache:
                state_cache[text] = first_violated(mask, triple_masks)
            if state_cache[text] is not None:
                errors.append({'invalid_state_index': index, **state_cache[text]})
        except ValueError as exc:
            errors.append({'invalid_state_index': index, 'reason': str(exc)})
            masks.append(None)
    expected_subsets = {tuple(sorted(set(support) - {v})) for v in support}
    actual_subsets = []
    projections = []
    references = 0
    for item in cert.get('maximal_proper', []):
        subset = item.get('support', [])
        indices = item.get('state_indices', [])
        signature = tuple(sorted(subset))
        actual_subsets.append(signature)
        values = []
        for index in indices:
            references += 1
            if type(index) is not int or index < 0 or index >= len(masks) or masks[index] is None:
                errors.append('invalid state-pool reference')
                continue
            values.append(sum(((masks[index] >> v) & 1) << j for j, v in enumerate(subset)))
        full = set(values) == set(range(1 << len(subset)))
        if len(set(subset)) != len(subset) or len(indices) != (1 << (L - 1)) or not full:
            errors.append({'maximal_subset_not_full': subset, 'indices': len(indices), 'distinct_values': len(set(values))})
        projections.append({'support': subset, 'state_references': len(indices), 'distinct_assignments': len(set(values)),
                            'full': full, 'list_order_matches_bitmask_order': values == list(range(1 << len(subset)))})
    if set(actual_subsets) != expected_subsets or len(actual_subsets) != L:
        errors.append('maximal proper subset roster incomplete or duplicated')
    if cert.get('assignments_checked') != references:
        errors.append('reported assignment count mismatch')
    answer.update(state_pool_entries=len(pools), state_references=references,
                  maximal_proper=projections, all_recorded_states_checked=True,
                  bond_inclusion_minimal_certified=not errors, seconds=time.monotonic() - started)
    return answer


def controls():
    sat = [[1, 2, 3], [-1, -2, -3]]
    good = sat + [[-1], [-2], [-3]]
    valid = hint_free_lrat(good, 3, ['6 0 1 2 3 4 5 0'])
    wrong = hint_free_lrat(sat, 3, ['3 0 1 2 0'])
    malformed = hint_free_lrat(good, 3, ['6 0 1 2'])
    newvar = hint_free_lrat(good, 3, ['6 4 0 1 0'])
    hint_mutated = hint_free_lrat(good, 3, ['6 0 -999999 777777 0'])
    state_valid = decode_state('01', 3)
    state_wrong = state_valid ^ 1
    result = {'positive_empty_clause_accepted': valid['valid'],
              'mathematically_wrong_empty_clause_rejected': not wrong['valid'],
              'malformed_LRAT_rejected': not malformed['valid'],
              'out_of_range_literal_rejected': not newvar['valid'],
              'hint_mutation_irrelevant_by_design': hint_mutated['valid'],
              'changed_CNF_clause_detected': clause_counter(sat) != clause_counter([[1, 2, -3], [-1, -2, -3]]),
              'valid_state_accepted': first_violated(state_valid, [7]) is None,
              'one_bit_wrong_state_rejected': first_violated(state_wrong, [7]) is not None,
              'details': {'valid': valid, 'wrong': wrong, 'malformed': malformed, 'new_variable': newvar}}
    result['all_passed'] = all(v for k, v in result.items() if isinstance(v, bool))
    save('controls.json', result)
    return result


def dead_union_metadata():
    """Check retention binding separately from the numeric bond inventory."""
    records = []
    with gzip.open(DATA / 'results.jsonl.gz', 'rt') as f:
        for line in f:
            row = json.loads(line)
            r = row['result']
            union = r.get('union', {})
            if union.get('verdict') != 'dead':
                continue
            triples = rebuild(r['key'], r['N'])
            base = fresh.cnf(triples)
            minimum = min(v for t in triples for v in t) + 1
            candidates = []
            for unit in (None, minimum, -minimum):
                clauses = base if unit is None else base + [[unit]]
                data = (f'p cnf {r["nvars"]} {len(clauses)}\n' + ''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses)).encode()
                name = digest(data)
                candidates.append({'symmetry_unit': unit, 'canonical_cnf_sha256': name,
                                   'cnf_file_exists': (CERTS / (name + '.cnf.gz')).is_file(),
                                   'proof_file_exists': (CERTS / (name + '.lrat.gz')).is_file()})
            records.append({'case': row['case'], 'key': r['key'], 'union_record': union,
                            'has_cnf_digest': bool(union.get('cnf_sha256')),
                            'has_proof_digest': bool(union.get('proof_sha256')),
                            'has_kept_name': bool(union.get('kept_as')),
                            'canonical_serialization_candidates': candidates,
                            'note': 'Filename probes cover the fresh sorted serialization with no unit or either minimum-variable unit; absence is not an exhaustive semantic search of retained files.'})
    result = {'dead_union_records': len(records),
              'records_missing_cnf_digest': sum(not x['has_cnf_digest'] for x in records),
              'records_missing_proof_digest': sum(not x['has_proof_digest'] for x in records),
              'records_missing_kept_name': sum(not x['has_kept_name'] for x in records),
              'canonical_candidate_pairs_present': sum(x['cnf_file_exists'] and x['proof_file_exists'] for r in records for x in r['canonical_serialization_candidates']),
              'records': records}
    save('dead_union_metadata.json', result)
    return result


def run(selection):
    chosen = {(x['case'], x['s']): x for x in selection}
    results = []
    with gzip.open(DATA / 'results.jsonl.gz', 'rt') as f:
        for line in f:
            row = json.loads(line)
            matches = [s for case, s in chosen if case == row['case']]
            if not matches:
                continue
            r = row['result']
            started = time.monotonic()
            triples = rebuild(r['key'], r['N'])
            state_cache = {}
            union = r.get('union', {})
            model_issue = None
            if 'model' in union:
                model = decode_state(union['model'], r['nvars'])
                model_issue = first_violated(model, [sum(1 << v for v in t) for t in triples])
            for level in r['levels']:
                if level['s'] not in matches:
                    continue
                info = chosen[(row['case'], level['s'])]
                record = {**info, 'key': r['key'], 'N': r['N'], 'nvars': r['nvars'],
                          'recorded_L_N': level.get('L_N'), 'recorded_L_target': level.get('L_target'),
                          'recorded_overshoot': level.get('overshoot'),
                          'rebuilt_knot_count': len(triples), 'recorded_knot_count': r['knot_count'],
                          'knot_count_matches': len(triples) == r['knot_count'],
                          'rebuilt_triples_sha256': digest(json.dumps(triples, separators=(',', ':')).encode()),
                          'union_model_present': 'model' in union, 'union_model_violation': model_issue,
                          'claims': []}
                for context, claim in claims(level):
                    if isinstance(claim.get('L'), int):
                        try:
                            checked = check_claim(claim, context, triples, r['nvars'], r['k0'], level['s'], state_cache)
                        except Exception as exc:
                            checked = {'context': context, 'L': claim.get('L'), 'errors': [f'{type(exc).__name__}: {exc}']}
                        record['claims'].append(checked)
                record['seconds'] = time.monotonic() - started
                record['valid'] = record['knot_count_matches'] and model_issue is None and all(not x['errors'] for x in record['claims'])
                results.append(record)
                save('sample_results.json', results)
                print(json.dumps({'case': row['case'], 's': level['s'], 'stratum': info['stratum'],
                                  'claims': len(record['claims']), 'valid': record['valid'],
                                  'seconds': record['seconds']}), flush=True)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory-only', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
    started = time.monotonic()
    inv, selection = make_inventory_and_selection()
    ctrl = controls()
    if args.inventory_only:
        print(json.dumps({'inventory': inv['counts'], 'selected_cells': len(selection),
                          'missing': len(inv['missing']), 'inconsistent': len(inv['inconsistent']),
                          'controls_passed': ctrl['all_passed']}), flush=True)
        return
    results = run(selection)
    dead = dead_union_metadata()
    all_claims = [x for row in results for x in row['claims']]
    summary = {'scope_kind': 'epic', 'scope_id': 'LEVEL-REACH-20261114-001',
               'selected_cells': len(selection), 'checked_cells': len(results),
               'strata': dict(Counter(r['stratum'] for r in results)), 'checked_bond_claims': len(all_claims),
               'unique_sample_certificate_pairs': len({x.get('certificate_name') for x in all_claims}),
               'state_pool_entries_checked': sum(x.get('state_pool_entries', 0) for x in all_claims),
               'maximal_proper_state_references_checked': sum(x.get('state_references', 0) for x in all_claims),
               'proof_additions_checked': sum(x.get('rup', {}).get('additions', 0) for x in all_claims),
               'proof_deletion_lines_ignored': sum(x.get('rup', {}).get('ignored_deletions', 0) for x in all_claims),
               'all_sample_claims_passed': len(results) == len(selection) and all(x['valid'] for x in results),
               'controls_passed': ctrl['all_passed'], 'inventory_missing_count': len(inv['missing']),
               'inventory_inconsistency_count': len(inv['inconsistent']),
               'dead_union_records_without_proof_hash_or_retained_name': dead['records_missing_proof_digest'],
               'dead_union_canonical_candidate_pairs_present': dead['canonical_candidate_pairs_present'],
               'seconds': time.monotonic() - started,
               'peak_rss_mb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
               'reused_readonly_sources': {str(p.relative_to(ROOT)): file_digest(p) for p in (OLD / 'fresh_patterns.py', OLD / 'check_rup.py')},
               'audit_script_sha256': file_digest(Path(__file__)),
               'validation': 'independent same-task referee reconstruction; old independent checker reused; no study implementation imported; not external replication',
               'nonclaims': ['global least cardinality', 'search exhaustion through ten', 'uniform theorem']}
    save('summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
