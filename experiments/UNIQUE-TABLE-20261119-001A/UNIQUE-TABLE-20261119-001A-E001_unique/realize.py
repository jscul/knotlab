"""After the main run (not a prediction): (i) the same-equation rivals again with the frozen bound B4 applied (at most as many
junctions as the truth; the run's enumeration also offered the truth plus the loose set, n + 1 junctions, at single-block stages);
(ii) for each stage where the one-missing search found a code C' != C with the truth's table, every legal arrangement (B1-B4)
whose junctions span C', found by exhaustive search over n-sets of circuits of C', each verified by its own exact table.
Run: .venv/bin/python -B realize.py runs/unique-table [runs/unique-table-amend]  -> realize.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import uniq as U  # noqa: E402
from longrun import load_results  # noqa: E402


def other_codes(stars, table, forced):
    labels = sorted(U.R.owners(stars))
    idx = {b: i for i, b in enumerate(labels)}
    N = len(labels)
    Fw = [sum(1 << idx[b] for b in s) for s in forced]
    rF, basis = U.rank(Fw)
    Cw = [sum(1 << idx[b] for b in s) for s in stars]
    Cspan = U.span_words(Cw)
    free = [i for i in range(N) if i not in basis]
    target = {(idx[a], idx[b]): d for (a, b), d in table.items()}
    target.update({(j, i): d for (i, j), d in list(target.items())})
    codes = []
    for mask in range(1, 1 << len(free)):
        v = 0
        for j, i in enumerate(free):
            if mask >> j & 1:
                v |= 1 << i
        code = U.span_words(Fw + [v])
        if code != Cspan and U.code_table_matches(code, target, N) and frozenset(code) not in {frozenset(c) for c in codes}:
            codes.append(code)
    return codes, labels


def realizations(code, labels, n, table):
    """Legal arrangements with n junctions whose junctions span the code."""
    N = len(labels)
    words = sorted((w for w in code if w), key=lambda w: (w.bit_count(), w))
    circuits = []
    for w in words:
        if not any((w & c) == c for c in circuits):
            circuits.append(w)
    circuits = [c for c in circuits if c.bit_count() >= 3]
    found = []
    cover = [0] * N

    def rec(start, chosen):
        if len(chosen) == n:
            if all(1 <= x <= 2 for x in cover):
                junctions = [frozenset(labels[i] for i in range(N) if c >> i & 1) for c in chosen]
                r, _ = U.rank(chosen)
                if r == n and U.legal(junctions, labels):
                    edges = {}
                    own = U.R.owners(junctions)
                    if U.full_table(junctions) == table:
                        found.append(sorted(sorted(s) for s in junctions))
            return
        for k in range(start, len(circuits)):
            c = circuits[k]
            bits = [i for i in range(N) if c >> i & 1]
            if any(cover[i] >= 2 for i in bits):
                continue
            if any((c & d).bit_count() > 1 for d in chosen):
                continue
            for i in bits:
                cover[i] += 1
            rec(k + 1, chosen + [c])
            for i in bits:
                cover[i] -= 1
            if len(found) > 20:
                return
    rec(0, [])
    return found, len(circuits)


def main(*dirs):
    recs = {}
    for d in dirs:
        for c, r in load_results(d).items():
            if c not in recs or r['status'] == 'ok':
                recs[c] = r
    out = {'b4_same_code': Counter(), 'other_codes': []}
    for c, r in sorted(recs.items()):
        if r['status'] != 'ok' or c.startswith('dev'):
            continue
        res = r['result']
        stars = U.stage(res['key'], res['round'])
        n = len(stars)
        if res['same_code_rivals']:
            rivals, _, _ = U.same_code_rivals(stars)
            kept = [x for x in rivals if len(x) <= n]
            out['b4_same_code'][f"{res['part']}:{'rival' if kept else 'none'}"] += 1
            res['b4_rivals'] = len(kept)
        om = res.get('one_missing', {})
        if om.get('codes_matching_other_than_C'):
            table = U.full_table(stars)
            f = U.forcing(stars, table)
            codes, labels = other_codes(stars, table, f['forced'])
            for code in codes:
                reals, ncirc = realizations(code, labels, n, table)
                out['other_codes'].append({'case': c, 'key': res['key'], 'round': res['round'], 'junctions': n,
                                           'connectivity': res['connectivity'], 'circuits': ncirc,
                                           'legal_realizations': len(reals), 'example': reals[:1],
                                           'truth': sorted(sorted(s) for s in stars)})
    out['b4_same_code'] = dict(out['b4_same_code'])
    out['stages_with_other_code'] = len({x['case'] for x in out['other_codes']})
    out['stages_with_a_legal_other_arrangement'] = len({x['case'] for x in out['other_codes'] if x['legal_realizations']})
    dest = ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'realize.json').write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'other_codes'}, indent=1))
    for x in out['other_codes'][:6]:
        print(json.dumps({k: x[k] for k in ('case', 'junctions', 'connectivity', 'circuits', 'legal_realizations', 'example', 'truth')}))


if __name__ == '__main__':
    main(*sys.argv[1:])
