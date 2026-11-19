"""Shared-runner job for HUNT-SHORTEN-20261119-001A part 3 (the advisor's self-pairs: a real test of Claim B on reached stages).
Every census start regrown (complete rounds, cheapest counts); every open stage of round 1 or later with at most 14 junctions.
For each: every isometry of its full table onto itself taken on holder twin classes (plib.carriers, cap 2,000; those breaking holder
classes are not enumerated).  An isometry that carries the
equation space onto itself is skipped (Claim B* covers it).  For the others: does it keep what the round reads (EXTEND-ROUND's R)?
If so (at most 20 per stage), the census's own next stage is the round's output; the extension (EXTEND-ROUND's construction) is
checked entry by entry against the next stage's full table (bonds when at most 15 vertices, else exact_table_v2 with no bound under
a 300 s alarm per stage).  A failure is a counterexample to Claim B.  Shards of 100 starts."""
import importlib.util
import signal
import sys
from collections import Counter
from pathlib import Path

from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'))
import census_job as C  # noqa: E402
_e = importlib.util.spec_from_file_location('extend_round', ROOT / 'experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.py')
EX = importlib.util.module_from_spec(_e)
sys.modules[_e.name] = EX
_e.loader.exec_module(EX)
L = EX.L
FULL = 14
CAP_AUT = 2000
CAP_TEST = 20
LIMIT = 300
_ARR = None


def setup(params):
    global _ARR
    _ARR = C.CJ.load()


def cases():
    data = _ARR if _ARR is not None else C.CJ.load()
    for s in range(0, len(data), 100):
        yield f'census-{s // 100:04d}', {'lo': s, 'hi': min(len(data), s + 100)}


def stage_test(a, a1, c, examples, where):
    ta, la = L.table(a)
    R = EX.reading(a)
    tested = 0
    t1 = None
    # automorphisms taken on holder twin classes (plib.carriers): permutations inside a class carry the states and keep the
    # reading, so this loses nothing up to them; automorphisms that break holder classes are not enumerated (stated)
    for phi, carries in L.carriers(a, a, ta, ta, CAP_AUT):
        if phi == 'cap':
            c['aut_capped'] += 1
            break
        if carries:
            c['auts_carrying_states'] += 1
            continue
        c['auts_not_carrying_states'] += 1
        psi = EX.keeps_reading(phi, a, a, R, R)
        if psi is None:
            continue
        c['auts_keeping_reading_not_states'] += 1
        if tested >= CAP_TEST:
            continue
        tested += 1
        phi2 = EX.extension(phi, psi, a, a, a1, a1)
        if phi2 is None:
            c['rounds_do_not_correspond'] += 1
            continue
        if t1 is None:
            t1 = EX.full_table(a1)
        ta1, la1 = t1
        ok = all(ta1[(x, y)] == ta1[tuple(sorted((phi2[x], phi2[y])))] for (x, y) in ta1)
        c['extensions_isometry' if ok else 'extensions_fail_CLAIM_B'] += 1
        if not ok and len(examples) < 5:
            examples.append({'where': where, 'stage': [sorted(s) for s in a], 'phi': {str(k): v for k, v in phi.items()}})
    c['stages_with_reading_keeping_nonstate_aut'] += tested > 0


def run(case_id, p):
    data = _ARR if _ARR is not None else C.CJ.load()
    c = Counter()
    examples = []
    for i in range(p['lo'], p['hi']):
        P = C.S.from_junctions(C.A.stars_of(data[i]))
        stars = [frozenset(b) for b in P.bits_of]
        for r in range(1, C.CJ.RMAX + 1):
            res = P.step(C.S.gf2(C.F.fewest), None)
            if res is None or res['new'] == 0:
                break
            nxt = [frozenset(b) for b in P.bits_of]
            if r >= 2 and len(stars) <= FULL and L.live_set(stars):
                # stars is the stage of round r - 1 >= 1; nxt is its next stage
                c['open_stages'] += 1
                c['meet_once' if L.max_shared(stars) < 2 else 'two_shared'] += 1
                signal.signal(signal.SIGALRM, EX._late)
                signal.alarm(LIMIT)
                try:
                    stage_test(stars, nxt, c, examples, (i, r - 1))
                except EX.Late:
                    c['late'] += 1
                finally:
                    signal.alarm(0)
            stars = nxt
            if len(stars) > FULL + 40:
                break
    return {'counts': dict(c), 'examples': examples}
