"""Gates of the handle and the carry rule (SIGNED-NAV-20261117-001; groundwork, no claims).

  H-plain            a handle run of the whole budget equals the plain run (flips, total incidences, final state), for
                     every rule and policy, on unsigned and signed patterns;
  H-epochs           the same run split into epochs of random lengths equals it;
  H-rebuild-identity the run split into epochs with a rebuild onto the unchanged pattern at every boundary (state read,
                     carried by the rule, a new handle) equals it: the carried state is the whole state;
  H-rebuild-gauge    re-signing a random set of distinctions at every rebuild (their values flipped by the rule's parity)
                     continues the run exactly, final states differing by the accumulated re-signing;
  H-merge            replaying the slow loop's real rebuild sequences (tie merges; capture_rebuilt.py --sequences), with the
                     memory carried by the rule at each merge: every run solves, its state mapped back satisfies every
                     original knot, and the carried memory is consistent (last flips and visits not after t). Flips are
                     reported beside a fresh restart at each rebuild (memory dropped) as context, not as a result.
Exits non-zero on any failure; writes handle_gates.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import engine as E  # noqa: E402
import handle as H  # noqa: E402

POL = json.loads((ROOT / "artifacts/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/policies.json").read_text())
ART = ROOT / "artifacts/SIGNED-NAV-20261117-001/SIGNED-NAV-20261117-001-E001_signed_engine"
RULES = [("walksat", (0.5,)), ("probsat_poly", (1.8, 1.0)), ("novelty_plus", (0.7, 0.01)), ("sticky", (1.8, 1.0, 0.6)), ("fms", (0.5,))]
ARMS = ["D_s0", "Dr_s0", "Dn_s0", "L3sm_s0"]
CAP = 10**6


def arms():
    for a, prm in RULES:
        yield a, a, prm, None, 0
    for arm in ARMS:
        yield arm, "policy", (), np.load(POL[arm]["theta"]), int(POL[arm]["flags"])


def instances():
    rng = np.random.default_rng(3)
    for i in range(6):
        fam, alpha, w = [("rand", 2.1, 10), ("local", 4.0, 10), ("block", 2.5, 20)][i % 3]
        base = E.planted(fam, 300, alpha, 960_100 + i, w=w)
        signs = rng.integers(0, 2, (base.m, 3)).astype(np.uint8) if i >= 3 else None
        yield f"{fam}{'-signed' if signs is not None else ''}-{i}", E.Instance(base.n, base.knots, signs=signs)


def epochs(rng, cap):
    left = cap
    while left > 0:
        b = int(rng.integers(1, 400))
        yield min(b, left)
        left -= b


def main():
    fails, rep = [], {}
    counts = dict.fromkeys(["H-plain", "H-epochs", "H-rebuild-identity", "H-rebuild-gauge"], 0)
    for name, inst in instances():
        x0 = np.random.default_rng(len(name)).integers(0, 2, inst.n).astype(np.uint8)
        for label, algo, prm, th, fl in arms():
            seed = 77
            ref = E.run(inst, algo, prm, theta=th, flags=fl, seed=seed, max_flips=CAP, want_state=True, x0=x0)
            # H-plain
            h = H.AgentHandle(inst, algo, prm, th, fl, seed, x0=x0)
            r = h.run(CAP)
            ok = r["flips"] == ref["flips"] and np.array_equal(h.state().x, ref["state"]) and h.work_total() == ref["work"]
            counts["H-plain"] += 1
            if not ok:
                fails.append(f"H-plain {name} {label}: {r['flips']} vs {ref['flips']}")
            h.close()
            # H-epochs
            rng = np.random.default_rng(5)
            h = H.AgentHandle(inst, algo, prm, th, fl, seed, x0=x0)
            tot = 0
            for b in epochs(rng, CAP):
                r = h.run(b)
                tot += r["flips"]
                if r["solved"]:
                    break
            ok = tot == ref["flips"] and np.array_equal(h.state().x, ref["state"]) and h.work_total() == ref["work"]
            counts["H-epochs"] += 1
            if not ok:
                fails.append(f"H-epochs {name} {label}: {tot} vs {ref['flips']}")
            h.close()
            # H-rebuild-identity
            rng = np.random.default_rng(6)
            h = H.AgentHandle(inst, algo, prm, th, fl, seed, x0=x0)
            tot = 0
            dist_from, par, knot_from = H.identity_maps(inst)
            for b in epochs(rng, CAP):
                r = h.run(b)
                tot += r["flips"]
                if r["solved"]:
                    break
                st = H.carry(h.state(), inst.n, inst.m, dist_from, par, knot_from)
                h.close()
                h = H.AgentHandle(inst, algo, prm, th, fl, seed, state=st)
            ok = tot == ref["flips"] and np.array_equal(h.state().x, ref["state"])
            counts["H-rebuild-identity"] += 1
            if not ok:
                fails.append(f"H-rebuild-identity {name} {label}: {tot} vs {ref['flips']}")
            h.close()
            # H-rebuild-gauge
            rng = np.random.default_rng(8)
            h = H.AgentHandle(inst, algo, prm, th, fl, seed, x0=x0)
            cur = inst
            gacc = np.zeros(inst.n, np.uint8)
            tot = 0
            for b in epochs(rng, CAP):
                r = h.run(b)
                tot += r["flips"]
                if r["solved"]:
                    break
                g = rng.integers(0, 2, inst.n).astype(np.uint8)
                signs = (cur.signs if cur.signs is not None else np.zeros((cur.m, 3), np.uint8)) ^ g[cur.knots]
                new = E.Instance(cur.n, cur.knots, signs=signs)
                st = H.carry(h.state(), new.n, new.m, [[v] for v in range(new.n)], g, [[k] for k in range(new.m)])
                h.close()
                h = H.AgentHandle(new, algo, prm, th, fl, seed, state=st)
                cur = new
                gacc ^= g
            ok = tot == ref["flips"] and np.array_equal(h.state().x ^ gacc, ref["state"])
            counts["H-rebuild-gauge"] += 1
            if not ok:
                fails.append(f"H-rebuild-gauge {name} {label}: {tot} vs {ref['flips']}")
            h.close()
        print(name, "ok so far" if not fails else f"{len(fails)} failures", flush=True)
    rep.update(counts)

    # H-merge
    rows = []
    for f in sorted(ART.glob("rebuilt/seq_*.npz")):
        d = np.load(f)
        knots0 = d["knots0"]
        n0 = int(knots0.max()) + 1 if len(knots0) else 0
        n0 = max(n0, int(d["root0"].shape[0]))
        cnt = int(d["count"])
        pats = [(np.arange(n0), knots0.astype(np.int32), np.zeros(knots0.shape, np.uint8), np.arange(n0), np.zeros(n0, np.uint8))]
        for j in range(cnt):
            pats.append((d[f"roots{j}"], d[f"kv{j}"], d[f"ks{j}"], d[f"root{j}"], d[f"rpar{j}"]))
        for arm in ("Dr_s0", "D_s0"):
            th, fl = np.load(POL[arm]["theta"]), int(POL[arm]["flags"])
            for carry_mem in (True, False):
                roots, kv, ks, root, rpar = pats[0]
                inst = E.Instance(len(roots), kv, signs=ks)
                h = H.AgentHandle(inst, "policy", (), th, fl, 99)
                tot, solved, j = 0, False, 0
                while tot < 2 * 10**6:
                    r = h.run(inst.n)
                    tot += r["flips"]
                    if r["solved"]:
                        solved = True
                        break
                    if j + 1 < len(pats):
                        j += 1
                        roots2, kv2, ks2, root2, rpar2 = pats[j]
                        new = E.Instance(len(roots2), kv2, signs=ks2)
                        idx2 = {int(r_): i for i, r_ in enumerate(roots2)}
                        # old class i (root roots[i]) -> new class of that root; parity rpar2 at the old root
                        dist_from = [[] for _ in range(len(roots2))]
                        par = np.zeros(len(roots), np.uint8)
                        for i, r_ in enumerate(roots):
                            c = idx2[int(root2[int(r_)])]
                            dist_from[c].append(i)
                            par[i] = rpar2[int(r_)]
                        # knots by canonical signature in the new class ids
                        def canon(members, signs):
                            o = np.argsort(members)
                            m_, s_ = members[o], signs[o]
                            if s_[0]:
                                s_ = s_ ^ 1
                            return tuple(m_) + tuple(s_)
                        newsig = {canon(kv2[k], ks2[k]): k for k in range(len(kv2))}
                        knot_from = [[] for _ in range(len(kv2))]
                        for k in range(len(kv)):
                            mem = np.array([idx2[int(root2[int(roots[v])])] for v in kv[k]])
                            sg = np.array([ks[k][q] ^ par[kv[k][q]] for q in range(3)], dtype=np.uint8)
                            key = canon(mem, sg)
                            if key in newsig:
                                knot_from[newsig[key]].append(k)
                        st = h.state()
                        if carry_mem:
                            st2 = H.carry(st, new.n, new.m, dist_from, par, knot_from)
                            if np.any(st2.lastflip > st2.t) or np.any(st2.lastvisit > st2.t):
                                fails.append(f"H-merge memory after t on {f.name}")
                            h.close()
                            h = H.AgentHandle(new, "policy", (), th, fl, 99, state=st2)
                        else:
                            x2 = H.carry(st, new.n, new.m, dist_from, par, knot_from).x
                            h.close()
                            h = H.AgentHandle(new, "policy", (), th, fl, 99 + j, x0=x2)
                        roots, kv, ks, root, rpar, inst = roots2, kv2, ks2, root2, rpar2, new
                # map back to the original distinctions and check on the original knots
                xr = h.state().x
                idxr = {int(r_): i for i, r_ in enumerate(roots)}
                xo = np.array([xr[idxr[int(root[v])]] ^ rpar[v] for v in range(n0)], dtype=np.uint8)
                s = xo[knots0].sum(axis=1)
                ok = solved and bool(np.all((s == 1) | (s == 2)))
                if not ok:
                    fails.append(f"H-merge {f.name} {arm} carry={carry_mem}: solved {solved}, original knots satisfied {bool(np.all((s == 1) | (s == 2)))}")
                rows.append({"pattern": f.name, "arm": arm, "carry_memory": carry_mem, "rebuilds_used": j, "flips": tot, "ok": ok})
                h.close()
        print(f.name, [(r_["arm"], r_["carry_memory"], r_["flips"], r_["ok"]) for r_ in rows[-4:]], flush=True)
    rep["H-merge"] = rows
    rep["fails"] = fails
    (ART / "handle_gates.json").write_text(json.dumps(rep, indent=1, default=float))
    print({k: v for k, v in counts.items()}, "H-merge runs", len(rows))
    print("GATE", "PASS" if not fails else "FAIL")
    for x in fails[:20]:
        print("  ", x)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
