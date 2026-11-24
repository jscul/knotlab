"""Load the census (B2): the shared runner's final records (census/results.jsonl, latest record of each case) and the
supplementary records of the blocks completed outside the runner (census/extra_blocks.jsonl, deviations.md B14), merged
by block.  A block from extra_blocks.jsonl may come in several ranges of starts; they must cover its starts exactly once.
"""
import json
import os
import sys

from bref import OUT, ROOT

sys.path.insert(0, os.path.join(ROOT, 'scripts'))

N_CASES = 432


def load_census(census_dir=None):
    """Returns (census, state).  census: {'starts': [...86,032 start records in case order...], 'case_seconds',
    'case_peak_mb', 'sources': {case: 'runner' | 'extra_blocks'}}; None with a state string if incomplete."""
    from longrun import load_results
    census_dir = census_dir or os.path.join(OUT, 'census')
    if not os.path.exists(os.path.join(census_dir, 'results.jsonl')):
        return None, 'no results'
    rs = load_results(census_dir)
    recs = list(rs.values()) if isinstance(rs, dict) else list(rs)
    blocks = {r['case']: r for r in recs if r['status'] == 'ok'}
    sources = {c: 'runner' for c in blocks}
    extra = os.path.join(census_dir, 'extra_blocks.jsonl')
    ranges = {}
    if os.path.exists(extra):
        for line in open(extra):
            if not line.strip():
                continue
            r = json.loads(line)
            base = r['case'].split('[')[0]
            ranges.setdefault(base, []).append(r)
    problems = []
    for base, lines in ranges.items():
        if base in blocks:
            problems.append('%s finished in the runner and in extra_blocks' % base)
            continue
        lines.sort(key=lambda r: (r['start_range'] or [0])[0])
        n_all = lines[0]['block_starts']
        covered = []
        for r in lines:
            a, b = r['start_range'] if r['start_range'] else (0, n_all - 1)
            covered.extend(range(a, b + 1))
            if len(r['result']['starts']) != b - a + 1:
                problems.append('%s: range %d-%d has %d starts' % (r['case'], a, b, len(r['result']['starts'])))
        if covered != list(range(n_all)):
            problems.append('%s: ranges do not cover its %d starts exactly once' % (base, n_all))
            continue
        res = dict(lines[0]['result'])
        res['case'] = base
        res['starts'] = [s for r in lines for s in r['result']['starts']]
        res['seconds'] = round(sum(r['result']['seconds'] for r in lines), 2)
        blocks[base] = {'case': base, 'status': 'ok', 'result': res,
                        'seconds': round(sum(r['seconds'] for r in lines), 2), 'peak_rss_mb': None}
        sources[base] = 'extra_blocks'
    if problems:
        return None, '; '.join(problems)
    if len(blocks) < N_CASES:
        return None, '%d of %d blocks complete' % (len(blocks), N_CASES)
    starts = []
    for c in sorted(blocks):
        starts.extend(blocks[c]['result']['starts'])
    return {'starts': starts, 'case_seconds': [blocks[c]['seconds'] for c in blocks],
            'case_peak_mb': max((blocks[c].get('peak_rss_mb') or 0) for c in blocks),
            'sources': sources}, 'complete'


def law_state(rec, law):
    """'completed' or 'not completed' for one law of a start record (set-aside starts have no laws)."""
    c = rec['laws'][law]
    return 'not completed' if c.get('not_completed') else 'completed'


def law_view(rec, law):
    """The compact record of a law; for a run not completed, the record of its completed rounds."""
    c = rec['laws'][law]
    return c['partial'] if c.get('not_completed') else c


def has_off(rec, law):
    """True / False whether the run has a return giving parts off; None when not completed and none was found in its
    completed rounds (a return found there stays found; one at the uncompleted round is unknown)."""
    c = rec['laws'][law]
    if c.get('not_completed'):
        p = c.get('partial')
        if p is not None and p['n_off'] > 0:
            return True
        return None
    return c['n_off'] > 0
