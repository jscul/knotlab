"""Regrow the frozen starts independently and recount their witnessed rosters."""

from __future__ import annotations

import argparse
from array import array
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import subprocess
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONTRACT_DIR = HERE.parent
CENSUS = ROOT / 'research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'
ENGINE = ROOT / ('experiments/LOCAL-ROUND-20261123-001A/'
                 'LOCAL-ROUND-20261123-001A-E001_local_round')
sys.path.insert(0, str(ENGINE))
from lr_core import Str, own_round


LAWS = {
    'L0': ('STALL', None),
    'L1': ('CANCEL-WAIT', 3),
    'L6': ('CANCEL-RETIRE', 3),
    'L7': ('CANCEL-OFFSHOOT', 3),
    'L9': ('CANCEL-RETIRE', None),
    'L11': ('CANCEL-RETIRE', 4),
}
KNOT_LAWS = ('nae', 'parity')
ASSAY_SOURCES = 64


def read_json(path):
    return json.loads(path.read_bytes())


def verify_input(path, digests):
    expected = digests[str(path.relative_to(ROOT))]
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'frozen input has changed: {path}')


def touching_stars(knot_count):
    stars = [[] for _ in range(knot_count)]
    distinction = 0
    for first in range(knot_count):
        for second in range(first + 1, knot_count):
            stars[first].append(distinction)
            stars[second].append(distinction)
            distinction += 1
    for star in stars:
        star.extend((distinction, distinction + 1))
        distinction += 2
    return stars


def start_stars(name, census):
    kind, index = name.split(':')
    if kind == 'census':
        return census[int(index)]['stars']
    if kind == 'touching':
        return touching_stars(int(index))
    raise ValueError(f'unknown start: {name}')


def read_roster(structure):
    """Recover every witnessed pair using only holders and barred distinctions."""
    members = sorted({holders[0] for holders, barred in zip(
        structure.holders, structure.barred, strict=True)
        if len(holders) == 1 and not barred})
    position = {knot: index for index, knot in enumerate(members)}
    met_by_knot = defaultdict(set)
    for holders in structure.holders:
        if len(holders) == 2:
            first, second = holders
            if first in position:
                met_by_knot[second].add(position[first])
            if second in position:
                met_by_knot[first].add(position[second])
    met_sets = {frozenset(met) for met in met_by_knot.values() if len(met) >= 2}
    witnessed = [set() for _ in members]
    for met in met_sets:
        for member in met:
            witnessed[member].update(met)
    for member, neighbors in enumerate(witnessed):
        neighbors.discard(member)
    return members, witnessed


def measure_parts(witnessed):
    part_size_of = [0] * len(witnessed)
    sizes = []
    for member, part_size in enumerate(part_size_of):
        if part_size:
            continue
        part = [member]
        part_size_of[member] = -1
        for reached in part:
            for neighbor in witnessed[reached]:
                if not part_size_of[neighbor]:
                    part_size_of[neighbor] = -1
                    part.append(neighbor)
        for reached in part:
            part_size_of[reached] = len(part)
        sizes.append(len(part))
    return part_size_of, sorted(sizes, reverse=True)


def count_reach(binary, witnessed, part_size_of, last_step, source_limit):
    if not witnessed:
        return []
    header = array('I', (len(witnessed), last_step, source_limit))
    if header.itemsize != 4:
        raise RuntimeError('reach helper requires native 32-bit unsigned integers')
    offsets = array('I', (0,))
    neighbors = array('I')
    for choices in witnessed:
        neighbors.extend(sorted(choices))
        offsets.append(len(neighbors))
    data = b''.join(values.tobytes() for values in (
        header, offsets, array('I', part_size_of), neighbors))
    output = subprocess.run([str(binary)], input=data, capture_output=True, check=True).stdout
    spectra = []
    for line in output.splitlines():
        multiplicity, *counts = map(int, line.split())
        if len(counts) != last_step + 1:
            raise ValueError('a reach vector has the wrong length')
        spectra.append((counts, multiplicity))
    expected = min(len(witnessed), source_limit) if source_limit else len(witnessed)
    if sum(count for _, count in spectra) != expected:
        raise ValueError('reach helper did not return one vector per source')
    return spectra


def summarize_reach(spectra, last_step):
    greatest = [0] * (last_step + 1)
    digest = hashlib.sha256(b'[')
    needs_comma = False
    for counts, multiplicity in sorted(spectra):
        greatest = [max(a, b) for a, b in zip(greatest, counts, strict=True)]
        encoded = json.dumps(counts, separators=(',', ':')).encode('ascii')
        if not needs_comma:
            digest.update(encoded)
            needs_comma = True
            multiplicity -= 1
        while multiplicity:
            batch = min(multiplicity, 1024)
            digest.update((b',' + encoded) * batch)
            multiplicity -= batch
    digest.update(b']')
    return greatest, digest.hexdigest()


def stage_record(binary, structure, case, knot_law, source_limit=0):
    setup_start = perf_counter()
    members, witnessed = read_roster(structure)
    part_size_of, part_sizes = measure_parts(witnessed)
    last_step = case['r_max']
    start_reach = perf_counter()
    spectra = count_reach(binary, witnessed, part_size_of, last_step, source_limit)
    elapsed_reach = perf_counter() - start_reach
    if source_limit:
        # Startup and serialization are included, so scaling these up is conservative
        # for the observed sources. It is still an estimate for the other sources.
        scale = max(len(members) / source_limit, 1)
        return {
            'round': structure.round,
            'setup_seconds': start_reach - setup_start,
            'sample_seconds': elapsed_reach,
            'projected_reach_seconds': elapsed_reach * scale,
        }
    greatest, digest = summarize_reach(spectra, last_step)
    degrees = Counter(map(len, witnessed))
    twice_pairs = sum(degree * multiplicity for degree, multiplicity in degrees.items())
    if twice_pairs % 2:
        raise ValueError('witnessed relation is not symmetric')
    return {
        'case': case['id'],
        'kl': knot_law,
        'round': structure.round,
        'knots': len(structure.places),
        'members': len(members),
        'pairs': twice_pairs // 2,
        'part_sizes': part_sizes,
        'degree_histogram': {str(degree): degrees[degree] for degree in sorted(degrees)},
        'greatest_counts': greatest,
        'reach_sha256': digest,
    }


def recount(case, knot_law, census, binary, source_limit=0):
    started = perf_counter()
    treatment, cap = LAWS[case['law']]
    structure = Str(start_stars(case['start'], census))
    target_rounds = set(case['rounds'])
    final_round = max(target_rounds)
    stages = []

    def fresh_count(parent_count, ordinary_count):
        if ordinary_count == 0:
            if knot_law == 'parity':
                return 0
            # The apparent closing birth is the demand roster's sole member.
            ordinary_count = max(3 - parent_count, 1)
        if cap is None:
            return ordinary_count
        return min(ordinary_count, cap)

    while True:
        if structure.round in target_rounds:
            stages.append(stage_record(binary, structure, case, knot_law, source_limit))
        if len(structure.places) > case['knot_bound']:
            reason = 'knot_bound'
            break
        if structure.round == final_round:
            reason = 'last_scheduled_round'
            break
        if not any(len(holders) == 1 and not barred for holders, barred in zip(
                structure.holders, structure.barred, strict=True)):
            reason = 'empty_roster'
            break
        result = own_round(structure, 'ORD', treatment, fresh_override=fresh_count)
        if result['stalled'] or not result['births']:
            if structure.round in target_rounds:
                stages.append(stage_record(binary, structure, case, knot_law, source_limit))
            reason = 'stalled' if result['stalled'] else 'zero_births'
            break

    run_seconds = perf_counter() - started
    terminal = {
        'case': case['id'],
        'kl': knot_law,
        'round': structure.round,
        'reason': reason,
        'seconds': run_seconds,
        'peak_self_rss_kib': getrusage(RUSAGE_SELF).ru_maxrss,
    }
    if source_limit:
        terminal['projected_seconds'] = run_seconds + sum(
            row['projected_reach_seconds'] - row['sample_seconds'] for row in stages)
        terminal['stage_timings'] = stages
        return {'terminal': terminal}
    terminal['knots'] = len(structure.places)
    terminal['omitted_rounds'] = sorted(target_rounds - {row['round'] for row in stages})
    return {'terminal': terminal, 'stages': stages}


def setup(params):
    global settings
    contract = read_json(CONTRACT_DIR / 'contract.json')
    cases_path = CONTRACT_DIR / contract['cases']
    for path in (CENSUS, cases_path):
        verify_input(path, contract['inputs'])
    settings = {
        'cases': read_json(cases_path),
        'census': read_json(CENSUS),
        'binary': Path(params['reach_bin']).resolve(strict=True),
        'source_limit': ASSAY_SOURCES if params.get('assay') == '1' else 0,
        'first': int(params.get('first', 0)),
        'limit': int(params['limit']) if 'limit' in params else None,
        'case_id': params.get('case_id'),
        'knot_law': params.get('knot_law'),
    }


def cases():
    active_cases = settings['cases'][settings['first']:]
    if settings['limit'] is not None:
        active_cases = active_cases[:settings['limit']]
    for case in active_cases:
        if settings['case_id'] and settings['case_id'] != case['id']:
            continue
        for knot_law in KNOT_LAWS:
            if settings['knot_law'] and settings['knot_law'] != knot_law:
                continue
            yield f"{case['id']}/{knot_law}", (case, knot_law)


def run(case_id, payload):
    case, knot_law = payload
    return recount(case, knot_law, settings['census'], settings['binary'],
                   settings['source_limit'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reach-bin', type=Path, required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--kl', choices=KNOT_LAWS)
    parser.add_argument('--assay', action='store_true', help='record only timing for 64 sources')
    args = parser.parse_args()
    setup({'reach_bin': str(args.reach_bin), 'case_id': args.case,
           'knot_law': args.kl, 'assay': str(int(args.assay))})
    selected = list(cases())
    if not selected:
        parser.error(f'no frozen case with ID {args.case}')
    for case_id, payload in selected:
        print(json.dumps(run(case_id, payload), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
