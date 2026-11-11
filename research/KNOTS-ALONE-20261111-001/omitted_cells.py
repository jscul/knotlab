"""Supplement to KNOTS-ALONE-20261111-001A-E001, after the referee: the two registered non-surface cells (d, V) = (6, 6) and
(7, 6) that the frozen census.py dropped through an unregistered filter d <= V - 1. Same generator, size and seed rule as the
frozen code (60 per cell, seed 20261111 + 100 d + V), NAE by SAT, PAR by GF(2), OR and NOL by SAT, brute force cross-check.
Writes omitted_cells.json beside this file."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census"))
import knots_alone as ka
out = {}
for d, V in ((6, 6), (7, 6)):
    worlds = [T for T in ka.random_regular_worlds_sat(V, d, 60, seed=20261111 + 100 * d + V) if not ka.is_surface(V, T)]
    cell = {"sampled": len(worlds), "mismatches": 0}
    for law in ("NAE", "PAR", "OR", "NOL"):
        cell[law + " native"] = 0
    cell["NAE faithful"] = 0
    for T in worlds:
        r = {"NAE": ka.read_law_sat(V, T, ka.LAWS["NAE"]), "PAR": ka.read_parity_gf2(V, T),
             "OR": ka.read_law_sat(V, T, ka.LAWS["OR"]), "NOL": ka.read_law_sat(V, T, ka.LAWS["NOL"])}
        for law, res in r.items():
            b = ka.read_law_brute(V, T, ka.LAWS[law])
            if any(b.get(k) != res.get(k) for k in res if k != "states"):
                cell["mismatches"] += 1
            cell[law + " native"] += bool(res.get("native"))
        cell["NAE faithful"] += bool(r["NAE"].get("faithful"))
    out[f"d={d}, V={V}"] = cell
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "omitted_cells.json"), "w"), indent=1)
