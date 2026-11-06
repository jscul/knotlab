"""Checks for COPRIME-PAIRS-20261027-001B-P001 (the corrected and expanded presentation).

  1 every artifact the presentation cites is closed: proofs Proved (result.json and ticket status), experiments supported
  2 frozen predecessors unchanged: SHA256 of the reviewed proof files (and the reviewed presentation) equal the recorded hashes
  3 the corrections replay: Fox normalization on random braids; the integer-exponent cable map with theta' of order 6; the
    parity-automorphism example; the reversed Artin identity; J_(-1) equals the earlier J
  4 the text: artifact index, correction items, replaced wordings only in correction context, reference tags defined and used
Run: python3 -B check.py [--write]"""
import glob, hashlib, json, os, re, sys, time
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*"))[0])
sys.path.insert(1, glob.glob(os.path.join(ROOT, "experiments/COPRIME-DICHOTOMY-20261027-001B/*E002_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
from cd_lib import BraidAlg, Grp, CyclicBraidModel, GLie, braid_meta, criterion, root_of_unity, nullspace  # noqa: E402
import gd  # noqa: E402  (read-only)
import mlib  # noqa: E402  (read-only)
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:700], flush=True)


PROOFS = ["COPRIME-CLASS2-20261026-001B", "COPRIME-CLASS2-20261026-001C", "COPRIME-CLASS2-20261026-001D",
          "CLASSK-DICHOTOMY-20261026-001A", "CLASSK-DICHOTOMY-20261026-001C", "BEYOND-CLASS2-20261027-001A",
          "BEYOND-CLASS2-20261027-001C", "TRIPLE-SYSTEM-20261027-001A", "TRIPLE-SYSTEM-20261027-001C",
          "COPRIME-DICHOTOMY-20261027-001A", "COPRIME-DICHOTOMY-20261027-001C", "COPRIME-DICHOTOMY-20261027-001D",
          "COPRIME-PAIRS-20261027-001A"]
EXPERIMENTS = {"COPRIME-DICHOTOMY-20261027-001B": "E002", "CLASSK-DICHOTOMY-20261026-001B": "E001",
               "BEYOND-CLASS2-20261027-001B": "E001", "TRIPLE-SYSTEM-20261027-001B": "E001"}
rows, ok = {}, True
for T in PROOFS:
    P = glob.glob(os.path.join(ROOT, f"proofs/{T}/*P001_*"))[0]
    res = json.load(open(os.path.join(P, "result.json")))
    st = res.get("status") or ("Proved" if res.get("checks", {}).get("all_ok") else "?")
    tk = json.load(open(os.path.join(ROOT, f"tickets/{T}.json")))
    rows[T] = {"result": st, "ticket": tk.get("status_class")}
    ok &= st == "Proved" and tk.get("status_class") == "proved"
for T, e in EXPERIMENTS.items():
    A = glob.glob(os.path.join(ROOT, f"artifacts/{T}/*{e}_*"))[0]
    res = json.load(open(os.path.join(A, "result.json")))
    tk = json.load(open(os.path.join(ROOT, f"tickets/{T}.json")))
    rows[f"{T} {e}"] = {"verdict": res.get("verdict"), "ticket": tk.get("status_class")}
    ok &= res.get("verdict") == "supported" and tk.get("status_class") == "supported"
report("1 cited artifacts closed", ok, rows)

REVIEWED = {("CLASSK-DICHOTOMY-20261026-001C", "proof.md"): "0b88b4489c92a29eca9af2bdd7f20ca9e33a69285b90be7e5835dbee7b875712",
            ("BEYOND-CLASS2-20261027-001C", "proof.md"): "be25c1edfd295370ad575d4d5e180297d9278a255985a01f550977a62f98d0de",
            ("TRIPLE-SYSTEM-20261027-001A", "proof.md"): "1095b10af6f43cf56fae612406932d55a7eeb8bda12e18d4d9dbd671d59d01bb",
            ("TRIPLE-SYSTEM-20261027-001C", "proof.md"): "e9cd7ca956ea77a0fc032b1c80b102fad691cf19fe264f0470049dc9de6977a4",
            ("COPRIME-DICHOTOMY-20261027-001A", "proof.md"): "57e54adb3e1800f4ce4981ef9df93e1f3776042a506b5fe2ccd19883ac66ec43",
            ("COPRIME-DICHOTOMY-20261027-001C", "proof.md"): "5b9239dcc54447ac9da65bbcb400a0e156e3dba0e045c08409b4f3f70139ee40",
            ("COPRIME-DICHOTOMY-20261027-001D", "presentation.md"): "16c6e2c38ae4457de7a26910e852e83317982d8dc312a962f538f4b0b91a1d59"}
rows, ok = {}, True
for (T, f), h in REVIEWED.items():
    P = glob.glob(os.path.join(ROOT, f"proofs/{T}/*P001_*"))[0]
    got = hashlib.sha256(open(os.path.join(P, f), "rb").read()).hexdigest()
    rows[f"{T}/{f}"] = got == h
    ok &= got == h
report("2 frozen predecessors unchanged", ok, rows)

rows, ok = {}, True
rng = np.random.default_rng(27)
bad, tested = 0, 0
for (p, d) in [(7, 3), (13, 4), (11, 5)]:
    zeta = root_of_unity(p, d)
    A = BraidAlg(gd.four_way(p, d, 1), zeta)
    nb = 0
    while nb < 5:
        n = int(rng.integers(2, 6))
        word = [int(rng.integers(1, n)) * int(rng.choice([1, -1])) for _ in range(int(rng.integers(3, 12)))]
        try:
            M = CyclicBraidModel(word, n, A, p)
        except AssertionError:
            continue
        nb += 1
        for c in range(1, d):
            t = pow(zeta, c, p)
            pred = pow(t, p - 2, p) * (gd.bur_word(word, n, t, p) - np.eye(n, dtype=np.int64)) % p
            bad += int((M.Lin[c][:n] % p != pred).any()); tested += 1
rows["Fox rows = t^-1 (Bur_t - I)"] = f"{tested - bad}/{tested}"
ok &= bad == 0 and tested > 0
p, d, k = 13, 12, 2
zeta = root_of_unity(p, d)
Rset = [c for c in range(1, d) if pow(zeta, c * k, p) == p - 1]
L = gd.four_way(p, d, 3)
G = Grp(BraidAlg(L, zeta))
U = [kk for kk in range(L.D) if int(L.chars[kk]) % d in Rset]
Av = np.zeros((8, L.D), dtype=np.int64); Av[:, U] = rng.integers(0, p, (8, len(U)))
word = [1] * p
assert len(nullspace((gd.bur_word(word, 2, p - 1, p) - np.eye(2, dtype=np.int64)) % p, p)) == 2
gens = [(np.zeros_like(Av), k), (Av % p, k)]               # c(x0) = 0, c(x1) = 1: a sign-twisted cocycle
cur, overs = list(gens), {}
for l, g in enumerate(word):
    a, b = cur[0], cur[1]
    overs[l] = a
    cur[0], cur[1] = G.mul(G.mul(G.inv(a), b), a), a
rel = all(G.mul(G.inv(gens[j]), cur[j])[1] == 0 and not (G.mul(G.inv(gens[j]), cur[j])[0] % p).any() for j in range(2))
order, writhe = braid_meta(word, 2)
lam = (np.zeros_like(Av), 0)
for l in order: lam = G.mul(lam, overs[l])
for _ in range(writhe): lam = G.mul(lam, G.inv(gens[0]))
rows["integer-exponent map (d = 12, k = 2, theta' of order 6)"] = {"root characters": Rset, "order": d // int(np.gcd(k, d)),
                                                                   "relators hold": bool(rel),
                                                                   "longitude -> 1": bool(lam[1] == 0 and not (lam[0] % p).any())}
ok &= rel and lam[1] == 0 and not (lam[0] % p).any() and d // int(np.gcd(k, d)) == 6
L1 = GLie(7, 3, ["e"], [1], [1], np.zeros((1, 1, 1), dtype=np.int64), check=False)
ex = criterion(L1)
rows["one-dimensional algebra over F_7, order-3 action: criterion holds"] = bool(ex)
ok &= bool(ex)
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
rows["reversed Artin identity"] = f"{rev}/40"
rows["forward identity fails"] = fwd_fail
rows["J_(-1) equals the earlier J (n <= 12)"] = bool(Jok)
ok &= rev == 40 and fwd_fail > 0 and Jok
report("3 corrections replay", ok, rows)

txt = open(os.path.join(HERE, "presentation.md")).read()
lines = txt.splitlines()
missing = [T for T in PROOFS + list(EXPERIMENTS) if T not in txt]
items = ["Artin product order", "Sector count", "Lemma I is per fixed group", "Channel terms", "Interpretation", "Process",
         "Parity automorphism", "Fox normalization", "The cable exponent", "The edge-weight lemma", "Canonical pinned coordinates",
         "Reading strands and the basis"]
missing_items = [c for c in items if f"**{c}" not in txt]
contexts = {"collaps": ("corrected", "replaced", "Not a collapse"), "I − Bur_t": ("not I − Bur_t",),
            "θ′^{ψ": (), "depend on the κ_t": ("withdrawn", "asserted")}
bad_lines = []
for key, allowed in contexts.items():
    for i, ln in enumerate(lines):
        if key in ln and not any(a in ln for a in allowed):
            bad_lines.append((i + 1, key))
used = set(re.findall(r"\[([A-Z][A-Za-z]{1,3})(?=[,\]])", txt))
defined = set(re.findall(r"^- \*\*\[([A-Za-z]+)\]\*\*", txt, flags=re.M))
body = "\n".join(ln for ln in lines if not re.match(r"^- \*\*\[[A-Za-z]+\]\*\*", ln))
used_body = set(re.findall(r"\[([A-Z][A-Za-z]{1,3})(?=[,\]])", body))
review_status = "None is a human" in txt and "formal certification" in txt and "independent AI review" in txt
ok = not missing and not missing_items and not bad_lines and used_body <= defined and defined <= used_body and review_status
report("4 presentation text", ok, {"tickets missing": missing, "correction items missing": missing_items,
                                   "replaced wordings outside correction context": bad_lines,
                                   "tags used but undefined": sorted(used_body - defined),
                                   "tags defined but unused": sorted(defined - used_body), "reference tags": len(defined),
                                   "reviews recorded as AI reviews, not human or formal": review_status,
                                   "characters": len(txt)})
out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-PAIRS-20261027-001B-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T0, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
