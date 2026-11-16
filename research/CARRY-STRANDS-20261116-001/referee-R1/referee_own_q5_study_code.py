# Referee: run the study's own code (as the thing under test) on subdivided trees, w = 1, 2, 3, spend-only
import sys, glob, importlib.util
d = glob.glob('/home/jscul/p-vs-np-contact-first/experiments/CARRY-STRANDS-20261116-001A/*/')[0]
sw = glob.glob('/home/jscul/p-vs-np-contact-first/experiments/SEQUENTIAL-WALL-20261116-001A/*/')[0]
sys.path.insert(0, sw); sys.path.insert(0, d)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
strands = load('strands', d + 'strands.py')
cjob = load('cs_job', d + 'job.py')
for dd, ell in ((4, 4), (4, 8), (3, 16)):
    p, top = cjob.subdivided_tree(dd, ell)
    out = {}
    for w in (1, 2, 3):
        try:
            r = strands.carried_phases(p, w, keep=False, max_states=4_000_000)
            out[w] = {k: r[k] for k in ('P', 'T', 'L') if k in r} if isinstance(r, dict) else r
        except strands.StateCap:
            out[w] = 'cap'
    print(dd, ell, out, flush=True)
