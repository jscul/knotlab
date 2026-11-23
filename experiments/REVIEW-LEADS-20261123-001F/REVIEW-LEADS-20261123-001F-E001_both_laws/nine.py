"""Structure 3: the nine-knot drawn source (READS-HOLDERS-SOURCES-20261120-001C,
39 distinctions) to 6 parent steps or 300 knots, all three arms."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import both_laws as B
import structure_run

if __name__ == "__main__":
    structure_run.run("nine", B.nine_source(), 6, 300)
