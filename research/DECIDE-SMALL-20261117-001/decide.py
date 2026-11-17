"""Does the toolkit decide every small-orbit pattern? (DECIDE-SMALL-20261117-001, the thread's own code, 2026-11-17.)

Sample: KEEP-REACH's fair-coin sampler (run_sample.draw) with a new seed, 'DECIDE-1117-<i>':
- s uniform in {1, 2, 3} automaton states, each with an output flip and two transitions uniform;
- 1 to 4 placements (uniform), each a sorted triple of distinct slots uniform among the 3 (1 + s + s^2) slots.

Kept: small orbits (at most four addresses, so the block code builds) and alive at every depth. Each kept description is deduplicated
to its pattern, by the SHA-256 of its clause set at depth 12, before any test; only a pattern's first description is tested.

Tests, in this order, each proved in an earlier study:
- T1 forgetting on all assignments along blocks (BLOCK-REACH's forget.py): grows (Theorem F).
- T2 a two-orbit bond from level 3 at every s and depth tier (KEEP-REACH's two_orbit.py): bounded (Theorem K).
- T5 the product test along joined children on the component of level 3 (MODE-BOND's growth13.py): grows (Theorem G on the component).
- T3 forgetting on the values states take, from level 3 (KEEP-REACH's analyze_third.actual_forget, copied): grows (Theorem F').
- T4 orbit-and-block bonds, or stem bonds of depth 2, at every s and tier, searched to 8 members (CARRIER's two_block.py and
  head_bond.py): bounded (Theorem K*).

After the advisor's check, the run does not stop at the first undecided pattern. It runs every draw and collects every pattern that
none decides; the object of study is the first in draw order. Then:
- every tenth distinct pattern also runs all five tests, and no pattern may be both growing and bounded;
- every merge is rechecked at depth 14;
- each undecided pattern gets a second tier: T4 again with 12 members, stems of depth 3, and stem bonds of depth 2 with the lower
  orbit's children. It is labelled exhaustive or cap-limited;
- timeouts are rerun with a limit four times longer.

Usage: decide.py <draws>. Writes draws.jsonl, patterns.jsonl, undecided.json and summary.json."""
import hashlib
import json
import random
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ('research/DIRECT-REACH-20261115-001/exploratory', 'research/BLOCK-REACH-20261116-001', 'research/KEEP-REACH-20261117-001',
          'research/KEEP-REACH-20261117-001/exploratory', 'research/CARRIER-20261117-001', 'research/MODE-BOND-20261117-001',
          'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'):
    sys.path.insert(0, str(ROOT / p))
from window_tree import WindowTree, level_states  # noqa: E402
from forget import Steps  # noqa: E402
from two_orbit import every_depth_cross  # noqa: E402
from look_four import rectangular  # noqa: E402
from two_block import every_depth_block  # noqa: E402
from head_bond import every_depth_head  # noqa: E402
from growth13 import joined_automaton  # noqa: E402
from joined_census import light  # noqa: E402
from pattern import pattern  # noqa: E402

LIMIT = 120  # seconds per test; timeouts are rerun with four times this


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def draw(i):
    rng = random.Random('DECIDE-1117-%d' % i)
    s = rng.choice([1, 2, 3])
    sw = [rng.randrange(2) for _ in range(s)]
    d0 = [rng.randrange(s) for _ in range(s)]
    d1 = [rng.randrange(s) for _ in range(s)]
    slots = 3 * (1 + s + s * s)
    placements = [sorted(rng.sample(range(slots), 3)) for _ in range(rng.choice([1, 2, 3, 4]))]
    return [s, sw, d0, d1, placements]


def actual_forget(tree, jmin, levels=16, rmax=10):
    """KEEP-REACH's analyze_third.actual_forget (copied: that file runs its read-out on import)."""
    F = tree.feasible(20)
    r0 = next(r for r in range(19) if F[r] == F[r + 1])
    Fc = F[r0]
    st = level_states(tree, levels, [Fc] * (levels + 2))
    for r in range(1, rmax + 1):
        ok = True
        for j in range(jmin, levels + 1):
            for t, up in st[j]:
                fr = {(t, frozenset((x, x) for x in up))}
                for _ in range(r):
                    fr = {(tree.children[t2][ci][0], tree.step(t2, Fc, ci, J)) for t2, J in fr for ci in range(len(tree.children[t2]))}
                for c, J in fr:
                    Jf = frozenset((a, z) for a, z in J if z in Fc[c])
                    if Jf and not rectangular(Jf):
                        ok = False
        if ok:
            return r
    return None


def at(e, r, s, first, R):
    P = e['sequences']['r=%d' % r if r < R else 'r>=%d' % R]
    j = s - first
    if j < 0:
        return None
    while j >= len(P):
        j -= e['period']
    return P[j]


def carriers_bounded(tree):
    """T4: the least of the block and stem carriers at every s and tier (as CARRIER's check): (bounded, max)."""
    b = every_depth_block(tree, 3, cap=8)
    h = every_depth_head(tree, 3, 2, cap=8)
    reach = 2 * (b['start'] + b['period'] + h['start'] + h['period'] + 3) + b['period'] * h['period']
    vals = []
    for s in range(1, reach + 1):
        for r in range(0, max(b['r0'], h['r0']) + 3):
            v = [at(b, r, s, 1, b['r0'] + 1), at(h, r, s, h['first_s'], h['r0'])]
            v = [x for x in v if x is not None]
            vals.append(min(v) if v else None)
    ok = all(v is not None for v in vals)
    return ok, (max(vals) if ok else None)


def _timed(f, limit):
    signal.alarm(limit)
    try:
        return f()
    except Timeout:
        return 'timeout'
    finally:
        signal.alarm(0)


def tests(key, full=False, limit=None):
    """The five tests in order, each under its own time limit; with full, every test is run and the verdicts are all kept (the
    consistency check). A test that times out is recorded as 'timeout' and does not decide."""
    limit = limit or LIMIT
    tree = WindowTree(key)
    out, verdicts = {}, []

    def t1():
        st = Steps(tree)
        return st.least_r(12) if st.stable_closure() is not None else None

    def t2():
        e = every_depth_cross(tree, 3)
        return bool(e) and all(x is not None for seq in e['sequences'].values() for x in seq)

    def t5():
        return joined_automaton(light(key))['l0']

    def t3():
        return actual_forget(tree, 3)

    def t4():
        return carriers_bounded(tree)

    for name, f, good, verdict in (('T1_r', t1, lambda v: v is not None, 'grows (T1)'), ('T2', t2, lambda v: v is True, 'bounded (T2)'),
                                   ('T5_l0', t5, lambda v: v is not None, 'grows (T5)'), ('T3_r', t3, lambda v: v is not None, 'grows (T3)'),
                                   ('T4', t4, lambda v: v != 'timeout' and v[0], 'bounded (T4)')):
        v = _timed(f, limit)
        if name == 'T4' and v != 'timeout':
            out['T4'], out['T4_max'] = v
        else:
            out[name] = v
        if v != 'timeout' and good(v):
            verdicts.append(verdict)
            if not full:
                break
    if full:
        out['all_verdicts'] = verdicts
    timeouts = [k for k, v in out.items() if v == 'timeout']
    if verdicts:
        return out, verdicts[0]
    return out, ('timeout' if timeouts else 'undecided')


def second_tier(key):
    """For an undecided pattern: the least of four carriers at every s and tier (orbit-and-block and stem bonds of depth 2 searched to
    12 members, stems of depth 3 to 10, and stems of depth 2 with the lower orbit's children to 8). Bounded if finite everywhere."""
    import head_bond
    tree = WindowTree(key)
    head_bond.DP_BITS = 20
    try:
        es = [(every_depth_block(tree, 3, cap=12), 1, 'block'), (every_depth_head(tree, 3, 2, cap=12), 3, 'stem'),
              (every_depth_head(tree, 3, 3, cap=10), 4, 'stem'), (every_depth_head(tree, 3, 2, children=True, cap=8), 3, 'block')]
    finally:
        head_bond.DP_BITS = 18
    reach = 2 * sum(e['start'] + e['period'] for e, _, _ in es) + 6
    for e, _, _ in es:
        reach += e['period']
    rmax = max(e['r0'] for e, _, _ in es) + 3
    vals = []
    for s_ in range(1, reach + 1):
        for r in range(rmax):
            v = []
            for e, first, kind in es:
                R = e['r0'] + 1 if kind == 'block' and 'first_s' not in e else e['r0'] + (1 if e.get('children') else 0)
                v.append(at(e, r, s_, first, R))
            v = [x for x in v if x is not None]
            vals.append(min(v) if v else None)
    ok = all(v is not None for v in vals)
    return dict(bounded=ok, max=max(vals) if ok else None, missing=sum(v is None for v in vals))


if __name__ == '__main__':
    signal.signal(signal.SIGALRM, _alarm)
    draws = int(sys.argv[1])
    seen, first14, tally = {}, {}, {}
    merge_split, contradictions, pending = [], [], []
    with open(HERE / 'draws.jsonl', 'w') as fd, open(HERE / 'patterns.jsonl', 'w') as fp:
        for i in range(draws):
            key = draw(i)
            row = dict(index=i, key=key)
            try:
                tree = WindowTree(key)
            except ValueError:
                row['kept'] = 'large orbits'
                fd.write(json.dumps(row) + '\n')
                continue
            except Exception as ex:  # recorded, not dropped
                row['kept'] = 'error: ' + type(ex).__name__
                fd.write(json.dumps(row) + '\n')
                continue
            F = tree.feasible(20)
            r0 = next(r for r in range(19) if F[r] == F[r + 1])
            if not all(F[n][0] for n in range(r0 + 1)):
                row['kept'] = 'dies'
                fd.write(json.dumps(row) + '\n')
                continue
            K = pattern(key, 12)
            h = hashlib.sha256(K.tobytes() + bytes(str(K.shape), 'ascii')).hexdigest()[:16]
            row.update(kept='small, alive', pattern=h, first=h not in seen)
            fd.write(json.dumps(row) + '\n')
            if h in seen:
                seen[h] += 1
                K14 = pattern(key, 14)
                h14 = hashlib.sha256(K14.tobytes() + bytes(str(K14.shape), 'ascii')).hexdigest()[:16]
                if h14 != first14[h]:
                    merge_split.append((i, h))
                continue
            seen[h] = 1
            K14 = pattern(key, 14)
            first14[h] = hashlib.sha256(K14.tobytes() + bytes(str(K14.shape), 'ascii')).hexdigest()[:16]
            full = len(seen) % 10 == 0
            t0 = time.time()
            try:
                res, verdict = tests(key, full=full)
            except Exception as ex:
                res, verdict = {'error': type(ex).__name__ + ': ' + str(ex)[:80]}, 'error'
            if full and len({v.split()[0] for v in res.get('all_verdicts', [])}) > 1:
                contradictions.append((i, h, res['all_verdicts']))
            tally[verdict] = tally.get(verdict, 0) + 1
            fp.write(json.dumps(dict(index=i, pattern=h, key=key, verdict=verdict, full=full, seconds=round(time.time() - t0, 2), **res)) + '\n')
            fp.flush()
            fd.flush()
            if verdict in ('undecided', 'timeout', 'error'):
                pending.append(dict(index=i, pattern=h, key=key, verdict=verdict, **res))
            if len(seen) % 100 == 0:
                print(i, len(seen), tally, flush=True)
    # second pass: timeouts rerun with four times the limit; undecided patterns get the second tier
    for p in pending:
        if p['verdict'] == 'timeout':
            res, verdict = tests(p['key'], limit=LIMIT * 4)
            p.update(res, verdict=verdict if verdict != 'timeout' else 'timeout (x4)', rerun=True)
        if p['verdict'] == 'undecided':
            signal.alarm(LIMIT * 4)
            try:
                p['second_tier'] = second_tier(p['key'])
            except Timeout:
                p['second_tier'] = 'timeout'
            signal.alarm(0)
            t2 = p['second_tier']
            p['label'] = 'bounded by the second tier' if isinstance(t2, dict) and t2['bounded'] else 'undecided by both tiers'
    json.dump(dict(pending=pending, contradictions=contradictions, merge_split=merge_split), open(HERE / 'undecided.json', 'w'), indent=1)
    summary = dict(draws=draws, distinct_patterns=len(seen), kept_descriptions=sum(seen.values()), tally=tally,
                   full_checked=sum(1 for _ in range(len(seen) // 10)), contradictions=len(contradictions),
                   merges_split_at_14=len(merge_split), pending=[(p['index'], p['verdict'], p.get('label')) for p in pending])
    json.dump(summary, open(HERE / 'summary.json', 'w'), indent=1)
    print(summary, flush=True)
