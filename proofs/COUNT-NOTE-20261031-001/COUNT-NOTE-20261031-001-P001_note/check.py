"""Checks for COUNT-NOTE-20261031-001-P001 (the note 'Counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence graphs').

  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 the replay: replay_result.json reports every cited check rerun in a temporary copy, exit 0, Proved, equal to its frozen result
  2 the independent replay: independent_result.json reports all six parts of the separately written recomputation
  3 the note's numbers: every quoted number appears in the note and equals the frozen result that proves it (and the independent
    replay where that covers it); every cited ticket is named in the note
  4 the note compiles (two pdflatex passes, no undefined references); the PDF is written next to the source (git-ignored)
  5 controls: a tampered number, a missing quotation, a failing replay row and a failing independent part are all caught; the replay's
    two hash-order tolerances accept their own frozen details and reject a different polynomial and a failure
Run: .venv/bin/python -B check.py [--write]   (needs pdflatex; replay.py --write and independent.py --write first)"""
import glob
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TEX = HERE / "note" / "counting_note.tex"
T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


def frozen(ticket):
    return json.loads(Path(glob.glob(str(ROOT / "proofs" / ticket / f"{ticket}-P001_*" / "result.json"))[0]).read_text())["checks"]


def section(ticket, prefix):
    ch = frozen(ticket)
    hits = [k for k in ch if k.startswith(prefix + " ")]
    assert len(hits) == 1, (ticket, prefix, hits)
    return ch[hits[0]]["detail"]


# ---------------------------------------------------------------- 0
man = json.loads((HERE / "manifest.json").read_text())
mism = {r: d for r, d in man["parent_bindings"].items() if hashlib.sha256((ROOT / r).read_bytes()).hexdigest() != d}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 the replay
CITED = ["SEYMOUR-COUNT-20261030-001A", "SEYMOUR-COUNT-20261030-001B", "TWIST-COUNT-20261030-001A", "TWIST-COUNT-20261030-001B",
         "SOFT-CROSS-20261031-001A", "SOFT-CROSS-20261031-001B", "SOFT-CROSS-20261031-001C", "PLAIN-COUNT-20261031-001A",
         "PLAIN-COUNT-20261031-001B", "PLAIN-BRACE-20261031-001A", "PLAIN-BRACE-20261031-001B"]


def replay_ok(rep):
    rows = {r["ticket"]: r for r in rep["rows"]}
    return rep["ok"] and set(rows) == set(CITED) and all(r["exit_code"] == 0 and r["matches_frozen_result"] and r["fresh_status"] == "Proved"
                                                         for r in rows.values())


rep = json.loads((HERE / "replay_result.json").read_text())
report("1 the replay: every cited check rerun in a temporary copy equals its frozen result", replay_ok(rep),
       {"rows": [(r["ticket"], r["matches_frozen_result"], r["fresh_status"]) for r in rep["rows"]], "copied directories": len(rep["copied_directories"])})

# ---------------------------------------------------------------- 2 the independent replay
ind = json.loads((HERE / "independent_result.json").read_text())
PARTS = ["I1 soft crossing", "I2 cube junction", "I3 K3,3 through plain braces", "I4 signs are path lengths",
         "I5 Theorem A on Fano compositions", "I6 similitude"]


def ind_ok(r):
    return r["ok"] and all(r[p]["ok"] for p in PARTS)


report("2 the independent replay (fresh code) agrees", ind_ok(ind), {p: ind[p]["ok"] for p in PARTS})

# ---------------------------------------------------------------- 3 the note's numbers


def ties(text):
    """(snippet in the note, value from the evidence) -> list of failures"""
    twB2 = section("TWIST-COUNT-20261030-001B", "2")["cube and 6-prism pages, all pairs and signs"]
    twB3 = section("TWIST-COUNT-20261030-001B", "3")
    twA3 = section("TWIST-COUNT-20261030-001A", "3")["symbolic (pattern, leg signs) -> multiplier"]
    seB4 = section("SEYMOUR-COUNT-20261030-001B", "4")
    seB5 = section("SEYMOUR-COUNT-20261030-001B", "5")
    seB6 = section("SEYMOUR-COUNT-20261030-001B", "6")
    scA3 = section("SOFT-CROSS-20261031-001A", "3")["Hadamard straight entries"]
    scA4 = section("SOFT-CROSS-20261031-001A", "4")["valuations (2, 3, 5, 139)"]
    scA6 = section("SOFT-CROSS-20261031-001A", "6")["recovered"]
    scB3 = section("SOFT-CROSS-20261031-001B", "3")
    scC2 = section("SOFT-CROSS-20261031-001C", "2")
    pcA3 = section("PLAIN-COUNT-20261031-001A", "3")
    pcB1 = section("PLAIN-COUNT-20261031-001B", "1")
    pcB2 = section("PLAIN-COUNT-20261031-001B", "2")
    pbA1 = section("PLAIN-BRACE-20261031-001A", "1")
    pbA2 = section("PLAIN-BRACE-20261031-001A", "2")
    pbA4 = section("PLAIN-BRACE-20261031-001A", "4")
    pbB3 = section("PLAIN-BRACE-20261031-001B", "3")
    sig = twB3["first soft crossing"]["straight entries (0000, 0101, 1010, 1111), exact"]
    lam = [a // b for a, b in zip(scA3["2"], scA3["1"])]
    woven = [v["vertices"] for k, v in pbB3.items() if isinstance(v, dict) and "vertices" in v]
    pts = [v["points"] for v in seB5.values()]
    rows = [
        ("(40000,-1112,3336,-192)", sig == [40000, -1112, 3336, -192] == ind["I1 soft crossing"]["straight entries"]),
        ("(810000,\\ 7506,\\ -22518,\\ -432)", lam == [810000, 7506, -22518, -432] == ind["I1 soft crossing"]["snake multipliers"]),
        ("v_5=(4,0,0,0)", scA4["5"] == [4, 0, 0, 0]),
        ("v_{139}=(0,1,1,0)", scA4["139"] == [0, 1, 1, 0]),
        ("v_3=(4,3,4,3)", scA4["3"] == [4, 3, 4, 3]),
        ("include 256 that are", twB3["truncated octahedron"]["crossover-type, nonzero double entry, off the matchgate class"] == 256),
        ("13120 junctions", twB2["junctions"] == 13120 and twB2["crossovers"] == 0),
        ("all 32 pattern and sign choices", len(twA3) == 32 and set(twA3.values()) == {"alpha**2 + alpha*beta + beta**2"}),
        ("on 67 braces", seB4["braces"] == 67),
        ("amplitudes $125$", seB5["tripod core (22)"]["pipeline"] == 125 == seB5["tripod core (22)"]["direct"][0]),
        ("$3906250000$", seB5["truncated octahedron glue"]["pipeline"] == 3906250000 and seB5["truncated octahedron glue"]["points"] == 90),
        ("22 to 118 points", (min(pts), max(pts)) == (22, 118)),
        ("up to 480 vertices", seB6["against direct counts"]["depth-3 chain of omnitruncations"]["vertices"] == 480),
        ("(1720", seB6["beyond elimination"]["Omni(9x9 grid) x 3"]["vertices"] == 1720),
        ("width 30", seB6["beyond elimination"]["Omni(9x9 grid) x 3"]["elimination width"] == 30),
        ("$54,18,18=9\\cdot(6,2,2)$", [scA6[k]["recovered"] for k in ("unsigned", "two negations", "five negations")] == ["54", "18", "18"]
         and [scA6[k]["#col(K3,3)"] for k in ("unsigned", "two negations", "five negations")] == [6, 2, 2]),
        ("up to 2710 vertices", max(v["largest graph (vertices)"] for v in scB3.values()) == 2710),
        ("44 certified Pfaffian instances", sum(v["certified"] for v in scC2.values()) == 44 == sum(v["instances"] for v in scC2.values())),
        ("100 counts", sum(pcA3[k]["plain counts"] for k in ("1", "3", "5", "7")) == 100),
        ("18504 vertices", max(pcA3[k]["largest plain instance (vertices)"] for k in ("1", "3", "5", "7")) == 18504),
        ("454 plain pages", pcB2["pages"] == 454 == pcB2["twisted (cut test)"]),
        ("33 planar graphs", pcB1["graphs"] == 33),
        ("2&3&2&5\\\\8&4&8&9\\\\9&8&4&8\\\\5&2&3&2", pbA1["S' (colour basis)"] == [["2", "3", "2", "5"], ["8", "4", "8", "9"],
                                                                                    ["9", "8", "4", "8"], ["5", "2", "3", "2"]]
         and ind["I2 cube junction"]["ok"]),
        ("(x^2-19x-1)(x^2+7x+13)", pbA1["characteristic polynomial"] == "(x**2 - 19*x - 1)*(x**2 + 7*x + 13)"),
        ("\\tfrac{53451621}{2804438}", pbA4["rational coefficients f_0..f_3"][0] == "-53451621/2804438"),
        ("\\tfrac{521319}{200317}", pbA4["rational coefficients f_0..f_3"][1] == "521319/200317"),
        ("\\tfrac{23524}{200317}", pbA4["rational coefficients f_0..f_3"][2] == "-23524/200317"),
        ("\\tfrac{853}{2804438}", pbA4["rational coefficients f_0..f_3"][3] == "853/2804438"),
        ("80, 31500, 11459396 and 4159886188", [pbA2[k]["direct count"] for k in ("1", "3", "5", "7")] == [80, 31500, 11459396, 4159886188]
         == [ind["I3 K3,3 through plain braces"]["counts"][k] for k in ("1", "3", "5", "7")]),
        ("20, 48, 76 and 104", [pbA2[k]["vertices"] for k in ("1", "3", "5", "7")] == [20, 48, 76, 104]),
        ("214 to 1078", (min(woven), max(woven)) == (214, 1078)),
        ("a(K)=5", ind["I5 Theorem A on Fano compositions"]["Fano"]["colourings minus a line, halved"] == 5),
        ("norm 13", ind["I2 cube junction"]["ok"]),
    ]
    fails = [snip for snip, good in rows if snip not in text or not good]
    fails += [t for t in CITED if t not in text]
    return fails, len(rows)


text = TEX.read_text()
fails, nrows = ties(text)
report("3 the note's numbers are the evidence's; every cited ticket is named", not fails, {"quoted numbers": nrows, "failures": fails})

# ---------------------------------------------------------------- 4 compile


def compile_note():
    with tempfile.TemporaryDirectory(prefix="count_note_tex_") as tmp:
        tmp = Path(tmp)
        shutil.copy(TEX, tmp / TEX.name)
        log = ""
        for _ in range(2):
            run = subprocess.run(["pdflatex", "-interaction=nonstopmode", TEX.name], cwd=tmp, capture_output=True, text=True, timeout=300)
            log = run.stdout
        pdf = tmp / TEX.with_suffix(".pdf").name
        good = pdf.exists() and "Output written" in log and "undefined" not in log and "\n!" not in log
        pages = int(log.split("Output written on")[1].split("(")[1].split(" page")[0]) if "Output written on" in log else 0
        if pdf.exists():
            shutil.copy(pdf, TEX.with_suffix(".pdf"))
        return good, pages, "Overfull" in log


good, pages, overfull = compile_note()
report("4 the note compiles", good and pages > 0, {"pages": pages, "overfull boxes": overfull})

# ---------------------------------------------------------------- 5 controls
ctrl = {}
ctrl["a tampered number in the note is caught"] = "80, 31500, 11459396 and 4159886189" in ties(text.replace("4159886188", "4159886189"))[0] \
    or bool(ties(text.replace("4159886188", "4159886189"))[0])
ctrl["a missing quotation is caught"] = bool(ties(text.replace("13120", "13121"))[0])
bad = json.loads(json.dumps(rep))
bad["rows"][4]["matches_frozen_result"] = False
ctrl["a mismatching replay row is caught"] = not replay_ok(bad)
bad = json.loads(json.dumps(ind))
bad["I3 K3,3 through plain braces"]["ok"] = False
ctrl["a failing independent part is caught"] = not ind_ok(bad)
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("replay_driver", HERE / "replay.py")
RP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RP)
sym = section("SEYMOUR-COUNT-20261030-001B", "2")
other = json.loads(json.dumps(sym))
k0 = sorted(other["symbolic"])[0]
other["symbolic"][k0] = other["symbolic"][k0] + " + a0"
ctrl["the hash-order tolerance accepts its own frozen polynomials"] = RP.equivalent("SEYMOUR-COUNT-20261030-001B", "2", sym, sym)
ctrl["the hash-order tolerance rejects a different polynomial"] = not RP.equivalent("SEYMOUR-COUNT-20261030-001B", "2", other, sym)
net = section("TWIST-COUNT-20261030-001A", "5")
bad_net = json.loads(json.dumps(net))
first = sorted(bad_net)[0]
bad_net[first]["failures"] = ["a failure"]
ctrl["the random-signing tolerance rejects a failure"] = not RP.equivalent("TWIST-COUNT-20261030-001A", "5", bad_net, net)
report("5 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact_id": "COUNT-NOTE-20261031-001-P001",
                                                  "status": "Proved" if ok_all else "Failed", "checks": out}, indent=1, default=str) + "\n")
sys.exit(0 if ok_all else 1)
