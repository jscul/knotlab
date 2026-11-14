"""Replay retained fresh rigidity proofs (run standalone, two processes max)."""
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CHECKER = HERE / "certificates/check_rup_fast"


def main():
    records = []
    for path in sorted((HERE / "rigidity").glob("reduced-L*.json")):
        record = json.loads(path.read_text())
        if record["sat_second_state"] is False:
            result = subprocess.run([str(CHECKER), str(HERE / record["cnf"]),
                                     str(HERE / record["proof"])],
                                    text=True, capture_output=True, timeout=600)
            check = json.loads(result.stdout)
            assert result.returncode == 0 and check["valid"], (result.stdout, result.stderr)
            record["independent_proof_check"] = check
            path.write_text(json.dumps(record, indent=2) + "\n")
        records.append(record)
    (HERE / "rigidity/verified_results.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps({"certified_rigid_levels": [r["level"] for r in records
                       if r.get("independent_proof_check", {}).get("valid")],
                      "nonrigid_levels": [r["level"] for r in records
                       if r["sat_second_state"] is True]}))


if __name__ == "__main__":
    main()
