"""Enumerate the six-rule study and lawful controls without using archive values."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from gzip import GzipFile
from hashlib import sha256
from itertools import product
from json import dumps, loads
from pathlib import Path
import resource
import sys

from mechanism_checks import incidence_control, marked_reads, permutations, recodings
from predict import calculate
from readouts import adaptive, changed_mass, events, fixed_histories, fresh, single_reads, sweep, unilateral
from replay import (CLEAR, EPIC, FRESH, HISTORY_FIELD_ORDER, ROOT, Catalogue, Replay,
                    catalogue, encode_law, output_record, state_code)

FREEZE = '83095b5467e30fb395e0005986fbb07fea14e3e8ad67a2e45fb94f7c7d3a41a2'
CATALOGUES = ('signed', 'even', 'nae', 'small_even', 'small_nae')
ORDINARY_MODES = ('coherent', 'relaxed', 'dephased', 'independent', 'literal', 'literal_biased')


def joint_script(replay, left, right, *, tag=CLEAR, profiles=None):
    rows = replay.run(left, right, tag=tag, profiles=profiles, poststates=True)
    if rows is None:
        return None
    detail = []
    for (ready, a, b, states), p in rows.items():
        both = []
        for role, path in enumerate((a, b)):
            expanded = []
            snapshot = ()
            for slot, code in enumerate(path):
                tag_mode = profiles[slot][0][role] if profiles is not None else tag[role]
                field = output_record(code, replay.c, role, slot+1, ready, tags=tag_mode,
                                      calibrated=frozenset() if replay.literal else replay.device.reversed_occurrences,
                                      prior=snapshot)
                snapshot = tuple(field['keeper_snapshot'].items())
                expanded.append(field)
            both.append(expanded)
        detail.append(dict(weight=p, prepared=ready, left=both[0], right=both[1],
                           calculation_states=[state_code(s) for s in states]))
    return detail


def route_failures(replay):
    c = replay.c
    h, k = 0, 3
    attacks = [(('bank', (1, 1, 0)), 'duplicate_address'),
               (('bank', (1, 0)), 'unfitted_address'),
               (('bank', (0, 0, 0)), 'unfitted_address'),
               (k, 'out_of_role')]
    checks = []
    for actual, expected in attacks:
        trajectory = replay.run((h, actual, h), (None, None, None), poststates=True)
        assert all(a[1][1] == expected and a[0][3] == a[2][3] and states[1] == states[2]
                   for (_, a, _, states) in trajectory)
        checks.append(dict(request=actual, expected=expected, actual_history=encode_law({
            (ready, a): p for (ready, a, _, _), p in trajectory.items()})))
    return checks


def writer_failures(replay):
    c = replay.c
    h, k = next(((0, h) for h in range(1, len(c.holdings)) if set(c.holdings[0]) & set(c.holdings[h])), (0, 0))
    all_holders = tuple(range(len(c.holdings)))
    wide = Replay(Catalogue(c.holdings, (all_holders, all_holders), c.allowed), replay.mode)
    scripts = ((h, k, h), (None, None, None))
    conditions = {}
    for mode in ('write', 'not_ready', 'disconnected'):
        profiles = ((CLEAR, FRESH), (CLEAR, (mode, 'write')), (CLEAR, FRESH))
        trajectory = wide.run(*scripts, profiles=profiles, poststates=True)
        if mode == 'not_ready':
            assert all(states[1] == states[2] and (a[0][3] == a[2][3])
                       for (ready, a, _, states) in trajectory if ready)
        visible = Counter()
        for (ready,a,b,_),p in trajectory.items():
            visible[ready, a, b] += p
        expected = 'success' if mode == 'write' else mode
        assert {a[1][1] for (ready, a, _) in visible if ready} == {expected}
        conditions[mode] = dict(script=scripts, launch=encode_law(visible),
                                source_ready=wide.acceptance, changes=changed_mass(wide.c, visible,0,0,2),
                                slot_two_events=events(wide.c, visible, 1),
                                full_detailed_replay=joint_script(wide,*scripts,profiles=profiles))
    return conditions


def mode_study(replay):
    c = replay.c
    all_holders = tuple(range(len(c.holdings)))
    wide = Replay(replace(c, roles=(all_holders, all_holders)), replay.mode, device=replay.device)
    primary = {
        'source_acceptance': replay.acceptance,
        'fresh': fresh(replay),
        'single_reader': single_reads(wide),
        'fixed_histories': fixed_histories(replay),
        'held_reader_sweep': sweep(replay),
        'adaptive_histories': adaptive(replay),
        'unilateral': [],
    }
    for a, b in product(*c.roles):
        for observer, first, then in ((0,a,b), (1,b,a)):
            launch = unilateral(replay, first, then, observer)
            accepted = (launch if replay.acceptance == 1 else unilateral(replay, first, then, observer, on_success=True))
            primary['unilateral'].append(dict(launch=launch, conditional_on_source=accepted))
    if len(c.holdings) == 6:
        primary['no_shared_control_outside_roles'] = [
            dict(launch=unilateral(wide, a, b, i), conditional_on_source=unilateral(wide, a, b, i, on_success=True))
            for i,a,b in ((0,0,1),(1,1,0))]
    else:
        primary['same_address_synchrony_outside_roles'] = []
        for h, i in product(range(len(c.holdings)), (0,1)):
            primary['same_address_synchrony_outside_roles'].append(dict(holder=h, first_role=i,
                fresh=encode_law(wide.run((h,), (h,))),
                launch=unilateral(wide, h, h, i),
                conditional_on_source=unilateral(wide, h, h, i, on_success=True)))
    if replay.device is not None:
        primary['compiler'] = replay.device.certificate()
    return primary


def compare_prospective(study, expected):
    compared = 0
    for model, old_pairs in expected['tables'].items():
        for setting, old in old_pairs.items():
            actual = study[model]['fresh'][setting]
            for k in ('launch', 'conditional'):
                assert actual[k]['ordinary_cells'] == old[k]
                compared += len(old[k])
            assert actual['launch']['left_failure_row'][-1] == old['launch_both_refused']
    return compared


def run(names):
    shared_files = ('measurement.py', 'literal_read.py', 'preregistration.md')
    mechanism_root = ROOT / 'research' / EPIC
    shared_digests = {name: sha256((mechanism_root / name).read_bytes()).hexdigest() for name in shared_files}
    assert shared_digests['preregistration.md'] == FREEZE
    prediction = calculate()
    out = {'frozen_design_sha256': FREEZE,
           'shared_source_sha256': shared_digests,
           'sequential_replay_source_sha256': {path.name: sha256(path.read_bytes()).hexdigest()
               for path in sorted(Path(__file__).resolve().parent.glob('*.py'))},
           'catalogues': {},
           'record_code_fields': HISTORY_FIELD_ORDER,
           'record_code_context': 'Per slot local plan, own offered holders, own raw and calibrated values and first-mark tag status.',
           'herald_conditioning': 'For a launch law retain source_ready records and divide by source_acceptance; null when this mass is zero.',
           'fixed_histories_reproduction': 'Re-run a pair of scripts via --case [catalogue,mode,left,right] for their full joint, state and local record laws.',
           'complete_history_code': 'See replay.output_record; local choice only sees its own prior complete compact record.',
           'preparations': {'coherent': 'uniform equal-word amplitudes on the accepted subspace after the common herald',
                            'dephased': 'uniform equal-word diagonal mixture on the accepted basis words with the same herald',
                            'independent': 'uncorrelated uniform accepted halves with the same input-independent launch herald',
                            'ordinary': 'direct common uniform draw from all known lawful words; always ready',
                            'literal': 'central uniform eligible union draw; each requesting wing keeps its most recent successful word',
                            'literal_biased': 'central eligible union draw reweighted by 2 if its least shared mark is 1',
                            'erasure': 'no prepared source and a readable failure on every addressed slot'},
           'setup_attempts_note': 'Zero-first measurements compile once before all settings. Conditional failure rows are readout failures; the launch denominator includes pre-setting herald rejection.'}
    for name in names:
        c = catalogue(name)
        modes = ORDINARY_MODES + (('erasure',) if name == 'signed' else ('ordinary',))
        studies = {}
        expected = prediction['catalogues'][name]
        for mode in modes:
            replay = Replay(c, mode)
            if mode == 'relaxed' and replay.device.certificate() == studies['coherent']['compiler']:
                assert replay.device.minimum_masks == ((),) and not replay.device.reversed_occurrences
                studies[mode] = {'identical_to': 'coherent', 'compiler': replay.device.certificate(),
                                 'nonempty_minimum_masks': [], 'changed_shared_agreements': [],
                                 'unmodified_meetings': [a for a in product(*c.roles)]}
            else:
                studies[mode] = mode_study(replay)
            print(f'{name} {mode} enumerated', file=sys.stderr)
        coherent = Replay(c, 'coherent')
        d = coherent.device
        assert [d.flips[e] for e in d.marks] == list(expected['masks'])
        assert [d.signs[e] for e in d.marks] == list(expected['signs'])
        assert list(d.carrier) == list(expected['carrier']) and list(d.accepted_words) == list(expected['accepted'])
        checks = {'independently_verified_complete_probabilities': compare_prospective(studies, expected),
                  'basis_word_and_permutation_checks': permutations(coherent),
                  'coherence_and_marks': marked_reads(coherent),
                  'writer_failures': writer_failures(coherent)}
        if name == 'signed':
            checks['address_failures'] = route_failures(coherent)
            refuse = Replay(replace(c, allowed=c.allowed[:-1]+((),)), 'coherent')
            assert not refuse.acceptance and refuse.device.reason == 'empty local relation'
            checks['actual_invalid_setup_control'] = dict(certificate=refuse.device.certificate(),
                                                        fresh=fresh(refuse))
            checks['recodings'] = recodings(coherent)
            checks['nonminimal_incidence_change_control'] = incidence_control(coherent)
        out['catalogues'][name] = dict(holdings=c.holdings, allowed=c.allowed, independent_settings=c.roles,
                                      settings_pair_weight=Fraction(1, len(c.roles[0])*len(c.roles[1])),
                                      models=studies, mechanism_checks=checks)
        print(f'{name} independent mechanism controls checked', file=sys.stderr)
    return out


def hashable(value):
    return tuple(hashable(x) for x in value) if isinstance(value, list) else value


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--catalogue', action='append', choices=CATALOGUES)
    parser.add_argument('--case', metavar='JSON', help='[catalogue, model, left script, right script], optionally followed by a tag pair')
    parser.add_argument('--allow-all-addresses', action='store_true', help='Permit any holder on either reader for a selected replay case')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (4 << 30, 4 << 30))
    if args.output.exists():
        parser.error('output already exists; choose a fresh result path')
    if args.case is None:
        content = run(args.catalogue or CATALOGUES)
    else:
        cat, mode, left, right, *tag = hashable(loads(args.case))
        c = catalogue(cat)
        if args.allow_all_addresses:
            role = tuple(range(len(c.holdings)))
            c = replace(c, roles=(role,role))
        content = joint_script(Replay(c, mode), left, right, tag=tag[0] if tag else CLEAR)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = (dumps(content, default=str, separators=(',',':')) + '\n').encode()
    with args.output.open('xb') as stream:
        if args.output.suffix == '.gz':
            with GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as zip_stream:
                zip_stream.write(payload)
        else:
            stream.write(payload)


if __name__ == '__main__':
    main()
