"""Pre-freeze construction check: build both fixtures and the controls, verify the geometry (no near-intersections,
generic crossings), H1 from the linking matrix, psi well defined. No cohomology or counts are computed here."""
import time
import numpy as np
from pc_core import Diagram, smith_diagonal, R
from pc_fixtures import build_fixture

FIX = {
    "K2": (["x", "x", "y", "t"], [(0, 1, 2, 3)]),
    "digon": (["x", "x", "y", "y", "t", "t"], [(0, 1, 2, 4), (0, 1, 3, 5)]),
}
for name, (slots, edges) in FIX.items():
    for variant, kw in (("projector", {"wdir": -1}), ("unbalanced", {"wdir": -1, "unbalanced_edge": 1}),
                        ("reversed", {"wdir": 1})):
        if variant == "unbalanced" and name != "digon":
            continue
        if variant == "reversed" and name != "K2":
            continue
        t = time.time()
        comps, info, L, base = build_fixture(slots, edges, **kw)
        D = Diagram(comps)
        rels = D.crossing_rels + D.framing_rels()
        Lm = D.lk.copy()
        for i, c in enumerate(comps):
            Lm[i, i] = c.framing
        sd = [d for d in smith_diagonal(Lm.tolist()) if d != 1]
        cl = Lm[1:, 1:]
        sd_cl = [d for d in smith_diagonal(cl.tolist()) if d != 1]
        psi_ok = all(sum(D.psi[g] * s for g, s in rel) % R == 0 for rel in rels)
        print(name, variant, "choice", info["choice"], "components", len(comps), "crossings", len(D.crossings),
              "min|dz|", round(D.min_dz, 4), "H1 factors", sd, "clasper-only H1 factors", sd_cl, "psi ok", psi_ok,
              "lk(K, others)", D.lk[0, 1:].tolist(), round(time.time() - t, 1), "s", flush=True)
