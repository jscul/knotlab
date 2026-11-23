"""Shared code for REVIEW-LEADS-20261123-001G-E001 (does repeated release need a failing pattern?).

Frozen definitions: research/REVIEW-LEADS-20261123-001G/preregistration.md.  Nothing here changes a definition.

Reused by import, not rewritten (sources named at each use):
  * ticket A's code, experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test/lib.py:
    the growth driver `grow` (around the recorded engine end_operator.step of ORDINARY-DYNAMICS-20261120-001A, both laws),
    the pattern `incidence_graph`, the test `passes`, `first_failing_stage`, `growth_kind`;
  * the recorded populations and verdicts of READS-HOLDERS-SOURCES-20261120-001C (edits.json, draws.jsonl, certificates.json)
    and that study's own generators (edits.py edit_population, survey.py draw_specs), loaded by path.
"""
import json
import signal
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUT = ROOT / "artifacts" / TICKET / HERE.name

A_DIR = ROOT / "experiments/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test"
A_OUT = ROOT / "artifacts/REVIEW-LEADS-20261123-001A/REVIEW-LEADS-20261123-001A-E001_operator_test"
sys.path.insert(0, str(A_DIR))
import lib as A  # noqa: E402  (ticket A's code; its OUT is never written here)

RHS = "READS-HOLDERS-SOURCES-20261120-001C"
RHS_EXP = ROOT / "experiments" / RHS / f"{RHS}-E001_repeated_release"
RHS_ART = ROOT / "artifacts" / RHS / f"{RHS}-E001_repeated_release"

LAWS = ("parity", "nae")
HORIZON, CAP = 12, 5000          # pre-registration, "Horizon": 12 parent steps or 5,000 knots
GROW_SECONDS = 240               # resource limit per growth (outcome 'time' if reached); fixed before any start was read
CERT_SECONDS = 60                # resource limit for the forbidden sub-pattern of one stage


class Slow(Exception):
    pass


def _alarm(signum, frame):
    raise Slow()


def with_alarm(seconds, fn, *args, **kwargs):
    """Run fn under a wall-clock alarm; returns (value, None) or (None, 'not finished in N s')."""
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn(*args, **kwargs), None
    except Slow:
        return None, f"not finished in {seconds} s"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def dump(path, rows, mode="w"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode) as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")


def load_populations():
    return json.loads((OUT / "populations.json").read_text())
