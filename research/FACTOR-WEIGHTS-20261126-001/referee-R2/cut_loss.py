"""Count old states that actually lose all completions in the original retained NAE histories."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import resource
import sys
from time import perf_counter


def run(limit):
    root = Path(__file__).resolve().parents[3]
    directory = root / 'research/FORBID-EDITS-20261126-001'
    sys.path.insert(0, str(directory))
    import forbid
    census = json.loads((directory / 'starts.json').read_text())
    sample = random.Random(20261129).sample(range(len(census)), 300)[:limit]
    totals = {}
    for arm in forbid.ARMS:
        tally = Counter()
        loss_cases = []
        for index in sample:
            stages = [forbid.supports_of(census[index])]
            births = []
            for _ in range(2):
                next_stage, status, produced = forbid.grown(stages[-1], 'nae', arm)
                if status != 'funded':
                    break
                stages.append(next_stage)
                births.append(produced)
            if not births or len(set.union(*map(set, stages[-1]))) > 14:
                continue
            tally['kept'] += 1
            for r, batch in enumerate(births):
                cuts = [b['inputs'] for b in batch if not b['fresh']]
                if not cuts:
                    continue
                names = sorted(set.union(*map(set, stages[r])))
                def masks(rows):
                    return [sum(1 << names.index(d) for d in row) for row in rows]
                old_masks = masks(stages[r])
                cut_masks = masks(cuts)
                old = lost = 0
                for word in range(1 << len(names)):
                    if all((word & m) not in (0, m) for m in old_masks):
                        old += 1
                        lost += any((word & m) in (0, m) for m in cut_masks)
                tally['rounds_with_old_only_rule'] += 1
                if lost:
                    loss_cases.append(dict(index=index, round=r+1, old_states=old, lost=lost))
        tally['histories_with_loss'] = len({row['index'] for row in loss_cases})
        totals[arm] = dict(counts=tally, lost=loss_cases)
    return totals


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--starts', type=int, required=True)
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))
    t = perf_counter()
    out = run(args.starts)
    out.update(starts=args.starts, seconds=round(perf_counter()-t, 4),
               peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print(json.dumps(out, indent=2))
