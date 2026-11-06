"""scoping before the freeze: build every fixture and its diagram (crossings, depth gaps); no cohomology, no counts"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ck_core import Diagram
from ck_fixtures import Spec, build_fixture
from ck_specs import FIXTURES
for fname, fx in FIXTURES.items():
    t = time.time()
    p, r, S, knots, gname, n, E, roles, fedges = fx
    z = 3 if (p, r) == (7, 6) else 2
    spec = Spec(p, r, z, S, knots)
    comps, info, L, base = build_fixture(spec, roles, fedges)
    D = Diagram(comps)
    print(fname, len(comps), "components", len(D.crossings), "crossings", "min depth gap", round(D.min_dz, 4),
          round(time.time() - t, 1), "s", flush=True)
