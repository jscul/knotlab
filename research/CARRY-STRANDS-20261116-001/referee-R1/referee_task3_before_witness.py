"""Referee R1: witnesses for 'keeping saves no phase for any distinction
forced before the narrowest phase' on the study's own instances (rebuilt by
referee_task3_random.study_instance).  Lists, per sample with a positive
before-fraction, the distinctions v with w=1 phase <= narrowest phase and
keep-law (w = 2) phase < ceil(sigma(v) / 2), marking those strictly before."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import referee_carry as R  # noqa: E402
import referee_task3_random as T  # noqa: E402

CASES = [(128, 10), (256, 17), (1024, 3), (1024, 8), (2048, 0), (2048, 4), (2048, 6), (4096, 1), (4096, 2)]
out = []
for n, s in CASES:
    atoms, order = T.study_instance(n, s)
    k = R.k_star(n, atoms, order)
    H = set(order[:k])
    sig = R.sigma(n, atoms, H)
    p1 = R.run_law(n, atoms, H, 1, "spend")["phase"]
    kp = R.run_law(n, atoms, H, 2, "keep")["phase"]
    sizes = [p1.count(t) for t in range(1, max(p1) + 1)]
    narrow = 1 + min(range(len(sizes) - 2), key=lambda i: sizes[i])
    wit = [{"v": v, "sigma": sig[v], "w1_phase": p1[v], "keep_w2_phase": kp[v], "strictly_before": p1[v] < narrow}
           for v in range(n) if v not in H and sig[v] < R.INF and p1[v] <= narrow and kp[v] < math.ceil(sig[v] / 2)]
    out.append({"case": f"rand-n{n}-s{s}", "narrow": narrow, "sizes": sizes, "witnesses": wit})
    print(n, s, narrow, sizes, [(w["v"], w["sigma"], w["w1_phase"], w["keep_w2_phase"], w["strictly_before"]) for w in wit])
with open(os.path.join(HERE, "referee_task3_before_witness.json"), "w") as fh:
    json.dump(out, fh, indent=1)
