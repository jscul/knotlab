"""Check for JOINT-RECORDS-20261116-001A-P001: reruns seam.py and requires S1-S4."""
import json
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":
    runpy.run_path(os.path.join(HERE, "seam.py"), run_name="__main__")
    out = json.load(open(os.path.join(HERE, "seam.json")))
    assert all(out[k] for k in ("S1", "S2", "S3", "S4")), "seam checks failed"
    print("check passed")
