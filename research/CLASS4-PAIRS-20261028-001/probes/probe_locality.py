"""Scoping probe (not frozen evidence): does locality up to relabeling (R1-R4 of CLASS4-PAIRS-20261028-001B-E001) hold for
free class 4 on (1, 2), slots (1, 2, 3), d = 5, p = 11, where slot 1's degree-3 twists sit at characters 4 and 0, outside the
root set {2, 3} of the preceding slot 2?  Also free class 4 on (1, 3), slots (1, 3, 4)."""
import glob, json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "experiments/CLASS4-PAIRS-20261028-001B/*E001_*"))[0])
from c4_lib import *  # noqa
T0 = time.time()
SHAPES = [("P3", 3, [(0, 1), (1, 2)]), ("skip", 3, [(0, 2)]), ("star", 4, [(0, 1), (0, 2), (0, 3)]),
          ("triangle", 3, [(0, 1), (0, 2), (1, 2)]), ("P3 reversed", 3, [(0, 2), (1, 2)])]
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
PRESETS = {"K12": ([1, 2], (1, 2, 3)), "K13": ([1, 3], (1, 3, 4)), "K12r": ([1, 2], (2, 1, 3)), "K13r": ([1, 3], (3, 1, 4)),
           "K012": ([0, 1, 2], (1, 2, 3)), "K012r": ([0, 1, 2], (2, 1, 3)), "K013r": ([0, 1, 3], (3, 1, 4))}
gens, slots = PRESETS[sys.argv[1]]
C = Case(gens, slots)
nvs = len(C.low(C.VK, ("v", 0)))
for sname, nv, edges in SHAPES:
    for cname in ("diagonal", "off-diagonal", "mixed"):
        s = rng.integers(0, 11, nvs)
        states = {"diagonal": [s] * nv, "off-diagonal": [rng.integers(0, 11, nvs) for _ in range(nv)],
                  "mixed": [s if v % 2 == 0 else rng.integers(0, 11, nvs) for v in range(nv)]}[cname]
        try:
            r = C.graph(nv, edges, states, rng)
        except AssertionError as ex:
            r = {"error": str(ex)}
        print(sys.argv[1], sname, cname, json.dumps(r), f"({time.time() - T0:.0f}s)", flush=True)
