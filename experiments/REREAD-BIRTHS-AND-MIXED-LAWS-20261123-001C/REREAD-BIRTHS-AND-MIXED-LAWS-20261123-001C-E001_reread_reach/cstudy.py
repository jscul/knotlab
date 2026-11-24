"""Shared code for REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C-E001 (does a birth that takes a shared distinction let
growth finish a structure with a hidden excess?).

Frozen definitions: research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/preregistration.md.  Nothing here changes a
definition; readings are listed in deviations.md of this folder.

Recorded code reused read-only (imported by path, never changed):
  * ticket B (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach) `common.py`, imported as `bc`: target knots,
    founder starts (`start_stars`), the ordinary growth wrapper `grow`, law tensors and the exact contraction
    (`stage_tables`), word-by-word tables (`brute_table`), the exact hiding test and score (`hidden_batch`,
    `score_batch`, `exact_best`, `exact_hidden_obj`, `Evaluator`, `normalize`), `load_starter` (the recorded scorer);
  * ticket B `verify_excess.py`, imported as `bve`: enumeration of every word of the four finished structures
    (`brute_joint_all`, `brute_joint`, `evaluate_joint`);
  * ticket A (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law) `rlaw.py`: class `Growth` (rule R on full
    holdings, conventions O and N, `allowed_choices`, `plan_with`).  Its C search is switched off here
    (`rlaw.USE_C = False`) so that nothing is built in ticket A's artifact folder; the Python search is the same algorithm
    (ticket A deviations B1, compared there on every end).
Ticket B's outputs are read compressed (gzip.open); nothing in its folder is written.
"""
import gzip
import hashlib
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
ART = ROOT / 'artifacts' / TICKET / HERE.name
B_EXP = ROOT / 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach'
B_ART = ROOT / 'artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach'
A_EXP = ROOT / 'experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law'
RLAW_SHA = '29aa3d9112d4a12b2d7970756c455e11dd3ed7abaef99b85daa64f4c4222d8f8'   # contract.json "inputs"

sys.path.insert(0, str(B_EXP))
import common as bc  # noqa: E402  (ticket B; its module-level ART.mkdir is a no-op on the existing folder)
import verify_excess as bve  # noqa: E402
sys.path.insert(0, str(A_EXP))
import rlaw  # noqa: E402

rlaw.USE_C = False

ROUNDS = 3              # "for 3 rounds"
DMAX = 20               # "or until a stage passes 20 distinctions"
CHOICE_CAP = 64         # "every allowed round-1 choice when there are at most 64"
CHOICE_MORE = 62        # "otherwise under 62 more choices drawn"
SEED_CHOICE = 2026112350
LAW_CAP = 4096          # "every assignment when there are at most 4,096, otherwise 4,096 drawn"
SEED_LAW = 2026112351
ORIGIN_CAP = 4096       # arm 2 origin: "every choice when there are at most 4,096, otherwise ... not decided"
CH3 = ('even', 'odd', 'nae')   # "Each newborn is even parity, odd parity or not-all-equal"
# seeds chosen here for the checks of row G (not fixed by the note; deviations A9)
SEED_G_TWO = 2026112352
SEED_G_THREE = 2026112353
SEED_G_STAGES = 2026112354
SEED_G_PAIRS = 2026112355
OBS = bc.OBS


def rlaw_sha():
    return hashlib.sha256((A_EXP / 'rlaw.py').read_bytes()).hexdigest()


def jl_load(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        return [json.loads(l) for l in f if l.strip()]


def dump(path, rows, mode='w'):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, mode + 't') as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(',', ':'), default=str) + '\n')


# ======================================================================================================================
# Starts, classes and ticket B's record
# ======================================================================================================================
_CACHE = {}


def starts():
    if 'starts' not in _CACHE:
        _CACHE['starts'] = jl_load(B_ART / 'starts.jsonl.gz')
    return _CACHE['starts']


def targets():
    if 'targets' not in _CACHE:
        _CACHE['targets'] = {t['tid']: t for t in json.loads((B_ART / 'targets.json').read_text())}
    return _CACHE['targets']


def target_knots():
    if 'tk' not in _CACHE:
        _CACHE['tk'] = {t['tid']: t['knots'] for t in bc.load_targets()}
    return _CACHE['tk']


def b_lines(version='c3'):
    """Ticket B's T1 lines (one per history), by start index."""
    key = 'b_' + version
    if key not in _CACHE:
        out = {}
        for f in sorted(B_ART.glob(f't1_{version}_*.jsonl.gz')):
            for l in jl_load(f):
                out[l['si']] = l
        _CACHE[key] = out
    return _CACHE[key]


def start_class(s):
    return 'two' if s['max_holders'] <= 2 else 'three'


def start_struct(si):
    s = starts()[si]
    stars, laws, names, obs, sub = bc.start_stars(target_knots()[s['tid']], s['mask'])
    return stars, laws, names, obs


def name_of(names, d):
    return names[d] if d < len(names) else f'f{d}'


# ======================================================================================================================
# Growth under rule R (ticket A's engine), with the stop of ticket B
# ======================================================================================================================
def choice_of_plan(r):
    """The payment choice {knot: {birth: distinction}} made by a planned round of status 'extend'."""
    ch = defaultdict(dict)
    for i, (ps, row, prow) in enumerate(zip(r.parents, r.inputs, r.paid, strict=True)):
        for p, d, x in zip(ps, row, prow, strict=True):
            if x:
                ch[p][i] = d
    return {k: dict(v) for k, v in ch.items()}


def choice_key(ch):
    return tuple(sorted((k, tuple(sorted(v.items()))) for k, v in ch.items()))


def grow_R(stars, conv='O', first_choice=None, conv_later=None, rounds=ROUNDS, dmax=DMAX):
    """Grow `stars` under rule R by rlaw.Growth (structure rule not-all-equal: every birth has a fresh distinction), for
    `rounds` rounds or until a stage has more than `dmax` distinctions (that stage is kept), as ticket B's `grow`.
    Round 1 uses `first_choice` (a full payment choice, rlaw.plan_with) when given, else convention `conv`; later rounds
    use `conv_later` (default `conv`).  Returns a dict: stars, n_at, D_at, births (per round: list of dicts parents,
    inputs, fresh, paid flags, paying = some input already has two or more holders), outcome, residual (when the
    history ends in a residual stall), short (per planned round: the short knots), max_holders."""
    g = rlaw.Growth(stars, 'nae', 'R', conv)
    n_at = [len(g.stars)]
    D_at = [len(g.holders)]
    births, shorts = [], []
    outcome, residual, residual_round = None, None, None
    while True:
        if len(g.rounds) >= rounds:
            outcome = 'rounds'
            break
        if D_at[-1] > dmax:
            outcome = 'distinctions'
            break
        if len(g.rounds) >= 1 and conv_later is not None:
            g.convention = conv_later
        r = g.plan(None)
        if r.status == 'closed':
            outcome = 'closed'
            break
        shorts.append([list(x) for x in (r.shortages or ())])
        if first_choice is not None and len(g.rounds) == 0:
            assert r.shortages, 'a choice was given for a round with no short knot'
            r = g.plan_with(r, first_choice)
        if r.status == 'residual_stall':
            outcome = 'residual_stall'
            residual = [list(x) for x in r.residual]
            residual_round = len(g.rounds) + 1
            break
        assert r.status == 'extend', r.status
        rec = []
        for ps, row, prow, f in zip(r.parents, r.inputs, r.paid, r.fresh, strict=True):
            paying = any(len(g.holders[d]) >= 2 for d in row)
            assert paying == any(prow), 'a payment is not a shared distinction (or the reverse)'
            rec.append(dict(parents=list(ps), inputs=list(row), fresh=f, paid=[bool(x) for x in prow], paying=paying))
        g.apply(r)
        assert g.outcome is None, g.outcome
        births.append(rec)
        n_at.append(len(g.stars))
        D_at.append(len(g.holders))
    return dict(stars=[tuple(s) for s in g.stars], n_at=n_at, D_at=D_at, births=births, outcome=outcome,
                residual=residual, residual_round=residual_round, short=shorts, max_holders=g.max_holders())


def round1_options(stars):
    """Round 1 under rule R: (planned Round under convention O, per-knot allowed options or None when no knot is short,
    total number of allowed choices, the Growth object)."""
    g = rlaw.Growth(stars, 'nae', 'R', 'O')
    r = g.plan(None)
    if r.status == 'closed' or not r.shortages:
        return r, None, (1 if r.status != 'closed' else 0), g
    per = g.allowed_choices(r)
    total = math.prod(len(o) for _, o in per)
    return r, per, total, g


def choice_from_index(per, idx):
    return {k: opts[i] for (k, opts), i in zip(per, idx, strict=True)}


def all_choice_indices(per):
    return list(itertools.product(*[range(len(o)) for _, o in per]))


def index_of_choice(per, ch):
    idx = []
    for k, opts in per:
        want = ch.get(k, {})
        j = next((j for j, o in enumerate(opts) if o == want), None)
        if j is None:
            return None
        idx.append(j)
    return tuple(idx)


def convention_choice(stars, conv):
    """The payment choice convention `conv` makes at round 1 (None when it is a residual stall or no knot is short)."""
    g = rlaw.Growth(stars, 'nae', 'R', conv)
    r = g.plan(None)
    if r.status != 'extend' or not r.shortages:
        return None
    return choice_of_plan(r)


def drawn_choice_indices(per, tid, mask, exclude, n=CHOICE_MORE):
    """`n` distinct allowed round-1 choices drawn uniformly (each short knot's option index uniform and independent, so
    uniform over the product), none equal to a choice in `exclude`; generator numpy default_rng([2026112350, target,
    start bitmask])."""
    rng = np.random.default_rng([SEED_CHOICE, tid, mask])
    seen = set(exclude)
    out = []
    while len(out) < n:
        idx = tuple(int(rng.integers(0, len(o))) for _, o in per)
        if idx in seen:
            continue
        seen.add(idx)
        out.append(idx)
    return out


def round1_input_sets(g, r, choice):
    """Input sets of the births of round 1 under a full payment choice: COPIED allocation of rlaw.Growth.plan_with
    (without its fresh-count lookahead, which does not change inputs)."""
    pool = {k: list(v) for k, v in g.loose.items()}
    out = []
    for i, ps in enumerate(r.parents):
        row = []
        for p in ps:
            if p in choice and i in choice[p]:
                row.append(choice[p][i])
            else:
                row.append(pool[p].pop())
        out.append(tuple(row))
    assert not any(pool.values())
    return out


# ======================================================================================================================
# Law assignments of the newborns (three laws)
# ======================================================================================================================
def assignments3(n, key):
    """Every assignment of a law index (0 even, 1 odd, 2 not-all-equal) to n newborns when 3^n <= 4,096; else 4,096
    distinct assignments drawn by numpy default_rng([2026112351, *key]), one generator per history.  Column j is the j-th
    newborn in birth order (ticket B's convention: the assignment of a stage is a prefix of the columns)."""
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


# ======================================================================================================================
# Evaluation of many tables (B's evaluator logic, vectorized over a batch with in-batch deduplication)
# ======================================================================================================================
class Eval:
    """Hidden (both sides), float score, exact score for hidden tables with float score >= 2 - 1e-6 (as bc.Evaluator),
    with a cache on normalized tables."""

    def __init__(self):
        self.ev = bc.Evaluator()

    def run(self, T):
        """T: array (B, 64) of non-negative integers (int64 or object).  Returns list of (hA, hB, fscore, exact)."""
        norm = [bc.normalize(row) for row in T]
        return self.ev.run(norm)

    @property
    def exact_calls(self):
        return self.ev.exact_calls


def is_excess(e):
    return bc.is_excess(e)


def support(T):
    return tuple(int(i) for i in np.nonzero(np.asarray([int(v) for v in np.asarray(T).reshape(-1)]))[0])


def knots_text(stars, laws_all, names):
    return [bc.fmt_knot(l, [name_of(names, d) for d in s]) for s, l in zip(stars, laws_all)]


def full_check(knot_list):
    """Word-by-word enumeration of the four finished structures (ticket B verify_excess.brute_joint_all and
    evaluate_joint).  knot_list: [(law, tuple of names)], observers named x1..y3.  Returns a dict."""
    J, nn = bve.brute_joint_all(knot_list)
    ev = bve.evaluate_joint(J)
    return dict(J=J, hidden=ev['hidden'], hidden_A=ev['hidden_A'], hidden_B=ev['hidden_B'], score=ev['score'],
                change=ev['change'], arg=ev['arg'], words=[int(J[a, b].sum()) for a in (0, 1) for b in (0, 1)],
                distinctions_finished=nn)


def joint_from_table(M):
    """The four joint record tables implied by an 8x8 old-word table (F_a^T M F_b), for comparison with enumeration."""
    M = np.asarray(M, dtype=object).reshape(8, 8)
    return {(a, b): (bc.F[a].T.astype(object).dot(M).dot(bc.F[b].astype(object))).astype(np.int64)
            for a in (0, 1) for b in (0, 1)}


def named_knots(stars, laws_all, names):
    return [(l, tuple(name_of(names, d) for d in s)) for s, l in zip(stars, laws_all)]


def frac(x):
    return None if x is None else str(x)


# ======================================================================================================================
# Arm 2: allowed words of a start, by joining its knots one at a time (exact)
# ======================================================================================================================
def _law_ok(law, s, k):
    if law == 'nae':
        return (s != 0) & (s != k)
    if law == 'even':
        return s % 2 == 0
    if law == 'odd':
        return s % 2 == 1
    raise ValueError(law)


def allowed_words(stars, laws):
    """Every allowed word of the structure (bit d of an int64 = value of distinction d), by adding the knots one at a
    time (the next knot is the one sharing most distinctions with those already placed) and keeping the words that
    satisfy every knot whose distinctions are all placed.  Distinctions are 0..D-1."""
    D = len({d for s in stars for d in s})
    assert {d for s in stars for d in s} == set(range(D)) and D <= 62
    words = np.zeros(1, dtype=np.int64)
    placed = set()
    left = list(range(len(stars)))
    while left:
        k = max(left, key=lambda q: (sum(d in placed for d in stars[q]), -len(stars[q]), -q))
        new = [d for d in stars[k] if d not in placed]
        if new:
            combos = np.arange(1 << len(new), dtype=np.int64)
            add = np.zeros_like(combos)
            for i, d in enumerate(new):
                add |= ((combos >> i) & 1) << d
            words = (words[:, None] | add[None, :]).reshape(-1)
            placed.update(new)
        done = [q for q in left if all(d in placed for d in stars[q])]
        for q in done:
            s = np.zeros(len(words), dtype=np.int64)
            for d in stars[q]:
                s += (words >> d) & 1
            words = words[_law_ok(laws[q], s, len(stars[q]))]
            left.remove(q)
    return np.sort(words)


def obs_index(words, obs):
    """Index x1*32 + x2*16 + x3*8 + y1*4 + y2*2 + y3 (ticket B's table order) of each word."""
    idx = np.zeros(len(words), dtype=np.int64)
    for j, o in enumerate(obs):
        idx |= ((words >> o) & 1) << (5 - j)
    return idx
