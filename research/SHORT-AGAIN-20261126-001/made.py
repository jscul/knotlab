"""made.py: the bench and the census of TWO-PATTERNS-20261126-001 under the rations made here (rations.py).

    made.py bench SPEC      one bench case (SPEC as bench.py takes it, with a made ration's name)
    made.py pair I J        sited starts I and J of the census, at one step, by a meeting and by a shared
                            distinction, under ODD-FEWER and BUSY-FEWER and the three treatments: 12 cases"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
import rations
bench = rations.bench
sys.path.insert(0, os.path.join(HERE, '..', 'TWO-PATTERNS-20261126-001', 'census'))
import census

if sys.argv[1] == 'bench':
    s = json.loads(sys.argv[2])
    print(json.dumps(bench.case(s['A'], s['B'], s['steps'], s['ration'], s['treatment'], None, s.get('rounds', 12), s.get('bound', 3000),
                                marks=True, join=s.get('join', 'meeting'))))
else:
    i, j = int(sys.argv[2]), int(sys.argv[3]); S = census.sited()
    for k in (i, j): bench.STARS[S[k][0]] = S[k][1]; bench.SITE[S[k][0]] = S[k][2]
    A, B = S[i][0], S[j][0]; last = lambda xs: max((n + 1 for n, x in enumerate(xs) if x), default=0)
    for join in ('meeting', 'share'):
        for ration in ('ODD-FEWER', 'BUSY-FEWER'):
            for treatment in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
                t0 = time.time()
                r = bench.case(A, B, 1, ration, treatment, None, rounds=census.ROUNDS, bound=census.BOUND, checkpoints=(), marks=True, join=join)
                line = {'i': i, 'j': j, 'A': A, 'B': B, 'join': join, 'law': [ration, treatment], 'rounds': r['rounds read'], 'ended': r['ended by'],
                        'knots': r['knots'], 'short': r['short members by round'], 'joint': r['joint descent, births by round'], 'reads': {}}
                for X in 'AB':
                    a = r['reads'][X]
                    line['reads'][X] = {'last kept': last(a['kept by round']), 'stub': a['own making differs from with a stub, first round'],
                                        'marks': [[m['own making first differs'], m['joint descent first differs']]
                                                  for _, m in sorted(a['mark at a start knot of the other'].items(), key=lambda kv: int(kv[0]))]}
                line['seconds'] = round(time.time() - t0, 2)
                print(json.dumps(line), flush=True)
