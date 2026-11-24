"""Complete census blocks outside the shared runner (deviations.md B14), writing one record per block in the runner's
format to a supplementary file (default census/extra_blocks.jsonl).

job.py is imported unchanged and its own functions and parameters are used (R = 10, cut-off past 1,500 knots,
compact_run, run_record, ordinary_checks).  The only difference from job.run is isolation: the knot test of each start
is run here, and each (start, law) run is computed in a forked child process with its own address-space limit
(--law-gb) and time limit (--law-sec).  A run that finishes gives exactly the record job.one_start gives.  A run that
cannot finish within those limits is recorded as not completed, with the reason, the round that could not be
completed, the record of the rounds before it (the same run with R set to the last completed round), and a description
of the round that could not be completed; its kind is not given.

Usage (from this folder):
  ../../../.venv/bin/python -B extra_blocks.py --cases n6-b0032 [--starts 0-99] [--out PATH] [--law-gb 10] [--law-sec 240]
  ../../../.venv/bin/python -B extra_blocks.py --verify n6-b0000,n6-b0100     (compare with the runner's records)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import resource
import signal
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import job  # noqa: E402
from bref import E, LAWS3, OUT, ROOT, census_stars, graph_edges, ordinary_checks, run_record  # noqa: E402

CENSUS = os.path.join(OUT, 'census')
JOB_PATH = os.path.join(HERE, 'job.py')


def rss_mb():
    for line in open('/proc/self/status'):
        if line.startswith('VmRSS'):
            return int(line.split()[1]) // 1024
    return None


def law_record(S, lname, law, rounds):
    """Exactly job.one_start's computation for one law, with job's parameters (rounds may be lowered)."""
    run = E.Run(S, law, rounds, knot_cap=job.CAP)
    rr = run_record(run)
    c = job.compact_run(rr)
    if lname == 'ordinary':
        oc = ordinary_checks(run)
        c['ord'] = {'ok': oc['ok'], 'viol': len(oc['member_two_rounds_violations']),
                    'stalled_rounds': oc['stalled_rounds']}
    return c, run


def next_round_description(run, law):
    """Describe the round after the last one of `run` (reporting only; no verdict rests on it): the births it would
    make by steps 1 to 5, and the largest met set its new knots would form (the offshoots and joins taking the
    distinctions of one member)."""
    S = run.S
    ros = E.live_roster(S)
    groups = E.groups_from(ros.members, ros.maxsets)
    owe = Counter(u for g in groups for u in g)
    short = [u for u in ros.members if owe[u] > ros.h[u]]
    hs = sorted((ros.h[u] for u in ros.members), reverse=True)
    if law.treatment == 'STALL' and short:
        births = 0
    else:
        births = len([g for g in groups if not set(g) & set(short)]) + sum(
            ros.h[u] - owe[u] for u in ros.members if u not in short and ros.h[u] > owe[u])
    return {'knots_before': S.n_knots, 'members_before': len(ros.members), 'groups': len(groups),
            'short': len(short), 'births_by_steps_1_to_5': births, 'largest_h': hs[:3],
            'sum_h': sum(hs), 'pairs_in_largest_met_set_after': hs[0] * (hs[0] - 1) // 2 if hs else 0}


def run_child(fn, gb, sec):
    """Run fn() in a forked child under an address-space limit (GB) and a time limit (s).  fn returns a JSON-able
    object; progress(obj) lines may be written by fn through the given writer.  Returns (result, progress, failure)."""
    r, w = os.pipe()
    t0 = time.time()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        try:
            lim = int(gb * 2 ** 30)
            resource.setrlimit(resource.RLIMIT_AS, (lim, lim))

            def say(obj):
                os.write(w, (json.dumps(obj) + '\n').encode())
            res = fn(say)
            say({'result': res})
        except MemoryError:
            try:
                os.write(w, (json.dumps({'failure': 'MemoryError', 'rss_mb': rss_mb()}) + '\n').encode())
            except Exception:
                pass
        except BaseException as exc:  # noqa: BLE001
            try:
                os.write(w, (json.dumps({'failure': 'error: %r' % (exc,)}) + '\n').encode())
            except Exception:
                pass
        os._exit(0)
    os.close(w)
    os.set_blocking(r, False)
    buf = b''
    killed = False
    while True:
        try:
            buf += os.read(r, 1 << 20)
        except BlockingIOError:
            pass
        done, status = os.waitpid(pid, os.WNOHANG)
        if done:
            break
        if time.time() - t0 > sec:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            killed = True
            break
        time.sleep(0.01)
    os.set_blocking(r, True)
    while True:
        chunk = os.read(r, 1 << 20)
        if not chunk:
            break
        buf += chunk
    os.close(r)
    msgs = [json.loads(x) for x in buf.decode().splitlines() if x.strip()]
    res = next((m['result'] for m in msgs if 'result' in m), None)
    prog = [m for m in msgs if 'progress' in m]
    fail = next((m for m in msgs if 'failure' in m), None)
    if killed:
        fail = {'failure': 'time limit of %d s' % sec}
    elif res is None and fail is None:
        fail = {'failure': 'child ended without a result'}
    return res, prog, fail, round(time.time() - t0, 2)


def one_start_isolated(g, loose, gb, sec):
    n = len(loose)
    S = E.from_stars(census_stars(g, loose))
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
        def full(say, law=law, lname=lname):
            def hook(S2, r, rr, before):
                if rr is not None:
                    say({'progress': [r, S2.n_knots, rr['n_births']]})
            run = E.Run(S, law, job.R, knot_cap=job.CAP, hook=hook)
            rr = run_record(run)
            c = job.compact_run(rr)
            if lname == 'ordinary':
                oc = ordinary_checks(run)
                c['ord'] = {'ok': oc['ok'], 'viol': len(oc['member_two_rounds_violations']),
                            'stalled_rounds': oc['stalled_rounds']}
            return c
        res, prog, fail, secs = run_child(full, gb, sec)
        if fail is None:
            laws[lname] = res
            continue
        last = prog[-1]['progress'][0] if prog else 0
        t_bad = last + 1

        def partial(say, law=law, lname=lname, last=last):
            c, run = law_record(S, lname, law, last)
            return {'partial': c, 'next_round': next_round_description(run, law)}
        pres, _, pfail, psecs = run_child(partial, gb, min(sec, 120))   # repeats completed rounds only
        laws[lname] = {'not_completed': True, 'reason': fail['failure'],
                       'failure_rss_mb': fail.get('rss_mb'), 'seconds_to_failure': secs,
                       'round_not_completed': t_bad, 'rounds_completed': last,
                       'progress': [p['progress'] for p in prog],
                       'partial': pres['partial'] if pres else None,
                       'next_round': pres['next_round'] if pres else None,
                       'partial_failure': pfail['failure'] if pfail else None,
                       'limits': {'gb': gb, 'sec': sec}}
    rec['laws'] = laws
    return rec


def block_payload(cid):
    for c, p in job.cases():
        if c == cid:
            return p
    raise KeyError(cid)


def run_block(cid, gb, sec, start_range=None):
    p = block_payload(cid)
    t0 = time.time()
    out = []
    for i, (g, loose) in enumerate(p['starts']):
        if start_range is not None and not (start_range[0] <= i <= start_range[1]):
            continue
        ts = time.time()
        rec = one_start_isolated(g, list(loose), gb, sec)
        rec['sec'] = round(time.time() - ts, 3)
        out.append(rec)
        bad = [l for l, c in rec.get('laws', {}).items() if c.get('not_completed')]
        if bad or rec['sec'] > 5:
            print('[%s] start %d g=%d loose=%s %.1fs %s' % (cid, i, g, loose, rec['sec'],
                                                            ('NOT COMPLETED: ' + ','.join(bad)) if bad else ''),
                  flush=True)
    return {'case': cid, 'n': p['n'], 'block': p['block'], 'starts': out, 'seconds': round(time.time() - t0, 2),
            'rounds': job.R, 'cap': job.CAP}, len(p['starts'])


def strip_times(starts):
    out = []
    for s in starts:
        s = dict(s)
        s.pop('sec', None)
        out.append(s)
    return out


def verify(cids, gb, sec):
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    from longrun import load_results
    rs = load_results(CENSUS)
    recs = {r['case']: r for r in (rs.values() if isinstance(rs, dict) else rs) if r['status'] == 'ok'}
    ok_all = True
    for cid in cids:
        mine, _ = run_block(cid, gb, sec)
        theirs = recs[cid]['result']
        same = (strip_times(mine['starts']) == strip_times(theirs['starts'])
                and all(mine[k] == theirs[k] for k in ('case', 'n', 'block', 'rounds', 'cap')))
        ok_all = ok_all and same
        print('verify %s: %d starts, identical records apart from timings: %s (%.1fs here, %.1fs in the runner)'
              % (cid, len(mine['starts']), same, mine['seconds'], theirs['seconds']), flush=True)
    return ok_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', default='')
    ap.add_argument('--starts', default=None, help='range a-b of start indices within the block (inclusive)')
    ap.add_argument('--out', default=os.path.join(CENSUS, 'extra_blocks.jsonl'))
    ap.add_argument('--law-gb', type=float, default=10.0)
    ap.add_argument('--law-sec', type=int, default=240)
    ap.add_argument('--verify', default='')
    a = ap.parse_args()
    if a.verify:
        ok = verify(a.verify.split(','), a.law_gb, a.law_sec)
        print('VERIFY', 'PASS' if ok else 'FAIL', flush=True)
        return
    sha = hashlib.sha256(open(JOB_PATH, 'rb').read()).hexdigest()
    sr = tuple(int(x) for x in a.starts.split('-')) if a.starts else None
    for cid in a.cases.split(','):
        t0 = time.time()
        res, n_all = run_block(cid, a.law_gb, a.law_sec, sr)
        line = {'case': cid if sr is None else '%s[%d-%d]' % (cid, sr[0], sr[1]), 'status': 'ok', 'attempt': 1,
                'result': res, 'seconds': round(time.time() - t0, 2),
                'finished_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds'),
                'source': 'extra_blocks.py (deviations.md B14)', 'job_sha': sha,
                'limits': {'law_gb': a.law_gb, 'law_sec': a.law_sec, 'process': 'ulimit -v 12000000, timeout 1200'},
                'start_range': list(sr) if sr else None, 'block_starts': n_all}
        with open(a.out, 'a') as f:
            f.write(json.dumps(line) + '\n')
        nc = sum(1 for s in res['starts'] for c in s.get('laws', {}).values() if c.get('not_completed'))
        print('wrote %s %s: %d starts, %d runs not completed, %.1fs' % (a.out, line['case'], len(res['starts']), nc,
                                                                         line['seconds']), flush=True)


if __name__ == '__main__':
    main()
