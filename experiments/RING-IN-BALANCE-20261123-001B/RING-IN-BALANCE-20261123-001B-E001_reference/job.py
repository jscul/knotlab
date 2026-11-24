"""Shared-runner job for run B2, the census of RING-IN-BALANCE-20261123-001B (docs/tooling/shared-runner.md).

Every start of the census (bref.census_starts: connected meeting graphs on 3 to 6 knots, loose counts 0 to 3 on each
knot, at least three places on every knot and at least one live knot, each start up to isomorphism once; 86,032
starts) in a fixed order, in blocks of BLOCK starts.  For each start: the parity knot test (both methods); if every
knot passes, one run under each of the ordinary law, the two added rules and the three added rules, to round 10 or
past 1,500 knots, with the kind of outcome (first that applies, as in the definitions), the first return and the first
return giving parts off (rounds, parts that came apart and their sizes, size of the returning part, whether each of
its members waited in the round of the return), counts over every return giving parts off, and the numbers of knots,
members and dead knots of the start; if a knot fails, that the start was set aside.  Readings: deviations.md.

Parameters (--param): block (starts per case, default 200), rounds (10), cap (1500), start_timeout (seconds for one
start, default 300; a start that exceeds it is recorded as timed out, not dropped).
"""
import os
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from bref import E, LAWS3, census_starts, census_stars, graph_edges, ordinary_checks, run_record  # noqa: E402

BLOCK = 200
R = 10
CAP = 1500
START_TIMEOUT = 300


def setup(params):
    global BLOCK, R, CAP, START_TIMEOUT
    BLOCK = int(params.get('block', BLOCK))
    R = int(params.get('rounds', R))
    CAP = int(params.get('cap', CAP))
    START_TIMEOUT = int(params.get('start_timeout', START_TIMEOUT))


def cases():
    for n in (3, 4, 5, 6):
        buf, bi = [], 0
        for s in census_starts(n):
            buf.append([s['g'], s['loose']])
            if len(buf) == BLOCK:
                yield 'n%d-b%04d' % (n, bi), {'n': n, 'block': bi, 'starts': buf}
                buf, bi = [], bi + 1
        if buf:
            yield 'n%d-b%04d' % (n, bi), {'n': n, 'block': bi, 'starts': buf}


def _flags(xs):
    return None if xs is None else ''.join('1' if x else '0' for x in xs)


def _compact_sizes(sizes):
    out = {}
    for z in sizes:
        out[z] = out.get(z, 0) + 1
    return [[z, c] for z, c in sorted(out.items())]


def compact_return(d):
    if d is None:
        return None
    sh = d['shape']
    return {'s': d['s'], 't': d['t'], 'size': d['part_size'], 'n_off': d['n_off'],
            'off_sizes': _compact_sizes(d['off_sizes']), 'copy_waited': _flags(d['copy_waited']),
            'y_waited': _flags(d['y_waited_in_s']), 'ring_like': d['ring_like'],
            'h': sh['h'], 'k': sh['k'], 'metsets': sh['metset_sizes']}


def compact_run(rec):
    out = {'kind': rec['kind'], 'event': rec['first_event'], 'rounds': rec['rounds_done'], 'cut': rec['cut_off'],
           'knots': rec['knots'], 'n_ret': rec['n_returns'], 'n_off': rec['n_off_returns'], 'mixed': rec['mixed_parts'],
           'first': compact_return(rec['first_return']), 'first_off': compact_return(rec['first_off_return'])}
    off = rec['off']
    if off is not None:
        out['off'] = {'n': off['n'], 'copy_all_waited': off['copy_all_waited'],
                      'y_all_waited': off['y_all_waited_in_s'], 'sizes': off['sizes'], 'ring_like': off['ring_like'],
                      'by': off['by'], 'first_not_waited': compact_return(off['first_not_all_waited']),
                      'smallest': compact_return(off['smallest'])}
    return out


class _StartTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise _StartTimeout()


def one_start(g, loose):
    n = len(loose)
    stars = census_stars(g, loose)
    S = E.from_stars(stars)
    par = E.parity_knot_test(S)
    rec = {'g': g, 'n': n, 'loose': loose, 'dead': loose.count(0), 'members': n - loose.count(0),
           'edges': len(graph_edges(g)),
           'kt': {'pass': par['all_pass'], 'rank_fail': par['rank_fail'], 'cut_fail': par['cut_fail'],
                  'disagree': par['disagree']}}
    if not par['all_pass']:
        rec['set_aside'] = True
        return rec
    rec['set_aside'] = False
    laws = {}
    for lname, law in LAWS3:
        run = E.Run(S, law, R, knot_cap=CAP)
        rr = run_record(run)
        c = compact_run(rr)
        if lname == 'ordinary':
            oc = ordinary_checks(run)
            c['ord'] = {'ok': oc['ok'], 'viol': len(oc['member_two_rounds_violations']),
                        'stalled_rounds': oc['stalled_rounds']}
        laws[lname] = c
    rec['laws'] = laws
    return rec


def run(case_id, payload):
    t_case = time.time()
    out = []
    old = signal.signal(signal.SIGALRM, _alarm)
    try:
        for g, loose in payload['starts']:
            t0 = time.time()
            signal.alarm(START_TIMEOUT)
            try:
                rec = one_start(g, list(loose))
            except _StartTimeout:
                rec = {'g': g, 'n': len(loose), 'loose': list(loose), 'timeout': True}
            finally:
                signal.alarm(0)
            rec['sec'] = round(time.time() - t0, 3)
            out.append(rec)
    finally:
        signal.signal(signal.SIGALRM, old)
    return {'case': case_id, 'n': payload['n'], 'block': payload['block'], 'starts': out,
            'seconds': round(time.time() - t_case, 2), 'rounds': R, 'cap': CAP}
