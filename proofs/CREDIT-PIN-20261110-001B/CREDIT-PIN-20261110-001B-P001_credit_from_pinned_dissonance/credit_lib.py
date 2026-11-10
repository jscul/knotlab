"""The credit learner (research/CREDIT-PIN-20261110-001/preregistration.md, ticket B, stage 2).

Ticket A's fixed learner, plus credit from pinned dissonance: while some example asks for a decided output, every 10 failed probes the
learner runs a state-only plateau walk (a random point flipped when W does not rise) of 20,000 steps on a copy. A face is pinned when
its closed neighbourhood (the face and every face sharing a line with it) never clears of dissonance during the walk. An attention line
whose three corner faces are all pinned, and which does not pass through an interface point, is cooled: the learner no longer changes
its signs, keeping what holds. The cooled set is replaced at each such walk and emptied at each new target. Nothing else changes."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CREDIT-PIN-20261110-001A/CREDIT-PIN-20261110-001A-P001_the_fixed_learner"))
import fix_lib as F  # noqa: E402

I, W = F.I, F.W
PARAMS = dict(F.PARAMS, pin_every=10, tau_pin=20000)


def neighbourhoods(E):
    """for each face, itself and every face sharing a line with it"""
    nb = [{v} for v in range(E.V)]
    for i in range(E.n):
        for a in E.face[i]:
            nb[a] |= set(E.face[i])
    return nb


def cooled_lines(E, nb, rng, tau, att, interface):
    snap = E.snapshot()

    def dissonant(v):
        return E.ag[v] >= 2 or E.ag[v] % 2 == 0
    cand = {v for i in att for v in E.face[i]}
    pinned = {v for v in cand if any(dissonant(u) for u in nb[v])}
    for _ in range(tau):
        if not pinned:
            break
        p = rng.randrange(E.n)
        sites = E.sites_of_point[p]
        d, nv, dag = E.delta(sites)
        if d <= 0:
            E.x[p] ^= 1
            E.apply(sites, d, nv, dag)
            pinned = {v for v in pinned if any(dissonant(u) for u in nb[v])}
    E.restore(snap)
    return {i for i in att if all(v in pinned for v in E.face[i]) and not any(E.pt[i][k] in interface for k in range(3))}


def learn(E, K, ports, target, floor2, rng, params=PARAMS):
    """fix_lib.learn with cooling; returns (steps, probes, radius, stalls, credit), credit the cooled-set sizes at each walk"""
    nb = neighbourhoods(E)
    use_credit = any(y != "u" for y in target)
    r, att, fails, probes, above, stalls = 0, I.near_lines(K, ports, 0), 0, 0, 0, 0
    cool, credit = set(), []
    for t in range(params["budget"]):
        if t % params["probe_every"] == 0:
            if E.W == floor2:
                above = 0
                probes += 1
                if I.probe(E, ports, target, floor2, rng, params["tau"]) == 0:
                    return t, probes, r, stalls, credit
                fails += 1
                if fails % params["widen"] == 0 and r < params["rmax"]:
                    r += 1
                    att = I.near_lines(K, ports, r)
                if use_credit and fails % params["pin_every"] == 0:
                    cool = cooled_lines(E, nb, rng, params["tau_pin"], att, set(ports))
                    credit.append(len(cool))
            else:
                above += 1
                if above % params["widen"] == 0:
                    stalls += 1
                    if r < params["rmax"]:
                        r += 1
                        att = I.near_lines(K, ports, r)
        if rng.random() < 0.5:
            p = rng.randrange(E.n)
            sites, mv = E.sites_of_point[p], ("flip", p)
            hot = any(i in att for (i, _) in sites)
        else:
            ls = [st for st in E.learn_sites() if st[0] in att and st[0] not in cool]
            if not ls:
                continue
            st = rng.choice(ls)
            sites, mv, hot = [st], ("learn",) + st, True
        T = params["T_hot"] if hot else params["T_cold"]
        d, nv, dag = E.delta(sites)
        if E.W + d > floor2 + params["envelope"]:
            continue
        if d <= 0 or rng.random() < math.exp(-d / T):
            if mv[0] == "flip":
                E.x[mv[1]] ^= 1
            else:
                E.s[3 * mv[1] + mv[2]] ^= 1
            E.apply(sites, d, nv, dag)
    return None, probes, r, stalls, credit
