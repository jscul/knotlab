"""READ-RULE task 4: exact supplied families and read-only CARRY entry points.

This module writes no result files and starts no processes.  The caller owns
execution scheduling and serialization.  In particular the original CARRY
direct search is used unchanged, including its size-six exclusion boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CARRY = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex"
GADGET_SOURCE = ROOT / "experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.py"
VARIANTS = ("a_repeated_argument", "b_positive_gadget")
_CARRY_MODULES = None


def variant_rows():
    """Return fresh rows in the census's compact raw-definition key format.

    Local indices: a,b,c=0,1,2 and own u,x,w=3,4,5.  In b the gadget's
    own distinctions are 6,7,8.  The four positive gadget calls reproduce
    gadget_control.gadget(0,3,6,7,8), without importing that script's
    top-level computation and output-file write.
    """
    common = [["K", [0, 4, 1]], ["K", [2, 4, 5]], ["SELF", [0, 3, 4]]]
    inequality = {
        VARIANTS[0]: (3, [["K", [0, 3, 3]]]),
        VARIANTS[1]: (6, [["K", [0, 3, 6]], ["K", [0, 3, 7]],
                         ["K", [0, 3, 8]], ["K", [6, 7, 8]]]),
    }
    rows = {}
    for variant in VARIANTS:
        own, calls = inequality[variant]
        defs = [[3, own, calls + common]]
        key = json.dumps(defs, separators=(",", ":"), ensure_ascii=True)
        rows[variant] = dict(variant=variant, key=key, defs=defs, S=0, main=0,
                             main_equals_S=True, own_names=["u", "x", "w"] +
                             (["gadget_u", "gadget_v", "gadget_w"] if own == 6 else []))
    return rows


def _carry_modules():
    """Use original modules, rejecting rather than overriding name conflicts."""
    global _CARRY_MODULES
    if _CARRY_MODULES is None:
        for name in ("inputs", "scope", "window", "brute", "direct"):
            existing = sys.modules.get(name)
            if existing is not None and Path(getattr(existing, "__file__", "")).resolve() != CARRY / (name + ".py"):
                raise RuntimeError(f"CARRY import name {name!r} already refers to another module")
        sys.path.insert(0, str(CARRY))
        try:
            window = importlib.import_module("window")
            direct = importlib.import_module("direct")
        finally:
            sys.path.remove(str(CARRY))
        _CARRY_MODULES = window, direct
    return _CARRY_MODULES


def source_hashes():
    """Hashes of the direct entry points and exact gadget source used here."""
    paths = [Path(__file__).resolve(), GADGET_SOURCE]
    paths += [CARRY / name for name in ("window.py", "direct.py", "brute.py", "inputs.py", "scope.py")]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run_window(variant):
    """Run the original per-family window and all original growth tests."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown counterexample variant {variant!r}")
    window, _ = _carry_modules()
    row = variant_rows()[variant]
    try:
        answer = window.run_family(row["key"], include_growth=True)
    except (ValueError, AssertionError, IndexError, TypeError) as exc:
        # A rejected repeated argument is a recorded unsupported input, not
        # permission to replace the prescribed family or change the parser.
        answer = dict(key=row["key"], status="not_computed", invalid=True,
                      reason=f"{type(exc).__name__}: {exc}",
                      ambiguity="Does the original shared machinery admit this prescribed raw family?")
    return dict(variant=variant, operation="window_growth", result=answer)


def run_direct(variant, s, **limits):
    """Run unchanged direct.run_case; exact minima can be at most six."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown counterexample variant {variant!r}")
    _, direct = _carry_modules()
    row = variant_rows()[variant]
    try:
        answer = direct.run_case(row, s, **limits)
    except (ValueError, AssertionError, IndexError, TypeError) as exc:
        answer = dict(key=row["key"], s=int(s), status="not_computed", minimum=None,
                      reason=f"{type(exc).__name__}: {exc}",
                      ambiguity="Does the original shared machinery admit this prescribed raw family?")
    return dict(variant=variant, operation="direct", s=int(s), result=answer)


def cases(*, depths=range(1, 7), include_window=True):
    """Small shared-runner-compatible case sequence; no work is run here."""
    depths = tuple(int(s) for s in depths)
    if len(set(depths)) != len(depths) or any(s not in range(1, 7) for s in depths):
        raise ValueError("direct depths must be a distinct subset of 1..6")
    for variant in VARIANTS:
        if include_window:
            yield variant + ":window_growth", dict(variant=variant, operation="window_growth")
        for s in depths:
            yield f"{variant}:direct:s={s}", dict(variant=variant, operation="direct", s=s)


def run(case_id, payload):
    """Execute one original entry point; runner/caller serializes the answer."""
    variant, operation = payload["variant"], payload["operation"]
    if operation == "window_growth" and case_id == variant + ":window_growth":
        return run_window(variant)
    if operation == "direct" and case_id == f"{variant}:direct:s={int(payload['s'])}":
        return run_direct(variant, int(payload["s"]))
    raise ValueError("counterexample case ID/payload mismatch")


def q3_from_results(records):
    """Three-valued Q3, derived only from actual supplied result records.

    An overall failure follows any observed contradiction; otherwise missing,
    capped or size-excluded cells remain undecided, with no extrapolation.
    """
    by_variant = {name: dict(direct={}) for name in VARIANTS}
    for record in records:
        target = by_variant[record["variant"]]
        if record["operation"] == "window_growth":
            target["window_growth"] = record["result"]
        elif record["operation"] == "direct":
            target["direct"][int(record["s"])] = record["result"]
    checks = []
    for variant in VARIANTS:
        measured = by_variant[variant]
        wr = measured.get("window_growth", {})
        window = wr.get("window", {})
        status = ("pass" if window.get("complete") and window.get("verdict") == "none"
                  else "fail" if window.get("verdict") in ("bounded", "progressions")
                  else "undecided")
        checks.append(dict(variant=variant, check="window_no_bound", status=status))
        cert = wr.get("growth", {}).get("G", {})
        status = ("fail" if cert.get("certified") else "pass"
                  if cert and cert.get("complete", True) and not cert.get("cap") else "undecided")
        checks.append(dict(variant=variant, check="G_no_certificate", status=status))
        exact = {s: row["minimum"] for s, row in measured["direct"].items()
                 if row.get("status") == "exact_minimum" and isinstance(row.get("minimum"), int)}
        if variant == VARIANTS[0]:
            for s in range(1, 7):
                status = "undecided" if s not in exact else "pass" if exact[s] == s + 3 else "fail"
                checks.append(dict(variant=variant, check="direct_s_plus_3", s=s,
                                   expected=s + 3, observed=exact.get(s), status=status))
        else:
            for s in range(2, 7):
                pair = (exact.get(s - 1), exact.get(s))
                status = "undecided" if None in pair else "pass" if pair[1] >= pair[0] + 1 else "fail"
                checks.append(dict(variant=variant, check="direct_growth_at_least_one", s=s,
                                   observed=list(pair), status=status))
    status = "fail" if any(c["status"] == "fail" for c in checks) else "pass" if all(
        c["status"] == "pass" for c in checks) else "undecided"
    return dict(status=status, checks=checks,
                evidence_scope="Original finite-window and finite-reading direct searches only; no extrapolated L(s).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--operation", choices=("window_growth", "direct"), required=True)
    parser.add_argument("--depth", type=int, choices=range(1, 7))
    args = parser.parse_args()
    if args.operation == "direct":
        if args.depth is None:
            parser.error("--depth is required for direct")
        answer = run_direct(args.variant, args.depth)
    else:
        if args.depth is not None:
            parser.error("--depth only applies to direct")
        answer = run_window(args.variant)
    print(json.dumps(answer, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
