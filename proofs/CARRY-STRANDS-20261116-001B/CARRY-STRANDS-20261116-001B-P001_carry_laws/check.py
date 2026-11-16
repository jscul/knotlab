"""Checks for CARRY-STRANDS-20261116-001B-P001 (proof.md beside this file).

Reruns the experiment's gates: w = 1 is the forcing law; every law ends in
the closure; spend-only phases are ceil(sigma / w) (Theorem 1) and the
doubling rounds are at least the largest sigma (Theorem 2) on 400 random
patterns; keeping and more carried distinctions never add phases; the ladder
is forced in one phase with two carried distinctions and keeping, and in
ceil((k + 1) / 2) spend-only phases (Theorem 3).
    python3 -B check.py
"""
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GATES = os.path.join(ROOT, "experiments", "CARRY-STRANDS-20261116-001A", "CARRY-STRANDS-20261116-001A-E001_carried", "gates.py")

if __name__ == "__main__":
    runpy.run_path(GATES, run_name="__main__")
