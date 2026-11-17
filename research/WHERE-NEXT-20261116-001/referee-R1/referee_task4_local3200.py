"""Task 4: local n = 3200 (window 10, alpha = 4.0), the referee's Novelty+, probSAT and WalkSAT with the
study's re-tuned (and, where different, training-tuned) parameters on the study's 100 test instances
(seeds 3,500,000 + i), two runs each, cap 4e8; compared with the study's same-arm runs as in task 1."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import referee_task1_reference as T1  # noqa: E402

if __name__ == "__main__":
    T1.main(cells=[("local", 3200)], reps=2, out_name="referee_task4_local3200.json", task="4 local n = 3200")
