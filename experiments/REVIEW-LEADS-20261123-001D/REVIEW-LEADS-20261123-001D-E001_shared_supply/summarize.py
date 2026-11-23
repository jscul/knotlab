"""Read the artifacts and print the tables of the draft result note. No growth is run here.

    .venv/bin/python -B <this file>
"""
import json

import lib

ART = lib.ARTIFACTS
ORDER = ("S1", "S2", "T1", "T2", "T3")
RULES = ("guarded", "recompute unrestricted", "recompute joins_first")


PREFIX = "grow_strict_" if "--strict" in __import__("sys").argv else "grow_"


def load(name):
    return json.loads((ART / f"{PREFIX}{name}.json").read_text())[name]


def guarded_outcome(row):
    t = row["ticks"]
    if row["stall"]:
        return "stalled", {"X": "stalled", "Y": "stalled"}
    lost = {"X": any(v["status"] == "lost" for k, v in t.items() if k.startswith("X")),
            "Y": any(v["status"] == "lost" for k, v in t.items() if k.startswith("Y"))}
    return "run", {k: "lost" if v else "keeps" for k, v in lost.items()}


def classes(entry, s, rule):
    """branch counts by (X, Y) status for one rule."""
    cell = entry[f"s{s}"]
    if rule == "guarded":
        kind, st = guarded_outcome(cell["guarded"])
        return {f"X {st['X']}, Y {st['Y']}": 1}, 1
    pol = rule.split()[1]
    r = cell["recompute"][pol]
    return r["outcome_by_choice_sequences"], r["choice_sequences"]


def main():
    add = json.loads((lib.HERE / "construction_addendum.json").read_text())
    g1 = json.loads((ART / "gate1.json").read_text())
    g2 = json.loads((ART / "gate2.json").read_text())
    out = []
    P = out.append
    P("### Joint starts")
    P("")
    P("| start | class | X + Y | knots | donor | loose s=0 / s=1 | demand X + Y | first asks in the sources' own histories | first parent step of the joint plan that asks it |")
    P("| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |")
    for n in ORDER:
        e = add["starts"][n]
        v0, v1 = e["variants"]["s0"], e["variants"]["s1"]
        sx, sy = add["sources"][e["x"]], add["sources"][e["y"]]
        P(f"| {n} | {e['class'].split(' (')[0]} | {e['x']} + {e['y']} | {v0['knots']} | {v0['donor']} | {v0['donor_loose']} / {v1['donor_loose']} | "
          f"{sx['demand_on_donor']} + {sy['demand_on_donor']} | {sx['first_ask_recorded_step']} / {sy['first_ask_recorded_step']} | 1 / 1 |")
    P("")
    P("### Branches by outcome (counts of choice sequences; a source is `lost` if any registered tick has a loss certificate)")
    P("")
    P("| start | s | rule | choice sequences | X keeps, Y keeps | X lost, Y keeps | X keeps, Y lost | both lost | stalled |")
    P("| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for n in ORDER:
        e = load(n)
        for s in (0, 1):
            for rule in RULES:
                c, total = classes(e, s, rule)
                P(f"| {n} | {s} | {rule} | {total} | {c.get('X keeps, Y keeps', 0)} | {c.get('X lost, Y keeps', 0)} | "
                  f"{c.get('X keeps, Y lost', 0)} | {c.get('X lost, Y lost', 0)} | "
                  f"{c.get('X stalled, Y stalled', 0)} |")
    P("")
    P("### Predictions")
    P("")
    verdicts = {}
    # P1
    p1 = {}
    for rule in RULES:
        lost = 0
        total = 0
        for n in ORDER:
            c, t = classes(load(n), 0, rule)
            total += t
            lost += sum(v for k, v in c.items() if "lost" in k or "stalled" in k)
        p1[rule] = (lost, total)
    P("P1 (s = 0, no source loses a tick in any branch): " + "; ".join(
        f"{rule}: {l} of {t} branches with a loss or stall" for rule, (l, t) in p1.items()) + ".")
    P("")
    # P2
    P("P2 (s = 1, staggered starts T1, T2, T3: the earlier asker X keeps ticking in every branch):")
    P("")
    P("| start | rule | branches | X lost | X lost and Y keeps (the failing clause) | X keeps in every branch |")
    P("| --- | --- | ---: | ---: | ---: | --- |")
    for n in ("T1", "T2", "T3"):
        e = load(n)
        for rule in RULES:
            c, t = classes(e, 1, rule)
            xlost = sum(v for k, v in c.items() if k.startswith("X lost") or k.startswith("X stalled"))
            clause = sum(v for k, v in c.items() if k.startswith("X lost") and k.endswith("Y keeps"))
            P(f"| {n} | {rule} | {t} | {xlost} | {clause} | {'yes' if xlost == 0 else 'no'} |")
    P("")
    # P3
    P("P3 (s = 1, same-step starts S1, S2: both outcomes occur among the branches):")
    P("")
    P("| start | rule | branches | X lost, Y keeps | Y lost, X keeps | both keep | both outcomes occur | every branch ends the same source |")
    P("| --- | --- | ---: | ---: | ---: | ---: | --- | --- |")
    for n in ("S1", "S2"):
        e = load(n)
        for rule in RULES:
            c, t = classes(e, 1, rule)
            a, b = c.get("X lost, Y keeps", 0), c.get("X keeps, Y lost", 0)
            both = c.get("X keeps, Y keeps", 0)
            P(f"| {n} | {rule} | {t} | {a} | {b} | {both} | {'yes' if a and b else 'no'} | "
              f"{'yes' if (a == t or b == t) else 'no'} |")
    P("")
    P("### Guarded rule, shortfall 0: births at which each registered tick is made (cap 400)")
    P("")
    P("| start | X tick 6 | X tick 10 | Y tick 6 | Y tick 10 |")
    P("| --- | --- | --- | --- | --- |")
    for n in ORDER:
        t = load(n)["s0"]["guarded"]["ticks"]
        def cell(k):
            if k not in t:
                return "none registered"
            v = t[k]
            return f"birth {v['birth']} (step {v['step']})" if v["status"] == "made" else v["status"]
        P(f"| {n} | {cell('X tick 6')} | {cell('X tick 10')} | {cell('Y tick 6')} | {cell('Y tick 10')} |")
    P("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    print(main())
