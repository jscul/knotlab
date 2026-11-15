"""Exploratory: random descriptions with exactly one tree-type joining placement ((g, none), (h1, 0), (h2, 1)) and one to three
within-level placements; exact least bonds by the reach census's code at N = 7, k0 = 2, S = 3. Does the ruler L(s) = s + 2 hold
whenever the union lives?"""
import sys, random, json, os, shutil, collections
C = 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'
sys.path.insert(0, C)
import job
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
n_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 120
out = collections.Counter(); bad = []
wd = os.path.join('research/RULER-LEVEL-20261114-001/exploratory', 'work'); 
for i in range(n_samples):
    s = rng.choice([2, 3]); W = 1 + s + s * s
    sw = [rng.randrange(2) for _ in range(s)]; d0 = [rng.randrange(s) for _ in range(s)]; d1 = [rng.randrange(s) for _ in range(s)]
    g, h1, h2 = rng.randrange(W), rng.randrange(W), rng.randrange(W)
    tree = sorted([3 * g + 0, 3 * h1 + 1, 3 * h2 + 2])
    pls = [tree]
    for _ in range(rng.choice([1, 2, 3])):
        if rng.random() < 0.7:
            ws = rng.sample(range(W), 3); pls.append(sorted(3 * w for w in ws))
        else:
            ws = rng.sample(range(W), 3); a = rng.choice([1, 2]); pls.append(sorted(3 * w + a for w in ws))
    key = [s, sw, d0, d1, pls]
    shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
    try:
        job.BUDGET = 60; r = job.compute(key, wd, N=6, k0=1, S=3, histograms=False)
    except Exception as e:
        out['error'] += 1; continue
    Ls = [l['L_N'] for l in r['levels']]; un = r['union']['verdict']
    if un != 'alive': o = 'union ' + un
    elif any(x == 'undecided' for x in Ls): o = 'undecided'
    elif Ls == [3, 4, 5]: o = "ruler"
    else: o = 'NOT ruler'; bad.append(dict(key=key, L=Ls))
    out[o] += 1
    print(i + 1, o, Ls, flush=True)
shutil.rmtree(wd, ignore_errors=True)
print('final', dict(out)); print('counterexamples', json.dumps(bad[:5]))
