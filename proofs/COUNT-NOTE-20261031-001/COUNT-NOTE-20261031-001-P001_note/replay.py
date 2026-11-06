"""Replay driver for the note 'Counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence graphs'.

Copies every proof the note cites, and every proof directory they import from or bind by hash, into a temporary directory with the
same relative layout. Reruns each cited check there with --write, in dependency order, and compares each fresh result.json with the
frozen one, ignoring timing fields. After each comparison the frozen result.json is put back, so that later checks, which bind earlier
results by hash, see the frozen files. The repository is never written, except replay_result.json here with --write.

Two cited checks depend on Python's per-run hash order: SEYMOUR-COUNT-20261030-001B labels the two weights of a child square in that
order, and TWIST-COUNT-20261030-001A draws random signings. For those two sections the comparison is by equivalence (see TOLERATED), and
the row records what was tolerated.

Standard library plus sympy (for one equivalence). Run with the Python that has the checks' packages (the workspace .venv):
    .venv/bin/python -B replay.py [--write]"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

# (ticket, what the note uses it for), in dependency order
CITED = [
    ("SEYMOUR-COUNT-20261030-001A", "the trisum law (Theorem 8)"),
    ("SEYMOUR-COUNT-20261030-001B", "weighted Berman determinants, polynomial counting (Proposition 9, Theorem 1)"),
    ("TWIST-COUNT-20261030-001A", "the similitude, unbranched twists (Theorems 11 and 2)"),
    ("TWIST-COUNT-20261030-001B", "no exact crossover, soft crossings (Proposition 12)"),
    ("SOFT-CROSS-20261031-001A", "snakes, the lattice condition, universality (Lemma 13, Theorem 14)"),
    ("SOFT-CROSS-20261031-001B", "the source reduction, hardness under signings (Theorem 3)"),
    ("SOFT-CROSS-20261031-001C", "end to end through certified Pfaffian instances (Theorem 3)"),
    ("PLAIN-COUNT-20261031-001A", "signs are path lengths, hardness without signs (Lemma 15, Theorem 4)"),
    ("PLAIN-COUNT-20261031-001B", "plain pages twisted, the Fano plane among braces (Propositions 16, 17)"),
    ("PLAIN-BRACE-20261031-001A", "the ladder site and the cube junction (Lemmas 18, 19)"),
    ("PLAIN-BRACE-20261031-001B", "weaving, the cube junction lemma, hardness on braces (Lemma 20, Theorem 5)"),
]
IGNORED_KEYS = {"seconds"}
TOLERATED = {
    ("SEYMOUR-COUNT-20261030-001B", "2"): "symbolic weighted determinants equal up to exchanging the two weights of child squares, which are "
                                          "labelled in hash order",
    ("TWIST-COUNT-20261030-001A", "5"): "random signings: per instance the number of signings of each kind, the sizes and the (empty) failure "
                                        "lists agree; which random signings come out branched varies",
}


def section_of(path):
    """the section number of a difference path /checks/<n ...>/..."""
    parts = path.split("/")
    return parts[2].split(" ")[0] if len(parts) > 2 and parts[1] == "checks" else None


def equivalent(ticket, sec, fresh, frozen):
    """the tolerated equivalence for one section's detail"""
    if ticket == "SEYMOUR-COUNT-20261030-001B":
        import itertools
        import sympy as sp
        fs, zs = fresh["symbolic"], frozen["symbolic"]
        if set(fs) != set(zs):
            return False
        names = {k.split(", lean")[0] for k in fs}
        for name in names:
            keys = [k for k in fs if k.startswith(name + ", lean")]
            syms = {v: sp.Symbol(v) for v in ("a0", "b0", "a1", "b1")}
            ok = False
            for perm in ((0, 1), (1, 0)):
                for swap in itertools.product((False, True), repeat=2):
                    sub = {}
                    for i in (0, 1):
                        j = perm[i]
                        a, b = syms[f"a{j}"], syms[f"b{j}"]
                        sub[syms[f"a{i}"]], sub[syms[f"b{i}"]] = (b, a) if swap[i] else (a, b)
                    if all(sp.expand(sp.sympify(fs[k], locals=syms).subs(sub, simultaneous=True) - sp.sympify(zs[k], locals=syms)) == 0
                           for k in keys):
                        ok = True
            if not ok:
                return False
        rest_f = {k: v for k, v in fresh.items() if k != "symbolic"}
        rest_z = {k: v for k, v in frozen.items() if k != "symbolic"}
        return not diff(rest_f, rest_z)
    if ticket == "TWIST-COUNT-20261030-001A":
        if set(fresh) != set(frozen):
            return False
        for inst in fresh:
            a, b = fresh[inst], frozen[inst]
            if a.get("failures") != [] or b.get("failures") != [] or a.get("vertices") != b.get("vertices") \
                    or a.get("planar leaves") != b.get("planar leaves"):
                return False
            kinds = lambda d: {k.split(" / ")[0]: sum(v for kk, v in d["signings"].items() if kk.split(" / ")[0] == k.split(" / ")[0])
                               for k in d["signings"]}  # noqa: E731
            if kinds(a) != kinds(b):
                return False
        return True
    return False
TICKET = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{8}-\d{3}[A-Z]")


def proof_dir(ticket):
    hits = sorted((ROOT / "proofs" / ticket).glob(f"{ticket}-P001_*"))
    assert len(hits) == 1, (ticket, hits)
    return hits[0]


def needed():
    """cited tickets, plus every ticket directory named in their own files (check, libraries) or bound by their manifests"""
    out = set(t for t, _ in CITED)
    for t, _ in CITED:
        d = proof_dir(t)
        text = "".join(p.read_text(errors="ignore") for p in d.glob("*.py"))
        text += " ".join(json.loads((d / "manifest.json").read_text()).get("parent_bindings", {}))
        out |= {u for u in TICKET.findall(text) if (ROOT / "proofs" / u).is_dir()}
    return sorted(out)


def diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k in IGNORED_KEYS:
                continue
            if k not in a or k not in b:
                out.append(f"{path}/{k}: present in only one")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: lengths {len(a)} and {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
        return out
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def main():
    t0 = time.time()
    rows = []
    dirs = needed()
    with tempfile.TemporaryDirectory(prefix="count_note_replay_") as tmp:
        tmp = Path(tmp)
        for t in dirs:
            src = proof_dir(t)
            shutil.copytree(src, tmp / src.relative_to(ROOT), ignore=shutil.ignore_patterns("__pycache__"))
        for ticket, use in CITED:
            src = proof_dir(ticket)
            dst = tmp / src.relative_to(ROOT)
            t1 = time.time()
            run = subprocess.run([sys.executable, "-B", "check.py", "--write"], cwd=dst, capture_output=True, text=True, timeout=7200)
            fresh = json.loads((dst / "result.json").read_text()) if (dst / "result.json").exists() else None
            frozen = json.loads((src / "result.json").read_text())
            differences = diff(fresh, frozen) if fresh is not None else ["no fresh result.json"]
            tolerated = []
            for sec in sorted({section_of(d_) for d_ in differences} - {None}):
                if (ticket, sec) in TOLERATED:
                    key = [k for k in fresh["checks"] if k.startswith(sec + " ")][0]
                    if fresh["checks"][key]["ok"] and frozen["checks"][key]["ok"] and \
                            equivalent(ticket, sec, fresh["checks"][key]["detail"], frozen["checks"][key]["detail"]):
                        differences = [d_ for d_ in differences if section_of(d_) != sec]
                        tolerated.append(TOLERATED[(ticket, sec)])
            shutil.copy(src / "result.json", dst / "result.json")         # later checks bind the frozen result by hash
            row = {"ticket": ticket, "used_for": use, "exit_code": run.returncode,
                   "last_line": (run.stdout.strip().splitlines() or [""])[-1],
                   "fresh_status": fresh.get("status") if fresh else None,
                   "matches_frozen_result": not differences, "tolerated": tolerated, "differences": differences[:20],
                   "seconds": round(time.time() - t1, 1)}
            rows.append(row)
            flag = "ok " if run.returncode == 0 and not differences and row["fresh_status"] == "Proved" else "BAD"
            print(f"{flag} {ticket:30s} {row['seconds']:7.1f} s  {row['last_line']}" + ("  (tolerated: hash order)" if tolerated else ""),
                  flush=True)
            if run.returncode != 0:
                print(run.stderr[-2000:])
    ok = all(r["exit_code"] == 0 and r["matches_frozen_result"] and r["fresh_status"] == "Proved" for r in rows)
    summary = {"schema_version": 1, "artifact_id": "COUNT-NOTE-20261031-001-P001",
               "replay": "every cited check rerun in a temporary copy and compared with its frozen result, timing ignored",
               "copied_directories": dirs, "ok": ok, "seconds": round(time.time() - t0, 1), "rows": rows}
    if "--write" in sys.argv:
        (HERE / "replay_result.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print("ALL OK" if ok else "FAILURES", summary["seconds"], "s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
