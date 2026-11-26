"""Challenge the assertion about a free return on the two recorded parity cuts."""
from argparse import ArgumentParser
from collections import Counter
from itertools import islice
import json
from pathlib import Path
import resource
from time import perf_counter

from exchange import exchange, holders, renaming
from growth import census, heldout, round_detail

HERE = Path(__file__).resolve().parent


def run(cases, arm, limit):
    counts = Counter()
    examples = []
    for name, start in islice(cases, limit):
        grown, status, _ = round_detail(start, arm=arm)
        counts[status] += 1
        if status != 'funded':
            continue
        result = exchange(grown, False)
        if not result.lawful:
            continue
        counts['lawful'] += 1
        if len(result.supports) != len(start):
            continue
        counts['equal holder count'] += 1
        mapping = renaming(start, result.supports)
        if mapping is None:
            continue
        counts['returns'] += 1
        examples.append({'start_id':name, 'start':list(map(sorted,start)),
                         'grown':list(map(sorted,grown)), 'exchange':list(map(sorted,result.supports)),
                         'loose':sorted(i for i,h in holders(grown).items() if len(h)==1),
                         'mapping':mapping})
    return {'counts':counts, 'returns':examples}


def main():
    args = ArgumentParser()
    args.add_argument('--limit',type=int)
    args.add_argument('--output',type=Path)
    opts = args.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1 << 30,1 << 30))
    start_time = perf_counter()
    tables = {}
    for arm in ('one_fewer','arity_floor'):
        for cohort, data in [('census',enumerate(census())),('heldout',heldout().items())]:
            tables[f'{arm} / {cohort}'] = run(data,arm,opts.limit)
    tables['seconds'] = round(perf_counter()-start_time, 4)
    if opts.output:
        opts.output.write_text(json.dumps(tables,indent=2)+'\n')
    print({k:v['counts'] for k,v in tables.items() if k!='seconds'},tables['seconds'])


if __name__ == '__main__':
    main()
