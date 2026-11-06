"""Checks for COPRIME-DICHOTOMY-20261027-001D-P001 (the consolidated presentation).

  1 every artifact the presentation cites is closed: proofs Proved (result.json and ticket status), experiments supported
  2 frozen predecessors unchanged: SHA256 of the proof files equal the hashes recorded by the independent reviews
  3 the corrections replay: the reversed Artin identity holds and the forward one fails (free group); J_t at t = -1 is the form J
    of BEYOND-CLASS2-20261027-001C (lower unitriangular, 2(-1)^(q-q') below the diagonal)
  4 the presentation's artifact index covers every cited ticket, and its corrections section names each correction
Run: python3 -B check.py [--write]"""
import glob, hashlib, json, os, re, sys, time
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "experiments/COPRIME-DICHOTOMY-20261027-001B/*E002_*"))[0])
sys.path.insert(1, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
import gd  # noqa: E402  (read-only)
import mlib  # noqa: E402  (read-only)
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:600], flush=True)


PROOFS = ["COPRIME-CLASS2-20261026-001B", "COPRIME-CLASS2-20261026-001C", "COPRIME-CLASS2-20261026-001D",
          "CLASSK-DICHOTOMY-20261026-001A", "CLASSK-DICHOTOMY-20261026-001C", "BEYOND-CLASS2-20261027-001A",
          "BEYOND-CLASS2-20261027-001C", "TRIPLE-SYSTEM-20261027-001A", "TRIPLE-SYSTEM-20261027-001C",
          "COPRIME-DICHOTOMY-20261027-001A", "COPRIME-DICHOTOMY-20261027-001C"]
EXPERIMENTS = {"COPRIME-DICHOTOMY-20261027-001B": "E002", "CLASSK-DICHOTOMY-20261026-001B": "E001",
               "BEYOND-CLASS2-20261027-001B": "E001", "TRIPLE-SYSTEM-20261027-001B": "E001"}
rows, ok = {}, True
for T in PROOFS:
    P = glob.glob(os.path.join(ROOT, f"proofs/{T}/*P001_*"))[0]
    res = json.load(open(os.path.join(P, "result.json")))
    st = res.get("status") or ("Proved" if res.get("checks", {}).get("all_ok") else "?")
    tk = json.load(open(os.path.join(ROOT, f"tickets/{T}.json")))
    good = st == "Proved" and tk.get("status_class") == "proved"
    rows[T] = {"result": st, "ticket": tk.get("status_class")}
    ok &= good
for T, e in EXPERIMENTS.items():
    A = glob.glob(os.path.join(ROOT, f"artifacts/{T}/*{e}_*"))[0]
    res = json.load(open(os.path.join(A, "result.json")))
    tk = json.load(open(os.path.join(ROOT, f"tickets/{T}.json")))
    rows[f"{T} {e}"] = {"verdict": res.get("verdict"), "ticket": tk.get("status_class")}
    ok &= res.get("verdict") == "supported" and tk.get("status_class") == "supported"
report("1 cited artifacts closed", ok, rows)

REVIEWED = {"CLASSK-DICHOTOMY-20261026-001C": "0b88b4489c92a29eca9af2bdd7f20ca9e33a69285b90be7e5835dbee7b875712",
            "BEYOND-CLASS2-20261027-001C": "be25c1edfd295370ad575d4d5e180297d9278a255985a01f550977a62f98d0de",
            "TRIPLE-SYSTEM-20261027-001A": "1095b10af6f43cf56fae612406932d55a7eeb8bda12e18d4d9dbd671d59d01bb",
            "TRIPLE-SYSTEM-20261027-001C": "e9cd7ca956ea77a0fc032b1c80b102fad691cf19fe264f0470049dc9de6977a4"}
rows, ok = {}, True
for T, h in REVIEWED.items():
    P = glob.glob(os.path.join(ROOT, f"proofs/{T}/*P001_*"))[0]
    got = hashlib.sha256(open(os.path.join(P, "proof.md"), "rb").read()).hexdigest()
    rows[T] = got == h
    ok &= got == h
report("2 frozen predecessors unchanged", ok, rows)

rng = np.random.default_rng(2026)
rev = fwd_fail = 0
for _ in range(40):
    n = int(rng.integers(2, 7))
    word = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(1, 11)))]
    img = mlib.artin(word, n)
    R = [mlib.red([(j, -1)] + img[j]) for j in range(n)]
    a, b = [], []
    for j in range(n - 1, -1, -1):
        P = [(q, 1) for q in range(n - 1, j - 1, -1)]
        a += P + R[j] + mlib.inv(P)
    for j in range(n):
        P = [(q, 1) for q in range(0, j + 1)]
        b += P + R[j] + mlib.inv(P)
    rev += int(not mlib.red(a)); fwd_fail += int(bool(mlib.red(b)))
Jok = True
for n in range(2, 13):
    J = gd.squier(n, -1, 10 ** 9 + 7)
    Jb = np.array([[1 if q == q2 else (2 * (-1) ** (q - q2) if q > q2 else 0) for q2 in range(n)] for q in range(n)], dtype=np.int64)
    Jok &= not ((J - Jb) % (10 ** 9 + 7)).any()
report("3 corrections replay", rev == 40 and fwd_fail > 0 and Jok,
       {"reversed identity": f"{rev}/40", "forward identity fails": fwd_fail, "J_(-1) equals the earlier J (n <= 12)": Jok})

txt = open(os.path.join(HERE, "presentation.md")).read()
missing = [T for T in PROOFS + list(EXPERIMENTS) if T not in txt]
corr = ["Artin product order", "Sector count", "Lemma I is per fixed group", "Channel terms", "Interpretation", "Process"]
missing_corr = [c for c in corr if c not in txt]
report("4 presentation index and corrections", not missing and not missing_corr,
       {"tickets missing from the presentation": missing, "corrections missing": missing_corr, "characters": len(txt)})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-DICHOTOMY-20261027-001D-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T0, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
