"""Census of parts under rule Q (test (c)): shared code.

Frozen definitions: research/ONE-PARENT-REREAD-20261123-001A/preregistration.md, "(c) Census of parts", "Uniform arm",
"Mixed arm", "Control", "The 27 liftable parts".  Readings: deviations.md of this folder.

Recorded code reused read-only (imported by path, never changed):
  * ticket C of the re-read epic, `cstudy.py` (imported as `cs`): ticket B's starts, targets and record, `start_struct`,
    the evaluator `Eval` (ticket B's exact hiding test, float screen and exact Fraction score), `full_check` (ticket B's
    word-by-word enumeration of the four finished structures), `allowed_words` and `obs_index`; and `arm1.py`:
    `effective_rows` (the reduction of ticket C's deviations A9, called here with this study's own set of reduced columns,
    the newborns of the stage's round with two or more INPUTS; re-verified in q_rowg.py);
  * through cs: ticket B's `common.py` (`bc`: `stage_tables`, `brute_table`, `normalize`, `is_excess`, `fmt_knot`) and
    `verify_excess.py` (`bve`), ticket A's `rlaw.py` (with `rlaw.USE_C = False`).
  * this folder's `qlaw.py` (rule Q).
"""
import itertools
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import qlaw  # noqa: E402  (asserts rlaw's sha256)

ROOT = qlaw.ROOT
C_EXP = ROOT / 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach'
C_ART = ROOT / 'artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001_reread_reach'
sys.path.insert(1, str(C_EXP))
import cstudy as cs  # noqa: E402
import arm1 as c_arm1  # noqa: E402

assert cs.rlaw_sha() == qlaw.RLAW_SHA
assert qlaw.rlaw.USE_C is False
bc = cs.bc
bve = cs.bve
ART = qlaw.ART

ROUNDS = 3                 # "for 3 rounds"
DMAX = 20                  # "or until a stage passes 20 distinctions"
CHOICE_CAP = 64            # "under every round-1 choice when there are at most 64"
CHOICE_MORE = 62           # "otherwise under 62 more drawn"
SEED_CHOICE = 2026112370
LAW_CAP = 4096             # "every assignment when there are at most 4,096, otherwise 4,096 drawn"
SEED_LAW = 2026112371
CH3 = ('even', 'odd', 'nae')   # law index of a newborn: 0 even parity, 1 odd parity, 2 not-all-equal
NAE = 2
KIND_CODE = {'O': 0, 'N': 1, 'choice': 2}


def population():
    """The census parts: two-holder founder starts of ticket B with no hidden excess at stage 0 that do not stall at
    round 1 under ordinary growth (ticket B's record), in start order."""
    S = cs.starts()
    B = cs.b_lines('c3')
    return [i for i in range(len(S)) if cs.start_class(S[i]) == 'two' and not B[i]['stage0_excess']
            and B[i]['outcome'] != 'stall']


def stalled_two_holder():
    S = cs.starts()
    B = cs.b_lines('c3')
    return [i for i in range(len(S)) if cs.start_class(S[i]) == 'two' and not B[i]['stage0_excess']
            and B[i]['outcome'] == 'stall']


def liftable_parts():
    """The 27 liftable parts: ticket C's arm-2 lines with a non-empty `gains` (read compressed)."""
    out = {}
    for f in sorted(C_ART.glob('arm2_all_*.jsonl.gz')):
        for l in cs.jl_load(f):
            if l['gains']:
                out[l['si']] = l
    return out


# ======================================================================================================================
# Growth under rule Q with the census stop
# ======================================================================================================================
def grow_census(stars, conv='O', choice=None, reread=True, rounds=ROUNDS, dmax=DMAX):
    """Rule Q (qlaw.QGrowth, structure rule not-all-equal: every birth has at least one fresh distinction; no knot cap),
    for `rounds` rounds or until a stage has more than `dmax` distinctions (that stage is kept), checked before each
    round as in tickets B and C.  Round 1 uses `choice` ({birth index: distinction}) for its re-reading births when
    given; every other re-read is by convention `conv` (choice histories are built with conv 'O').
    Returns a dict: stars, n_at, D_at, births (per round: list of dicts parents, inputs, fresh, reread, shared, loose),
    outcome, stall (shortages when it stalled: [knot, excess, born under Q]), holders_at."""
    g = qlaw.QGrowth(stars, 'nae', conv, reread=reread, bound_next=False)
    n_at = [len(g.stars)]
    D_at = [len(g.holders)]
    births = []
    outcome, stall = None, None
    while True:
        if len(g.rounds) >= rounds:
            outcome = 'rounds'
            break
        if D_at[-1] > dmax:
            outcome = 'distinctions'
            break
        r = g.plan(None, choice=(choice if len(g.rounds) == 0 else None))
        if r.status == 'closed':
            outcome = 'closed'
            break
        if r.status == 'stall':
            outcome = 'stall'
            stall = [[int(k), int(x), bool(k >= g.n_founders)] for k, x in r.shortages]
            break
        assert r.status == 'extend', r.status
        if choice is not None and len(g.rounds) == 0:
            got = {i for i, prow in enumerate(r.paid) if any(prow)}
            assert got == set(choice), 'the choice does not cover every re-reading birth of round 1'
        rec = []
        for ps, row, prow, f in zip(r.parents, r.inputs, r.paid, r.fresh, strict=True):
            rr = bool(any(prow))
            took_shared = [d for d in row if len(g.holders[d]) >= 2]
            assert (len(took_shared) == 1) == rr and (rr or not took_shared), 'a birth took a shared distinction outside rule Q'
            rec.append(dict(parents=list(ps), inputs=list(row), fresh=int(f), reread=rr,
                            shared=(row[-1] if rr else None), loose=list(row[:len(ps)])))
        g.apply(r)
        births.append(rec)
        n_at.append(len(g.stars))
        D_at.append(len(g.holders))
    return dict(stars=[tuple(s) for s in g.stars], n_at=n_at, D_at=D_at, births=births, outcome=outcome, stall=stall,
                holders_at=g.holders_at)


def round1_options(stars):
    """Round 1 under rule Q: [(birth index, parent, [shared distinctions of the parent])] for every one-parent birth
    whose parent shares a distinction at the start of the round; and the planned round (convention O).
    Round 1 has the groups of ordinary growth, so the births and their parents do not depend on the choice."""
    g = qlaw.QGrowth(stars, 'nae', 'O')
    r = g.plan(None)
    if r.status != 'extend':
        return r, []
    opts = [(i, ps[0], g.shared_of(ps[0])) for i, ps in enumerate(r.parents) if len(ps) == 1 and g.shared_of(ps[0])]
    return r, opts


def choice_dict(opts, idx):
    return {i: sh[j] for (i, _, sh), j in zip(opts, idx, strict=True)}


def part_choices(opts, tid, mask):
    """The round-1 choice histories of a part: every choice when there are at most 64, else 62 more drawn (distinct,
    none equal to the choice of convention O or N; each birth's option uniform and independent) by
    numpy default_rng([2026112370, target, start bitmask]), one generator per part.
    Returns (list of index tuples, mode 'all' | 'drawn', total, index of O, index of N)."""
    sizes = [len(sh) for _, _, sh in opts]
    total = math.prod(sizes)
    iO = tuple(0 for _ in sizes)
    iN = tuple(s - 1 for s in sizes)
    if total <= CHOICE_CAP:
        return list(itertools.product(*[range(s) for s in sizes])), 'all', total, iO, iN
    rng = np.random.default_rng([SEED_CHOICE, tid, mask])
    seen = {iO, iN}
    out = []
    while len(out) < CHOICE_MORE:
        idx = tuple(int(rng.integers(0, s)) for s in sizes)
        if idx in seen:
            continue
        seen.add(idx)
        out.append(idx)
    return out, 'drawn', total, iO, iN


def histories_of_part(si):
    """Every history of one part: [(kind, j, choice index tuple or None, choice dict or None, history)], the choice
    record, and the part's structure."""
    s = cs.starts()[si]
    stars, laws, names, obs = cs.start_struct(si)
    hs = [('O', 0, None, None, grow_census(stars, 'O')), ('N', 0, None, None, grow_census(stars, 'N'))]
    if s['D0'] > DMAX:
        return hs, dict(total=None, mode='no round', sizes=[]), (stars, laws, names, obs)
    r, opts = round1_options(stars)
    idxs, mode, total, iO, iN = part_choices(opts, s['tid'], s['mask'])
    for j, ix in enumerate(idxs):
        ch = choice_dict(opts, ix)
        hs.append(('choice', j, list(ix), ch, grow_census(stars, 'O', choice=ch)))
    crec = dict(total=total, mode=mode, sizes=[len(sh) for _, _, sh in opts], births=[i for i, _, _ in opts],
                parents=[p for _, p, _ in opts], index_O=list(iO), index_N=list(iN))
    return hs, crec, (stars, laws, names, obs)


def history_by_key(si, kind, j):
    """Rebuild one history deterministically (for the checks)."""
    hs, crec, struct = histories_of_part(si)
    for k, jj, ix, ch, h in hs:
        if k == kind and jj == j:
            return h, ix, ch, struct
    raise KeyError((si, kind, j))


# ======================================================================================================================
# Law assignments of the newborns (mixed arm)
# ======================================================================================================================
def assignments3(n, key):
    """Every assignment of a law index (0 even, 1 odd, 2 not-all-equal) to n newborns when 3^n <= 4,096; else 4,096
    distinct assignments drawn by numpy default_rng([2026112371, *key]), one generator per history (key: target, start
    bitmask, kind code, choice position).  Column j is the j-th newborn in birth order (the assignment of a stage is a
    prefix).  The order and draw rule are ticket C's (cstudy.assignments3) with this study's seed."""
    if n == 0:
        return np.zeros((1, 0), dtype=np.int8), 'all'
    if 3 ** n <= LAW_CAP:
        a = np.array(list(itertools.product(range(3), repeat=n)), dtype=np.int8)[:, ::-1].copy()
        return a, 'all'
    rng = np.random.default_rng([SEED_LAW, *key])
    seen, rows = set(), []
    while len(rows) < LAW_CAP:
        row = rng.integers(0, 3, size=n, dtype=np.int8)
        b = row.tobytes()
        if b not in seen:
            seen.add(b)
            rows.append(row)
    return np.array(rows, dtype=np.int8), 'drawn'


def newborn_info(h):
    """Per newborn in birth order: (round, index in round, number of inputs, reread, fresh)."""
    out = []
    for t, rd in enumerate(h['births'], start=1):
        for i, b in enumerate(rd):
            out.append((t, i, len(b['inputs']), b['reread'], b['fresh']))
    return out


def multi_input_cols(h, nb_prev, nb):
    """Columns of the newborns of the stage's round (positions nb_prev..nb-1) with two or more inputs: the only newborns
    of that round whose law changes how much an old word counts (deviations A)."""
    info = newborn_info(h)
    return {k for k in range(nb_prev, nb) if info[k][2] >= 2}


def control_stars(h, n1, nf):
    """Stage 1 with the shared input removed from every re-reading birth of round 1 (fresh distinctions kept)."""
    st = list(h['stars'][:n1])
    for i, b in enumerate(h['births'][0]):
        if b['reread']:
            k = nf + i
            s = st[k]
            assert s[len(b['inputs']) - 1] == b['shared'] and tuple(s[:len(b['inputs'])]) == tuple(b['inputs'])
            st[k] = tuple(d for d in s if d != b['shared'])
    return st


def sibling_class(rd):
    """'same': every parent with two or more re-reading births in the round gave them one distinction; 'different':
    some such parent's births took different distinctions; 'single': no parent has two re-reading births."""
    by_parent = {}
    for b in rd:
        if b['reread']:
            by_parent.setdefault(b['parents'][0], []).append(b['shared'])
    multi = [v for v in by_parent.values() if len(v) >= 2]
    if not multi:
        return 'single'
    return 'different' if any(len(set(v)) > 1 for v in multi) else 'same'


def name_of(names, d):
    return names[d] if d < len(names) else f'f{d}'


def knots_text(stars, laws_all, names):
    return [bc.fmt_knot(l, [name_of(names, d) for d in s]) for s, l in zip(stars, laws_all)]


def named_knots(stars, laws_all, names):
    return [(l, tuple(name_of(names, d) for d in s)) for s, l in zip(stars, laws_all)]
