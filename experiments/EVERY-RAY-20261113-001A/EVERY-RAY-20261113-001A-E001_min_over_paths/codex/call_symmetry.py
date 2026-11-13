"""A6: SELF-call equivalence under full flat-block port symmetries.

The allowed assignments retain every flat distinction. Only the three ports
are permuted; own distinctions are fixed. Every non-K call, including every
SELF call, is read by its limit relation, as in a terminal census block. There
is no distinguished continuing call in this diagnostic.
"""
from __future__ import annotations

from itertools import permutations


def diagnostics(prep, flat_S):
    """Return the exact A6 port group and its orbits on SELF-call tuples.

    Call indices in ``symmetry_equivalence_classes`` are positions in the list
    of SELF calls, rather than positions in the flat block's complete body.
    The block must have passed the experiment's 12-distinction cap before this
    function is called; no projection or renaming of own distinctions is used.
    """
    import numpy as np

    V = int(flat_S["V"])
    if flat_S["k"] != 3 or V < 3:
        raise ValueError("A6 requires exactly three ports")
    if V > 12:
        raise ValueError("A6 flat block exceeds the experiment's 12-distinction cap")
    calls = flat_S["calls"]
    self_calls = [tuple(args) for target, args in calls if target in (prep.S, "SELF")]
    assignments = np.arange(1 << V, dtype=np.int64)
    allowed = np.ones(len(assignments), dtype=bool)
    for target, args in calls:
        if len(args) != 3 or any(not 0 <= int(x) < V for x in args):
            raise ValueError("Invalid three-port call in S's flat block")
        values = sum(((assignments >> int(x)) & 1) << j for j, x in enumerate(args))
        if target == "K":
            allowed &= (values != 0) & (values != 7)
        else:
            relation = prep.G[prep.S if target == "SELF" else target]
            if len(relation) != 8:
                raise ValueError("A6 side relation must have eight three-port states")
            allowed &= np.asarray(relation, dtype=bool)[values]

    symmetries = []
    for permutation in permutations(range(3)):
        image = assignments & ~7
        for old, new in enumerate(permutation):
            image = image | (((assignments >> old) & 1) << new)
        if np.array_equal(allowed, allowed[image]):
            symmetries.append(permutation)
    if not symmetries or symmetries[0] != (0, 1, 2):
        raise AssertionError("The identity must preserve the full allowed set")

    classes = {}
    for index, args in enumerate(self_calls):
        representative = min(tuple(p[x] if x < 3 else x for x in args) for p in symmetries)
        classes.setdefault(representative, []).append(index)
    ordered = sorted(classes.items())
    return {
        "symmetry_status": "done",
        "symmetry_inequivalent": len(ordered) >= 2,
        "symmetry_equivalence_class_count": len(ordered),
        "symmetry_equivalence_classes": [indices for _, indices in ordered],
        "symmetry_class_representatives": [list(args) for args, _ in ordered],
        "symmetry_port_permutations": [list(p) for p in symmetries],
        "symmetry_flat_allowed_states": int(allowed.sum()),
        "symmetry_flat_distinctions": V,
        "symmetry_self_treatment": "every SELF call read as G[S]; no continuing call",
        "literal_duplicate_self_calls": len(self_calls) - len(set(self_calls)),
    }
