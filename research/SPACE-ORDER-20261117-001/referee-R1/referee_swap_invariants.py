"""Referee R1 for SPACE-ORDER-20261117-001: invariants of the study's role-preserving twins, on its registered instances.

  .venv/bin/python -B referee_swap_invariants.py > referee_swap_invariants.json

For each law and sample (L = 24, 48, 96): every distinction keeps how many knots it has in each role (two/one: demanded or free;
nae: value and odd member or pair), every twin knot holds three distinct distinctions, the planted state stays not-all-equal
on the twin, and how much of the weave's local structure is left (the share of co-knotted pairs in two knots, 1 on the weave)
and its largest steps apart.
"""
import json

import numpy as np

import referee_core as C
import referee_recompute as R

job = R._job()
W = job.W
out = {}
for law in ("two", "one", "nae"):
    for L in (24, 48, 96):
        rows = []
        for s in range(5):
            # the twin's own build: the weave with the twin's draws, before and after its swaps (roles stay with slots)
            Kr, choice_r, state_r, _ = R.instance(job, law, "R6", L, s)
            Kw = W.weave(L)
            n, m = L * L, len(Kw)
            if law == "nae":
                role_w, role_r = W.nae_roles(Kw, state_r), W.nae_roles(Kr, state_r)
            else:
                role_w = np.zeros((m, 3), int); role_w[np.arange(m), choice_r] = 1
                role_r = role_w
            nr = int(role_w.max()) + 1
            cw = np.zeros((n, nr), int); np.add.at(cw, (Kw.ravel(), role_w.ravel()), 1)
            cr = np.zeros((n, nr), int); np.add.at(cr, (Kr.ravel(), role_r.ravel()), 1)
            distinct = bool(np.all((Kr[:, 0] != Kr[:, 1]) & (Kr[:, 0] != Kr[:, 2]) & (Kr[:, 1] != Kr[:, 2])))
            nae_ok = None if law != "nae" else bool(all(min(state_r[u] for u in t) != max(state_r[u] for u in t) for t in Kr.tolist()))
            ecc = int(C.steps_from(C.neighbours(Kr, n), [0]).max())
            dup = len(Kr) - len({tuple(sorted(t)) for t in Kr.tolist()})
            rows.append({"role_counts_kept": bool(np.array_equal(cw, cr)), "slot_roles_kept": bool(np.array_equal(role_w, role_r)), "distinct_members": distinct, "nae_on_twin": nae_ok,
                         "pair_in_two_twin": C.pair_multiplicity(Kr)[0], "duplicate_knots_twin": dup, "ecc_twin": ecc,
                         "ecc_weave": 2 * L // 3})
        out[f"{law}-L{L}"] = rows
print(json.dumps(out, indent=1))
