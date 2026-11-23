"""Gate row G of REVIEW-LEADS-20261123-001F (run first; stop if any part fails).

G1  the canonical checker reports that the rule fails K2 at three and four places
    (also at the other arities met, and the controls: parity alone and
    not-all-equal alone are knots);
G2  parity alone and not-all-equal alone reproduce, on the five-founder clock from
    the quiet start, the recorded range of signal fractions from 0 to 1;
G3  the quiet start stays quiet under the rule.

Also runs the checks of this study's own tooling (not part of row G): the
history counts against explicit named-distinction enumeration, the abstract ring
against the engine's real births, the SAT survival test against the counts.
"""

import itertools
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import both_laws as B

from knotlab.knots import check_knot  # noqa: E402  (tools is on sys.path via both_laws)
from knotlab.relations import Relation  # noqa: E402

OUT = B.OUT
OUT.mkdir(parents=True, exist_ok=True)


def words(arm, n):
    return [w for w in itertools.product((0, 1), repeat=n) if B.lawful(arm, n, sum(w))]


def relation(arm, n):
    names = tuple(f"x{i}" for i in range(n))
    return names, Relation(names, frozenset(tuple(bool(b) for b in w) for w in words(arm, n)))


def cnf(arm, n):
    names = [f"x{i}" for i in range(n)]
    allowed = set(words(arm, n))
    clauses = []
    for w in itertools.product((0, 1), repeat=n):
        if w not in allowed:
            clauses.append(" ".join(("~" if b else "") + nm for b, nm in zip(w, names)))
    return "; ".join(clauses), names


def cli_check(arm, n):
    text, names = cnf(arm, n)
    env = dict(os.environ, PYTHONPATH=str(B.ROOT / "tools"))
    r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", text,
                        "--loops", *names[:-1], "--contact", names[-1], "--json"],
                       capture_output=True, text=True, env=env, cwd=B.ROOT, check=True)
    return json.loads(r.stdout)


def g1():
    rows = []
    for arm in B.ARMS:
        for n in (3, 4, 5, 6, 7):
            names, rel = relation(arm, n)
            api = check_knot(rel, names[:-1], names[-1])
            row = {"arm": arm, "places": n, "allowed_words": len(rel.rows),
                   "K1": api.binding, "K2": api.loss_on_erasure, "K3": api.coexistence,
                   "is_knot": api.is_knot, "notes": list(api.notes)}
            if n in (3, 4):
                cli = cli_check(arm, n)
                row["cli"] = {"binding": cli["binding"], "loss_on_erasure": cli["loss_on_erasure"],
                              "coexistence": cli["coexistence"], "is_knot": cli["is_knot"]}
                assert (cli["binding"], cli["loss_on_erasure"], cli["coexistence"]) == (
                    api.binding, api.loss_on_erasure, api.coexistence)
            rows.append(row)
    rule34 = [r for r in rows if r["arm"] == "rule" and r["places"] in (3, 4)]
    controls = [r for r in rows if r["arm"] != "rule" and r["places"] in (3, 4)]
    ok = (all(r["K1"] and r["K3"] and not r["K2"] and not r["is_knot"] for r in rule34)
          and all(r["is_knot"] for r in controls))
    return {"pass": ok, "rows": rows}


def quiet_start_value():
    # ones at the first distinction of each of the five original meetings (0, 2, 3, 4, 5)
    return sum(1 << d for d in (0, 2, 3, 4, 5))


def g2_g3(five, order, ring_struct):
    S = B.Starts(five.stars)
    live = [u for u in range(five.n0) if five.loose(u) > 0]
    quiet = quiet_start_value()
    lawful_arms = {arm: S.is_lawful(arm, quiet) for arm in B.ARMS}
    c_knot = S.carried(quiet, live)
    c_phase = tuple(c_knot[live.index(order[p])] for p in range(5))
    out = {"quiet_start_value": quiet, "founding_ones_at_distinctions": [0, 2, 3, 4, 5],
           "lawful_under": lawful_arms, "carried_by_phase": c_phase}
    g2 = {}
    for arm in ("parity", "nae"):
        R = B.Ring(arm, 30)
        pats = R.future(0, c_phase)
        counts = sorted({sum(p) for p in pats})
        g2[arm] = {"patterns_of_six": len(pats), "signal_counts": counts,
                   "fractions": [f"{k}/6" for k in counts], "histories": str(sum(pats.values())),
                   "pass": len(pats) == 64 and counts == list(range(7))}
    R = B.Ring("rule", 30)
    pats = R.future(0, c_phase)
    ok_quiet = (len(pats) == 1 and set(pats) == {(0,) * 6} and sum(pats.values()) == 1)
    reach = R.reach([c_phase])
    carried = [sorted({sum(c) for c in layer}) for layer in reach]
    alternating = all(carried[t] == [0 if t % 2 == 0 else 10] for t in range(31))
    # engine cross-check at depth 4
    generic = B.HistoryCounter(five, "rule", 4).count(c_knot)
    g3 = {"histories": sum(pats.values()), "patterns": [list(p) for p in pats],
          "carried_count_by_stage": carried, "alternates_0_10": alternating,
          "engine_count_depth4": generic,
          "pass": bool(lawful_arms["rule"] and ok_quiet and alternating and generic == 1)}
    out["G2"], out["G3"] = g2, g3
    out["pass_G2"] = all(v["pass"] for v in g2.values()) and lawful_arms["parity"] and lawful_arms["nae"]
    out["pass_G3"] = g3["pass"]
    return out


def tooling(five, order):
    S = B.Starts(five.stars)
    live = [u for u in range(five.n0) if five.loose(u) > 0]
    res = {}
    # (i) engine counts against explicit named-distinction enumeration
    rows = []
    for arm, depth, want in (("rule", 1, 5), ("parity", 1, 5), ("nae", 1, 3), ("rule", 2, 2)):
        hc = B.HistoryCounter(five, arm, depth)
        rng = random.Random(5 + depth)
        n = 0
        while n < want:
            v = rng.getrandbits(S.D)
            if not S.is_lawful(arm, v):
                continue
            c = S.carried(v, live)
            cnt = hc.count(c)
            if cnt == 0:
                continue
            lit, flow = B.brute_force_classes(five, arm, depth, v)
            fac = math.prod(math.factorial(ci) * math.factorial(five.loose(u) - ci)
                            for u, ci in zip(live, c))
            rows.append({"arm": arm, "depth": depth, "start": v, "carried": c,
                         "engine_value_flow": cnt, "enumerated_value_flow": flow,
                         "engine_times_label_factor": cnt * fac, "enumerated_fresh_renaming_only": lit,
                         "agree": cnt == flow and cnt * fac == lit})
            n += 1
    res["engine_vs_named_distinction_enumeration"] = rows
    # (ii) abstract ring against the engine on the real births
    rows = []
    for arm in B.ARMS:
        rng = random.Random(77)
        for depth in (1, 2, 3, 5, 6):
            R = B.Ring(arm, depth)
            hc = B.HistoryCounter(five, arm, depth)
            for _ in range(6):
                while True:
                    v = rng.getrandbits(S.D)
                    if S.is_lawful(arm, v):
                        break
                c = S.carried(v, live)
                cp = tuple(c[live.index(order[p])] for p in range(5))
                a, b = sum(R.future(0, cp).values()), hc.count(c)
                rows.append({"arm": arm, "depth": depth, "ring": str(a), "engine": str(b), "agree": a == b})
    res["ring_vs_engine"] = rows
    # (iii) SAT survival against the counts
    rows = []
    for arm in B.ARMS:
        for depth in (1, 2, 3):
            sat = B.Survival(five, arm, depth)
            hc = B.HistoryCounter(five, arm, depth)
            rng = random.Random(9)
            for _ in range(8):
                while True:
                    v = rng.getrandbits(S.D)
                    if S.is_lawful(arm, v):
                        break
                c = S.carried(v, live)
                rows.append({"arm": arm, "depth": depth, "sat_alive": sat.alive(c),
                             "count_positive": hc.count(c) > 0,
                             "agree": sat.alive(c) == (hc.count(c) > 0)})
    res["sat_vs_count_on_clock"] = rows
    seven = B.build_structure("seven", B.seven_source(), 8, 300)
    S7 = B.Starts(seven.stars)
    live7 = [u for u in range(seven.n0) if seven.loose(u) > 0]
    rows = []
    for arm in B.ARMS:
        for depth in (1, 2):
            sat = B.Survival(seven, arm, depth)
            hc = B.HistoryCounter(seven, arm, depth)
            rng = random.Random(10)
            for _ in range(10):
                while True:
                    v = rng.getrandbits(S7.D)
                    if S7.is_lawful(arm, v):
                        break
                c = S7.carried(v, live7)
                rows.append({"arm": arm, "depth": depth, "sat_alive": sat.alive(c),
                             "count_positive": hc.count(c) > 0,
                             "agree": sat.alive(c) == (hc.count(c) > 0)})
    res["sat_vs_count_on_seven"] = rows
    # (iv) the hand null of counting_null.md (H7) for carried count 1 and 9, which no lawful
    # start has (the five founders' weights sum to twice the shared ones plus C0, so C0 is even)
    R = B.Ring("rule", 30)
    rows = []
    for p0 in range(5):
        c1 = tuple(1 if p == p0 else 0 for p in range(5))
        c9 = tuple(1 if p == p0 else 2 for p in range(5))
        nul = dict(B.null_single_position(p0))
        for label, c in (("C0=1", c1), ("C0=9", c9)):
            byk = dict(R.future_counts(0, c))
            rows.append({"single_at_phase": p0, "case": label, "histories": str(sum(byk.values())),
                         "agree": byk == nul and sum(byk.values()) == 2 ** 30})
    res["hand_null_H7_carried_count_1_and_9"] = rows
    # (v) negative controls: arms that do remove starts, SAT against counts
    rows = []
    orig = B.lawful

    def patched(arm, n, k):
        if arm == "zero":
            return k == 0
        if arm == "le1":
            return k <= 1
        return orig(arm, n, k)

    B.lawful = patched
    try:
        import itertools as it
        cs = list(it.product(*[range(seven.loose(u) + 1) for u in live7]))
        for arm in ("zero", "le1"):
            for depth in (1, 2, 6):
                sat = B.Survival(seven, arm, depth)
                dead = sum(1 for c in cs if not sat.alive(c))
                mism = None
                if depth <= 2:
                    hc = B.HistoryCounter(seven, arm, depth)
                    mism = sum(1 for c in cs if sat.alive(c) != (hc.count(c) > 0))
                rows.append({"control_arm": arm, "depth": depth, "carried_vectors": len(cs),
                             "removed": dead, "sat_count_mismatches": mism,
                             "agree": (mism in (0, None)) and dead > 0})
    finally:
        B.lawful = orig
    res["negative_controls_removal_is_detected"] = rows
    res["pass"] = all(r["agree"] for key in res if key != "pass" for r in res[key])
    return res


def main():
    t0 = time.time()
    five = B.build_structure("five", B.five_source(), 30, 300)
    order, marker, ring, words_, returns = B.clock_phases(five)
    facts = {"horizon": five.horizon, "knots_by_step": five.knots_by_step,
             "both_laws_give_same_births": five.both_laws_agree,
             "phase_order_of_founders": order, "marker": marker, "returns_at_cuts": returns,
             "founder_arities": sorted(Counter(len(r) for r in five.stars).items()),
             "each_cut": "5 births, 2 parents, 2 fresh, 4 places"}
    result = {"sources": B.source_hashes(), "clock_facts": facts}
    result["G1"] = g1()
    print("G1", result["G1"]["pass"], round(time.time() - t0, 1), flush=True)
    result["G23"] = g2_g3(five, order, ring)
    print("G2", result["G23"]["pass_G2"], "G3", result["G23"]["pass_G3"], round(time.time() - t0, 1), flush=True)
    result["tooling_checks"] = tooling(five, order)
    print("tooling", result["tooling_checks"]["pass"], round(time.time() - t0, 1), flush=True)
    result["returns_ok"] = returns == [5, 10, 15, 20, 25, 30]
    result["row_G_pass"] = bool(result["G1"]["pass"] and result["G23"]["pass_G2"]
                                and result["G23"]["pass_G3"] and result["returns_ok"])
    result["tooling_pass"] = result["tooling_checks"]["pass"]
    result["seconds"] = round(time.time() - t0, 1)
    (OUT / "gate.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    print("ROW G", "PASS" if result["row_G_pass"] else "FAIL", "tooling", result["tooling_pass"])
    return 0 if result["row_G_pass"] and result["tooling_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
