#!/usr/bin/env python3
"""Check TSEITIN-NS-DEGREE-NOTE-20261020-001-P001: the note on the Nullstellensatz degree of Tseitin formulas.

- replay.py imports only the standard library, runs in an isolated interpreter, and passes every check on
  all ten graphs.
- The note's table, parsed from the source, matches the replay: vertices, edges, treewidth, cutwidth, the
  degree outside characteristic 2 (by direct elimination over F3, equal to the toggle width and to
  cutwidth + 1) and the degree 3 over F2.
- The note's other numbers match the replay: the Sherali-Adams example (its edge list, line-graph treewidth
  4, cutwidth 5, degree 6 against 5), the +-1 degrees (cutwidth after reduction, toggle width + 1 before),
  and K4 and K33 sharing treewidth 3 with different degrees.
- The roster is as the note describes it: ten connected cubic graphs; K4; the two six-vertex cubic graphs;
  five pairwise non-isomorphic eight-vertex ones (the known number), among them the cube and the Wagner
  graph; and the Petersen graph, recognized as the cubic graph on ten vertices of girth 5.
- The note compiles with pdflatex, without errors, warnings or overfull lines, and a stored PDF carries the
  same text as a fresh build (PDFs are git-ignored in this repository).
- The parent bindings in manifest.json match the files.

Five controls tamper with a table entry, a replay value, a number in a remark, a parent digest and the
roster; each must be caught.

    python3 -B check.py          verify result.json (and any stored PDF) against a fresh run
    python3 -B check.py --write  write them from a fresh run
"""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NOTE = HERE / "note"
TEX = NOTE / "tseitin_ns_degree.tex"
TABLE_NAMES = {"$K_4$": "K4", "triangular prism": "prism", "$K_{3,3}$": "K33", "cube $Q_3$": "cube",
               "Wagner graph": "wagner", "Petersen graph": "petersen"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def replay_graphs() -> dict[str, list[tuple[int, int]]]:
    spec = importlib.util.spec_from_file_location("note_replay", HERE / "replay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return copy.deepcopy(module.GRAPHS)


def standard_library_only() -> bool:
    tree = ast.parse((HERE / "replay.py").read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add((node.module or "").split(".")[0])
    return bool(names) and names <= set(sys.stdlib_module_names)


def run_replay() -> tuple[int, dict, float]:
    start = time.monotonic()
    run = subprocess.run([sys.executable, "-B", "-I", str(HERE / "replay.py")], capture_output=True, text=True,
                         timeout=3600)
    seconds = time.monotonic() - start
    lines = run.stdout.strip().splitlines()
    return run.returncode, (json.loads(lines[-1]) if lines else {}), seconds


# ---------------------------------------------------------------- the note against the replay

def table_rows(tex: str) -> dict[str, list[int]]:
    body = tex[tex.index("\\midrule"):tex.index("\\bottomrule")]
    rows = {}
    for line in body.splitlines()[1:]:
        line = line.strip()
        if line.endswith("\\\\"):
            cells = [cell.strip() for cell in line[:-2].split("&")]
            rows[TABLE_NAMES[cells[0]]] = [int(cell) for cell in cells[1:]]
    return rows


def table_ok(tex: str, graphs: dict) -> bool:
    try:
        rows = table_rows(tex)
    except (KeyError, ValueError):
        return False
    if sorted(rows) != sorted(TABLE_NAMES.values()):
        return False
    for name, cells in rows.items():
        g = graphs[name]
        if cells != [g["vertices"], g["edges"], g["treewidth"], g["cutwidth"], g["direct_F3_degree"], 3]:
            return False
        if not (g["direct_F3_degree"] == g["toggle_width"] == g["cutwidth"] + 1
                and g["checks"]["direct F2 degree is 3"]):
            return False
    return True


def remarks_ok(tex: str, graphs: dict, edges: dict) -> bool:
    text = flat(tex)
    c10 = graphs["cubic10"]
    listed = ",".join(f"{a}{b}" for a, b in edges["cubic10"])
    sherali_adams = (
        f"edges ${listed}$" in text
        and f"the line graph has treewidth ${c10['line_graph_treewidth']}$ while $\\cw={c10['cutwidth']}$" in text
        and (f"Nullstellensatz needs degree ${c10['direct_F3_degree']}$ there, while Sherali--Adams refutes at "
             f"degree ${c10['line_graph_treewidth'] + 1}$") in text
        and c10["line_graph_treewidth"] + 1 < c10["direct_F3_degree"])
    pm1 = ("the replay finds degree $\\cw(G)$ after reduction and $\\tgw(G)+1$ before" in text
           and all(g["pm1_reduced_degree"] == g["cutwidth"] and g["pm1_unreduced_degree"] == g["toggle_width"] + 1
                   for g in graphs.values()))
    caption = ("$K_4$ and $K_{3,3}$ both have treewidth~$3$" in text
               and graphs["K4"]["treewidth"] == graphs["K33"]["treewidth"] == 3
               and graphs["K4"]["direct_F3_degree"] != graphs["K33"]["direct_F3_degree"])
    return sherali_adams and pm1 and caption


# ---------------------------------------------------------------- the roster

def adjacency(edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    adj: dict[int, set[int]] = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    return adj


def connected_cubic(edges: list[tuple[int, int]]) -> bool:
    adj = adjacency(edges)
    simple = len({frozenset(e) for e in edges}) == len(edges) and all(a != b for a, b in edges)
    seen, stack = {0}, [0]
    while stack:
        for y in adj[stack.pop()]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return simple and set(adj) == set(range(len(adj))) and len(seen) == len(adj) and all(
        len(n) == 3 for n in adj.values())


def canonical(edges: list[tuple[int, int]]) -> tuple:
    n = 1 + max(max(e) for e in edges)
    return min(tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges)) for p in permutations(range(n)))


def girth(edges: list[tuple[int, int]]) -> int:
    adj, best = adjacency(edges), 10 ** 9
    for root in adj:
        depth, parent, queue = {root: 0}, {root: None}, [root]
        for x in queue:
            for y in adj[x]:
                if y not in depth:
                    depth[y], parent[y] = depth[x] + 1, x
                    queue.append(y)
                elif parent[x] != y:
                    best = min(best, depth[x] + depth[y] + 1)
    return best


def bipartite(edges: list[tuple[int, int]]) -> bool:
    adj, colour = adjacency(edges), {0: 0}
    queue = [0]
    for x in queue:
        for y in adj[x]:
            if y not in colour:
                colour[y] = 1 - colour[x]
                queue.append(y)
            elif colour[y] == colour[x]:
                return False
    return True


def roster_ok(edges: dict) -> bool:
    if len(edges) != 10 or not all(connected_cubic(e) for e in edges.values()):
        return False
    by_size: dict[int, list[str]] = {}
    for name, e in edges.items():
        by_size.setdefault(len(adjacency(e)), []).append(name)
    if {k: len(v) for k, v in by_size.items()} != {4: 1, 6: 2, 8: 5, 10: 2}:
        return False
    cube = [(a, a ^ (1 << i)) for a in range(8) for i in range(3) if a < a ^ (1 << i)]
    wagner = [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]
    eight = {name: canonical(edges[name]) for name in by_size[8]}
    return (len(set(eight.values())) == 5
            and eight["cube"] == canonical(cube) and eight["wagner"] == canonical(wagner)
            and bipartite(edges["K33"]) and girth(edges["prism"]) == 3
            and girth(edges["petersen"]) == 5 and girth(edges["cubic10"]) < 5)


# ---------------------------------------------------------------- the PDF and the bindings

def build_pdf(outdir: Path) -> dict[str, object]:
    for _ in range(2):
        run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={outdir}",
                              TEX.name], cwd=NOTE, capture_output=True, text=True, timeout=600)
    pdf, log_path = outdir / "tseitin_ns_degree.pdf", outdir / "tseitin_ns_degree.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    pages = None
    if pdf.exists():
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    return {"built": run.returncode == 0 and pdf.exists(), "pages": pages,
            "latex_warnings": len(re.findall(r"Warning", log)),
            "overfull_boxes": len(re.findall(r"Overfull \\[hv]box", log))}


def pdf_text(pdf: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout


def bindings_ok(manifest: dict) -> bool:
    bindings = manifest["parent_bindings"]
    return bool(bindings) and all((ROOT / p).exists() and sha256(ROOT / p) == d for p, d in bindings.items())


# ---------------------------------------------------------------- run

def run(write: bool) -> dict[str, object]:
    manifest = json.loads((HERE / "manifest.json").read_text())
    tex = TEX.read_text()
    edges = replay_graphs()
    checks: dict[str, object] = {}
    controls: dict[str, bool] = {}

    checks["replay_imports_only_the_standard_library"] = standard_library_only()
    code, summary, seconds = run_replay()
    graphs = summary.get("graphs", {})
    checks["replay_exit_status_zero"] = code == 0
    checks["replay_passed_on_all_ten_graphs"] = summary.get("passed") is True and sorted(graphs) == sorted(edges)
    checks["replay_runs_within_two_minutes"] = seconds < 120
    checks["replay_summary"] = graphs
    checks["note_table_matches_replay"] = table_ok(tex, graphs)
    checks["note_remarks_match_replay"] = remarks_ok(tex, graphs, edges)
    checks["roster_as_described"] = roster_ok(edges)
    checks["parent_bindings_match"] = bindings_ok(manifest)

    with tempfile.TemporaryDirectory() as tmp:
        report = build_pdf(Path(tmp))
        checks["pdf"] = report
        checks["pdf_builds_cleanly"] = (report["built"] and report["latex_warnings"] == 0
                                        and report["overfull_boxes"] == 0)
        fresh, kept = Path(tmp) / "tseitin_ns_degree.pdf", NOTE / "tseitin_ns_degree.pdf"
        if write and fresh.exists():
            shutil.copyfile(fresh, kept)
        # PDFs are git-ignored here; compare only a local copy
        checks["stored_pdf_matches_source"] = not kept.exists() or (fresh.exists() and pdf_text(kept) == pdf_text(fresh))

    petersen_row = re.search(r"Petersen graph & 10 & 15 & 4 & 6 & 7 & 3\\\\", tex)
    controls["tampered_table_entry_caught"] = petersen_row is not None and not table_ok(
        tex.replace(petersen_row.group(0), petersen_row.group(0).replace("& 7 & 3", "& 8 & 3")), graphs)
    broken = copy.deepcopy(graphs)
    broken["cubic10"]["direct_F3_degree"] = 5
    controls["tampered_replay_value_caught"] = not remarks_ok(tex, broken, edges)
    controls["tampered_remark_number_caught"] = not remarks_ok(
        tex.replace("Sherali--Adams refutes at degree $5$", "Sherali--Adams refutes at degree $6$"), graphs, edges)
    forged = copy.deepcopy(manifest)
    first = next(iter(forged["parent_bindings"]))
    forged["parent_bindings"][first] = "0" * 64
    controls["tampered_parent_digest_caught"] = not bindings_ok(forged)
    swapped = copy.deepcopy(edges)
    swapped["cubic8-c"] = [(7 - a, 7 - b) for a, b in edges["cube"]]
    controls["duplicated_roster_graph_caught"] = not roster_ok(swapped)

    expected_true = ["replay_imports_only_the_standard_library", "replay_exit_status_zero",
                     "replay_passed_on_all_ten_graphs", "replay_runs_within_two_minutes",
                     "note_table_matches_replay", "note_remarks_match_replay", "roster_as_described",
                     "parent_bindings_match", "pdf_builds_cleanly", "stored_pdf_matches_source"]
    failures = [name for name in expected_true if checks.get(name) is not True]
    failures += [f"control {name}" for name, ok in controls.items() if not ok]
    return {"checks": checks, "controls": controls, "failures": failures}


def main() -> int:
    write = "--write" in sys.argv[1:]
    outcome = run(write)
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3,
        "artifact_id": manifest["artifact_id"],
        "kind": "proof",
        "ticket": manifest["ticket"],
        "proof": manifest["proof"],
        "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"],
        "controls": outcome["controls"],
        "failures": outcome["failures"],
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: {len(outcome['checks'])} checks, "
          f"{sum(outcome['controls'].values())}/{len(outcome['controls'])} controls caught tampering")
    for failure in outcome["failures"]:
        print(f"  failed: {failure}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
