"""A test class for the reduction of pairlib.py on pairs that do exceed 2: every side table of class S with at most 3 knots
and two shared distinctions, every 4-knot table that occurs in an excess pair of the class-S census, and 3,000 further
4-knot tables drawn with a fixed seed.  pairs_c.py is run on it with --full (every ordered pair) and with the reduction;
gates.py compares the two sets of excess old tables.

usage: gates_mix.py
"""
import json
import numpy as np
import common as c

d3 = np.load(f'{c.ART}/sides_S_c2_k3_i3_h3.npz'); d4 = np.load(f'{c.ART}/sides_S_c2_k4_i5_h3.npz')
summ = json.load(open(f'{c.ART}/pc_S_c2_k4_i5_h3__S_c2_k4_i5_h3_lemma_summary.json'))
need = sorted({e['rep_A'] for e in summ['excess']} | {e['rep_B'] for e in summ['excess']})
rng = np.random.default_rng(20261123)
extra = rng.choice(len(d4['T']), 3000, replace=False)
idx4 = sorted(set(need) | set(int(i) for i in extra))
K3 = d3['structs'].shape[1]; K4 = d4['structs'].shape[1]
S3 = np.full((len(d3['T']), K4, 6), -1, np.int8); S3[:, :K3] = d3['structs']
out = dict(T=np.concatenate([d3['T'], d4['T'][idx4]]), nonempty=np.concatenate([d3['nonempty'], d4['nonempty'][idx4]]),
           internal=np.concatenate([d3['internal'], d4['internal'][idx4]]), knots=np.concatenate([d3['knots'], d4['knots'][idx4]]),
           extra=np.concatenate([d3['extra'], d4['extra'][idx4]]), structs=np.concatenate([S3, d4['structs'][idx4]]))
out['alloc'] = np.zeros(len(out['T']), bool)
np.savez_compressed(f'{c.ART}/sides_mixS.npz', **out)
json.dump(dict(note='test class for gates.py', tables=int(len(out['T'])), three_knot=int(len(d3['T'])), four_knot_from_excess=len(need),
               four_knot_drawn=3000, four_knot_total=len(idx4)), open(f'{c.ART}/sides_mixS.json', 'w'), indent=1)
print('mix tables', len(out['T']), 'of which 4-knot', len(idx4), '(from excess pairs', len(need), ')')
