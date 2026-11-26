"""Run the copied fixture generator with its retirement filter removed."""

import argparse
from pathlib import Path
import sys


RETIREMENT_CLAUSE = """                            for retire_after in (None, 2, 4):
                                if retire_after is not None and not (steps == 1 and treatment == 'CANCEL-WAIT'):
                                    continue             # the switch is checked on a third of the menu
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generator", type=Path)
    parser.add_argument("public_checkout", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    source = args.generator.read_text()
    assert source.count(RETIREMENT_CLAUSE) == 1
    extended = source.replace(RETIREMENT_CLAUSE, "                            for retire_after in (None, 2, 4, 6):\n")
    namespace = {"__name__": "toy_menu_generator", "__file__": str(args.generator)}
    exec(compile(extended, str(args.generator), "exec"), namespace)
    if args.smoke:
        namespace["PATTERNS"] = ("source",)
    sys.argv = [str(args.generator), "--from", str(args.public_checkout), "--output", str(args.output)]
    namespace["main"]()


if __name__ == "__main__":
    main()
