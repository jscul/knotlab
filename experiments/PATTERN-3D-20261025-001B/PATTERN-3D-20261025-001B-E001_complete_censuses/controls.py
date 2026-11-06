#!/usr/bin/env python3
"""Controls for PATTERN-3D-20261025-001B-E001, run before run.py.
(i) The C census and the independent standard-library law test of PATTERN-3D-20261025-001A-P001 agree, verdict and constants, on
    3,000 random relations on three labels (densities 0.15 to 0.9), 1,500 random tables on four labels, 300 tables with one entry
    changed from a group table, and planted rules (groups, the pair groupoid inside a Latin square, a constant inside junk, two
    constants, the free law; and failing ones: merged identities, the projection, an unequal union, a non-group monoid).
(ii) The classifier rejects planted rules that are not groupoid pullbacks and accepts planted groupoids.
Writes controls.json."""
from __future__ import annotations

import itertools
import json
import random

from common import A, OUT, build_binary, classify_reduced, decode_relation, decode_table, encode_relation, encode_table, run_census

CAT = {"empty": "empty", "mu0": "mu = 0", "fail14": "fails 1-4", "fail23": "fails 2-3", "surv": "survives"}


def c_verdict(exe, mode, n, idx):
    surv, stats = run_census(exe, mode, n, idx, idx + 1)
    cat = next(CAT[k] for k, v in stats.items() if v)
    return (cat, surv[0][1], surv[0][2]) if surv else (cat, None, None)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    exe = build_binary()
    rng = random.Random(20261028)
    out = {}
    # (i) agreement
    disagreements = []
    tested = {"random relations (3 labels)": 0, "random tables (4 labels)": 0, "perturbed group tables": 0, "planted": 0}
    survivors_seen = 0

    def compare(kind, mode, n, idx, R):
        nonlocal survivors_seen
        cv = c_verdict(exe, mode, n, idx)
        pv = A.Law(R).verdict()
        tested[kind] += 1
        survivors_seen += cv[0] == "survives"
        if cv != pv:
            disagreements.append({"kind": kind, "mode": mode, "index": idx, "C": cv, "python": pv})
        return cv

    dens = [0.15, 0.35, 0.55, 0.75, 0.9]
    for k in range(3000):
        R = {t for t in itertools.product(range(3), repeat=3) if rng.random() < dens[k % 5]}
        compare("random relations (3 labels)", "rel", 3, encode_relation(R, 3), R)
    for k in range(1500):
        idx = rng.randrange(4 ** 16)
        compare("random tables (4 labels)", "tab", 4, idx, decode_table(idx, 4))
    groups4 = ["0123/1230/2301/3012", "0123/1032/2301/3210"]
    for k in range(300):
        rows = [list(r) for r in rng.choice(groups4).split("/")]
        perm = list(range(4)); rng.shuffle(perm)
        rows = [[str(perm[int(rows[perm.index(a)][perm.index(b)])]) for b in range(4)] for a in range(4)]
        a, b = rng.randrange(4), rng.randrange(4)
        rows[a][b] = str((int(rows[a][b]) + rng.randrange(1, 4)) % 4)
        idx = encode_table("/".join("".join(r) for r in rows))
        compare("perturbed group tables", "tab", 4, idx, decode_table(idx, 4))
    planted = {
        "Z3 relation (survives 1,3)": ("rel", 3, encode_relation({(a, b, (a + b) % 3) for a in range(3) for b in range(3)}, 3)),
        "free relation on three labels (survives 3,81)": ("rel", 3, 2 ** 27 - 1),
        "pair groupoid with identities merged (fails)": ("rel", 3, encode_relation({(0, 0, 0), (0, 1, 1), (1, 0, 1), (0, 2, 2), (2, 0, 2), (1, 2, 0), (2, 1, 0)}, 3)),
        "projection x*y = x (fails 2-3)": ("rel", 3, encode_relation({(a, b, a) for a in range(3) for b in range(3)}, 3)),
        "Z2 plus a constant (fails)": ("rel", 3, encode_relation({(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0), (2, 2, 2)}, 3)),
        "Z4 table (survives 1,4)": ("tab", 4, encode_table("0123/1230/2301/3012")),
        "Z2xZ2 table (survives 1,4)": ("tab", 4, encode_table("0123/1032/2301/3210")),
        "pair groupoid in a Latin square (survives 1,2)": ("tab", 4, encode_table("0213/1302/3120/2031")),
        "one constant inside junk (survives 1,1)": ("tab", 4, encode_table("1333/2102/3331/0000")),
        "two constants inside junk (survives 1,1)": ("tab", 4, encode_table("0212/3130/3003/2221")),
        "monoid {0,1} padded (fails)": ("tab", 4, encode_table("0000/0123/0222/0323")),
    }
    planted_verdicts = {}
    for name, (mode, n, idx) in planted.items():
        R = decode_relation(idx, n) if mode == "rel" else decode_table(idx, n)
        v = compare("planted", mode, n, idx, R)
        planted_verdicts[name] = v
    want = {"Z3 relation (survives 1,3)": ("survives", 1, 3), "free relation on three labels (survives 3,81)": ("survives", 3, 81),
            "Z4 table (survives 1,4)": ("survives", 1, 4), "Z2xZ2 table (survives 1,4)": ("survives", 1, 4),
            "pair groupoid in a Latin square (survives 1,2)": ("survives", 1, 2),
            "one constant inside junk (survives 1,1)": ("survives", 1, 1), "two constants inside junk (survives 1,1)": ("survives", 1, 1)}
    planted_ok = all((planted_verdicts[k] == want[k]) if k in want else planted_verdicts[k][0] != "survives" for k in planted)
    out["(i) agreement"] = {"tested": tested, "survivors among tested": survivors_seen, "disagreements": disagreements[:20],
                            "agree": not disagreements, "planted verdicts": planted_verdicts, "planted as expected": planted_ok}
    # (ii) classifier
    rejects = {
        "monoid {0,1}": {(a, b, a * b) for a in (0, 1) for b in (0, 1)},
        "Z3 with one entry changed": {(a, b, (a + b) % 3 if (a, b) != (1, 1) else 0) for a in range(3) for b in range(3)},
        "merged pair groupoid": {(0, 0, 0), (0, 1, 1), (1, 0, 1), (0, 2, 2), (2, 0, 2), (1, 2, 0), (2, 1, 0)},
        "free on two labels plus one constant": set(itertools.product((0, 1), repeat=3)) | {(2, 2, 2)},
    }
    accepts = {
        "Z3": ({(a, b, (a + b) % 3) for a in range(3) for b in range(3)}, 3, 1, 3),
        "free on three labels": (set(itertools.product(range(3), repeat=3)), 3, 3, 81),
        "two constants": ({(0, 0, 0), (1, 1, 1)}, 2, 1, 1),
        "pair groupoid": (A.reduced(decode_table(encode_table("0213/1302/3120/2031"), 4)), 4, 1, 2),
    }
    rej = {k: classify_reduced(R, 3, 1, 3)[1] for k, R in rejects.items()}
    acc = {k: classify_reduced(R, n, lam, mu) for k, (R, n, lam, mu) in accepts.items()}
    out["(ii) classifier"] = {"rejections (must be False)": rej, "acceptances": acc,
                              "pass": not any(rej.values()) and all(v[1] for v in acc.values())}
    out["all_pass"] = out["(i) agreement"]["agree"] and planted_ok and out["(ii) classifier"]["pass"]
    (OUT / "controls.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({"all_pass": out["all_pass"], "tested": tested, "survivors": survivors_seen,
                      "disagreements": len(disagreements), "planted_ok": planted_ok, "classifier": out["(ii) classifier"]["pass"]}))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
