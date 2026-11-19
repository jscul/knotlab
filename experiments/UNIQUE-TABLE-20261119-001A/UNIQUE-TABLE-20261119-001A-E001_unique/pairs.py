"""The six different-states pairs (verify_rivals.json), after the main run (the coordinator's three questions; not predictions):
(1) growth: one and two rounds of the cheapest counts from each arrangement's junctions alone: the joins made (which distinctions
    each new junction consumes, and its fresh count), counts per size, and the two grown arrangements' exact tables compared with
    fresh distinctions named by what they grew from;
(2) reachability: the junctions holding no loose distinction taken as a start (a census-type start: at most five knots of three to
    five places, connected), grown one round, compared with the arrangement;
(3) mechanism and other readings: the exchanged distinctions and their roles; three-way readings (least circuit holding a triple);
    the disagreement count (allowed states in which two distinctions differ).
Run: .venv/bin/python -B pairs.py  -> pairs.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import uniq as U  # noqa: E402
S, F = U.S, U.F
A = ROOT / 'artifacts/UNIQUE-TABLE-20261119-001A/UNIQUE-TABLE-20261119-001A-E001_unique'


def grow(junctions, rounds):
    """Rounds of the cheapest counts from these junctions alone; fresh distinctions renamed ('f', consumed..., k)."""
    names = {}
    cur = [sorted(s) for s in junctions]
    menus = []
    for _ in range(rounds):
        idx = {}
        flat = sorted({b for s in cur for b in s}, key=str)
        for i, b in enumerate(flat):
            idx[b] = i
        P = S.from_junctions([[idx[b] for b in s] for s in cur])
        P.linalg = False
        old = len(cur)
        res = P.step(S.gf2(F.fewest), None)
        if res is None:
            menus.append('stall')
            break
        inv = {i: b for b, i in idx.items()}
        new = []
        menu = []
        for j in range(old, len(P.bits_of)):
            consumed = sorted((inv[b] for b in P.bits_of[j] if b in inv), key=str)
            fresh = [b for b in P.bits_of[j] if b not in inv]
            tag = tuple(consumed)
            fresh_names = [('f',) + tuple(map(str, tag)) + (k,) for k in range(len(fresh))]
            new.append(consumed + fresh_names)
            menu.append((tuple(map(str, tag)), len(fresh)))
        menus.append(sorted(menu))
        cur = cur + new
    return [frozenset(s) for s in cur], menus


def table_named(junctions):
    labels = sorted({b for s in junctions for b in s}, key=str)
    idx = {b: i for i, b in enumerate(labels)}
    t = U.full_table([frozenset(idx[b] for b in s) for s in junctions])
    return {(labels[a], labels[b]): d for (a, b), d in t.items()}


def circuits(junctions):
    labels = sorted({b for s in junctions for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    code = U.span_words([sum(1 << idx[b] for b in s) for s in junctions])
    out = []
    for w in sorted((w for w in code if w), key=lambda w: (w.bit_count(), w)):
        if not any((w & c) == c for c in out):
            out.append(w)
    return out, labels, code


def triple_readings(junctions):
    cs, labels, _ = circuits(junctions)
    best = {}
    for c in cs:
        bits = [labels[i] for i in range(len(labels)) if c >> i & 1]
        for t in combinations(bits, 3):
            best.setdefault(t, len(bits) - 1)
    return best


def disagreement(junctions):
    """Allowed states (solutions of the junction equations, right-hand sides 0) in which two distinctions differ."""
    _, labels, code = circuits(junctions)
    N = len(labels)
    r, _ = U.rank(list(code))
    total = 1 << (N - r)
    two = {w for w in code if w.bit_count() == 2}
    out = {}
    for a, b in combinations(range(N), 2):
        out[(labels[a], labels[b])] = 0 if (1 << a | 1 << b) in two else total // 2
    return out


def reachable(junctions):
    own = U.R.owners(junctions)
    start = [s for s in junctions if all(len(own[b]) == 2 for b in s)]
    if not start or len(start) > 5 or any(not 3 <= len(s) <= 5 for s in start):
        return {'start_knots': len(start), 'census_type_start': False}
    grown, menus = grow(start, 1)
    rest = [s for s in junctions if s not in start]
    start_bits = {b for s in start for b in s}
    want = sorted((tuple(sorted(map(str, s & start_bits))), len(s - start_bits)) for s in rest)
    got = menus[0] if menus and menus[0] != 'stall' else None
    return {'start_knots': len(start), 'start_sizes': sorted(map(len, start)), 'census_type_start': True,
            'one_round_from_start_equals_arrangement': got == want}


def main():
    rows = json.loads((A / 'verify_rivals.json').read_text())
    seen, out = set(), []
    for r in rows:
        if r['case'] in seen:
            continue
        seen.add(r['case'])
        truth = [frozenset(s) for s in r['truth']]
        rival = [frozenset(s) for s in r['rival']]
        own_t, own_r = U.R.owners(truth), U.R.owners(rival)
        only_t, only_r = ([frozenset(x) for x in side] for side in r['junctions_that_differ'])
        moved = set().union(*only_t) ^ set().union(*only_r) if only_t and only_r else set()
        touched = sorted(set().union(*only_t) | set().union(*only_r))
        row = {'case': r['case'], 'key': r['key'], 'round': r['round'], 'junctions': len(truth),
               'differing_truth': [sorted(x) for x in only_t], 'differing_rival': [sorted(x) for x in only_r],
               'junctions_differing': len(only_t),
               'distinctions_changing_holders': sorted(b for b in touched if
                                                       sorted(j for j, x in enumerate(truth) if b in x) !=
                                                       sorted(j for j, x in enumerate(truth) if b in x) or True
                                                       if Counter(x for x in only_t if b in x) != Counter(x for x in only_r if b in x)),
               'roles_truth': {str(b): len(own_t[b]) for b in touched},
               'roles_rival': {str(b): len(own_r[b]) for b in touched}}
        for rounds in (1, 2):
            gt, mt = grow(truth, rounds)
            gr, mr = grow(rival, rounds)
            row[f'round_{rounds}'] = {'same_joins': mt == mr,
                                      'sizes_truth': dict(sorted(Counter(map(len, gt)).items())),
                                      'sizes_rival': dict(sorted(Counter(map(len, gr)).items())),
                                      'junctions': [len(gt), len(gr)]}
            if mt == mr:
                tt, tr = table_named(gt), table_named(gr)
                row[f'round_{rounds}']['tables_equal'] = tt == tr
                row[f'round_{rounds}']['entries_differing'] = sum(1 for p in tt if tt[p] != tr.get(p))
        row['reachable_truth'] = reachable(truth)
        row['reachable_rival'] = reachable(rival)
        t3t, t3r = triple_readings(truth), triple_readings(rival)
        keys = set(t3t) | set(t3r)
        row['three_way_readings_differing'] = sum(1 for k in keys if t3t.get(k) != t3r.get(k))
        row['three_way_readings'] = len(keys)
        dt, dr = disagreement(truth), disagreement(rival)
        row['disagreement_counts_equal'] = dt == dr
        out.append(row)
    (A / 'pairs.json').write_text(json.dumps(out, indent=1, default=list))
    for row in out:
        print(json.dumps({k: row[k] for k in ('case', 'junctions', 'differing_truth', 'differing_rival', 'roles_truth', 'roles_rival',
                                              'round_1', 'round_2', 'reachable_truth', 'reachable_rival',
                                              'three_way_readings_differing', 'disagreement_counts_equal')}, default=list))


if __name__ == '__main__':
    main()
