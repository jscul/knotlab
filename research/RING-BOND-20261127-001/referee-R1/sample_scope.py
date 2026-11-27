"""Check the sampling order and the start sizes actually reached by each run."""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'out'
STARTS = HERE.parents[1] / 'FORBID-EDITS-20261126-001' / 'starts.json'


def run(limit):
    starts = json.loads(STARTS.read_text())
    ids = list(range(len(starts)))
    pilot = set(random.Random(1).sample(ids, 10))
    sample = sorted(random.Random(20261127).sample([i for i in ids if i not in pilot], 1000))

    def counts(indices):
        return dict(sorted(Counter(starts[i][0] for i in indices).items()))

    out = {'population by knot count': counts(ids), 'sample by knot count': counts(sample),
           'excluded pilot': sorted(pilot), 'archive size': len(ids)}
    for law, chunks in [('nae', 6), ('parity', 8)]:
        drawn, records = [], []
        for chunk in range(chunks):
            with (DATA / f'census_{law}_{chunk}.jsonl').open() as stream:
                rows = [json.loads(line) for _, line in zip(range(limit), stream)]
            part = [int(r['start'].split()[-1]) for r in rows]
            assert part == sample[chunk::chunks][:len(part)]
            drawn += part
            records.extend(rows)
        assert len(set(drawn)) == len(drawn)
        stage_sizes = {}
        for row, idx in zip(records, drawn):
            x = stage_sizes.setdefault(starts[idx][0], Counter())
            x.update({'starts': 1, 'positive at round 0': int(row['round 0']['bonds'] > 0)})
        out[law] = {'completed': len(drawn), 'min and max archive index': [min(drawn), max(drawn)],
                    'by knot count': stage_sizes, 'pilot intersection': sorted(pilot.intersection(drawn))}
    with (DATA / 'census_nae_m5.jsonl').open() as stream:
        indices = [int(json.loads(line)['start'].split()[-1]) for _, line in zip(range(limit), stream)]
    assert indices == sample[::10][:len(indices)]
    out['five-holder check count by knot count'] = counts(indices)
    sys.path.insert(0, str(HERE.parents[1] / 'NAE-LAYER-20261127-001' / 'referee-R1'))
    from growth_rule import advance, supports_of
    small = [i for i in ids if starts[i][0] == 3][:limit]
    above = []
    funded = 0
    for i in small:
        step = advance(supports_of(starts[i]))
        if step.status == 'funded':
            funded += 1
            n = len({x for k in step.supports for x in k})
            if n - len(step.supports) > 6:
                above.append(i)
    out['three-knot census, every-law count obstruction after one birth round'] = {
        'starts': len(small), 'funded': funded, 'distinctions minus knots exceeds six': len(above),
        'archive indices satisfying that inequality': above}
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('limit_per_file', type=int)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    start = perf_counter()
    result = run(args.limit_per_file)
    result['seconds'] = round(perf_counter() - start, 4)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
