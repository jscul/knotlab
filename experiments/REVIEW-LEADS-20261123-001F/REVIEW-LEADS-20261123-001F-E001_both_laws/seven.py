"""Structure 2: the seven-knot source (GENERATORS-20261120-001, 25 distinctions)
to 8 parent steps or 300 knots, all three arms."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import both_laws as B
import structure_run

if __name__ == "__main__":
    structure_run.run("seven", B.seven_source(), 8, 300)
