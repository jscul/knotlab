"""Shared classification (KEEP-REACH-20261117-001, the thread's own code, 2026-11-17): for one description with orbits of at most four
addresses, its forgetting length (BLOCK-REACH's forget.py: least r at every remaining depth, None = never forgets, by the closure) and
its two-orbit bond profile at every depth (two_orbit.every_depth_cross from top level 3): whether some two-orbit bond exists at every
s >= 1 at every depth tier, and the largest least value over s once the sequence is periodic."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/BLOCK-REACH-20261116-001'))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from forget import Steps  # noqa: E402
from two_orbit import every_depth_cross  # noqa: E402
from window_tree import WindowTree  # noqa: E402


def classify(key, k=3):
    try:
        tree = WindowTree(key)
    except ValueError:
        return dict(small_orbits=False)
    F = tree.feasible(20)
    r0 = next(r for r in range(19) if F[r] == F[r + 1])
    alive = all(bool(F[n][0]) for n in range(r0 + 1))
    st = Steps(tree)
    rs = st.stable_closure()
    ra = st.least_r(12) if rs is not None else None
    e = every_depth_cross(tree, k)
    seqs = e['sequences']
    every_s = all(x is not None for seq in seqs.values() for x in seq)
    stable = seqs['r>=%d' % e['r0']]
    tail = stable[e['start']:] if e['start'] < len(stable) else stable
    return dict(small_orbits=True, alive_every_depth=alive, r0=r0, types=len(tree.types), r_stable=rs, r_all=ra,
                two_orbit_every_s=every_s, two_orbit_tail_max=max((x for x in tail if x is not None), default=None),
                two_orbit_first=stable[:8], tiers=sorted(seqs))
