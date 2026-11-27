"""Enumerate the source truth tables behind the cited lower and upper readings."""
import argparse
import contextlib
import io
import json
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from time import perf_counter

from growth_replay import LAWS, advance, census_starts, ordinary_advance, stages

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = HERE.parents[1]
UPPER = RESEARCH / "UPPER-GROWN-20261127-001"
PREVIOUS = UPPER / "referee-R1"
RING = RESEARCH / "RING-BOND-20261127-001/referee-R1"
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.cli import main as knot_check

EIGHT = list(product((0, 1), (2, 3), (4, 5)))
FOUR = [t for t in EIGHT if sum(t) % 2 == 0]


def read(path):
    return json.loads(path.read_text())


def words(width):
    return list(product((0, 1), repeat=width))


def join_bits(bits):
    return ''.join(map(str, bits))


def letter(name, value):
    return ('~' if value else '') + name


def roles(cnf, witnesses=()):
    results = []
    for contact in 'PQR':
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = knot_check(['check', '--cnf', cnf, '--loops', *(c for c in 'PQR' if c != contact),
                                 '--contact', contact, '--witnesses', *witnesses, '--json'])
        report = json.loads(output.getvalue())
        assert status == 0 and report['is_knot'] and len(report['allowed']) == 7
        results.append(contact)
    return results


def tuples_in(population, readings):
    cells = {(): population}
    for reading in readings:
        cells = {key + (bit,): subset for key, group in cells.items()
                 for bit, subset in enumerate((group & ~reading, group & reading)) if subset}
    return cells


def column(position, nbits):
    # Bit k is this distinction's value in assignment k, including both complements.
    byte_count = 1 << (nbits - 3)
    if position < 3:
        pattern = bytes([(0xaa,0xcc,0xf0)[position]])
    else:
        half = 1 << (position - 3)
        pattern = bytes(half) + b'\xff' * half
    return int.from_bytes(pattern * (byte_count // len(pattern)),'little')


def inspect(supports, carriers, selected, clauses, both=None, detailed=True, upper_only=False):
    names = sorted(set().union(*map(set, supports)))
    assert len(carriers) == len(selected) == 6
    assert all(2 <= len(c) <= 3 for c in carriers)
    assert sum(map(len, carriers)) == len(set().union(*map(set, carriers)))
    universe = (1 << (1 << len(names))) - 1
    raw = {x: column(i, len(names)) for i, x in enumerate(names)}

    def equal(group):
        ones, zeros = universe, universe
        for x in group:
            ones &= raw[x]
            zeros &= ~raw[x]
        return ones | zeros

    def pair_read(pair, a, b):
        if both is None:
            return a ^ b
        return a & b if pair == both else a | b

    def upper(w):
        return tuple(pair_read(i, w[2*i], w[2*i+1]) for i in range(3))

    def satisfies(word, clause):
        return not all(word[k] for k in clause)

    values = [equal(c) if v else universe ^ equal(c) for c, v in zip(carriers, selected, strict=True)]
    laws = [universe ^ equal(k) for k in supports]
    allowed = universe
    for law in laws:
        allowed &= law
    upper_bits = upper(values)
    blocked = upper_bits[0] & upper_bits[1] & upper_bits[2]
    cells = tuples_in(allowed, values)
    upper_counts = {join_bits(w): v.bit_count() for w, v in tuples_in(allowed, upper_bits).items()}
    if upper_only:
        return upper_counts
    assert set(upper_counts) == {join_bits(w) for w in words(3)} - {'111'}
    for c in clauses:
        assert set(tuple(w[i] for i in c) for w in cells) == set(words(3)) - {(1, 1, 1)}
    law_deletions = []
    for omit in range(len(supports)):
        u = blocked
        for i, law in enumerate(laws):
            if i != omit:
                u &= law
        law_deletions.append(u.bit_count())
    result = dict(knots=len(supports), distinctions=len(names), states=allowed.bit_count(),
                  loose=sorted(x for x,v in Counter(x for k in supports for x in k).items() if v==1),
                  lower_words=len(cells), upper_counts=upper_counts, source_deletions=law_deletions)
    if not detailed:
        return result

    abstract = [w for w in words(6) if all(satisfies(w, c) for c in clauses)]
    assert {upper(w) for w in abstract} == set(words(3)) - {(1, 1, 1)}
    assert set(cells) <= set(abstract)
    restored = [sum(upper(w) == (1, 1, 1) and all(satisfies(w, c) for j,c in enumerate(clauses)
                                               if j!=i) for w in words(6)) for i in range(len(clauses))]
    assert all(restored)

    def mixed(fixes, tests):
        return [sum(bool(group & mask) and bool(group & ~mask) for group in fixes) for mask in tests]

    source_fixes = [mixed(tuples_in(allowed, [raw[x] for x in knot]).values(), values) for knot in supports]
    lower_fixes = [mixed(tuples_in(allowed, [values[i] for i in c]).values(), upper_bits) for c in clauses]
    assert all(all(row) for row in source_fixes + lower_fixes)

    # A reading can be changed by changing only each particular carrier member.
    flips = []
    for group, value in zip(carriers, values):
        row = []
        for x in group:
            offset = 1 << names.index(x)
            paired = (allowed & ~raw[x]) & (allowed >> offset)
            row.append((paired & (value ^ (value >> offset))).bit_count())
        flips.append(row)
    assert all(all(row) for row in flips)

    lower_names = [f'L{i}' for i in range(6)]
    cnf = [' '.join('~' + lower_names[i] for i in c) for c in clauses]
    for i, dest in enumerate('PQR'):
        for a,b in words(2):
            cnf.append(' '.join(letter(x,v) for x,v in zip((lower_names[2*i],lower_names[2*i+1],dest),
                                                            (a,b,1-pair_read(i,a,b)))))
    result.update(abstract_lower_words=len(abstract), source_states_by_lower_word={
        join_bits(w):v.bit_count() for w,v in cells.items()}, upper_111_after_lower_clause_deletions=restored,
        minimum_source_fixes_per_reading=[min(col) for col in zip(*source_fixes)],
        minimum_lower_clause_fixes_per_upper_reading=[min(col) for col in zip(*lower_fixes)],
        allowed_single_flips_per_carrier_member=flips,
        knot_roles_on_projected_image=roles('~P ~Q ~R'),
        knot_roles_on_lower_clauses_with_six_witnesses=roles('; '.join(cnf), lower_names))
    return result


def as_supports(stage):
    return tuple(tuple(k) for k in stage)


def cross_records(pilot):
    ring = read(RING / 'layer_witness.json')
    data = inspect(ring['source_knots_not_all_equal'], ring['lower_carriers_in_A0_A1_B0_B1_C0_C1_order'],
                   [1]*6, EIGHT)
    assert data['states'] == ring['allowed_source_states']
    assert data['source_states_by_lower_word'] == ring['source_state_counts_by_lower_word']
    out = {'earlier_closed_twelve_knot_control':data}
    if pilot:
        return out

    sample = read(PREVIOUS / 'upper_sample.json')[0]
    w = sample['witness']
    actual = as_supports(w['source'])
    start = census_starts()[sample['census_rank']]
    assert start == actual[:len(start)]
    matches = {arm: list(stages(start, arm, 2))[-1][1] == actual for arm in LAWS}
    assert all(matches.values())
    cs,vs = zip(*w['raw_agreements_and_selected_value'])
    result = inspect(actual, cs, vs, w['lower_clauses'], w['both_tests_pair'])
    assert result['source_deletions'] == w['restored_upper_111_by_dropped_law']
    out['open_census_four_clause'] = dict(census_index=sample['census_rank'],round=2,
                                        start_knots=len(start), same_stage_by_law=matches, **result)

    w = read(PREVIOUS / 'upper_four_closed.json')[-1]['witness']
    data = inspect(w['knots'], w['carriers'], [1]*6, w['lower_clauses_missing_111'], w['and_pair'])
    assert data['source_deletions'] == w['restorations_by_dropped_source_law']
    out['earlier_closed_ten_knot_control'] = data

    w = read(PREVIOUS / 'open_witness.json')
    built = as_supports(w['start'])
    same = {law: advance(built,law).supports == as_supports(w['grown_supports']) for law in LAWS}
    assert all(same.values())
    data = inspect(w['grown_supports'],w['six_disjoint_carriers'],[1]*6,EIGHT)
    assert data['source_states_by_lower_word'] == w['source_states_by_raw_six_reading_word']
    post = read(UPPER/'post/grown_replay.json')
    assert data['states']==post['states'] and len(data['upper_counts'])==post['upper words']
    assert list(map(bool,data['source_deletions']))==post['each law needed (111 restored when removed)']
    assert list(map(list, as_supports(w['grown_supports'])[len(built):]))==post['births']
    out['constructed_open_twelve_knot_control']=dict(start_knots=len(built), same_stage_by_law=same, **data)

    # Complete the cited comparison of archived class counts and one-cut choices.
    source_by_row = {(r['file'],r['line']):r for r in map(json.loads,(PREVIOUS/'closed_boxes.jsonl').read_text().splitlines())}
    class_counts = defaultdict(Counter)
    examples=[]
    for path in sorted((UPPER/'out').glob('cubic_*.jsonl')):
        for i,line in enumerate(path.read_text().splitlines(),1):
            row=json.loads(line)
            old=source_by_row[(path.name,i)]
            assert row['points']==old['knots'] and row['links']==old['links'] and row['boxes']==old['boxes']
            counts=class_counts[row['points']]
            counts.update(classes=1, positive=int(bool(row['boxes'])), boxes=row['boxes'])
            if row['boxes']:
                first=row['example'][0]
                cs,vs=zip(*(entry for pair in first['box'] for entry in pair))
                replay=inspect(old['supports'],cs,vs,EIGHT,detailed=False)
                examples.append(dict(bonds=row['bonds'], missing=[[1,1,1]], reported=first['upper missing'],
                                     **{'knots needed':sum(map(bool,replay['source_deletions']))}))
    assert examples==read(UPPER/'post/replay_box.json')
    split_rows = [json.loads(line) for path in (RESEARCH/'CUT-BOXES-20261127-001/out').glob('cut_*.jsonl')
                  for line in path.read_text().splitlines()]
    all_splits=read(PREVIOUS/'open_full.json')
    counts=Counter()
    for row in all_splits['splits']:
        weight=len(row['equivalent_splits'])
        counts.update(choices=weight,positive=weight*bool(row['box_count']),strict_boxes=weight*row['box_count'])
    out['linked_archives']=dict(closed_classes=class_counts,closed_examples_matching_post=len(examples),
                                one_seeded_split_per_class=len(split_rows),positive_seeded_splits=sum(bool(r['boxes']) for r in split_rows),
                                boxes_before_seeded_splits=sum(r['boxes before'] for r in split_rows),
                                all_splits_prior_archive=counts)
    return out


def changed_census_witness(pilot):
    source = read(HERE/'open_four_changed.json')['results']
    witness = source[LAWS[0]]['witness']
    start = census_starts()[witness['entry']]
    cut_traces = {law:list(stages(start,law,witness['round'])) for law in LAWS}
    ordinary = [start]
    for _ in range(witness['round']):
        ordinary.append(ordinary_advance(ordinary[-1]).supports)
    assert all([s for _,s in trace[:-1]] == ordinary[:-1] for trace in cut_traces.values())
    cut = cut_traces[LAWS[0]][-1][1]
    for law,trace in cut_traces.items():
        assert cut == trace[-1][1] == as_supports(source[law]['witness']['stage'])
    after = ordinary[-1]
    changed = [i for i,(a,b) in enumerate(zip(cut,after,strict=True)) if a!=b]
    assert len(changed)==1 and changed==witness['decisively_shortened_latest_births']
    i=changed[0]
    r=witness['readout']
    c=r['carriers']
    if pilot:
        smaller=read(PREVIOUS/'upper_four_closed.json')[-1]['witness']
        return inspect(smaller['knots'],smaller['carriers'],[1]*6,smaller['lower_clauses_missing_111'],
                       both=smaller['and_pair'])
    cut_readout=inspect(cut,c,[1]*6,r['lower_indices'],both=0)
    upper=inspect(after,c,[1]*6,r['lower_indices'],both=0,upper_only=True)
    assert cut_readout['upper_counts'] == r['upper'] and upper==witness['ordinary_on_same_parent_upper']
    assert cut_readout['source_deletions'] == r['upper_111_restored_by_omitting_each_source_law']
    assert cut_readout['source_states_by_lower_word'] == r['six_reading_words']
    extra=set(after[i])-set(cut[i])
    assert len(extra)==1 and not extra.intersection(x for group in c for x in group)
    assert not extra.intersection(x for j,k in enumerate(after) if j!=i for x in k)
    return dict(census_index=witness['entry'],round=witness['round'],start_arities=list(map(len,start)),
                common_initial_rounds=witness['round']-1,carrier_order=c,ordinary_law=after[i],shortened_law=cut[i],
                number_of_differing_supports=len(changed),ordinary_upper_counts=upper,cut=cut_readout)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--changed',action='store_true')
    args=parser.parse_args()
    t=perf_counter()
    results=changed_census_witness(args.pilot) if args.changed else cross_records(args.pilot)
    seconds=round(perf_counter()-t,4)
    if not args.pilot:
        filename='changed_reading_check.json' if args.changed else 'reading_checks.json'
        (HERE/filename).write_text(json.dumps(results,indent=2)+'\n')
    print(f'{len(results)} records, {seconds} seconds')
