"""Match each archived seeded split against the complete independent open-system table."""

import argparse
import json
import random
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
SPLIT_ARCHIVE = HERE.parents[1] / 'CUT-BOXES-20261127-001' / 'out'


def records(datafile):
    return [json.loads(line) for line in datafile.read_text().splitlines()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=49)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    started = perf_counter()
    split_census = json.loads((HERE / 'open_full.json').read_text())
    split_by_identity = {(r['file'], r['line'], x): r for r in split_census['splits'] for x in r['equivalent_splits']}
    closed = [r for r in records(HERE / 'closed_boxes.jsonl') if r['knots'] == 12 and r['boxes']]
    closed.sort(key=lambda r: r['links'])
    assert len(closed) == 49
    file_rows = sorted((r['graph'], f.name, line, r) for f in sorted(SPLIT_ARCHIVE.glob('cut_*.jsonl'))
                       for line,r in enumerate(records(f),1))
    assert [x for x,*_ in file_rows] == list(range(49))
    matched = []
    other = []
    for position, filename, line, row in file_rows[:args.limit]:
        baseline = closed[position]
        marked = row['cut distinction']
        before = baseline['boxes']
        ends = baseline['distinction_links'][marked]
        seed_replay = random.Random(20261129 + position).choice(tuple(range(18)))
        result = split_by_identity[(baseline['file'], baseline['line'], marked)]
        after = result['box_count']
        assert row['boxes before'] == before and row['knots at its ends'] == ends and seed_replay == marked
        assert row['bonds'] == result['bonds'] and row['boxes'] == after
        matched.append({'followup_file': filename, 'followup_line': line, 'position': position,
                        'original_file': baseline['file'], 'original_line': baseline['line'],
                        'seeded_split': marked, 'both_holders': ends, 'equivalent_splits': result['equivalent_splits'],
                        'closed_boxes': before, 'after_split_bonds': result['bonds'], 'after_split_boxes': after})
        for x in range(18):
            alt = split_by_identity[(baseline['file'],baseline['line'],x)]
            if x != marked and alt['box_count']:
                other.append({'position':position, 'seeded_split':marked, 'seeded_holders':ends,
                              'positive_alternate_split':x, 'holders_of_alternate':baseline['distinction_links'][x],
                              'bonds_after_alternate':alt['bonds'], 'boxes_after_alternate':alt['box_count']})
    closed_boxes = [b for r in closed for b in r['all_upper']]
    complete_closed_deletions = all(b['missing'] == ['111'] and len(b['laws_needed']) == 12 for b in closed_boxes)
    assert complete_closed_deletions
    out = {'matched_marked_splits':matched, 'positive_alternates':other, 'matched_count':len(matched),
           'closed_boxes_in_49_sources':len(closed_boxes), 'all_801_miss_only_upper_111_and_need_all_12':complete_closed_deletions,
           'one_copy_transports_over_801_boxes_and_18_cuts':len(closed_boxes)*18*2,
           'total_closed_boxes_on_matched_rows':sum(r['closed_boxes'] for r in matched),
           'sum_bonds_on_matched_rows':sum(r['after_split_bonds'] for r in matched),
           'bond_range_on_matched_rows':[min(r['after_split_bonds'] for r in matched),max(r['after_split_bonds'] for r in matched)],
           'boxes_on_matched_rows':sum(r['after_split_boxes'] for r in matched),
           'elapsed_seconds':round(perf_counter()-started,6)}
    args.out.write_text(json.dumps(out,separators=(',',':'))+'\n')
    print({k:v for k,v in out.items() if k!='matched_marked_splits'})


if __name__ == '__main__':
    main()
