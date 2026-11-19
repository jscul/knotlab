"""THREE-WAY-20261119-001A: do three-way readings complete the bond-distance table?

Three-way reading t(x, y, z) = (smallest circuit of the equation space holding x, y and z) - 1, or 'none' when no circuit holds
all three.  A function of the equation space, like the pair table.
Parts:
- six: for each of UNIQUE-TABLE's 11 different-states rivals (verify_rivals.json), the number of triples whose reading differs
  from the truth's on the same names;
- undecided: UNIQUE-TABLE's 21 undecided stages, forcing with triples added (a triple at reading d lies in a circuit of d + 1
  distinctions all of whose pairs are at most d and triples at most d; a unique such set is forced; a pair candidate holding a
  triple read above its size less one is dropped), and the one-missing search requiring the code's pair and triple readings both to
  match;
- grown: for each of GROWN-PAIR's 152 different-states groups, whether some isomorphism of the pair tables also carries the
  three-way readings (one isomorphism test of the pair table with every triple attached as a vertex labelled by its reading).
Run: .venv/bin/python -B triples.py  -> triples.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UNIQ = ROOT / 'experiments/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'
GP = ROOT / 'experiments/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs'
sys.path.insert(0, str(UNIQ))
import uniq as U  # noqa: E402
import importlib.util  # noqa: E402
_s = importlib.util.spec_from_file_location('gp_pairs2', GP / 'pairs2.py')
P2 = importlib.util.module_from_spec(_s)
sys.modules[_s.name] = P2
_s.loader.exec_module(P2)
A_UNIQ = ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'
A_GP = ROOT / 'artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs'


def circuits_of(stars):
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    code = U.span_words([sum(1 << idx[b] for b in s) for s in stars])
    out = []
    for w in sorted((w for w in code if w), key=lambda w: (w.bit_count(), w)):
        if not any((w & c) == c for c in out):
            out.append(w)
    return out, labels


def readings(stars, k):
    cs, labels = circuits_of(stars)
    best = {}
    for c in cs:
        bits = [labels[i] for i in range(len(labels)) if c >> i & 1]
        for t in combinations(bits, k):
            best.setdefault(t, len(bits) - 1)
    return {t: best.get(t, 'none') for t in combinations(labels, k)}


def part_six():
    rows = json.loads((A_UNIQ / 'verify_rivals.json').read_text())
    out = []
    for r in rows:
        t3t = readings([frozenset(s) for s in r['truth']], 3)
        t3r = readings([frozenset(s) for s in r['rival']], 3)
        out.append({'case': r['case'], 'triples': len(t3t), 'differing': sum(1 for t in t3t if t3t[t] != t3r[t])})
    return out


def forcing3(stars, table, t3):
    """UNIQUE-TABLE's forcing with triples added (candidates from both pairs and triples; a candidate must not hold a triple read
    above its size less one)."""
    labels = sorted(U.R.owners(stars))
    K = max(map(len, stars))
    m = U.min_circuit(table, labels)
    by_size = {s: U.cliques(table, labels, s) for s in range(3, K + 1)}
    ok = {s: [c for c in cl if all(t3[t] != 'none' and t3[t] <= s - 1 for t in combinations(sorted(c), 3))] for s, cl in by_size.items()}
    containing = {}
    for s, cl in ok.items():
        for c in cl:
            for p in combinations(sorted(c), 2):
                containing.setdefault(('p', s, p), []).append(c)
            for t in combinations(sorted(c), 3):
                containing.setdefault(('t', s, t), []).append(c)
    keys = [('p', d + 1, p) for p, d in table.items() if 3 <= d + 1 <= K] + \
           [('t', d + 1, t) for t, d in t3.items() if d != 'none' and 3 <= d + 1 <= K]
    forced, dead = set(), set()
    for _ in range(20):
        Fspan = U.span_words([U.word(c) for c in forced])
        new = set()
        for key in keys:
            alive = []
            for c in containing.get(key, []):
                if c in dead:
                    continue
                if c not in forced:
                    w = U.word(c)
                    if any(f != w and ((f & w) == f or (f & w) == w) for f in (U.word(x) for x in forced)) or \
                            U.light({x ^ w for x in Fspan}, m, labels):
                        dead.add(c)
                        continue
                alive.append(c)
            if len(alive) == 1 and alive[0] not in forced:
                new.add(alive[0])
        if not new:
            break
        forced |= new
    rC, _ = U.rank([U.word(s) for s in stars])
    rF, _ = U.rank([U.word(s) for s in forced])
    rFC, _ = U.rank([U.word(s) for s in forced] + [U.word(s) for s in stars])
    return forced, rF, rC, rF == rC and rFC == rC


def code_triples_match(code, labels, t3):
    words = sorted((w for w in code if w), key=lambda w: (w.bit_count(), w))
    cs = []
    for w in words:
        if not any((w & c) == c for c in cs):
            cs.append(w)
    best = {}
    for c in cs:
        bits = [labels[i] for i in range(len(labels)) if c >> i & 1]
        for t in combinations(bits, 3):
            best.setdefault(t, len(bits) - 1)
    return all(best.get(t, 'none') == v for t, v in t3.items())


def undecided_one(row):
    stars = U.stage(row['key'], row['round'])
    table = U.full_table(stars)
    t3 = readings(stars, 3)
    forced, rF, rC, spans = forcing3(stars, table, t3)
    res = {'key': row['key'], 'round': row['round'], 'rank_C': rC, 'rank_F_pairs_and_triples': rF, 'spans': spans}
    if not spans and rF == rC - 1:
        labels = sorted(U.R.owners(stars))
        idx = {b: i for i, b in enumerate(labels)}
        N = len(labels)
        Fw = [sum(1 << idx[b] for b in s) for s in forced]
        _, basis = U.rank(Fw)
        Cspan = U.span_words([sum(1 << idx[b] for b in s) for s in stars])
        free = [i for i in range(N) if i not in basis]
        if len(free) <= 18:
            target = {(idx[a], idx[b]): d for (a, b), d in table.items()}
            target.update({(j, i): d for (i, j), d in list(target.items())})
            other = 0
            for mask in range(1, 1 << len(free)):
                v = 0
                for j, i in enumerate(free):
                    if mask >> j & 1:
                        v |= 1 << i
                code = U.span_words(Fw + [v])
                if code != Cspan and U.code_table_matches(code, target, N) and code_triples_match(code, labels, t3):
                    other += 1
            res['one_missing_other_codes'] = other
        else:
            res['one_missing_other_codes'] = 'capped'
    rivals, _, _ = U.same_code_rivals(stars)
    res['same_code_rivals_within_bound'] = sum(1 for r in rivals if len(r) <= len(stars))
    return res


def with_triples(stars):
    g = P2.coloured_table(stars)
    labels = sorted({b for s in stars for b in s})
    t3 = readings(stars, 3)
    for k, (t, v) in enumerate(sorted(t3.items())):
        g.add_node(('t', k), k=('t', str(v)))
        for b in t:
            g.add_edge(('t', k), ('b', b), d='in')
    return g


def grown_one(group):
    a, b = (frozenset(s) for s in group['reps'][0]['stars']), (frozenset(s) for s in group['reps'][1]['stars'])
    a, b = list(a), list(b)
    return {'distinctions': group['distinctions'], 'pair_tables_isomorphic': P2.iso(P2.coloured_table(a), P2.coloured_table(b)),
            'triples_also_isomorphic': P2.iso(with_triples(a), with_triples(b))}


def main():
    out = {'six': part_six()}
    pop = json.loads((UNIQ / 'population.json').read_text())['population'] + \
        json.loads((UNIQ / 'population_unknown.json').read_text())['population']
    final = json.loads((A_UNIQ / 'final.json').read_text())
    # the undecided stages, recomputed from the run records
    sys.path.insert(0, str(ROOT / 'scripts'))
    from longrun import load_results
    recs = {}
    for d in ('runs/unique-table', 'runs/unique-table-amend2'):
        for c, r in load_results(str(ROOT / d)).items():
            if c not in recs or r['status'] == 'ok':
                recs[c] = r
    undecided = []
    for c, r in sorted(recs.items()):
        if not c.startswith('pop') or r['status'] != 'ok':
            continue
        res = r['result']
        decided = res['forced_spans_C'] or (res.get('one_missing', {}).get('applicable') and not res['one_missing'].get('capped'))
        if not decided:
            undecided.append({'key': res['key'], 'round': res['round']})
    out['undecided_input'] = len(undecided)
    with Pool(8) as pool:
        out['undecided'] = pool.map(undecided_one, undecided, chunksize=1)
        groups = json.loads((A_GP / 'other_states.json').read_text())['group_list']
        out['grown'] = pool.map(grown_one, groups, chunksize=2)
    s = {'six_rivals_separated': sum(1 for x in out['six'] if x['differing'] > 0), 'six_rivals': len(out['six']),
         'undecided_now_forced': sum(1 for x in out['undecided'] if x['spans']),
         'undecided_one_missing': dict(Counter(str(x.get('one_missing_other_codes')) for x in out['undecided'] if not x['spans'])),
         'undecided_with_same_code_rivals': sum(1 for x in out['undecided'] if x['same_code_rivals_within_bound']),
         'grown_groups': len(out['grown']),
         'grown_separated_by_triples': sum(1 for x in out['grown'] if x['pair_tables_isomorphic'] and not x['triples_also_isomorphic']),
         'grown_not_separated': sum(1 for x in out['grown'] if x['triples_also_isomorphic'])}
    dest = ROOT / 'artifacts/THREE-WAY-20261119-001A/THREE-WAY-20261119-001A-E001_triples'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'triples.json').write_text(json.dumps({'summary': s, **out}, indent=1, default=str))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main()
