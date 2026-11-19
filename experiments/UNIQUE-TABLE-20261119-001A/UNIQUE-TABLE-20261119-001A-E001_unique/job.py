"""Shared-runner job for UNIQUE-TABLE-20261119-001A-E001: one stage per case (population, controls, and FRESH-COUNT's mixed stages
of at most 10 junctions as the development set)."""
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import uniq as U  # noqa: E402

_POP = None


def setup(params):
    global _POP
    _POP = json.loads((HERE / 'population.json').read_text())


def cases():
    pop = _POP if _POP is not None else json.loads((HERE / 'population.json').read_text())
    for i, row in enumerate(pop['population']):
        yield f'pop-{i:04d}', {'part': 'population', **row}
    for i, row in enumerate(pop['controls']):
        yield f'ctrl-{i:04d}', {'part': 'control', **row}
    for seed in range(700000, 700060):
        yield f'dev-{seed}', {'part': 'dev', 'seed': seed}


def analyse(stars):
    stars = [frozenset(s) for s in stars]
    own = U.R.owners(stars)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    holders = Counter(js[0] for b, js in own.items() if len(js) == 1)
    table = U.full_table(stars)
    f = U.forcing(stars, table)
    out = {'junctions': len(stars), 'distinctions': len(own), 'largest': max(map(len, stars)), 'loose': len(loose),
           'max_loose_at_one_junction': max(holders.values()) if holders else 0,
           'forced': len(f['forced']), 'rank_F': f['rank_F'], 'rank_C': f['rank_C'], 'forced_spans_C': f['forced_spans_C'],
           'F_within_C': f['F_within_C'], 'eliminated': f['eliminated']}
    rivals, options, capped = U.same_code_rivals(stars)
    out['same_code_options'] = options
    out['same_code_capped'] = capped
    C_words = [U.word(s) for s in stars]
    checks = [U.check_rival(r, table, C_words) for r in rivals]
    out['same_code_rivals'] = len(rivals)
    out['rivals_verified'] = all(c['same_table'] and c['same_states'] for c in checks)
    out['rival_examples'] = [sorted(sorted(s) for s in r) for r in list(rivals)[:2]]
    if not f['forced_spans_C']:
        out['one_missing'] = U.one_missing(stars, table, f['forced'])
    return out


def run(case_id, p):
    if p['part'] == 'dev':
        rng = random.Random(p['seed'])
        a = rng.choice([3, 4])
        q = rng.choice([0.1, 0.2, 0.4])
        P = U.F.Presentation(a)
        res = []
        for _ in range(6):
            if len(P.bits_of) > 10:
                break
            st = [frozenset(b) for b in P.bits_of]
            if len(st) >= 3:
                r = analyse(st)
                r['round'] = P.rounds
                res.append(r)
            s = P.step(U.F.surplus(q), None, rng)
            if s is None or s['new'] == 0:
                break
        return {'stages': res}
    stars = U.stage(p['key'], p['round'])
    out = analyse(stars)
    out.update({'key': p['key'], 'round': p['round'], 'connectivity': p['connectivity'], 'part': p['part']})
    return out
