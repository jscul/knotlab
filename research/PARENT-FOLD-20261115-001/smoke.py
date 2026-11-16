"""Exercise the public edit interface on trial indices excluded from every study split."""
from pathlib import Path
import sys
from time import process_time_ns

NOTES = Path(__file__).resolve().parent
ROOT = NOTES.parents[1]
HERE = ROOT / "experiments" / NOTES.name / (NOTES.name + "-E001_consumer_edits")
JOINT = ROOT / "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
sys.path[:0] = [str(HERE), str(NOTES), str(JOINT)]


def main():
    from panels import PLAN, _candidate
    from parent_engine import Parent, ordinary
    from parent_checker import Checker
    from fold import fold
    from controls import ordinary_exact
    from wire_return import attach_physical
    from job import PUBLIC_HISTORY
    for m, slot in ((7, 0), (9, 3)):
        case, roles = _candidate("oracle", m, PLAN["oracle"][1][0], slot, -10)
        for solver, name in ((ordinary, "ordinary"), (fold, "fold"), (ordinary_exact, "ordinary-exact")):
            started = process_time_ns()
            parent = Parent({k:case[k] for k in PUBLIC_HISTORY})
            checker = Checker(case)
            hint = tuple(roles["anchor"]) if name == "fold" else None
            rows = []
            for edit in [None, *case["edits"]]:
                state = parent.edit({k:edit[k] for k in ("gate","pin","to")} if edit else None)
                result, _ = solver(state, hint)
                packet = attach_physical(case, result)
                checker.verify(edit, packet)
                rows.append(packet["width"])
            print(name, m, rows, "cpu_ms", round((process_time_ns()-started)/1e6,3))


if __name__ == "__main__":
    main()
