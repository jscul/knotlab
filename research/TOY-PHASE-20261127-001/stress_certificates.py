"""stress_certificates.py: the toy-against-stabilizer test one size past the closure (TOY-PHASE-20261127-001).

The four-readings study stored a signed Pauli certificate for each of its 115 holder patterns that admit an operator
reading (79 of them on patterns ordinary growth closes): for every distinction an operator i^phase X^x Z^z, held by exactly
two holders, with the operators of each holder commuting and multiplying to plus or minus the identity, the signs' product
odd. For each certificate this script checks, with its own code:
  - the certificate: within each holder the operators commute and their product is +-I; the product of the signs is -1;
  - the toy reading (the phases dropped, each operator read as the toy question (x, z) of the same toy bits): within each
    holder the questions pairwise commute and sum to zero, so every holder's law is even for every toy state;
  - the gap: the sign of the product of all holders' operators, taken holder by holder, is the certificate's charge, and
    it equals the cost of bringing each distinction's two occurrences together (-1 for each anticommuting pair whose
    occurrences interleave).
Run from the repository root: .venv/bin/python -B research/TOY-PHASE-20261127-001/stress_certificates.py
"""
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parents[1] / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"


def par(x):
    return bin(x).count("1") % 2


def mul(a, b):
    """(phase, x, z) for i^phase X^x Z^z; the product of a then b."""
    pa, xa, za = a
    pb, xb, zb = b
    # Z^za X^xb = (-1)^{za.xb} X^xb Z^za
    return ((pa + pb + 2 * par(za & xb)) % 4, xa ^ xb, za ^ zb)


def commute(a, b):
    return par(a[1] & b[2]) == par(a[2] & b[1])


def main():
    census = json.loads(CENSUS.read_text())
    rows = []
    for t, entry in enumerate(census):
        cert = entry["pauli_i_phase_X_bits_Z_bits"]
        if not entry["operator"]:
            continue
        ops = [tuple(o) for o in cert]
        holders = {}
        for d, pair in enumerate(entry["sharing"]):
            for h in pair:
                holders.setdefault(h, []).append(d)
        signs, toy_even, toy_commute, cert_commute = [], True, True, True
        for h in sorted(holders):
            ds = holders[h]
            prod = (0, 0, 0)
            for d in ds:
                prod = mul(prod, ops[d])
            assert prod[1] == 0 and prod[2] == 0 and prod[0] % 2 == 0, (t, h, prod)
            signs.append(1 if prod[0] == 0 else -1)
            cert_commute &= all(commute(ops[a], ops[b]) for a, b in itertools.combinations(ds, 2))
            x = z = 0
            for d in ds:
                x, z = x ^ ops[d][1], z ^ ops[d][2]
            toy_even &= (x == 0 and z == 0)
            toy_commute &= all(par(ops[a][1] & ops[b][2]) == par(ops[a][2] & ops[b][1]) for a, b in itertools.combinations(ds, 2))
        charge = 1
        for s in signs:
            charge *= s
        # the cost of reordering: list the occurrences holder by holder, then count interleaved anticommuting pairs
        listing = [d for h in sorted(holders) for d in holders[h]]
        where = {}
        for i, d in enumerate(listing):
            where.setdefault(d, []).append(i)
        cost = 0
        for a, b in itertools.combinations(range(len(ops)), 2):
            if commute(ops[a], ops[b]):
                continue
            i, k = where[a]
            j, l = where[b]
            cost += (i < j < k < l) or (j < i < l < k)
        rows.append({"type": t, "holders": len(holders), "distinctions": len(ops), "grown": bool(entry["restored_last_holders"]),
                     "certificate holders commute": cert_commute, "certificate charge": charge,
                     "toy questions commute within holders": toy_commute, "toy laws even in every holder": toy_even,
                     "reordering cost": (-1) ** cost})
    out = {
        "certificates": len(rows), "on grown types": sum(r["grown"] for r in rows),
        "certificate holders commute (all)": all(r["certificate holders commute"] for r in rows),
        "certificate charge -1 (all)": all(r["certificate charge"] == -1 for r in rows),
        "toy questions commute within holders (all)": all(r["toy questions commute within holders"] for r in rows),
        "toy laws even in every holder (all)": all(r["toy laws even in every holder"] for r in rows),
        "reordering cost equals the charge (all)": all(r["reordering cost"] == r["certificate charge"] for r in rows),
        "rows": rows,
    }
    (HERE / "stress_certificates.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k != "rows"})


if __name__ == "__main__":
    main()
