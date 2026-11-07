"""The random island packing behind the size bound, for SPHERE-SIZE-20261107-001B.

Hard-core packing on K_k: every admissible point (farther than s + 3 from the corners) proposes itself as an island centre with
probability eps, independently; a proposal is kept when no other proposal lies within distance 2s + d_sep of it. Kept islands (balls of
radius s) are then pairwise at distance >= d_sep, and each gets an independent uniform label.

Coverage. A point p is fixed when some kept centre lies within distance s of p. Two kept centres cannot both do so, so
P(p fixed) = sum over admissible c within s of p of eps (1 - eps)^(|B(c, 2s + d_sep)| - 1) when all those c are admissible.
Locality. Whether p is fixed, and its colour, depends only on proposals within distance 3s + d_sep of p and on one label, so the events
for points farther than 2(3s + d_sep) apart are independent.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/SPHERE-SIZE-20261107-001A/SPHERE-SIZE-20261107-001A-P001_islands_keep_the_count_hard"))
import island_lib as I  # noqa: E402

W = I.W


def coverage_bound(K, s, d_sep, eps, p, dist_cache):
    """the exact coverage probability of point p (all centres near p admissible), from the formula above"""
    dp = dist_cache(p)
    tot = 0.0
    for c in range(K["n"]):
        if dp[c] <= s:
            dc = dist_cache(c)
            m = sum(1 for q in range(K["n"]) if dc[q] <= 2 * s + d_sep)
            tot += eps * (1 - eps) ** (m - 1)
    return tot


def sample_coverage(K, s, d_sep, eps, rng, trials, points):
    """Monte Carlo: fraction of packings that fix each listed point, and the minimum separation seen"""
    hits = {p: 0 for p in points}
    min_sep = None
    for _ in range(trials):
        isl = I.packing(K, s, d_sep, eps, rng, corner_margin=s + 3)
        allp = {}
        for j, (c, pts) in enumerate(isl):
            for q in pts:
                allp[q] = j
        for p in points:
            hits[p] += p in allp
        for j, (c, pts) in enumerate(isl):
            d = W.bfs(K["adj"], list(pts), K["n"])
            for j2, (c2, pts2) in enumerate(isl):
                if j2 != j:
                    sep = min(d[q] for q in pts2)
                    min_sep = sep if min_sep is None else min(min_sep, sep)
    return {p: hits[p] / trials for p in points}, min_sep
