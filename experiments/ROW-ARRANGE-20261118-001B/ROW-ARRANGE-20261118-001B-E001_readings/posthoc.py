"""Post hoc (after the frozen read-out, labelled as such): the bases behind the failing groups of N1 at n = 8, B6 at n = 7 and
B8 at n = 8, with their splits."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import readings as RD  # noqa: E402

ART = HERE.parents[2] / "artifacts/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings"


def show(m, n):
    return "".join(chr(97 + i) for i in range(n) if m >> i & 1) + "|" + "".join(chr(97 + i) for i in range(n) if not m >> i & 1)


canon, lv = RD.CB.reachable("one-split", 8)
out = {}
for n, name, f in ((8, "N1", RD.read_N1), (7, "B6", lambda D: RD.read_B(D, 6)), (8, "B8", lambda D: RD.read_B(D, 8))):
    groups = {}
    for c in lv[n]:
        st = list(canon.reps[c][0])
        groups.setdefault(RD.intern(f(RD.table(st, n))), []).append(st)
    mixed = []
    for g in groups.values():
        if len(g) > 1:
            kl = [RD.targets(st, n) for st in g]
            if len({k for k, _ in kl}) > 1:
                mixed.append([{"k": k, "lam": l, "N": len(st), "splits": [show(m, n) for m in RD.R.splits(st, n)]}
                              for st, (k, l) in zip(g, kl)])
    out[f"{name} at n = {n}"] = mixed
    print(name, n, len(mixed))
    for g in mixed[:2]:
        for b in g:
            print("  ", b)
json.dump(out, open(ART / "posthoc.json", "w"), indent=1)
