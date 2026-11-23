"""Gates, every learner/arm/control once, and the tables of REVIEW-LEADS-20261123-001B-E001.

Run from the repository root (stages in order; `score` refuses to run twice):
    timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/run.py gates
    timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/run.py score

`gates` never opens a scorer key.  `score` re-derives the (deterministic) predictions from training rows and test pixels
only, then joins them with the scorer keys.  `selftest` runs the same plumbing on a throw-away copy with RANDOM labels.
"""

import csv
import json
import random
import sys
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import learners as Lr  # noqa: E402

FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
TICKET = "REVIEW-LEADS-20261123-001B"
ART = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_example_knots"
PANEL = ART / "panel"
SEED = 2026112302
ARMS = ("narrow", "varied")
REGIMES = ("true", "shuffled")
CONDS = ("a", "b", "c")
MAIN = ("L1", "L1+", "L2", "C1")
LOG = []


def P(*args):
    text = " ".join(str(a) for a in args)
    print(text)
    LOG.append(text)


def hexhash(b):
    return sha256(b).hexdigest()


def load(name):
    return [json.loads(line) for line in (PANEL / name).read_text().splitlines()]


def verify_panel():
    manifest = json.loads((PANEL / "manifest.json").read_text())
    bad = []
    for name, meta in manifest["files"].items():
        if hexhash((PANEL / name).read_bytes()) != meta["sha256"]:
            bad.append(name)
    P("panel manifest sha256", hexhash((PANEL / "manifest.json").read_bytes()), "| files verified:", len(manifest["files"]),
      "| mismatches:", bad)
    if bad:
        raise SystemExit(f"Panel hash mismatch: {bad}")
    return manifest


# --- predictions: training rows and test pixels only ------------------------------------------------------------
def predict(arm, regime, train, test):
    tr = train[(arm, regime)]
    px = [r["pixels"] for r in tr]
    lab = [r["label"] for r in tr]
    tpx = [r["pixels"] for r in test[arm]]
    out = {"arm": arm, "regime": regime}
    l1 = Lr.ParityLearner(0).fit(px, lab)
    plus, tried = Lr.fit_plus(px, lab)
    l2 = Lr.NaeLearner().fit(px, lab)
    c1 = Lr.CountReader().fit(px, lab)
    # C1 totals must equal the label-wise sums of histograms (the update does not depend on the guess)
    chk = [[0] * 16 for _ in range(2)]
    for p, y in zip(px, lab):
        for i, v in enumerate(c1.mod.histogram(c1.bits(p))):
            chk[y][i] += v
    out["c1_totals_match_labelwise_sums"] = chk == c1.model.totals
    out["learners"] = {"L1": l1, "L1+": plus}
    out["l1"] = {"consistent": l1.consistent, "rank": l1.rank, "n_features": l1.n, "new": l1.n_new, "implied": l1.n_implied,
                 "contradicting_on_arrival": l1.n_contradicting}
    out["plus"] = {"level": None if plus is None else Lr.FAMILY_NAMES[plus.level], "tried": tried,
                   "rank": None if plus is None else plus.rank, "n_features": None if plus is None else plus.n}
    out["l2_allowed_words"] = l2.n_allowed
    ans = {"L1": [l1.answer(p) for p in tpx],
           "L1+": [plus.answer(p) if plus else None for p in tpx],
           "L2": [l2.answer(p) for p in tpx]}
    c1d = [c1.decide_with_margin(p) for p in tpx]
    ans["C1"] = [g for g, _ in c1d]
    out["margin"] = [m for _, m in c1d]
    out["ans"] = ans
    return out


def sizes_report(train):
    rep = {}
    for arm in ARMS:
        px = [r["pixels"] for r in train[(arm, "true")]]
        for level in range(4):
            s = Lr.knot_sizes(px, level)
            rep[(arm, Lr.FAMILY_NAMES[level])] = {"knots": len(s), "below_three": sum(1 for x in s if x < 3), "below_three_without_constant": sum(1 for x in s if x - 1 < 3),
                                                  "size1": sum(1 for x in s if x == 1), "size2": sum(1 for x in s if x == 2),
                                                  "min": min(s), "max": max(s), "distinct_masks": len({Lr.feature_mask(p, level) for p in px})}
    return rep


# --- gates -----------------------------------------------------------------------------------------------------
def gates(preds, train, test):
    g = {}
    # G1 second implementation agrees on every item (dense GF(2) ranks; plus enumeration of the 65,536 words at F0)
    cmp = {"items_compared_dense": 0, "mismatches_dense": 0, "items_compared_enum": 0, "mismatches_enum": 0, "detail": []}
    for (arm, regime), pr in preds.items():
        masks_cache = {}
        for name in ("L1", "L1+"):
            learner = pr["learners"][name]
            if learner is None:
                continue
            tpx = [r["pixels"] for r in test[arm]]
            masks = [Lr.feature_mask(p, learner.level) for p in tpx]
            d = Lr.dense_forced(learner.knots, learner.n, set(masks))
            second = [d[m] for m in masks]
            mism = sum(1 for a, b in zip(pr["ans"][name], second) if a != b)
            cmp["items_compared_dense"] += len(second)
            cmp["mismatches_dense"] += mism
            row = {"arm": arm, "regime": regime, "learner": name, "level": Lr.FAMILY_NAMES[learner.level], "dense_mismatch": mism,
                   "answered": sum(a is not None for a in pr["ans"][name])}
            if learner.level == 0:
                e, n_allowed = Lr.enum_forced_parity(learner.knots, set(masks))
                third = [e[m] for m in masks]
                em = sum(1 for a, b in zip(pr["ans"][name], third) if a != b)
                cmp["items_compared_enum"] += len(third)
                cmp["mismatches_enum"] += em
                row.update({"enum_mismatch": em, "allowed_words_by_enumeration": n_allowed})
                # also: allowed-word existence agrees
                if (n_allowed > 0) != learner.consistent:
                    cmp["mismatches_enum"] += 1
                    row["enum_existence_mismatch"] = True
            cmp["detail"].append(row)
    g["second_implementation"] = cmp
    # G2 exchange and clearing of the kept knots between learners trained with opposite label meanings
    ex = []
    for (arm, regime), pr in preds.items():
        tr = train[(arm, regime)]
        px = [r["pixels"] for r in tr]
        flipped = [1 - r["label"] for r in tr]
        tpx = [r["pixels"] for r in test[arm]]
        for name in ("L1", "L1+"):
            A = pr["learners"][name]
            if A is None or not A.consistent:
                ex.append({"arm": arm, "regime": regime, "learner": name, "applicable": False})
                continue
            B = Lr.ParityLearner(A.level).fit(px, flipped)
            a0 = [A.answer(p) for p in tpx]
            b0 = [B.answer(p) for p in tpx]
            ak, bk = A.export_knots(), B.export_knots()
            A2 = Lr.ParityLearner(A.level)
            A2.load_knots(bk)
            B2 = Lr.ParityLearner(A.level)
            B2.load_knots(ak)
            a1 = [A2.answer(p) for p in tpx]
            b1 = [B2.answer(p) for p in tpx]
            rev = lambda x, y: all((u is None and v is None) or (u is not None and v is not None and u == 1 - v) for u, v in zip(x, y))
            A3 = Lr.ParityLearner(A.level)
            A3.load_knots(ak)
            A3.clear()
            cleared = [A3.answer(p) for p in tpx]
            ex.append({"arm": arm, "regime": regime, "learner": name, "applicable": True, "level": Lr.FAMILY_NAMES[A.level],
                       "answered_before": sum(x is not None for x in a0), "exchange_reverses_every_answer_A": rev(a1, a0),
                       "exchange_reverses_every_answer_B": rev(b1, b0), "opposite_meaning_learner_is_reversed_copy": rev(b0, a0),
                       "cleared_answered": sum(x is not None for x in cleared)})
    g["exchange_clearing"] = ex
    g["exchange_clearing_ok"] = all(r["exchange_reverses_every_answer_A"] and r["exchange_reverses_every_answer_B"]
                                    and r["opposite_meaning_learner_is_reversed_copy"] and r["cleared_answered"] == 0
                                    for r in ex if r["applicable"]) and any(r["applicable"] for r in ex)
    # G3 planted parity rule over F0, 20 random examples
    rng = random.Random(SEED)
    m_star = rng.getrandbits(16)
    rnd = lambda: "".join(str(rng.getrandbits(1)) for _ in range(64))
    ex_px = [rnd() for _ in range(20)]
    fresh = [rnd() for _ in range(2000)]
    rule = lambda p: int(Lr._PAR[Lr.feature_mask(p, 0) & m_star])
    L = Lr.ParityLearner(0).fit(ex_px, [rule(p) for p in ex_px])
    ans = [L.answer(p) for p in fresh]
    right = sum(1 for p, a in zip(fresh, ans) if a is not None and a == rule(p))
    wrong = sum(1 for p, a in zip(fresh, ans) if a is not None and a != rule(p))
    space = Lr.ParityLearner(0).fit(ex_px + fresh, [rule(p) for p in ex_px + fresh])
    masks = {Lr.feature_mask(p, 0) for p in fresh}
    d = Lr.dense_forced(L.knots, L.n, masks)
    e, nw = Lr.enum_forced_parity(L.knots, masks)
    fm = [Lr.feature_mask(p, 0) for p in fresh]
    g["planted_rule"] = {"planted_word_hex": hex(m_star), "examples": 20, "consistent": L.consistent, "rank_of_examples": L.rank,
                         "rank_of_all_2020_images": space.rank, "fresh": 2000, "answered": right + wrong, "right": right, "wrong": wrong,
                         "dense_agrees": all(a == d[m] for a, m in zip(ans, fm)), "enum_agrees": all(a == e[m] for a, m in zip(ans, fm)),
                         "allowed_words_by_enumeration": nw,
                         "pass": bool(L.consistent and wrong == 0 and right == 2000)}
    g["second_implementation_ok"] = cmp["mismatches_dense"] == 0 and cmp["mismatches_enum"] == 0
    g["all_pass"] = bool(g["second_implementation_ok"] and g["exchange_clearing_ok"] and g["planted_rule"]["pass"]
                         and all(pr["c1_totals_match_labelwise_sums"] for pr in preds.values()))
    return g


# --- scoring ---------------------------------------------------------------------------------------------------
def outcome(a, y):
    return "unanswered" if a is None else ("right" if a == y else "wrong")


def build_items(arm, regime, pr, keys, test):
    items = test[arm]
    n = len(items)
    cond = [keys[it["id"]]["condition"] for it in items]
    ans = {k: list(v) for k, v in pr["ans"].items()}
    for X in ("L1", "L1+"):
        ans[f"C1@{X}"] = [c if a is not None else None for c, a in zip(pr["ans"]["C1"], pr["ans"][X])]
        matched = [None] * n
        for c in CONDS:
            idx = [i for i in range(n) if cond[i] == c]
            k = sum(1 for i in idx if pr["ans"][X][i] is not None)
            order = sorted(idx, key=lambda i: (-pr["margin"][i], items[i]["id"]))
            for i in order[:k]:
                matched[i] = pr["ans"]["C1"][i]
        ans[f"C1m@{X}"] = matched
    rows = []
    for i, it in enumerate(items):
        k = keys[it["id"]]
        row = {"id": it["id"], "condition": cond[i], "letter": k["letter"], "q": k["q"], "design": k["design"], "label": k["label"]}
        for name, vals in ans.items():
            row[name] = outcome(vals[i], k["label"])
        rows.append(row)
    return rows, list(ans)


def tally(rows, learner, **where):
    c = Counter()
    for r in rows:
        if all(r[k] == v for k, v in where.items()):
            c[r[learner]] += 1
    return c["right"], c["wrong"], c["unanswered"]


def fmt(t):
    r, w, u = t
    n = r + w + u
    return f"{r}/{w}/{u}" + (f" ({(r + w) / n:.0%} answered)" if n else "")


def tables_and_verdicts(preds, items_by, names_by, sizes, g):
    md, V, counts_rows = [], {}, []
    for (arm, regime), rows in items_by.items():
        for name in names_by[(arm, regime)]:
            for cond in CONDS + ("all",):
                for letter in ("L", "T", "all"):
                    for q in (0, 1, 2, 3, "all"):
                        where = {}
                        if cond != "all": where["condition"] = cond
                        if letter != "all": where["letter"] = letter
                        if q != "all": where["q"] = q
                        sel = [r for r in rows if all(r[k] == v for k, v in where.items())]
                        if not sel:
                            continue
                        r_, w_, u_ = tally(rows, name, **where)
                        counts_rows.append([arm, regime, name, cond, letter, q, r_ + w_ + u_, r_, w_, u_,
                                            f"{(r_ + w_) / (r_ + w_ + u_):.4f}"])
    for regime in REGIMES:
        md.append(f"\n### Counts right / wrong / unanswered (coverage), labels: {regime}\n")
        for arm in ARMS:
            rows = items_by[(arm, regime)]
            md.append(f"\nArm **{arm}**; test items per condition: " + ", ".join(f"{c}={sum(1 for r in rows if r['condition'] == c)}" for c in CONDS) + "\n")
            md.append("| learner | condition a | condition b | condition c |")
            md.append("| --- | --- | --- | --- |")
            for name in names_by[(arm, regime)]:
                md.append(f"| {name} | " + " | ".join(fmt(tally(rows, name, condition=c)) for c in CONDS) + " |")
    # by letter and turn (true labels): L1, L1+, C1 on same items
    md.append("\n### By condition, letter and turn (true labels; right/wrong/unanswered)\n")
    for arm in ARMS:
        rows = items_by[(arm, "true")]
        for cond in CONDS:
            if not any(r["condition"] == cond for r in rows):
                continue
            md.append(f"\nArm **{arm}**, condition {cond}\n")
            md.append("| learner | " + " | ".join(f"{l} q{q}" for l in ("L", "T") for q in (0, 1, 2, 3)) + " |")
            md.append("| --- |" + " --- |" * 8)
            for name in ("L1", "L1+", "C1@L1+", "C1m@L1+", "C1"):
                cells = []
                for l in ("L", "T"):
                    for q in (0, 1, 2, 3):
                        sel = [r for r in rows if r["condition"] == cond and r["letter"] == l and r["q"] == q]
                        cells.append(fmt(tally(rows, name, condition=cond, letter=l, q=q)) if sel else "-")
                md.append(f"| {name} | " + " | ".join(cells) + " |")
    # features reached
    md.append("\n### Feature family reached by L1+, coverage, and the memory\n")
    md.append("| arm | labels | L1 (F0) has an allowed word | L1 rank of 16 | L1+ family | features | rank | families tried (name, allowed word, rank, features) | L2 allowed words of 65,536 |")
    md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for (arm, regime), pr in preds.items():
        md.append(f"| {arm} | {regime} | {pr['l1']['consistent']} | {pr['l1']['rank']} | {pr['plus']['level']} | {pr['plus']['n_features']} | "
                  f"{pr['plus']['rank']} | {pr['plus']['tried']} | {pr['l2_allowed_words']} |")
    md.append("\n### Example knots with fewer than three memory distinctions (training knots; the constant counts as one distinction)\n")
    md.append("| arm | family level | knots | below three | below three without the constant | of size 1 | of size 2 | smallest size | largest size | distinct knots (by odd-feature set) |")
    md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for (arm, lvl), s in sizes.items():
        md.append(f"| {arm} | up to {lvl} | {s['knots']} | {s['below_three']} | {s['below_three_without_constant']} | {s['size1']} | {s['size2']} | {s['min']} | {s['max']} | {s['distinct_masks']} |")

    # --- verdicts ---
    def T(arm, regime, name, **w):
        return tally(items_by[(arm, regime)], name, **w)

    V["P1"], V["P3"], V["P4"] = {}, {}, {}
    for arm in ARMS:
        pr = preds[(arm, "true")]
        if not pr["l1"]["consistent"]:
            V["P1"][arm] = {"applicable": False, "note": "no allowed memory word for L1 at F0"}
        else:
            ra, wa, ua = T(arm, "true", "L1", condition="a")
            rb, wb, ub = T(arm, "true", "L1", condition="b")
            V["P1"][arm] = {"applicable": True, "a": [ra, wa, ua], "b": [rb, wb, ub], "wrong_in_a_and_b": wa + wb, "answered_in_a_and_b": ra + wa + rb + wb}
        plus = pr["plus"]["level"]
        rb, wb, ub = T(arm, "true", "L1+", condition="b")
        cr, cw, cu = T(arm, "true", "C1@L1+", condition="b")
        mr, mw, mu = T(arm, "true", "C1m@L1+", condition="b")
        ans_b = rb + wb
        V["P3"][arm] = {"L1+_family": plus, "L1+_b": [rb, wb, ub], "C1_same_items_b": [cr, cw, cu], "C1_matched_b": [mr, mw, mu],
                        "answered": ans_b, "L1+_wrong_share": (wb / ans_b if ans_b else None), "C1_same_items_wrong_share": (cw / (cr + cw) if cr + cw else None),
                        "holds": bool(ans_b >= 1 and wb / ans_b < cw / (cr + cw))}
        prs = preds[(arm, "shuffled")]
        if not prs["l1"]["consistent"]:
            V["P4"][arm] = {"word_allowed": False, "holds": True, "note": "no allowed memory word with shuffled labels"}
        else:
            r_ = sum(T(arm, "shuffled", "L1", condition=c)[0] for c in CONDS)
            w_ = sum(T(arm, "shuffled", "L1", condition=c)[1] for c in CONDS)
            share = r_ / (r_ + w_) if r_ + w_ else None
            V["P4"][arm] = {"word_allowed": True, "answered": r_ + w_, "right": r_, "wrong": w_, "right_share": share,
                            "holds": (None if share is None else bool(0.35 <= share <= 0.65))}
    prv = preds[("varied", "true")]
    V["P2"] = {"L1_allows_no_word_in_varied_arm": not prv["l1"]["consistent"], "holds": not prv["l1"]["consistent"],
               "L1_rank": prv["l1"]["rank"], "knots_contradicting_on_arrival": prv["l1"]["contradicting_on_arrival"]}
    md.append("\n### Prediction verdicts (computed from the counts above)\n")
    md.append("```json\n" + json.dumps(V, indent=1, default=str) + "\n```")
    return "\n".join(md), V, counts_rows


def run_all(mode):
    verify_panel()
    train = {}
    for arm in ARMS:
        train[(arm, "true")] = load(f"train_{arm}.jsonl")
        train[(arm, "shuffled")] = load(f"train_{arm}_shuffled.jsonl")
    test = {arm: load(f"test_{arm}.jsonl") for arm in ARMS}
    assert all(set(r) == {"id", "pixels"} for arm in ARMS for r in test[arm]), "test files must carry no labels"
    for arm in ARMS:
        trp = {r["pixels"] for r in train[(arm, "true")]}
        assert not trp & {r["pixels"] for r in test[arm]}, "identical bitmap on both sides"
    preds = {(arm, reg): predict(arm, reg, train, test) for arm in ARMS for reg in REGIMES}
    sizes = sizes_report(train)
    g = gates(preds, train, test)
    return train, test, preds, sizes, g


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "gates"
    if mode not in ("gates", "score", "selftest"):
        raise SystemExit("usage: run.py gates|score|selftest")
    out = ART / ("selftest" if mode == "selftest" else "results")
    if mode == "score" and out.exists():
        raise SystemExit("results/ already exists: each arm is scored once")
    train, test, preds, sizes, g = run_all(mode)
    P("== GATES ==")
    P(json.dumps(g, indent=1, default=str))
    if mode == "gates":
        (ART / "gates.json").write_text(json.dumps(g, indent=1, default=str) + "\n")
        (ART / "log_gates.txt").write_text("\n".join(LOG) + "\n")
        P("gates all pass:", g["all_pass"])
        return
    if not g["all_pass"]:
        (ART / "log_gates_failed.txt").write_text("\n".join(LOG) + "\n")
        raise SystemExit("A gate failed: stop and report")
    out.mkdir(parents=True)
    if mode == "selftest":
        rng = random.Random(1)
        keys_by = {arm: {r["id"]: {"label": rng.getrandbits(1), "letter": rng.choice("LT"), "condition": rng.choice(CONDS),
                                   "q": rng.randrange(4), "design": 0} for r in test[arm]} for arm in ARMS}
    else:
        keys_by = {arm: {k["id"]: k for k in load(f"scorer_key_{arm}.jsonl")} for arm in ARMS}
    items_by, names_by = {}, {}
    for (arm, regime), pr in preds.items():
        rows, names = build_items(arm, regime, pr, keys_by[arm], test)
        items_by[(arm, regime)] = rows
        names_by[(arm, regime)] = names
        (out / f"items_{arm}_{regime}.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    md, V, counts_rows = tables_and_verdicts(preds, items_by, names_by, sizes, g)
    (out / "tables.md").write_text(md + "\n")
    (out / "verdicts.json").write_text(json.dumps(V, indent=1, default=str) + "\n")
    with open(out / "counts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "labels", "learner", "condition", "letter", "turn", "items", "right", "wrong", "unanswered", "coverage"])
        w.writerows(counts_rows)
    (out / "gates.json").write_text(json.dumps(g, indent=1, default=str) + "\n")
    P(md)
    (out / "log.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
