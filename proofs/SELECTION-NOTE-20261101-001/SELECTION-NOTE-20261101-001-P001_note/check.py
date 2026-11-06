"""Checks for SELECTION-NOTE-20261101-001-P001 (the note 'Native selection on regular systems').

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the replay: replay_result.json reports every cited check rerun in a temporary copy, exit 0, passed, equal to its frozen result
  2 the independent recomputation: independent_result.json reports all nine parts in agreement
  3 the note's numbers: every quoted number appears in the note and equals the frozen result that proves it (and the independent
    recomputation where that covers it); every cited ticket (or its epic) is named in the note
  4 the note compiles (two pdflatex passes, no undefined references); the PDF is written next to the source (git-ignored)
  5 controls: a tampered number, a failing replay row and a failing independent part are all caught
Run: .venv/bin/python -B check.py [--write]   (needs pdflatex; replay.py --write and independent.py --write first)"""
import glob
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TEX = HERE / "note" / "selection_note.tex"
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:1500], flush=True)


def frozen(ticket):
    return json.loads(Path(glob.glob(str(ROOT / "proofs" / ticket / f"{ticket}-P001_*" / "result.json"))[0]).read_text())


def section(ticket, prefix):
    ch = frozen(ticket)["checks"]
    hits = [k for k in ch if k.startswith(prefix + " ")]
    assert len(hits) == 1, (ticket, prefix, hits)
    return ch[hits[0]].get("info", ch[hits[0]].get("detail"))


def passed(ticket, prefix):
    ch = frozen(ticket)["checks"]
    return ch[[k for k in ch if k.startswith(prefix + " ")][0]]["pass"]


# ---------------------------------------------------------------- 0
man = json.loads((HERE / "manifest.json").read_text())
mism = {r: d for r, d in man["parent_bindings"].items() if hashlib.sha256((ROOT / r).read_bytes()).hexdigest() != d}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the replay
CITED = ["KNOT-COUPLING-20261031-001A", "KNOT-COUPLING-20261031-001B", "KNOT-COUPLING-20261031-001C", "PINNING-20261031-001A",
         "PINNING-20261031-001B", "PINNING-20261031-001C", "PARITY-CORRECTION-20261031-001A", "PARITY-CORRECTION-20261031-001B",
         "FOUR-PLACE-20261031-001A", "FOUR-PLACE-20261031-001B", "FOUR-PLACE-20261031-001C", "FOUR-PLACE-20261031-001D",
         "FOUR-PREFER-20261101-001A", "FOUR-PREFER-20261101-001B", "FOUR-PREFER-20261101-001D", "KNOT-COMPOSE-20261101-001A"]


def replay_ok(rep):
    rows = {r["ticket"]: r for r in rep["rows"]}
    return rep["ok"] and set(rows) == set(CITED) and all(r["exit_code"] == 0 and r["matches_frozen_result"]
                                                         and r["fresh_status"] in ("passed", "Proved") for r in rows.values())


rep = json.loads((HERE / "replay_result.json").read_text())
report("1 the replay: every cited check rerun in a temporary copy equals its frozen result", replay_ok(rep),
       {"rows": [(r["ticket"], r["matches_frozen_result"], r["fresh_status"], r["seconds"]) for r in rep["rows"]],
        "copied directories": len(rep["copied_directories"]), "copied research files": len(rep["copied_research_files"])})

# ---------------------------------------------------------------- 2 the independent recomputation
ind = json.loads((HERE / "independent_result.json").read_text())
PARTS = [k for k in ind if k.startswith("I")]


def ind_ok(r):
    return r["ok"] and len([k for k in r if k.startswith("I")]) == 9 and all(r[p]["ok"] for p in r if p.startswith("I"))


report("2 the independent recomputation (fresh code) agrees in all nine parts", ind_ok(ind), {p: ind[p]["ok"] for p in PARTS})


# ---------------------------------------------------------------- 3 the note's numbers
def ties(text):
    pinA = section("PINNING-20261031-001A", "1")
    sizes = {k: v["relations in the class"] for k, v in pinA.items() if isinstance(v, dict) and "relations in the class" in v}
    kcA8 = section("KNOT-COUPLING-20261031-001A", "8")
    kcC = frozen("KNOT-COUPLING-20261031-001C")["claim"]
    pinB4 = section("PINNING-20261031-001B", "4")["explicit failing system"]
    pinC2 = section("PINNING-20261031-001C", "2")
    pcA4c = section("PARITY-CORRECTION-20261031-001A", "4c")
    pcA6 = section("PARITY-CORRECTION-20261031-001A", "6")
    pcB2 = section("PARITY-CORRECTION-20261031-001B", "2")
    fA1 = section("FOUR-PLACE-20261031-001A", "1")
    fC3 = section("FOUR-PLACE-20261031-001C", "3")["tallies"]
    prA1 = section("FOUR-PREFER-20261101-001A", "1")
    prB3 = section("FOUR-PREFER-20261101-001B", "3")
    prB5 = section("FOUR-PREFER-20261101-001B", "5")["tallies"]
    prD1 = section("FOUR-PREFER-20261101-001D", "1")
    rows = [
        ("For $k=3$ there are $34$ knots in $5$ classes", sum(sizes.values()) == 34 and len(sizes) == 5
         and ind["I1 three-place knots: 34 in 5 classes of sizes 2, 4, 8, 8, 12"]["knots"] == 34),
        ("for $k=4$ there are $742$ in $20$ classes", len(prA1["table"]) == 20 and sum(r["relations"] for r in prA1["table"]) == 742
         and ind["I2 four-place knots: 742 in 20 classes; 30 value-free in 4 classes"]["knots"] == 742),
        ("$\\lambda\\in\\{0,1,-1,-3,\\infty\\}$", "outside {0, 1, -1, -3}" in kcC and "lam = oo" in kcC),
        ("$(-2)^n\\,|\\det|$", kcA8["Fano"]["M(H; -3)"] == kcA8["Fano"]["(-2)^|P| #PM"] == -3072
         and kcA8["13-point splice"]["M(H; -3)"] == -1572864 and kcA8["13-point splice"]["|det|"] == "192"
         and ind["I3 knot's coupling on Fano: M(0) = 0 and M(-3) = (-2)^7 * #PM = -3072, #PM = 24"]["M_minus3"] == -3072),
        ("$1{,}380{,}864$ signings", pinC2["signings"] == pinC2["agree"] == 1380864),
        ("parity ($2$ relations), the no-lone (Fibonacci) law ($8$),", sizes.get("parity") == 2 and sizes.get("Fibonacci (no-lone)") == 8),
        ("not-all-equal ($4$), $x\\vee(y\\neq z)$ ($12$) and the clause ($8$)",
         sizes.get("not-all-equal") == 4 and sizes.get("x or (y != z)") == 12 and sizes.get("clause") == 8),
        ("an explicit system of $25$ lines", pinB4["lines"] == 25 and pinB4["solvable"] is False and pinB4["cubic"]),
        ("$M_{\\mathrm{par}}(\\theta\\,\\mathrm{Fano};2)=10912465152$", pcA4c["Fano sample M_par(theta Fano; lam)"]["2"] == "10912465152"
         and ind["I4 theta identity: M_par(theta Fano; 2) = 10912465152 = (2*2*3)^7 * M_nae(Fano; 3/2)"]["left"] == 10912465152),
        ("$\\lambda\\in\\{0,1,-1,i,-i,\\infty\\}$", pcA6["easy points"] == ["0", "1", "-1", "i", "-i", "oo"]),
        ("$\\det G=-16\\lambda^2(\\lambda-1)^6(\\lambda+1)^6$", pcB2["det"] == "-16*lam**2*(lam - 1)**6*(lam + 1)**6"
         and ind["I9 the eight-line parity piece has det G = -16 lam^2 (lam-1)^6 (lam+1)^6"]["ok"]),
        ("$30$ are value-free", sum(v["relations"] for v in fA1.values()) == 30 and len(fA1) == 4
         and ind["I2 four-place knots: 742 in 20 classes; 30 value-free in 4 classes"]["value_free"] == 30),
        ("checked end to end on $160$ and $240$ instances", sum(v["instances"] for v in fC3.values()) == 160
         and sum(v["satisfiable"] + v["unsatisfiable"] for v in prB5.values()) == 240),
        ("nine value-preferring classes through a core of three points on four lines",
         len(prB3) == 9 and all(v["accepted relation is the link"] and v["internal points"] == 23 for v in prB3.values())),
        ("lie in one of five weak classes", sum(1 for v in prD1.values() if v["mutually selecting"] == "open") == 5 and len(prD1) == 20),
        ("$k-1\\ge3$", passed("FOUR-PLACE-20261031-001B", "2") and passed("FOUR-PLACE-20261031-001B", "3")),
        ("Two sides that both accept knots fail together only", all(passed("KNOT-COMPOSE-20261101-001A", s) for s in ("3", "4", "5", "6"))
         and ind["I7 complementarity: for k = 2, 3, 4 the knots with 2^(k-1) states are exactly the parity cosets"]["ok"]),
    ]
    fails = [snip for snip, cond in rows if snip not in text or not cond]
    named = [t for t in CITED if t not in text and t[:-1] not in text]
    return fails, named, len(rows)


text = TEX.read_text()
fails, named, nrows = ties(text)
report("3 the note's numbers: every quoted number is in the note and equals its frozen evidence; every cited ticket (or its epic) is named",
       not fails and not named, {"quotations": nrows, "failures": fails, "unnamed tickets": named})


# ---------------------------------------------------------------- 4 compile
def compile_note():
    with tempfile.TemporaryDirectory(prefix="selection_note_tex_") as tmp:
        shutil.copy(TEX, Path(tmp) / TEX.name)
        logs = []
        for _ in range(2):
            run = subprocess.run(["pdflatex", "-interaction=nonstopmode", TEX.name], cwd=tmp, capture_output=True, text=True, timeout=600)
            logs.append(run.returncode)
        log = (Path(tmp) / TEX.with_suffix(".log").name).read_text(errors="ignore")
        pdf = Path(tmp) / TEX.with_suffix(".pdf").name
        ok = pdf.exists() and logs[-1] == 0 and "undefined" not in log.lower()
        if ok:
            shutil.copy(pdf, TEX.with_suffix(".pdf"))
        return ok, {"pdflatex exit codes": logs, "undefined references": "undefined" in log.lower()}


ok4, det4 = compile_note()
report("4 the note compiles (two pdflatex passes, no undefined references)", ok4, det4)

# ---------------------------------------------------------------- 5 controls
tampered = text.replace("10912465152", "10912465153", 1)
bad_rep = json.loads(json.dumps(rep))
bad_rep["rows"][0]["matches_frozen_result"] = False
bad_ind = json.loads(json.dumps(ind))
bad_ind[PARTS[0]]["ok"] = False
controls = {"a tampered number is caught": bool(ties(tampered)[0]),
            "a failing replay row is caught": not replay_ok(bad_rep),
            "a failing independent part is caught": not ind_ok(bad_ind)}
report("5 controls fire", all(controls.values()), controls)

result = {"schema_version": 3, "artifact_id": man["artifact_id"], "kind": "proof", "ticket": man["ticket"], "proof": man["proof"],
          "status": "passed" if ok_all else "failed", "claim": man["claim"], "checks": out}
if "--write" in sys.argv:
    (HERE / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n")
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(json.dumps(result, sort_keys=True, default=str)):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
print("ALL OK" if ok_all else "FAILURES")
sys.exit(0 if ok_all else 1)
