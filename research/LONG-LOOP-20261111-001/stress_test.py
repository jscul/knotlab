"""Stress test one size past LONG-LOOP-20261111-001A-E001: the frozen census code, unchanged, on every 6-regular torus with 81 to 96
distinctions and Klein bottle with 41 to 48. Writes stress/census.json and stress/census_log.txt beside this file."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "LONG-LOOP-20261111-001A", "LONG-LOOP-20261111-001A-E001_long_loops"))
import census
census.TORUS_V = range(81, 97)
census.KLEIN_V = range(41, 49)
census.OUT = os.path.join(HERE, "stress")
census.main()
