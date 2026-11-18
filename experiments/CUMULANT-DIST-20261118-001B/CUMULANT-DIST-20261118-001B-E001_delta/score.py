"""Score the frozen predictions of research/CUMULANT-DIST-20261118-001/preregistration.md."""
import json
import math


def load(art, name):
    p = art / "parts" / f"{name}.json"
    return json.load(open(p))["result"] if p.exists() else None


def main(art):
    pred, res = {}, {}
    lin = load(art, "linear")
    if lin:
        bad = sum(r["mismatch"] for r in lin)
        res["linear"] = {"bases": len(lin), "pairs": sum(r["n"] * (r["n"] - 1) // 2 for r in lin), "mismatched_pairs": bad}
        pred["P1"] = bad == 0
    tr = load(art, "trees")
    if tr:
        bad = sum(r["mismatch"] for r in tr)
        res["trees"] = {"bases": len(tr), "pairs": sum(r["pairs"] for r in tr), "mismatched_pairs": bad,
                        "worst": max(r["worst"] for r in tr), "failing": [r for r in tr if r["mismatch"]][:10]}
        pred["P2"] = bad == 0
    mi = load(art, "mixed_identity")
    if mi:
        res["mixed_identity"] = {"chains": len(mi), "failing": [r for r in mi if not r["ok"]]}
        pred["P3"] = all(r["ok"] for r in mi)
    ns = load(art, "nae_separated")
    if ns:
        res["nae_separated"] = ns
        pred["P4"] = all(r["mismatch"] == 0 for r in ns)
    rg = load(art, "rings")
    if rg:
        par_short = all(any(v["delta"] < v["steps"] - 1e-9 for v in r["table"].values()) for r in rg if r["law"] == "P")
        nae_tau = all(abs(v["delta"] - v["tau"]) < 1e-9 for r in rg if r["law"] == "N" for v in r["table"].values())
        res["rings"] = {"parity_rings_with_a_shorter_pair": par_short, "nae_rings_delta_equals_tau": nae_tau}
        pred["P5"] = par_short and nae_tau
    cp, bu = load(art, "chain_patch"), load(art, "bubble")
    if cp and bu:
        short = [r for r in cp if r["delta"] < r["tau"] - 1e-9]
        res["chain_patch"] = {"pairs": len(cp), "shortcut_pairs": len(short), "examples": short[:5], "bubble": bu["bubble"]}
        pred["P6"] = not short and bu["bubble"] <= 4.5
    wp = load(art, "weave_patch")
    if wp:
        short = [r for r in wp["rows"] if r["delta"] < r["tau"] - 1e-9]
        res["weave_patch"] = {"n": wp["n"], "N": wp["N"], "pairs": len(wp["rows"]), "shortcut_pairs": len(short), "examples": short[:5]}
        pred["P7"] = not short
    sl = load(art, "split_line")
    if sl:
        res["split_line"] = {k: sl[k] for k in ("m", "N", "rotation_maps_states", "asymmetric_cumulants", "cap", "max_delta")}
        pred["P8"] = sl["rotation_maps_states"] and sl["asymmetric_cumulants"] == 0 and abs(sl["max_delta"] - sl["cap"]) < 1e-9
    sg = load(art, "split_grid")
    if sg:
        res["split_grid"] = sg
        pred["P9"] = all(r["neighbour_to_far_corner"] for r in sg)
    res["predictions"] = {k: ("held" if v else "failed") for k, v in pred.items()}
    json.dump(res, open(art / "results.json", "w"), indent=1, default=str)
    for k, v in res["predictions"].items():
        print(k, v)
