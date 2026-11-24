"""Tables for the draft result note, from the outputs under artifacts/.../ (no recomputation of growth).

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
Writes artifacts/.../summary.json and artifacts/.../tables.md.
"""
import glob
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rlaw  # noqa: E402

OUT = rlaw.OUT
LAWS = rlaw.LAWS
CAP_C = 5000
CONVS = ("O", "N")
md = []


def p(line=""):
    md.append(line)


def jl(path):
    return rlaw.load(path)


def gate():
    s = {}
    for f in sorted(glob.glob(str(OUT / "gate_*.json"))):
        s[Path(f).stem] = json.loads(Path(f).read_text())
    f_counts = Counter()
    f_unver = []
    for k, v in s.items():
        if k.startswith("gate_f_"):
            f_counts.update(v["counts"])
            f_unver.extend((k, u) for u in v["unverified"])
    check = Counter()
    for law in LAWS:
        for c in CONVS:
            for f in glob.glob(str(OUT / f"c_{law}_{c}_arm*.jsonl")):
                for r in jl(f):
                    check.update({f"{k}": v for k, v in r["check_log"].items()})
    b = [json.loads(Path(f).read_text()) for f in glob.glob(str(OUT / "b_*.json"))]
    by = {(r["source"], r["law"], r["rule"], r["conv"]): r for r in b}
    b_same = b_n = b_pay = 0
    for (src, law, rule, conv), r in by.items():
        if rule != "R":
            continue
        ref = by[(src, law, "ref", None)]
        b_n += 1
        b_same += (r["stars_sha256"] == ref["stars_sha256"] and r["n_at"] == ref["n_at"] and r["outcome"] == ref["outcome"]
                   and r["first_failing_step"] == ref["first_failing_step"])
        b_pay += sum(r["payments"]) + sum(r["short_knots"]) + sum(x or 0 for x in r["elim_vs_shortcut"])
    res = {"files": s, "gate_f": dict(f_counts), "gate_f_unverified": f_unver, "c_check_logs": dict(check),
           "b": {"R_histories": b_n, "identical": b_same, "payments_short_or_elim_disagreements": b_pay}}
    p("## Row G")
    p("| Check | Result |")
    p("| --- | --- |")
    for law in LAWS:
        a = s.get(f"gate_a_{law}", {}).get("counts", {})
        p(f"| R and the ordinary mode against the recorded driver, 280 funded draws, {law} | ordinary mode {a.get('ordinary_mode_equal')}/{a.get('funded')}, "
          f"R-O {a.get('R_O_equal')}/{a.get('funded')}, R-N {a.get('R_N_equal')}/{a.get('funded')} identical; payments {a.get('R_O_payments')}+{a.get('R_N_payments')}, "
          f"short knots {a.get('R_O_short_knots')}+{a.get('R_N_short_knots')}; rounds also matched against the recorded operator {a.get('R_O_check_rounds_compared')} (R-O) |")
    p(f"| R against the recorded driver on the seven recorded sources (test (b)) | {b_same}/{b_n} R histories identical (digest of full holdings, knots per stage, outcome, first failing step); payments, short knots and elimination disagreements: {b_pay} |")
    gb = s.get("gate_b", {}).get("counts", {})
    p(f"| Elimination against the shortcut, every parity birth of the 1,024 ordinary histories | {gb.get('births')} births, {gb.get('disagreements')} disagreements; closings met {gb.get('closings')} |")
    gc = s.get("gate_c", {}).get("counts", {})
    p(f"| Elimination against enumeration, stages of at most 20 distinctions in rounds 1-2 of R (O, parity) on all 1,024 draws | {gc.get('births_tested')} births on {gc.get('stages_tested')} stages, {gc.get('agree')} agree, {gc.get('implied_by_elimination')} implied |")
    gd = s.get("gate_d", {})
    p("| The two closings of test (d) at 00, ordinary growth | " + "; ".join(
        f"{k}: shortcut {v['shortcut_implied']}, elimination {v['elimination_implied']}, enumeration {v['enumeration_implied']}"
        for k, v in gd.items() if k != "seconds") + " |")
    p(f"| Rounds of test (c) also run by the recorded code (R, both laws, both conventions) | groups {check.get('groups_compared')}, lookaheads {check.get('lookaheads_compared')}, whole rounds with no short knot {check.get('rounds_compared')} (fresh counts equal {check.get('fresh_equal')}, differ by the replaced closing test {check.get('fresh_differ_by_closing_test', 0)}); every one equal |")
    p(f"| C search against Python search on ends and lookaheads beyond the recorded code's reach (gate f) | {f_counts.get('searches_equal')}/{f_counts.get('searches_compared')} equal |")
    p(f"| Next-round cap shortcut against full computation (gate f) | {f_counts.get('shortcut_agrees')}/{f_counts.get('shortcut_verified')} agree; {len(f_unver)} of {f_counts.get('shortcut_histories')} shortcut histories not verified (size) |")
    p()
    return res


def test_b():
    b = [json.loads(Path(f).read_text()) for f in glob.glob(str(OUT / "b_*.json"))]
    p("## Test (b): the seven recorded sources")
    p("| Source | Law | Rule | Outcome | Knots per stage (last) | Rounds | First failing step | Kind | Most holders | Payments |")
    p("| --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: |")
    rows = sorted(b, key=lambda r: (r["source"], r["law"], r["rule"], r["conv"] or ""))
    for r in rows:
        rule = "ordinary (recorded driver)" if r["rule"] == "ref" else f"R-{r['conv']}"
        p(f"| {r['source']} | {r['law']} | {rule} | {r['outcome']} | {r['n_at'][-1]} | {len(r['births'])} | {r['first_failing_step']} | {r['growth_kind']} | {r['max_holders']} | {sum(r.get('payments', [0]))} |")
    p()


def load_c():
    rows = defaultdict(list)
    for law in LAWS:
        for c in CONVS:
            for f in sorted(glob.glob(str(OUT / f"c_{law}_{c}_arm*.jsonl"))):
                rows[(law, c)].extend(jl(f))
    return rows


def stalled(r):
    return r["ord_outcome"] == "stall" or r["ord_rounds"] == 0


def test_c(rows):
    res = {}
    p("## Test (c): the 1,024 draws per law under R")
    p("Population: the 744 draws per law that make no birth at round 1 under ordinary growth (731 stall, 13 have no live knot). "
      "The other 280 per law are funded; under R they are identical to ordinary growth (row G).")
    p()
    p("| Law | Convention | Residual stall at round 1 | No live knot | Residual stall later | Closed | Alive at 12 rounds | Cap (5,000 knots) | Kind (recorded fn): stalled / bounded / growing | Kind by births: stalled / bounded / growing |")
    p("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for (law, c), rs in sorted(rows.items()):
        st = [r for r in rs if stalled(r)]
        nolive = [r for r in st if r["ord_rounds"] == 0 and r["ord_outcome"] == "closed"]
        out = Counter()
        for r in st:
            if r["outcome"] == "residual_stall":
                out["rs1" if r["rounds"] == 0 else "rs_later"] += 1
            elif r["outcome"] == "closed" and r["rounds"] == 0:
                out["nolive"] += 1
            else:
                out[r["outcome"]] += 1
        k1 = Counter(r["growth_kind"] for r in st)
        k2 = Counter(r["growth_kind_births"] for r in st)
        res[(law, c)] = {"n": len(st), "outcomes": dict(out), "kind": dict(k1), "kind_births": dict(k2), "nolive": len(nolive)}
        p(f"| {law} | {c} | {out['rs1']} | {out['nolive']} | {out['rs_later']} | {out['closed']} | {out['horizon']} | {out['cap']} | "
          f"{k1['stalled']} / {k1['bounded']} / {k1['growing']} | {k2['stalled']} / {k2['bounded']} / {k2['growing']} |")
    p()
    p("Largest number of holders of a distinction within the horizon (744 draws per law):")
    p()
    p("| Law | Convention | 2 | 3 | 4 | 5 | 6+ | Largest | Draws with 4 or more |")
    p("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for (law, c), rs in sorted(rows.items()):
        st = [r for r in rs if stalled(r)]
        h = Counter(r["max_holders"] for r in st)
        six = sum(v for k, v in h.items() if k >= 6)
        p(f"| {law} | {c} | {h[2]} | {h[3]} | {h[4]} | {h[5]} | {six} | {max(h)} | {sum(v for k, v in h.items() if k >= 4)} |")
        res[(law, c)]["holders"] = dict(sorted(h.items()))
    p()
    p("First failing step of the operator test (stage index; none = passes at every stage reached):")
    p()
    p("| Law | Convention | none | 0 | 1 | 2 | 3 | 4+ | Under ordinary growth (same draws): none / fails |")
    p("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for (law, c), rs in sorted(rows.items()):
        st = [r for r in rs if stalled(r)]
        f = Counter(r["first_failing_step"] for r in st)
        ordf = Counter(r["ord_first_failing_step"] is None for r in st)
        four = sum(v for k, v in f.items() if k is not None and k >= 4)
        p(f"| {law} | {c} | {f[None]} | {f[0]} | {f[1]} | {f[2]} | {f[3]} | {four} | {ordf[True]} / {ordf[False]} |")
        res[(law, c)]["first_failing"] = {str(k): v for k, v in f.items()}
    p()
    # payments
    p("Rounds and births with a payment by a shared distinction (744 draws per law):")
    p()
    p("| Law | Convention | Rounds | Rounds with a payment | Births | Births with a shared distinction | Payments | Short knots | Implied births (no fresh) | Births with fresh counts as lower bounds |")
    p("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for (law, c), rs in sorted(rows.items()):
        st = [r for r in rs if stalled(r)]
        rounds = sum(r["rounds"] for r in st)
        prounds = sum(1 for r in st for x in r["paid_births"] if x)
        births = sum(sum(r["births"]) for r in st)
        pb = sum(sum(r["paid_births"]) for r in st)
        pay = sum(sum(r["payments"]) for r in st)
        sk = sum(sum(r["short_knots"]) for r in st)
        imp = sum(sum(r["implied"]) for r in st)
        lb = sum(b for r in st for b, f in zip(r["births"], r["fresh_lower_bound"]) if f)
        p(f"| {law} | {c} | {rounds} | {prounds} | {births} | {pb} | {pay} | {sk} | {imp} | {lb} |")
        res[(law, c)]["payments"] = {"rounds": rounds, "paid_rounds": prounds, "births": births, "paid_births": pb,
                                     "payments": pay, "short_knots": sk, "implied": imp, "lower_bound_births": lb}
        # rounds after the first with a payment
        later = sum(1 for r in st for t, x in enumerate(r["paid_births"]) if x and t > 0)
        res[(law, c)]["paid_rounds_after_round_1"] = later
    p()
    p("Rounds with a payment after round 1: " + ", ".join(f"{law}-{c} {res[(law, c)]['paid_rounds_after_round_1']}" for law, c in sorted(rows)))
    p()
    # conventions
    p("Do the two conventions give the same numbers of births per round?")
    p()
    p("| Law | Draws (of 744) with the same births per round | Different | Different and both alive through round 2 | Same outcome |")
    p("| --- | ---: | ---: | ---: | ---: |")
    conv_res = {}
    for law in LAWS:
        A = {(r["arm"], r["draw"]): r for r in rows[(law, "O")]}
        B = {(r["arm"], r["draw"]): r for r in rows[(law, "N")]}
        same = diff = diff2 = same_out = 0
        examples = []
        funded_diff = 0
        for k, a in A.items():
            b = B[k]
            if not stalled(a):
                funded_diff += a["births"] != b["births"]
                continue
            if a["births"] == b["births"]:
                same += 1
            else:
                diff += 1
                if len(a["births"]) >= 2 and len(b["births"]) >= 2:
                    diff2 += 1
                if len(examples) < 3:
                    examples.append({"arm": k[0], "draw": k[1], "O": a["births"][:5], "N": b["births"][:5]})
            same_out += a["outcome"] == b["outcome"]
        conv_res[law] = {"same": same, "different": diff, "different_alive_2": diff2, "same_outcome": same_out,
                         "examples": examples, "funded_different": funded_diff}
        p(f"| {law} | {same} | {diff} | {diff2} | {same_out} |")
    p()
    for law in LAWS:
        p(f"Examples ({law}): " + "; ".join(f"arm {e['arm']} draw {e['draw']}: O {e['O']}, N {e['N']}" for e in conv_res[law]["examples"]))
    p()
    res["conventions"] = conv_res
    # funded draws consistency in test (c) runs
    cons = Counter()
    for (law, c), rs in rows.items():
        for r in rs:
            if not stalled(r):
                cons["funded"] += 1
                cons["same_as_ordinary"] += (r["n_at"] == r["ord_n_at"] and r["outcome"] == r["ord_outcome"]
                                             and r["first_failing_step"] == r["ord_first_failing_step"])
    res["funded_consistency"] = dict(cons)
    p(f"Funded draws in the test (c) runs: {cons['same_as_ordinary']} of {cons['funded']} histories (both laws, both conventions) equal ordinary growth in knots per stage, outcome and first failing step.")
    p()
    # residual stall details at round 1
    p("Residual stalls at round 1: knots left short, by number of unpaid births (744 draws per law):")
    for (law, c), rs in sorted(rows.items()):
        st = [r for r in rs if stalled(r) and r["outcome"] == "residual_stall" and r["rounds"] == 0]
        unpaid = Counter(sum(n for _, n in r["residual"]) for r in st)
        p(f"- {law}-{c}: {len(st)} draws; unpaid births per draw {dict(sorted(unpaid.items()))}")
    p()
    return res


def test_c_enum():
    res = {}
    p("## Test (c): every allowed choice, rounds 1 and 2")
    p("| Law | Draws | No live knot | No short knot at round 1 | Short | Every choice stalls at round 1 | Some choice pays | Choices at round 1 (sum; largest) | Of those: the convention O stalls but a choice pays / N |")
    p("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for law in LAWS:
        rows = []
        for f in sorted(glob.glob(str(OUT / "enum" / f"c_enum_{law}_arm*.jsonl"))):
            rows.extend(jl(f))
        kinds = Counter(r.get("r1_kind") for r in rows)
        short = [r for r in rows if r.get("r1_kind") == "short"]
        zero = [r for r in short if r["r1_choices"] == 0]
        pos = [r for r in short if r["r1_choices"] > 0]
        tot = sum(r["r1_choices"] for r in short)
        big = max((r["r1_choices"] for r in short), default=0)
        o_st = sum(1 for r in pos if r["conv_O"]["outcome"] == "residual_stall" and not r["conv_O"]["births"])
        n_st = sum(1 for r in pos if r["conv_N"]["outcome"] == "residual_stall" and not r["conv_N"]["births"])
        p(f"| {law} | {len(rows)} | {kinds['no live knot']} | {kinds['no short knot']} | {len(short)} | {len(zero)} | {len(pos)} | {tot}; {big} | {o_st} / {n_st} |")
        # round 2 variation
        vary = sum(1 for r in pos if len(r["r2_births"]) > 1)
        r2rs = sum(1 for r in pos if r["r2_status"].get("residual stall under every choice", 0))
        r2_short = sum(1 for r in pos if r["r2_choice_counts"])
        mh = Counter()
        for r in rows:
            for k, v in r.get("max_holders_after_two", {}).items():
                mh[int(k)] += v
        conv_in = 0
        conv_tot = 0
        for r in pos:
            for conv in ("conv_O", "conv_N"):
                cv = r[conv]
                if len(cv["births"]) == 2:
                    conv_tot += 1
                    conv_in += str(cv["births"][1]) in r["r2_births"]
        res[law] = {"draws": len(rows), "kinds": dict(kinds), "every_choice_stalls": len(zero), "some_choice_pays": len(pos),
                    "choices_r1": tot, "largest_r1": big, "conv_O_stalls_though_a_choice_pays": o_st,
                    "conv_N_stalls_though_a_choice_pays": n_st, "r2_births_vary_with_choice": vary,
                    "r2_short_after_some_choice": r2_short, "r2_every_choice_stalls_after_some_choice": r2rs,
                    "holders_after_two_over_all_choices": dict(sorted(mh.items())),
                    "convention_round2_births_within_enumerated": [conv_in, conv_tot]}
    # why every choice stalls: per draw, does some short knot owe more than it holds in all (loose + shared)?
    why = Counter()
    for dr in rlaw.lib.p3_draws():
        g = rlaw.Growth(dr["stars"], "parity", "R", "O")
        r = g.plan(max_births=CAP_C - len(g.stars))
        if r.status == "closed" or not r.shortages:
            continue
        per = g.allowed_choices(r)
        if any(not o for _, o in per):
            over = any(ex > sum(1 for d in g.stars[k] if len(g.holders[d]) >= 2) for k, ex in r.shortages)
            why["owes more than it holds in all" if over else "holds enough, but too few allowed (held by another parent)"] += 1
    p(f"Draws where every choice stalls at round 1 (the same under both laws), by cause: {dict(why)}.")
    res["every_choice_stalls_cause"] = dict(why)
    for law in LAWS:
        r = res[law]
        p()
        p(f"{law}: on the {r['some_choice_pays']} draws where some choice pays, round-2 births depend on the choice in {r['r2_births_vary_with_choice']}; "
          f"some round-1 choice leaves a short knot at round 2 in {r['r2_short_after_some_choice']} (every round-2 choice stalls after some round-1 choice in {r['r2_every_choice_stalls_after_some_choice']}); "
          f"largest number of holders after two rounds over all choices (histories): {r['holders_after_two_over_all_choices']}; "
          f"the conventions' round-2 births are among the enumerated ones in {r['convention_round2_births_within_enumerated'][0]} of {r['convention_round2_births_within_enumerated'][1]}.")
    p()
    return res


def test_a():
    a = {}
    for part in ("c", "d", "e", "enum"):
        f = OUT / f"a_{part}.json"
        if f.exists():
            a[part] = json.loads(f.read_text())[part]
    p("## Test (a): extension by enumeration (stages of at most 22 distinctions)")
    p("| Source | Histories | Rounds | Births | Births with a shared distinction | Births with no fresh distinction | Allowed words checked | Words that fail to extend | Projection cross-checks (equal) |")
    p("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    tot = Counter()
    for part, label in (("c", "test (c), conventions"), ("d", "test (d), R"), ("e", "test (e), R"), ("enum", "test (c), every choice")):
        c = a.get(part, {}).get("counts", {})
        tot.update({k: v for k, v in c.items() if isinstance(v, int)})
        hist = c.get("histories", "(per choice)")
        p(f"| {label} | {hist} | {c.get('rounds', 0)} | {c.get('births', 0)} | {c.get('births_with_shared', 0)} | {c.get('zero_fresh_births', 0)} | {c.get('words_checked', 0)} | {c.get('words_failing', 0)} | {c.get('projection_checks', '-')} ({c.get('projection_equal', '-')}) |")
    p(f"| all | | {tot['rounds']} | {tot['births']} | {tot['births_with_shared']} | {tot['zero_fresh_births']} | {tot['words_checked']} | {tot['words_failing']} | {tot['projection_checks']} ({tot['projection_equal']}) |")
    p()
    return {"parts": a, "total": dict(tot)}


def test_d():
    f = OUT / "d_tables.json"
    d = json.loads(f.read_text())
    p("## Test (d): the stalling set-ups")
    p("| Set-up | Law | Rule | Outcome pairs 00, 01, 10, 11 | Alice own / far | Bob own / far | Signed | Largest | Prepared words |")
    p("| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |")
    res = {}
    for name in ("S_cycle_five", "C_binary", "C_ternary"):
        for law in LAWS:
            e = d[name]["laws"][law]
            for key in ("ordinary", "R_O", "R_N"):
                t = e["rules"][key]["table"]
                yn = lambda x: "yes" if x else "no"
                p(f"| {name} | {law} | {key} | {', '.join(t['outcome_pairs'])} | {yn(t['own_edit_dependence']['alice'])} / {yn(t['far_edit_dependence']['alice'])} | "
                  f"{yn(t['own_edit_dependence']['bob'])} / {yn(t['far_edit_dependence']['bob'])} | {t['signed'] if t['signed'] is not None else '-'} | {t['largest'] if t['largest'] is not None else '-'} | {e['prepared_words']} |")
                res[(name, law, key)] = t
            ch = e["rules"]["R_every_choice"]
            p(f"| {name} | {law} | R, every choice | " + ", ".join(f"{s}: {c['choices']} choices -> {list(c['outcomes'])}" for s, c in ch.items()) + " | | | | | |")
    p()
    return {str(k): v for k, v in res.items()}


def test_e():
    res = {}
    p("## Test (e): pace")
    p("Largest distance of a changed birth by round t (over the 200 pairs), and the pairs judged:")
    p()
    p("| Law | Rule | t=1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | Pairs with a residual stall | Pairs with a stall | Pairs above 3t+3 (no residual stall) | Pairs with a changed birth at t=1 beyond 6 |")
    p("| --- | --- | " + " | ".join(["---:"] * 12) + " | ---: | ---: | ---: | ---: |")
    ecc = None
    for law in LAWS:
        for tag in ("ordinary", "RO", "RN"):
            rows = jl(OUT / f"e_{law}_{tag}.jsonl")
            if ecc is None:
                ecc = Counter(max(r["start_distances"]) for r in rows)
            md_ = {}
            viol = beyond = 0
            notc = 0
            for r in rows:
                for x in r["rounds"]:
                    if "status" in x:
                        notc += 1
                        continue
                    if x["max_distance"] is None:
                        continue
                    md_[x["t"]] = max(md_.get(x["t"], -1), x["max_distance"])
                    if not r["residual_stall"] and x["max_distance"] > 3 * x["t"] + 3:
                        viol += 1
                    if x["t"] == 1 and x["max_distance"] > 6:
                        beyond += 1
            rs = sum(r["residual_stall"] for r in rows)
            stl = sum(r["stall"] for r in rows)
            stall_r1 = [x["max_distance"] for r in rows if r["stall"] for x in r["rounds"] if x["t"] == 1]
            stall_ecc = sum(1 for r in rows if r["stall"] for x in r["rounds"]
                            if x["t"] == 1 and x["max_distance"] == max(r["start_distances"]))
            res[(law, tag)] = {"max_distance_by_round": md_, "residual_pairs": rs, "stall_pairs": stl,
                               "bound_violations": viol, "beyond6_at_round1": beyond, "rounds_not_compared": notc,
                               "stall_round1_max_distances": dict(Counter(stall_r1)),
                               "stall_pairs_reaching_largest_start_distance": stall_ecc,
                               "paid_rounds": sum(1 for r in rows for h in ("unedited", "edited") for x in r[h]["paid_births"] if x),
                               "paid_births": sum(sum(r[h]["paid_births"]) for r in rows for h in ("unedited", "edited")),
                               "births": sum(sum(r[h]["births"]) for r in rows for h in ("unedited", "edited")),
                               "rounds": sum(len(r[h]["births"]) for r in rows for h in ("unedited", "edited"))}
            p(f"| {law} | {tag} | " + " | ".join(str(md_.get(t, "-")) for t in range(1, 13)) + f" | {rs} | {stl} | {viol} | {beyond} |")
    p()
    p(f"Largest start distance from the edited knot over the 200 draws: {dict(sorted(ecc.items()))}.")
    for law in LAWS:
        r = res[(law, "ordinary")]
        p(f"Ordinary growth, {law}: {r['stall_pairs']} pairs stall (the edited start, at round 1); in them the largest distance of a changed birth at round 1 is {r['stall_round1_max_distances']}, equal to the start's largest distance from the edited knot in {r['stall_pairs_reaching_largest_start_distance']}.")
    for law in LAWS:
        for tag in ("RO", "RN"):
            r = res[(law, tag)]
            p(f"R-{tag[1]}, {law}: rounds {r['rounds']}, rounds with a payment {r['paid_rounds']}; births {r['births']}, with a shared distinction {r['paid_births']}.")
    p()
    return {str(k): v for k, v in res.items()}


def main():
    summary = {"gate": gate()}
    test_b()
    rows = load_c()
    summary["c"] = {str(k): v for k, v in test_c(rows).items()}
    summary["c_enum"] = test_c_enum()
    summary["d"] = test_d()
    summary["e"] = test_e()
    summary["a"] = test_a()
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    (OUT / "tables.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
