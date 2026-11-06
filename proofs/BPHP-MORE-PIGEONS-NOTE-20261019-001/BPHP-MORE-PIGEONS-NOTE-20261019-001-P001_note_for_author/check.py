#!/usr/bin/env python3
"""Check BPHP-MORE-PIGEONS-NOTE-20261019-001-P001: the note for Braun and its drop-in Lean file.

- The drop-in file is the kernel file of HOLE-CRITERION-COLOURING-20261019-001B-P001
  character for character after its header comment.
- Copied into the claims folder of the pinned checkout, it builds as a module of
  the author's library, and its eight theorems use only the standard axioms.
- Every formalization file it can depend on, and the build pins, are unchanged
  at the newest commit checked; the only differences are added files and two
  documentation files.
- The note quotes the formal statements exactly (lean_statements.txt is
  extracted from the drop-in file), its theorem constants match the Lean
  statements, and its numbers are recomputed here.
- The replay summary's figures are those recorded by
  BPHP-RES-PARITY-AUDIT-20261019-001.
- Both PDFs build with xelatex, and any stored PDF carries the same text as a
  fresh build (PDFs are git-ignored in this repository).

Four controls tamper with a quoted statement, a summary figure, the drop-in
body and a number in the note; each must be caught.

    python3 -B check.py          verify result.json, lean_statements.txt and the PDFs against a fresh run
    python3 -B check.py --write  write them from a fresh run
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NOTE = HERE / "note"
CHECKOUT = Path("/home/jscul/external-audits/bit-php-check")
FORMAL = CHECKOUT / "formalization"
TMP = FORMAL / ".lake" / "audit_controls"
DROP_IN = HERE / "MorePigeonsColouring.lean"
SOURCE = ROOT / ("proofs/HOLE-CRITERION-COLOURING-20261019-001B/"
                 "HOLE-CRITERION-COLOURING-20261019-001B-P001_more_pigeons_and_colouring/MorePigeonsColouring.lean")
AUDIT_A = ROOT / "artifacts/BPHP-RES-PARITY-AUDIT-20261019-001A/BPHP-RES-PARITY-AUDIT-20261019-001A-E001_formal_replay"
AUDIT_B = ROOT / ("proofs/BPHP-RES-PARITY-AUDIT-20261019-001B/"
                  "BPHP-RES-PARITY-AUDIT-20261019-001B-P001_definitional_fidelity")
THEOREMS = tuple(f"MorePigeonsColouring.{name}" for name in (
    "bitPHP_more_pigeons", "colouring_refutation_transfer", "bitColouring_more_pigeons", "range_nonempty",
    "usualBitPHP_unsat_more", "bitColouring_unsat", "bitColouring_sat", "complete_graph_is_bitPHP"))
QUOTED = ("structure Graph", "def bitColouringInitials", "theorem bitPHP_more_pigeons",
          "theorem colouring_refutation_transfer", "theorem bitColouring_more_pigeons")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
DOCS = {"formalization/AGENTS.md", "formalization/README.md"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(CHECKOUT), *args], capture_output=True, text=True).stdout.strip()


def body(text: str) -> str:
    """The file after its leading header comment."""
    assert text.startswith("/-\n")
    return text[text.index("\n-/\n") + 4:]


def statements(text: str) -> str:
    """The quoted declarations: each with its docstring, a theorem up to its `:=`."""
    lines = text.splitlines()
    blocks = []
    for head in QUOTED:
        start = next(i for i, line in enumerate(lines) if line.startswith(head + " ") or line.startswith(head + "\n")
                     or line == head)
        first = start
        if lines[start - 1].rstrip().endswith("-/"):
            first = start - 1
            while not lines[first].startswith("/--"):
                first -= 1
        if head.startswith("theorem"):
            end = next(i for i in range(start, len(lines)) if re.search(r":=( by)?$", lines[i]))
            block = lines[first:end] + [re.sub(r"\s*:=( by)?$", "", lines[end])]
        else:
            end = next(i for i in range(start, len(lines)) if not lines[i].strip())
            block = lines[first:end]
        blocks.append("\n".join(block))
    return "\n\n".join(blocks) + "\n"


def numbers() -> dict[str, object]:
    def in_range(m: int, l: int) -> bool:
        return 8192 * m * l * l * (2 * l + 5) <= (2 ** l) ** 2
    top = (2 ** 32) ** 2 // (8192 * 32 * 32 * (2 * 32 + 5))
    return {
        "top_at_32": top,
        "top_at_32_tex": f"{top:,}".replace(",", "{,}"),
        "ratio_at_32": f"{top / 2 ** 32:.2f}",
        "two_n_in_range_from": next(l for l in range(32, 300) if all(in_range(2 * 2 ** j, j) for j in range(l, 300))),
        "n_three_halves_in_range_from": next(l for l in range(32, 300)
                                             if all(in_range(isqrt((2 ** j) ** 3), j) for j in range(l, 300))),
    }


def note_numbers_ok(tex: str, nums: dict[str, object]) -> bool:
    flat = re.sub(r"\s+", " ", tex)
    return (nums["top_at_32_tex"] in flat and f"\\approx {nums['ratio_at_32']}" in flat
            and nums["two_n_in_range_from"] == 32 and "$m=2n$ is in range for every $\\ell\\ge32$" in flat
            and f"in range for every $\\ell\\ge{nums['n_three_halves_in_range_from']}$" in flat)


def constants_ok(tex: str, lean: str) -> bool:
    flat = re.sub(r"\s+", " ", tex)
    note = all(s in flat for s in ("8192\\,m\\,\\ell^2(2\\ell+5)\\le n^2", "\\exp\\bigl(n^2/(8192\\,m\\,\\ell^2)\\bigr)",
                                  "$\\ell\\ge 32$", "$n<m$"))
    formal = all(s in lean for s in ("∀ ℓ ≥ 32, ∀ m : ℕ, 2^ℓ + 1 ≤ m → 8192*m*ℓ^2*(2*ℓ+5) ≤ (2^ℓ)^2",
                                     "Real.exp ((((2^ℓ:ℕ):ℝ))^2/(8192*(m:ℝ)*(ℓ:ℝ)^2)) < (S:ℝ)"))
    return note and formal


def audit_figures() -> dict[str, object]:
    replay = json.loads((AUDIT_A / "result.json").read_text())
    steps = {s["label"]: s for s in replay["steps"]}
    supplementary = json.loads((AUDIT_A / "supplementary_controls.json").read_text())
    log = (AUDIT_A / "replay.log").read_text()
    fidelity = json.loads((AUDIT_B / "result.json").read_text())
    witnesses = (AUDIT_B / "AuditWitnesses.lean").read_text()
    declarations = int(re.search(r"(\d+) audited declarations", replay["verify_pass_line"]).group(1))
    lakefile = (FORMAL / "lakefile.lean").read_text()
    return {
        "declarations": declarations,
        "axioms_standard": replay["all_reported_axioms_standard"] is True,
        "leanchecker_seconds": round(steps["leanchecker_fresh"]["seconds"]),
        "leanchecker_passed": steps["leanchecker_fresh"]["exit"] == 0,
        "statement_control_line": int(re.search(r"MutatedExponential\.lean:(\d+)", log).group(1)),
        "all_constants_line": int(re.search(r":(\d+):\d+: error", supplementary["first_error"]).group(1)),
        "toolchain": replay["toolchain_pin"].split(":")[1],
        "mathlib": re.search(r'"([0-9a-f]{7})[0-9a-f]*"', lakefile).group(1),
        "commit": replay["checkout_commit"][:8],
        "refutation_lines": int(re.search(r"def lines : Fin (\d+)", witnesses).group(1)),
        "witnesses_standard": fidelity["checks"]["witness_axioms_standard"] is True,
        "witness_controls_rejected": all(fidelity["controls"].values()),
        "sorry_detected": replay["control_sorry_detected"] is True,
    }


def summary_ok(tex: str, fig: dict[str, object]) -> bool:
    flat = re.sub(r"\s+", " ", tex)
    expected = [
        f"passed on all {fig['declarations']} audited declarations",
        f"passed ({fig['leanchecker_seconds']}\\,s)",
        f"at line {fig['statement_control_line']} of the altered copy",
        f"fails only at line {fig['all_constants_line']}",
        f"\\texttt{{leanprover/lean4:{fig['toolchain']}}}",
        f"Mathlib \\texttt{{{fig['mathlib']}}}",
        f"Commit \\texttt{{{fig['commit']}}}",
        f"in {fig['refutation_lines']} lines",
    ]
    facts = all(fig[k] for k in ("axioms_standard", "leanchecker_passed", "witnesses_standard",
                                 "witness_controls_rejected", "sorry_detected"))
    return facts and all(s in flat for s in expected)


def build_pdfs(outdir: Path) -> dict[str, object]:
    report = {}
    for name in ("more_pigeons", "replay_summary"):
        run = subprocess.run(["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
                              f"-outdir={outdir}", f"{name}.tex"], cwd=NOTE, capture_output=True, text=True,
                             timeout=600)
        pdf = outdir / f"{name}.pdf"
        log = (outdir / f"{name}.log").read_text(errors="replace") if (outdir / f"{name}.log").exists() else ""
        pages = None
        if pdf.exists():
            info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
            pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        report[name] = {"built": run.returncode == 0 and pdf.exists(), "pages": pages,
                        "missing_characters": len(re.findall(r"Missing character", log)),
                        "overfull_boxes": len(re.findall(r"Overfull \\hbox", log))}
    return report


def pdf_text(pdf: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout


def compile_in_place(source: str) -> tuple[bool, dict[str, list[str]]]:
    target = FORMAL / "claims" / "MorePigeonsColouring.lean"
    assert not target.exists()
    try:
        target.write_text(source)
        built = subprocess.run(["lake", "build", "claims.MorePigeonsColouring"], cwd=FORMAL, capture_output=True,
                               text=True, timeout=3600)
        TMP.mkdir(parents=True, exist_ok=True)
        probe = TMP / "MorePigeonsColouringDropInProbe.lean"
        probe.write_text(source + "".join(f"\n#print axioms {name}" for name in THEOREMS) + "\n")
        printed = subprocess.run(["lake", "env", "lean", str(probe)], cwd=FORMAL, capture_output=True, text=True,
                                 timeout=3600)
    finally:
        target.unlink(missing_ok=True)
        for leftover in (FORMAL / ".lake" / "build").rglob("MorePigeonsColouring.*"):
            if "claims" in leftover.parts:
                leftover.unlink()
    used: dict[str, list[str]] = {}
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", re.sub(r"\n\s+", " ", printed.stdout)):
        used[match.group(1)] = sorted(a.strip() for a in match.group(2).split(",") if a.strip())
    return built.returncode == 0 and printed.returncode == 0, used


def run(write: bool) -> dict[str, object]:
    manifest = json.loads((HERE / "manifest.json").read_text())
    pin, newest = manifest["audited_source"]["commit"], manifest["audited_source"]["newest_commit_checked"]
    checks: dict[str, object] = {}
    controls: dict[str, bool] = {}

    checks["checkout_is_pinned_commit"] = git("rev-parse", "HEAD") == pin
    checks["checkout_has_no_tracked_changes"] = git("status", "--porcelain", "--untracked-files=no") == ""
    checks["relied_on_files_match_digests"] = all(
        sha256(FORMAL / name) == digest for name, digest in manifest["audited_source"]["files"].items())

    drop_in, source = DROP_IN.read_text(), SOURCE.read_text()
    checks["drop_in_body_is_B_P001"] = body(drop_in) == body(source)
    checks["drop_in_free_of_escapes"] = re.search(
        r"\bsorry\b|\badmit\b|^\s*axiom\b|\bnative_decide\b|\bimplemented_by\b|\bunsafe\b", drop_in, re.M) is None
    compiled, used = compile_in_place(drop_in)
    checks["drop_in_builds_in_claims_folder"] = compiled
    checks["theorem_axioms"] = used
    checks["theorem_axioms_standard"] = set(used) == set(THEOREMS) and all(set(v) <= STANDARD for v in used.values())
    checks["checkout_clean_after_build"] = (git("status", "--porcelain") == ""
                                            and not (FORMAL / "claims" / "MorePigeonsColouring.lean").exists())

    exists = subprocess.run(["git", "-C", str(CHECKOUT), "cat-file", "-e", f"{newest}^{{commit}}"]).returncode == 0
    changes = [line.split("\t") for line in git("diff", "--name-status", pin, newest, "--", "formalization").splitlines()]
    checks["newest_commit_present"] = exists
    checks["newest_changes_only_add_files_or_docs"] = exists and all(
        status == "A" or (status == "M" and path in DOCS) for status, path, *_ in changes)
    checks["newest_added_files"] = sum(1 for status, *_ in changes if status == "A")

    quoted = statements(drop_in)
    stored = NOTE / "lean_statements.txt"
    if write:
        stored.write_text(quoted)
    checks["note_quotes_lean_statements"] = stored.read_text() == quoted
    tex = (NOTE / "more_pigeons.tex").read_text()
    checks["note_constants_match_lean"] = constants_ok(tex, drop_in)
    nums = numbers()
    checks["numbers"] = {k: v for k, v in nums.items() if k != "top_at_32_tex"}
    checks["note_numbers_recomputed"] = note_numbers_ok(tex, nums)
    figures = audit_figures()
    checks["audit_figures"] = figures
    summary = (NOTE / "replay_summary.tex").read_text()
    checks["replay_summary_matches_audit"] = summary_ok(summary, figures)
    cover = (NOTE / "cover_message.txt").read_text()
    checks["cover_message_has_no_personal_address"] = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", cover) is None
    checks["cover_message_unsigned"] = "[Your name]" in cover

    with tempfile.TemporaryDirectory() as tmp:
        report = build_pdfs(Path(tmp))
        checks["pdfs"] = report
        checks["pdfs_build_cleanly"] = all(r["built"] and r["missing_characters"] == 0 for r in report.values())
        consistent = True
        for name in report:
            fresh, kept = Path(tmp) / f"{name}.pdf", NOTE / f"{name}.pdf"
            if write and fresh.exists():
                shutil.copyfile(fresh, kept)
            if kept.exists():  # PDFs are git-ignored here; compare only a local copy
                consistent = consistent and fresh.exists() and pdf_text(kept) == pdf_text(fresh)
        checks["stored_pdfs_match_sources"] = consistent

    controls["tampered_quotation_caught"] = (quoted.replace("8192*(m:ℝ)", "4096*(m:ℝ)", 1) != quoted
                                             and quoted.replace("8192*(m:ℝ)", "4096*(m:ℝ)", 1) != stored.read_text())
    controls["tampered_summary_figure_caught"] = not summary_ok(
        summary.replace(f"line {figures['all_constants_line']}", f"line {figures['all_constants_line'] - 1}"), figures)
    controls["tampered_drop_in_caught"] = body(drop_in.replace("hkpos hkm hsq", "hkpos hkm  hsq", 1)) != body(source)
    controls["tampered_note_number_caught"] = not note_numbers_ok(
        tex.replace(str(nums["top_at_32_tex"]), "31{,}870{,}250{,}457"), nums)

    expected_true = ["checkout_is_pinned_commit", "checkout_has_no_tracked_changes", "relied_on_files_match_digests",
                     "drop_in_body_is_B_P001", "drop_in_free_of_escapes", "drop_in_builds_in_claims_folder",
                     "theorem_axioms_standard", "checkout_clean_after_build", "newest_commit_present",
                     "newest_changes_only_add_files_or_docs", "note_quotes_lean_statements",
                     "note_constants_match_lean", "note_numbers_recomputed", "replay_summary_matches_audit",
                     "cover_message_has_no_personal_address", "cover_message_unsigned", "pdfs_build_cleanly",
                     "stored_pdfs_match_sources"]
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
