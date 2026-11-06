"""scoping before the freeze: the full pipeline on the checkpoint fixture (P1-K2) for the checkpoint group only, sectors 1 and 5,
whose values (133, 2401) and dimensions were published by PATTERN1-CHECKPOINT-20261026-001; nothing else is computed"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ck_fixtures import Spec, build_fixture, cohomology_data, measured_count
from ck_specs import FIXTURES, L, all_groups
t = time.time()
p, r, S, knots, gname, n, E, roles, fedges = FIXTURES["P1-K2"]
spec = Spec(p, r, 3, S, knots)
comps, info, Lay, base = build_fixture(spec, roles, fedges)
data = cohomology_data(comps, spec)
G = all_groups(p, r)["free class 2 on characters (3, 2, 6)"]
print("crossings", data["crossings"], "H1", data["H1_invariant_factors"], "dims", data["dims"], "cohomology s", data["seconds"])
print("sector 1:", measured_count(G, data, 1, L.count_bilinear_zeros), "sector 5:", measured_count(G, data, 5, L.count_bilinear_zeros),
      round(time.time() - t, 1), "s")
