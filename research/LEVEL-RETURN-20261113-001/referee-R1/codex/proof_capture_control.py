"""Check complete CaDiCaL trace capture with temporary writes kept local."""
import ctypes
import gzip
import json
import pathlib
import tempfile
from pysat.formula import CNF
from pysat.solvers import Cadical195

HERE = pathlib.Path(__file__).resolve().parent / "rigidity"


def main():
    scratch = HERE / "scratch"
    scratch.mkdir(exist_ok=True)
    tempfile.tempdir = str(scratch)
    clauses = CNF(from_file=str(HERE / "reduced-L08.cnf"))
    solver = Cadical195(bootstrap_with=clauses.clauses, with_proof=True)
    assert solver.solve() is False
    assert ctypes.CDLL(None).fflush(None) == 0
    proof = solver.get_proof()
    assert any(line.strip() == "0" for line in proof)
    with gzip.open(HERE / "cadical-L08-control.drup.gz", "wt") as f:
        f.write("\n".join(proof) + "\n")
    result = {"solver": "Cadical195", "C_stream_flush_before_get_proof": True,
              "proof_lines": len(proof), "contains_empty": True,
              "temporary_directory": str(scratch), "independent_check": "pending"}
    (HERE / "proof_capture_control.json").write_text(json.dumps(result, indent=2) + "\n")
    solver.delete()
    scratch.rmdir()
    print(json.dumps(result))


if __name__ == "__main__": main()
